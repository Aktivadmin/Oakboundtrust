"""Sign-up email verification (OTP) tests. Run: python manage.py test app"""
from datetime import timedelta
from unittest import mock

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.conf import settings
from django.utils import timezone

from users import otp
from users.models import EmailOTP

User = get_user_model()
FORM = {"firstname": "Ada", "lastname": "Okafor", "email": "ada@example.com", "password": "S3cure-pass!", "confirm-password": "S3cure-pass!",
        "zipcode": "10001", "phone": "+15551234567", "dob": "1990-04-02"}


class CodeCatcher:
    """Replaces the email sender and remembers the last code that would have been emailed."""
    def __init__(self, ok=True):
        self.ok, self.codes, self.sent = ok, [], []

    def __call__(self, template, context, subject, email, reply_to=None):
        self.sent.append((template, email))
        if "code" in context:
            self.codes.append(context["code"])
        return self.ok

    @property
    def last(self):
        return self.codes[-1]


@override_settings(OTP_REQUIRED='true')
class SignupOTPTests(TestCase):
    def setUp(self):
        self.mail = CodeCatcher()
        p1 = mock.patch("users.otp.send_email", self.mail); p2 = mock.patch("app.views.send_email", self.mail)
        p1.start(); p2.start(); self.addCleanup(p1.stop); self.addCleanup(p2.stop)

    def signup(self, **over):
        return self.client.post("/signup/", {**FORM, **over})

    def test_signup_creates_inactive_account_and_sends_a_code(self):
        r = self.signup()
        self.assertRedirects(r, "/verify-email/", fetch_redirect_response=False)
        u = User.objects.get(email="ada@example.com")
        self.assertFalse(u.is_active)
        self.assertIsNone(u.email_verified_at)
        self.assertEqual(len(self.mail.codes), 1)
        self.assertRegex(self.mail.last, r"^\d{6}$")

    def test_code_is_stored_hashed_not_in_plain_text(self):
        self.signup()
        row = EmailOTP.objects.get()
        self.assertNotIn(self.mail.last, row.code_hash)
        self.assertEqual(len(row.code_hash), 64)

    def test_correct_code_activates_logs_in_and_welcomes(self):
        self.signup()
        r = self.client.post("/verify-email/", {"action": "verify", "code": self.mail.last})
        self.assertRedirects(r, "/dashboard/", fetch_redirect_response=False)
        u = User.objects.get(email="ada@example.com")
        self.assertTrue(u.is_active)
        self.assertIsNotNone(u.email_verified_at)
        self.assertEqual(self.client.get("/dashboard/").status_code, 200)         # signed in
        self.assertFalse(EmailOTP.objects.exists())                                # code consumed
        self.assertIn(("emails/welcome.html", "ada@example.com"), self.mail.sent)

    def test_wrong_code_is_rejected_and_account_stays_inactive(self):
        self.signup()
        r = self.client.post("/verify-email/", {"action": "verify", "code": "000000" if self.mail.last != "000000" else "111111"})
        self.assertEqual(r.status_code, 400)
        self.assertFalse(User.objects.get(email="ada@example.com").is_active)

    def test_five_wrong_tries_burn_the_code_even_for_the_right_one(self):
        self.signup()
        wrong = "000000" if self.mail.last != "000000" else "111111"
        for _ in range(5):
            self.client.post("/verify-email/", {"action": "verify", "code": wrong})
        r = self.client.post("/verify-email/", {"action": "verify", "code": self.mail.last})
        self.assertEqual(r.status_code, 400)
        self.assertFalse(User.objects.get(email="ada@example.com").is_active)

    def test_expired_code_is_rejected(self):
        self.signup()
        EmailOTP.objects.update(expires_at=timezone.now() - timedelta(seconds=1))
        r = self.client.post("/verify-email/", {"action": "verify", "code": self.mail.last})
        self.assertEqual(r.status_code, 400)
        self.assertFalse(User.objects.get(email="ada@example.com").is_active)

    def test_a_code_cannot_be_used_twice(self):
        self.signup()
        code = self.mail.last
        self.client.post("/verify-email/", {"action": "verify", "code": code})
        self.client.logout()
        r = self.client.post("/verify-email/", {"action": "verify", "code": code})
        self.assertRedirects(r, "/signup/", fetch_redirect_response=False)       # no pending session any more

    def test_resend_has_a_cooldown_then_issues_a_new_code(self):
        self.signup()
        self.client.post("/verify-email/", {"action": "resend"})
        self.assertEqual(len(self.mail.codes), 1)                                  # blocked: too soon
        EmailOTP.objects.update(last_sent_at=timezone.now() - timedelta(seconds=60))
        self.client.post("/verify-email/", {"action": "resend"})
        self.assertEqual(len(self.mail.codes), 2)

    def test_resend_is_capped_per_hour(self):
        self.signup()
        for _ in range(8):
            EmailOTP.objects.update(last_sent_at=timezone.now() - timedelta(seconds=60))
            self.client.post("/verify-email/", {"action": "resend"})
        self.assertEqual(len(self.mail.codes), otp.MAX_SENDS)

    def test_new_code_replaces_the_old_one(self):
        self.signup(); old = self.mail.last
        EmailOTP.objects.update(last_sent_at=timezone.now() - timedelta(seconds=60))
        self.client.post("/verify-email/", {"action": "resend"})
        new = self.mail.last
        if old != new:
            r = self.client.post("/verify-email/", {"action": "verify", "code": old})
            self.assertEqual(r.status_code, 400)

    def test_login_before_verifying_sends_you_back_to_the_code_page(self):
        self.signup(); self.client.logout()
        r = self.client.post("/login/", {"email": "ada@example.com", "password": FORM["password"]})
        self.assertRedirects(r, "/verify-email/", fetch_redirect_response=False)

    def test_login_with_wrong_password_before_verifying_is_just_invalid(self):
        self.signup(); self.client.logout()
        r = self.client.post("/login/", {"email": "ada@example.com", "password": "nope-nope"})
        self.assertEqual(r.status_code, 401)

    def test_verified_email_cannot_be_registered_again(self):
        self.signup(); self.client.post("/verify-email/", {"action": "verify", "code": self.mail.last}); self.client.logout()
        r = self.signup()
        self.assertEqual(r.status_code, 200)
        self.assertEqual(User.objects.filter(email="ada@example.com").count(), 1)

    def test_unverified_signup_can_be_restarted_without_a_duplicate(self):
        self.signup(); self.client.logout()
        self.signup(firstname="Adaeze")
        self.assertEqual(User.objects.filter(email__iexact="ada@example.com").count(), 1)
        self.assertEqual(User.objects.get(email="ada@example.com").first_name, "Adaeze")

    def test_verify_page_without_a_pending_signup_redirects(self):
        self.assertRedirects(self.client.get("/verify-email/"), "/signup/", fetch_redirect_response=False)

    def test_email_failure_still_lets_the_user_retry(self):
        self.mail.ok = False
        r = self.signup()
        self.assertRedirects(r, "/verify-email/", fetch_redirect_response=False)
        self.mail.ok = True
        self.assertEqual(self.client.post("/verify-email/", {"action": "resend"}).status_code, 302)
        self.assertEqual(len(self.mail.codes), 2)                                  # retry allowed straight away

    def test_existing_active_customers_are_unaffected(self):
        User.objects.create_user(email="old@example.com", password="pw-123456")
        r = self.client.post("/login/", {"email": "old@example.com", "password": "pw-123456"})
        self.assertRedirects(r, "/dashboard/", fetch_redirect_response=False)

    def test_email_is_masked_on_the_page(self):
        self.signup()
        html = self.client.get("/verify-email/").content.decode()
        self.assertIn("a*a@example.com", html)
        self.assertNotIn("ada@example.com", html)

    def test_mask_helper(self):
        self.assertEqual(otp.mask_email("ab@x.com"), "a*@x.com")
        self.assertEqual(otp.mask_email("jonathan@x.com"), "j******n@x.com")


