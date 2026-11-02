from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from validate_email import validate_email
from datetime import datetime
from django.contrib import messages
from .models import *
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from helpers.views import otp_enabled
from users.otp import issue as issue_code, check as check_code, mask_email, seconds_until_resend


User = get_user_model()


# Create your views here.
def home(request):
    from .content import BLOG_POSTS, FAQS
    context = {
        'posts': BLOG_POSTS[:3],
        'faqs': FAQS[:6],
    }
    return render(request, 'index.html', context)


def about(request):
    context = {

    }
    return render(request, 'about.html', context)


def application(request):
    context = {

    }
    return render(request, 'application.html', context)


# logout view
def logout_user(request):

    logout(request)

    return redirect(reverse('login'))



def login_user(request):
    context = {

    }
    if request.method == 'POST':
        context = {'data': request.POST, 'title' : 'Dashboard'}
        email = (request.POST.get('email') or '').strip()
        password = request.POST.get('password')

        if not validate_email(email):
            messages.add_message(request, messages.ERROR,
                                 'Please enter a valid email address and try again')
            return render(request, 'login.html', context, status=401)

        pending = User.objects.filter(email__iexact=email, is_active=False, email_verified_at__isnull=True).first()
        if pending and pending.check_password(password):
            # Signed up but never confirmed their email: pick up where they left off.
            request.session['pending_user_id'] = pending.pk
            messages.info(request, 'Please confirm your email address to finish signing in.')
            return redirect('verify-email')

        user = authenticate(request, email=email, password=password)
        if not user:
            messages.add_message(request, messages.ERROR,
                                 'Invalid credentials, try again')
            return render(request, 'login.html', context, status=401)

            
        login(request, user)
        if user.is_superuser:
            return redirect(reverse('console'))
        return redirect(reverse('dashboard'))
    return render(request, 'login.html', context)


def signup(request):
    context = {

    }
    if request.method == "POST":
        context = {'has_error': False, 'data': request.POST, 'title' : 'Sign Up'}
        first_name = request.POST.get('firstname')
        last_name = request.POST.get('lastname')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password2 = request.POST.get('confirm-password')
        zipcode = request.POST.get('zipcode')
        phone = request.POST.get('phone')
        dob_str = request.POST.get('dob')
        image = request.FILES.get('image')


        try:
            # Convert the string to a datetime.date object
            dob = datetime.strptime(dob_str, "%Y-%m-%d").date()
        except ValueError:
            # Handle invalid date format
            dob = None   
        

        if len(password) < 6:
            messages.add_message(request, messages.ERROR,
                                 'Password should be at least 6 characters')
            return render(request, 'sign-up.html', context)

        if password != password2:
            messages.add_message(request, messages.ERROR,
                                 'Password mismatch')
            return render(request, 'sign-up.html', context)

        if not validate_email(email):
            messages.add_message(request, messages.ERROR,
                                 'Enter a valid email address')
            return render(request, 'sign-up.html', context)

        if not first_name or first_name =='':
            messages.add_message(request, messages.ERROR,
                                 'Please enter your first name')
            return render(request, 'sign-up.html', context)

        if not last_name or last_name =='':
            messages.add_message(request, messages.ERROR,
                                 'Please enter your last name')
            return render(request, 'sign-up.html', context)

        existing = User.objects.filter(email__iexact=email).first()
        if existing and (existing.is_active or existing.email_verified_at):
            messages.add_message(request, messages.ERROR,
                                 'Email is taken, choose another one')
            return render(request, 'sign-up.html', context)
        

        if context['has_error']:
            return render(request, 'sign-up.html', context)


        if not context['has_error']:
            # The account stays inactive until the emailed code is entered.
            user = existing or User.objects.create_user(email=email, is_active=False)
            user.set_password(password)
            user.dob = dob
            user.zipcode = zipcode
            user.phone = phone
            user.first_name = first_name
            user.last_name = last_name
            user.is_active = False
            user.save()

            if not otp_enabled():
                # No way to email a code yet (see OTP_REQUIRED): keep the original sign-up so nobody is locked out.
                user.is_active = True
                user.save(update_fields=['is_active'])
                send_email('emails/welcome.html', {'name': first_name}, 'Welcome', email)
                messages.success(request, "Please login")
                return redirect('login')

            request.session['pending_user_id'] = user.pk
            status = issue_code(user)
            if status == 'failed':
                messages.warning(request, "We could not send your code just now. Tap Resend code to try again.")
            else:
                messages.success(request, f"We sent a 6-digit code to {mask_email(user.email)}.")
            return redirect('verify-email')
    return render(request, 'sign-up.html', context)