class OTPSwitchTests(TestCase):
    """The code step turns on by itself once email sending exists, and never strands a sign-up before that."""
    def setUp(self):
        p = mock.patch("app.views.send_email", return_value=True); p.start(); self.addCleanup(p.stop)

    @override_settings(OTP_REQUIRED='auto', EMAIL_HOST_USER='', EMAIL_HOST_PASSWORD='')
    def test_auto_without_mail_keeps_signup_working(self):
        with mock.patch.dict("os.environ", {"RESEND_API_KEY": ""}):
            r = self.client.post("/signup/", FORM)
        self.assertRedirects(r, "/login/", fetch_redirect_response=False)
        self.assertTrue(User.objects.get(email="ada@example.com").is_active)

    @override_settings(OTP_REQUIRED='auto')
    def test_auto_with_a_mail_key_enforces_the_code(self):
        with mock.patch.dict("os.environ", {"RESEND_API_KEY": "re_test"}), mock.patch("users.otp.send_email", return_value=True):
            r = self.client.post("/signup/", FORM)
        self.assertRedirects(r, "/verify-email/", fetch_redirect_response=False)
        self.assertFalse(User.objects.get(email="ada@example.com").is_active)

    @override_settings(OTP_REQUIRED='auto', EMAIL_HOST_USER='support@oakboundtrust.com', EMAIL_HOST_PASSWORD='app-pass')
    def test_auto_with_smtp_login_enforces_the_code(self):
        with mock.patch.dict("os.environ", {"RESEND_API_KEY": ""}), mock.patch("users.otp.send_email", return_value=True):
            r = self.client.post("/signup/", FORM)
        self.assertRedirects(r, "/verify-email/", fetch_redirect_response=False)

    @override_settings(OTP_REQUIRED='false', EMAIL_HOST_USER='a', EMAIL_HOST_PASSWORD='b')
    def test_can_be_switched_off(self):
        r = self.client.post("/signup/", FORM)
        self.assertRedirects(r, "/login/", fetch_redirect_response=False)


class SenderTests(TestCase):
    def test_smtp_path_sends_from_the_support_address(self):
        from django.core import mail
        from helpers.views import send_email
        with self.settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend", EMAIL_HOST_USER="support@oakboundtrust.com",
                           EMAIL_HOST_PASSWORD="x", DEFAULT_FROM_EMAIL="support@oakboundtrust.com"), mock.patch.dict("os.environ", {"RESEND_API_KEY": ""}):
            ok = send_email("emails/otp.html", {"name": "Ada", "code": "123456", "minutes": 10}, "Your code", "ada@example.com", reply_to="help@x.com")
        self.assertTrue(ok)
        self.assertEqual(len(mail.outbox), 1)
        m = mail.outbox[0]
        self.assertEqual(m.from_email, "Oakbound Trust Bank <support@oakboundtrust.com>")
        self.assertEqual(m.to, ["ada@example.com"]); self.assertEqual(m.reply_to, ["help@x.com"])
        self.assertIn("123456", m.body); self.assertIn("123456", m.alternatives[0][0])

    def test_no_transport_returns_false_instead_of_crashing(self):
        from helpers.views import send_email
        with self.settings(EMAIL_HOST_USER="", EMAIL_HOST_PASSWORD=""), mock.patch.dict("os.environ", {"RESEND_API_KEY": ""}):
            self.assertFalse(send_email("emails/otp.html", {"code": "1", "minutes": 10}, "x", "a@b.com"))


# ---------------------------------------------------------------------------
# Transfers: receipts, failed-transfer page and the automatic status emails
# ---------------------------------------------------------------------------
from django.template.loader import render_to_string  # noqa: E402

from app.models import Transaction, Withdrawal  # noqa: E402

TRANSFER = {"amount": "250", "acc-no": "0123456789", "acc-name": "Chidi Eze", "swift_code": "OKBNUS33", "bank-name": "First Test Bank",
            "bank-address": "12 Market Street, Lagos", "description": "Rent", "access-code": "555555"}


class TransferFlowTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="sam@example.com", password="pw-123456", first_name="Sam", last_name="Ade", balance=1000.0)
        self.client.login(email="sam@example.com", password="pw-123456")
        self.sent = []
        p1 = mock.patch("app.views.send_email", return_value=True)
        p2 = mock.patch("app.signals.send_email", side_effect=lambda tpl, ctx, subj, to, reply_to=None: self.sent.append((tpl, subj, to, ctx)) or True)
        p1.start(); p2.start(); self.addCleanup(p1.stop); self.addCleanup(p2.stop)

    def send_transfer(self, **over):
        return self.client.post("/withdraw/", {**TRANSFER, **over})

    def tx(self):
        return Transaction.objects.get(user=self.user)

    # --- records and receipt ---
    def test_transfer_links_the_withdrawal_to_its_transaction(self):
        self.send_transfer()
        self.assertEqual(Withdrawal.objects.get().ref, self.tx().ref)

    def test_submitting_a_transfer_does_not_send_a_success_or_decline_email(self):
        self.send_transfer()
        self.assertEqual(self.sent, [])

    def test_receipt_right_after_sending_says_pending_review(self):
        html = self.send_transfer().content.decode()
        self.assertIn("Pending review", html); self.assertNotIn("Successful", html)

    def test_receipt_says_successful_once_approved(self):
        self.send_transfer(); t = self.tx(); t.status = "Approved"; t.save()
        html = self.client.get(f"/receipt/{t.ref}/").content.decode()
        self.assertIn("Successful", html); self.assertNotIn("Pending review", html)
        self.assertIn("Chidi Eze", html); self.assertIn("12 Market Street, Lagos", html); self.assertIn("Local", html)

    def test_receipt_says_declined_once_declined(self):
        self.send_transfer(); t = self.tx(); t.status = "Declined"; t.save()
        html = self.client.get(f"/receipt/{t.ref}/").content.decode()
        self.assertIn("Declined", html); self.assertIn("no money was sent", html)

    def test_receipt_is_private_to_its_owner(self):
        self.send_transfer(); ref = self.tx().ref
        other = User.objects.create_user(email="other@example.com", password="pw-123456")
        self.client.logout(); self.client.login(email="other@example.com", password="pw-123456")
        self.assertEqual(self.client.get(f"/receipt/{ref}/").status_code, 404)
        self.client.logout()
        self.assertEqual(self.client.get(f"/receipt/{ref}/").status_code, 302)       # anonymous: sent to log in

    # --- automatic emails ---
    def test_approving_sends_one_success_email_to_the_customer(self):
        self.send_transfer(); t = self.tx(); t.status = "Approved"; t.save()
        self.assertEqual(len(self.sent), 1)
        tpl, subject, to, ctx = self.sent[0]
        self.assertEqual((tpl, to), ("emails/transfer_success.html", "sam@example.com"))
        self.assertIn("successful", subject); self.assertIn("$250.00", subject)
        self.assertEqual((ctx["recipient"], ctx["bank"], ctx["ref"]), ("Chidi Eze", "First Test Bank", t.ref))

    def test_declining_sends_one_declined_email(self):
        self.send_transfer(); t = self.tx(); t.status = "Declined"; t.save()
        self.assertEqual([s[0] for s in self.sent], ["emails/transfer_declined.html"])

    def test_saving_again_without_a_status_change_sends_nothing_more(self):
        self.send_transfer(); t = self.tx(); t.status = "Approved"; t.save(); t.save(); t.description = "edited"; t.save()
        self.assertEqual(len(self.sent), 1)

    def test_changing_the_withdrawal_status_also_updates_the_transaction_and_emails_once(self):
        self.send_transfer(); w = Withdrawal.objects.get(); w.status = "Approved"; w.save()
        self.assertEqual(self.tx().status, "Approved")
        self.assertEqual(len(self.sent), 1)

    def test_changing_the_transaction_status_keeps_the_withdrawal_in_step_and_emails_once(self):
        self.send_transfer(); t = self.tx(); t.status = "Declined"; t.save()
        self.assertEqual(Withdrawal.objects.get().status, "Declined")
        self.assertEqual(len(self.sent), 1)

    def test_deposits_do_not_trigger_transfer_emails(self):
        d = Transaction.objects.create(user=self.user, amount=100, trans_type="Deposit", status="Pending")
        d.status = "Approved"; d.save()
        self.assertEqual(self.sent, [])

    def test_email_templates_render_with_the_details(self):
        ctx = {"name": "Sam", "amount": "$250.00", "ref": "ab123", "recipient": "Chidi Eze", "bank": "First Test Bank", "date": timezone.now().date(), "site_url": "https://www.oakboundtrust.com"}
        ok = render_to_string("emails/transfer_success.html", ctx); bad = render_to_string("emails/transfer_declined.html", ctx)
        for html in (ok, bad):
            for needle in ("$250.00", "ab123", "Chidi Eze", "First Test Bank", "support@oakboundtrust.com"):
                self.assertIn(needle, html)
        self.assertIn("https://www.oakboundtrust.com/receipt/ab123/", ok)
        self.assertIn("no money was sent", bad)

    # --- the redesigned failure page ---
    def test_wrong_access_code_shows_the_structured_failure_page_and_changes_nothing(self):
        r = self.send_transfer(**{"access-code": "000000"})
        html = r.content.decode()
        for needle in ("Transfer not completed", "Incorrect access code", "No money has left your account", "What you can do", "Try again", "support@oakboundtrust.com"):
            self.assertIn(needle, html)
        self.assertNotIn("blocked", html)
        self.assertFalse(Transaction.objects.exists()); self.assertFalse(Withdrawal.objects.exists())
        self.user.refresh_from_db(); self.assertEqual(self.user.balance, 1000.0)