def verify_email(request):
    """Step 2 of sign-up: enter the 6-digit code that was emailed."""
    pending_id = request.session.get('pending_user_id')
    user = User.objects.filter(pk=pending_id, is_active=False, email_verified_at__isnull=True).first() if pending_id else None
    if not user:
        request.session.pop('pending_user_id', None)
        messages.error(request, 'That sign-up session has ended. Please sign up again, or log in to continue.')
        return redirect('signup')

    if request.method == 'POST':
        if request.POST.get('action') == 'resend':
            status = issue_code(user)
            text = {
                'sent': (messages.success, f"A new code is on its way to {mask_email(user.email)}."),
                'cooldown': (messages.info, "Please wait a moment before asking for another code."),
                'limit': (messages.error, "Too many codes requested. Please try again in an hour or contact support."),
                'failed': (messages.warning, "We could not send the code just now. Please try again shortly."),
            }[status]
            text[0](request, text[1])
            return redirect('verify-email')

        code = ''.join(ch for ch in request.POST.get('code', '') if ch.isdigit())
        result = check_code(user, code)
        if result == 'ok':
            user.is_active = True
            user.email_verified_at = timezone.now()
            user.save(update_fields=['is_active', 'email_verified_at'])
            request.session.pop('pending_user_id', None)
            login(request, user)
            send_email('emails/welcome.html', {'name': user.first_name}, 'Welcome to Oakbound Trust Bank', user.email)
            messages.success(request, 'Email confirmed. Welcome to Oakbound Trust Bank.')
            return redirect('dashboard')
        problem = {
            'bad': 'That code is not right. Please check it and try again.',
            'expired': 'That code has expired. Tap Resend code for a new one.',
            'locked': 'Too many wrong tries. Tap Resend code for a new one.',
            'missing': 'There is no active code. Tap Resend code for a new one.',
        }[result]
        messages.error(request, problem)
        return render(request, 'verify-email.html', {'masked_email': mask_email(user.email), 'seconds': seconds_until_resend(user), 'title': 'Verify email'}, status=400)

    return render(request, 'verify-email.html', {'masked_email': mask_email(user.email), 'seconds': seconds_until_resend(user), 'title': 'Verify email'})


@login_required
def receipt(request, ref):
    """Reopen the receipt of any past transfer. Shows the transfer's real, current status."""
    tx = get_object_or_404(Transaction, ref=ref, user=request.user)
    w = Withdrawal.objects.filter(ref=ref, user=request.user).first()
    ctx = {
        'currency': request.user.currency, 'ref': tx.ref, 'amount': tx.amount, 'status': tx.status,
        'description': tx.description or (w.desc if w else ''), 'date': tx.creation_date, 'time': tx.creation_time,
        'name': request.user.first_name, 'transfer_type': 'Transfer',
    }
    if w:
        ctx.update(acc_no=w.acc_no, bank=w.bank_name, r_name=w.acc_name, address=w.bank_address, swift_code=w.swift_code,
                   iban=w.iban, transfer_type='International' if w.iban else 'Local')
    return render(request, 't-success.html', ctx)


def beneficiary(request):
    context = {

    }
    return render(request, 'beneficiary.html', context)

@login_required
def credit_card(request):
    current_user = request.user
    context = {
        'user':current_user,

    }
    if current_user.is_suspended:
        messages.error(request, "Your account is restricted, please contact support")
        return redirect('dashboard')
        
    return render(request, 'credit-cards.html', context)