class IdentifierTests(TestCase):
    def test_numbers_are_valid_and_unique(self):
        from users import identifiers as ids
        a = User.objects.create_user("a@example.com", "pw12345678", zipcode="1")
        b = User.objects.create_user("b@example.com", "pw12345678", zipcode="1")
        for u in (a, b):
            self.assertTrue(ids.routing_is_valid(u.routing_number))
            self.assertEqual(len(u.account_number), 12)
            self.assertEqual(len(u.card_number), 16)
            self.assertTrue(set(u.card_number) <= set("12345"))
            self.assertTrue(ids.luhn_is_valid(u.card_number))
        self.assertNotEqual(a.account_number, b.account_number)
        self.assertNotEqual(a.routing_number, b.routing_number)
        self.assertNotEqual(a.card_number, b.card_number)


class CardActivationTests(TestCase):
    def setUp(self):
        self.u = User.objects.create_user("c@example.com", "pw12345678", zipcode="1", first_name="Ada", last_name="Obi")
        self.client.force_login(self.u)

    def test_card_page_shows_holder_and_number(self):
        r = self.client.get("/credit_card/")
        self.assertContains(r, "ADA OBI")
        self.assertContains(r, self.u.card_number_spaced)
        self.assertContains(r, self.u.card_expiry)

    def test_activation_emails_support(self):
        from unittest import mock
        with mock.patch("app.views.send_email", return_value=True) as m:
            r = self.client.post("/credit_card/activate/", {"phone": "123", "note": "hi"})
            self.assertRedirects(r, "/credit_card/", fetch_redirect_response=False)
            self.assertEqual(m.call_args[0][3], settings.SUPPORT_EMAIL)
            self.client.post("/credit_card/activate/")
            self.assertEqual(m.call_count, 1)  # throttled

    def test_deposit_page_shows_own_numbers(self):
        r = self.client.get("/deposit/")
        self.assertContains(r, self.u.account_number)
        self.assertContains(r, self.u.routing_number)