@login_required
def deposit(request):
    current_user = request.user
    context = {
        'user':current_user,

    }
    if current_user.is_suspended:
        messages.error(request, "Your account is restricted, please contact support")
        return redirect('dashboard')
        
    return render(request, 'deposit.html', context)

@login_required
def withdraw(request):
    current_user = request.user
    balance = current_user.balance
    context = {
        'user':current_user,

    }
    if current_user.is_suspended:
        messages.error(request, "Your account is restricted, please contact support")
        return redirect('dashboard')
        
    if request.method == 'POST':
        context = {'has_error': False, 'data': request.POST, 'title' : 'Cash Out'}
        amount = request.POST.get('amount')
        acc_no = request.POST.get('acc-no')
        acc_name = request.POST.get('acc-name')
        bank_name = request.POST.get('bank-name')
        desc = request.POST.get('description') or request.POST.get('desc')            # the form field is "description"
        swift_code = request.POST.get('swift_code')
        address = request.POST.get('bank-address') or request.POST.get('address')     # the form field is "bank-address"
        access_code = request.POST.get('access-code')


        if not amount:
            messages.add_message(request, messages.ERROR,
                                 'Please enter a valid amount')
            context['has_error'] = True

        if float(amount) > current_user.balance:
            messages.add_message(request, messages.ERROR,
                                 'You have insufficient funds')
            context['has_error'] = True

        if not acc_no or acc_no == '':
            messages.add_message(request, messages.ERROR,
                                 "Please enter the recipient's account number")
            context['has_error'] = True

        if not acc_name or acc_name == '':
            messages.add_message(request, messages.ERROR,
                                 "Please enter the recipient's account name")
            context['has_error'] = True

        if not bank_name or bank_name == '':
            messages.add_message(request, messages.ERROR,
                                 "Please enter the recipient's bank name")
            context['has_error'] = True


        if context['has_error']:
            return render(request, 'withdraw.html', context)

        
        if access_code != current_user.access_code:
            context.update(reason='access_code', retry_url=reverse('withdraw'))
            return render(request, 'failed-transfer.html', context)

        if not context['has_error']:


            withdraw = Withdrawal()
            withdraw.user = current_user
            withdraw.amount = amount
            withdraw.acc_name = acc_name
            withdraw.acc_no = acc_no
            withdraw.bank_name = bank_name
            withdraw.swift_code = swift_code
            withdraw.desc = desc
            withdraw.bank_address = address
            withdraw.save()

            transaction = Transaction()
            transaction.user = current_user
            transaction.amount = amount
            transaction.description = desc
            transaction.trans_type = "Withdrawal"
            transaction.save()
            withdraw.ref = transaction.ref          # lets us find the transfer details from the transaction (and back)
            withdraw.save(update_fields=['ref'])
            
            balance = float(balance) - float(amount)
            current_user.balance = balance
            current_user.save()

            context = {
                'currency': current_user.currency,
                'acc_no': acc_no,
                'ref' : transaction.ref,
                'bank' : bank_name,
                'r_name' : acc_name,
                'address' : address,
                'description' : desc,
                'amount': amount,
                'swift_code': swift_code,
                'name': current_user.first_name,
                'date': transaction.creation_date,
                'time': transaction.creation_time,
                'transfer_type': 'Local',
                'status': transaction.status,

            }

            
            html_template = 'emails/withdraw.html'
            subject = 'Pending Transaction'
            send_email(html_template, context, subject, current_user.email)

            return render(request, 't-success.html', context)

    return render(request, 'withdraw.html', context)


@login_required
def international_transfer(request):
    current_user = request.user
    balance = current_user.balance
    context = {
        'user':current_user,

    }
    if current_user.is_suspended:
        messages.error(request, "Your account is restricted, please contact support")
        return redirect('dashboard')

    if request.method == 'POST':
        context = {'has_error': False, 'data': request.POST, 'title' : 'Cash Out'}
        amount = request.POST.get('amount')
        acc_no = request.POST.get('acc-no')
        acc_name = request.POST.get('acc-name')
        bank_name = request.POST.get('bank-name')
        bank_address = request.POST.get('bank-address')
        desc = request.POST.get('description') or request.POST.get('desc')   # the form field is "description"
        iban = request.POST.get('iban')
        swift_code = request.POST.get('swift_code')
        access_code = request.POST.get('access-code')


        if not amount:
            messages.add_message(request, messages.ERROR,
                                 'Please enter a valid amount')
            context['has_error'] = True

        if float(amount) > current_user.balance:
            messages.add_message(request, messages.ERROR,
                                 'You have insufficient funds')
            context['has_error'] = True

        if not acc_no or acc_no == '':
            messages.add_message(request, messages.ERROR,
                                 "Please enter the recipient's account number")
            context['has_error'] = True

        if not acc_name or acc_name == '':
            messages.add_message(request, messages.ERROR,
                                 "Please enter the recipient's account name")
            context['has_error'] = True

        if not bank_name or bank_name == '':
            messages.add_message(request, messages.ERROR,
                                 "Please enter the recipient's bank name")
            context['has_error'] = True


        if context['has_error']:
            return render(request, 'international-transfer.html', context)

        if access_code != current_user.access_code:
            context.update(reason='access_code', retry_url=reverse('international-transfer'))
            return render(request, 'failed-transfer.html', context)

        if not context['has_error']:

            withdraw = Withdrawal()
            withdraw.user = current_user
            withdraw.amount = amount
            withdraw.acc_name = acc_name
            withdraw.acc_no = acc_no
            withdraw.bank_name = bank_name
            withdraw.bank_address = bank_address
            withdraw.iban = iban
            withdraw.swift_code = swift_code
            withdraw.desc = desc
            withdraw.save()

            transaction = Transaction()
            transaction.user = current_user
            transaction.amount = amount
            transaction.description = desc
            transaction.trans_type = "Withdrawal"
            transaction.save()
            withdraw.ref = transaction.ref          # lets us find the transfer details from the transaction (and back)
            withdraw.save(update_fields=['ref'])
            
            balance = float(balance) - float(amount)
            current_user.balance = balance
            current_user.save()

            context = {
                'currency': current_user.currency,
                'acc_no': acc_no,
                'ref' : transaction.ref,
                'bank' : bank_name,
                'r_name' : acc_name,
                'description' : desc,
                'amount': amount,
                "address" : bank_address,
                'iban':iban,
                'swift_code': swift_code,
                'name': current_user.first_name,
                'date': transaction.creation_date,
                'time': transaction.creation_time,
                'transfer_type': 'International',
                'status': transaction.status,

            }

            
            html_template = 'emails/withdraw.html'
            subject = 'Pending Transaction'
            send_email(html_template, context, subject, current_user.email)

            return render(request, 't-success.html', context)

    return render(request, 'international-transfer.html', context)





@login_required
def transaction(request):
    current_user = request.user
    transactions = Transaction.objects.filter(user=current_user).order_by("-id")
    context = {
        'user':current_user,
        'transactions': transactions
    }
    if current_user.is_suspended:
        messages.error(request, "Your account is restricted, please contact support")
        return redirect('dashboard')
        
    return render(request, 'transaction.html', context)

@login_required
def dashboard(request):
    current_user = request.user
    transactions = Transaction.objects.filter(user=current_user).order_by("-id")
    context = {
        'user':current_user,
        'transactions': transactions,
        'total': current_user.balance + current_user.savings + current_user.pending_checking,
    }
    if current_user.is_suspended:
        messages.error(request, "Your account is restricted, please contact support")
        
    return render(request, 'dashboard.html', context)


def mortgage(request):
    context = {

    }
    return render(request, 'mortgage.html', context)


def loans(request):
    context = {

    }
    return render(request, 'loan.html', context)


def small_businesses(request):
    context = {

    }
    return render(request, 'small-businesses.html', context)


def investment(request):
    context = {

    }
    return render(request, 'investment.html', context)