class InsightsAndContactTests(TestCase):
    def test_every_post_has_an_image_and_page(self):
        import os
        from app import content
        self.assertGreaterEqual(len(content.BLOG_POSTS), 12)
        for p in content.BLOG_POSTS:
            self.assertTrue(os.path.exists(f"static/images/blog/{p['slug']}.svg"), p["slug"])
            self.assertEqual(self.client.get(f"/blog/{p['slug']}/").status_code, 200)
        self.assertContains(self.client.get("/blog/"), "images/blog/")

    def test_contact_shows_email_and_location_and_live_support(self):
        r = self.client.get("/contact/")
        self.assertContains(r, "support@oakboundtrust.com")
        self.assertContains(r, "Kentucky, USA")
        self.assertContains(r, "data-live-chat")


class ThemeTests(TestCase):
    def test_public_pages_have_theme_script_stylesheet_and_toggle(self):
        for url in ["/", "/pricing/", "/blog/", "/contact/", "/about/", "/login/", "/signup/"]:
            r = self.client.get(url)
            self.assertContains(r, "ob-theme", msg_prefix=url)
            self.assertContains(r, "css/theme.css", msg_prefix=url)
            self.assertContains(r, "data-theme-toggle", msg_prefix=url)

    def test_dashboard_pages_have_toggle(self):
        u = User.objects.create_user("t@example.com", "pw12345678", zipcode="1")
        self.client.force_login(u)
        for url in ["/dashboard/", "/transactions/", "/credit_card/", "/deposit/", "/withdraw/", "/international-transfer/"]:
            r = self.client.get(url)
            self.assertContains(r, "ob-theme", msg_prefix=url)
            self.assertContains(r, "css/theme.css", msg_prefix=url)
            self.assertContains(r, "data-theme-toggle", msg_prefix=url)


class SuspensionTests(TestCase):
    VIEWABLE = ["/dashboard/", "/transactions/", "/credit_card/"]
    BLOCKED = ["/deposit/", "/withdraw/", "/international-transfer/", "/beneficiary/"]

    def setUp(self):
        self.u = User.objects.create_user("s@example.com", "pw12345678", zipcode="1", balance=5000)
        self.client.force_login(self.u)

    def suspend(self):
        self.u.is_suspended = True
        self.u.save()

    def test_active_account_is_not_blocked_and_has_no_banner(self):
        for url in self.VIEWABLE + self.BLOCKED[:3]:
            r = self.client.get(url)
            self.assertEqual(r.status_code, 200, url)
            self.assertNotContains(r, "susp-banner")

    def test_suspended_dashboard_shows_banner_and_message_popup(self):
        self.suspend()
        for url in self.VIEWABLE:
            r = self.client.get(url)
            self.assertEqual(r.status_code, 200, url)
            self.assertContains(r, "Account suspended")
            self.assertContains(r, "extended compliance review")
            self.assertContains(r, "Business Account Compliance Department.")
            self.assertContains(r, "mailto:support@oakboundtrust.com")
            self.assertContains(r, "data-live-chat")

    def test_suspended_transaction_pages_show_the_notice(self):
        self.suspend()
        for url in self.BLOCKED:
            r = self.client.get(url)
            self.assertEqual(r.status_code, 403, url)
            self.assertContains(r, "extended compliance review", status_code=403)

    def test_suspended_account_cannot_transfer_or_request_card(self):
        self.suspend()
        r = self.client.post("/withdraw/", {"amount": "100", "acc-no": "12345678", "acc-name": "X", "bank-name": "Y",
                                            "description": "t", "access-code": "555555"})
        self.assertEqual(r.status_code, 403)
        self.assertEqual(self.client.post("/credit_card/activate/", {}).status_code, 403)
        self.u.refresh_from_db()
        self.assertEqual(self.u.balance, 5000)

    def test_suspended_can_still_log_out_and_see_public_pages(self):
        self.suspend()
        self.assertEqual(self.client.get("/pricing/").status_code, 200)
        self.assertEqual(self.client.get("/logout/").status_code, 302)