@login_required
def apply_for_loan(request):
    current_user = request.user
    balance = current_user.balance
    context = {
        'user':current_user,

    }
    if request.method == 'POST':
        context = {'has_error': False, 'data': request.POST, 'title' : 'Loan Application'}
        loan_amount = request.POST.get('loan-amount')
        loan_purpose = request.POST.get('loan-purpose')
        dob = request.POST.get('dob')
        loan_type = request.POST.get('loan-type')
        email = request.POST.get('email')
        ssn = request.POST.get('ssn')
        id_back = request.POST.get('id-back')
        id_front = request.POST.get('id_front')
        zipcode = request.POST.get('zipcode')
        phone = request.POST.get('phone')
        first_name = request.POST.get('first-name')
        last_name = request.POST.get('last-name')
        employment_status = request.POST.get('employment-status')
        contact_method = request.POST.get('contact-method')
        contact_time = request.POST.get('contact-time')
        existing_customer = request.POST.get('existing-customer')

        if not loan_amount or loan_amount == "":
            messages.add_message(request, messages.ERROR,
                                 'Please enter a valid amount')
            context['has_error'] = True

        if loan_purpose == "":
            messages.add_message(request, messages.ERROR,
                                 'Please choose a purpose for your loan')
            context['has_error'] = True

        if loan_type == "":
            messages.add_message(request, messages.ERROR,
                                 'Please choose the type of loan')
            context['has_error'] = True



        if context['has_error']:
            return render(request, 'application.html', context)


        if not context['has_error']:


            la = LoanApplication()
            la.user = current_user
            la.loan_amount = loan_amount
            la.loan_purpose = loan_purpose
            la.loan_type = loan_type
            la.phone = phone
            la.first_name = first_name
            la.last_name = last_name
            la.id_back = id_back
            la.id_front = id_front
            la.ssn = ssn
            la.contact_time = contact_time
            la.contact_method = contact_method
            la.existing_customer = existing_customer
            la.employment_status = employment_status
            la.zipcode = zipcode
            la.dob = dob
            la.email = email
            la.save()

            messages.add_message(request, messages.SUCCESS,
                                 'Your loan application will be processed immediately')

            return redirect('dashboard')
    return render(request, 'application.html', context)


def password_reset_confirm(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(id=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    
    if user and (user.is_staff or user.is_superuser):
        user = None  # admin passwords can only be changed from the admin panel

    if user and default_token_generator.check_token(user, token):
        
        if request.method == 'POST':
            
            password = request.POST.get('password')
            confirm_password = request.POST.get('confirm_password')

            if password != confirm_password:
                messages.error(request, 'Password mismatch')
                return render(request, 'password_reset_confirm.html', {'uidb64': uidb64, 'token': token, 'title':'Password Reset'})

            user.set_password(password)
            user.save()
            messages.success(request, 'Password has been reset successfully. You can now log in.')
            return redirect('login')
        else:
            return render(request, 'password_reset_confirm.html', {'uid': uidb64, 'token': token, 'title':'Password Reset'})
    else:
        
        return render(request, 'password_reset_link_invalid.html')


def reset_password(request):
    context = {
        'title':'Reset Password'
    }
    if request.method == 'POST':
        email = request.POST.get('email')
        if not validate_email(email):
            messages.add_message(request, messages.ERROR,
                                 'Please enter your email address')
            return render(request, 'password_reset_form.html', status=401)
        try:
            user = User.objects.get(email=email)
        except ObjectDoesNotExist:
            user = None

        if not user:
            messages.add_message(request, messages.ERROR,
                                 f"Please, there's no account associated with {email}")
            return render(request, 'password_reset_form.html', status=401)

        if user.is_staff or user.is_superuser:
            # Admin accounts are never reset by email: whoever owns that mailbox could take over the site.
            # Show the same page as a normal request so nothing is revealed.
            return render(request, 'password_reset_link_sent.html')

        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        reset_url = request.build_absolute_uri(f'/reset/{uid}/{token}')

        mydict = {'token': token, 'uid': uid, 'reset_url': reset_url }
        html_template = 'emails/password_reset_email.html'
        subject = 'Reset Password'
        send_email(html_template, mydict, subject, email)
        context = {
            'title': "Reset Password"
        }

        return render(request, 'password_reset_link_sent.html')

    return render(request, 'password_reset_form.html', context)
