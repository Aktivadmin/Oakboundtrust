from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse
from helpers.decorators import auth_user_should_not_access
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMessage
from validate_email import validate_email
from datetime import datetime
from django.contrib import messages
from .models import *
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist


User = get_user_model()


# Create your views here.
def home(request):
    context = {

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
        email = request.POST.get('email')
        password = request.POST.get('password')

        if not validate_email(email):
            messages.add_message(request, messages.ERROR,
                                 'Please enter a valid email address and try again')
            return render(request, 'login.html', context, status=401)

        user = authenticate(request, email=email, password=password)
        if not user:
            messages.add_message(request, messages.ERROR,
                                 'Invalid credentials, try again')
            return render(request, 'login.html', context, status=401)

            
        login(request, user)
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
        image = request.FILES['image']


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

        if User.objects.filter(email=email).exists():
            messages.add_message(request, messages.ERROR,
                                 'Email is taken, choose another one')
            return render(request, 'sign-up.html', context)
        

        if context['has_error']:
            return render(request, 'sign-up.html', context)


        if not context['has_error']:
            user = User.objects.create_user(email=email)
            user.set_password(password)
            user.dob = dob
            user.zipcode = zipcode
            user.phone = phone
            user.first_name = first_name
            user.last_name = last_name
            
            user.save()

            mydict = {'name': first_name}
            html_template = 'emails/welcome.html'
            html_message = render_to_string(html_template, context=mydict)
            subject = 'Welcome'
            email_from = settings.EMAIL_HOST_USER
            recipient_list = [email]
            message = EmailMessage(subject, html_message,
                                   email_from, recipient_list)
            message.content_subtype = 'html'
            message.send()

            messages.success(request, "Please login")

            return redirect('login')
    return render(request, 'sign-up.html', context)


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
    return render(request, 'credit-cards.html', context)

@login_required
def deposit(request):
    current_user = request.user
    context = {
        'user':current_user,

    }
    return render(request, 'deposit.html', context)

@login_required
def withdraw(request):
    current_user = request.user
    balance = current_user.balance
    context = {
        'user':current_user,

    }
    if request.method == 'POST':
        context = {'has_error': False, 'data': request.POST, 'title' : 'Cash Out'}
        amount = request.POST.get('amount')
        acc_no = request.POST.get('acc-no')
        acc_name = request.POST.get('acc-name')
        bank_name = request.POST.get('bank-name')
        desc = request.POST.get('desc')
        swift_code = request.POST.get('swift_code')
        address = request.POST.get('address')

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
            transaction.trans_type = "Withdrawal"
            transaction.save()
            
            balance = float(balance) - float(amount)
            current_user.balance = balance
            current_user.save()

            context = {
                'acc_no': acc_no,
                'ref' : transaction.ref,
                'bank' : bank_name,
                'r_name' : acc_name,
                'address' : address,
                'description' : desc,
                'amount': amount,
                'swift_code': swift_code,
                'name': current_user.first_name,
                'date': transaction.creation_date

            }

            
            html_template = 'emails/withdraw.html'
            html_message = render_to_string(html_template, context)
            subject = 'Pending Transaction'
            email_from = settings.EMAIL_HOST_USER
            recipient_list = [current_user.email]
            message = EmailMessage(subject, html_message,
                                   email_from, recipient_list)
            message.content_subtype = 'html'
            message.send()

            messages.add_message(request, messages.SUCCESS,
                                 'Your withdrawal will be processed immediately')

            return redirect('dashboard')
    return render(request, 'withdraw.html', context)


@login_required
def international_transfer(request):
    current_user = request.user
    balance = current_user.balance
    context = {
        'user':current_user,

    }
    if request.method == 'POST':
        context = {'has_error': False, 'data': request.POST, 'title' : 'Cash Out'}
        amount = request.POST.get('amount')
        acc_no = request.POST.get('acc-no')
        acc_name = request.POST.get('acc-name')
        bank_name = request.POST.get('bank-name')
        desc = request.POST.get('desc')
        iban = request.POST.get('iban')
        swift_code = request.POST.get('swift_code')

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


        if not context['has_error']:


            withdraw = Withdrawal()
            withdraw.user = current_user
            withdraw.amount = amount
            withdraw.acc_name = acc_name
            withdraw.acc_no = acc_no
            withdraw.bank_name = bank_name
            withdraw.iban = iban
            withdraw.swift_code = swift_code
            withdraw.desc = desc
            withdraw.save()

            transaction = Transaction()
            transaction.user = current_user
            transaction.amount = amount
            transaction.trans_type = "Withdrawal"
            transaction.save()
            
            balance = float(balance) - float(amount)
            current_user.balance = balance
            current_user.save()

            context = {
                'acc_no': acc_no,
                'ref' : transaction.ref,
                'bank' : bank_name,
                'r_name' : acc_name,
                'description' : desc,
                'amount': amount,
                'iban':iban,
                'swift_code': swift_code,
                'name': current_user.first_name,
                'date': transaction.creation_date

            }

            
            html_template = 'emails/withdraw.html'
            html_message = render_to_string(html_template, context)
            subject = 'Pending Transaction'
            email_from = settings.EMAIL_HOST_USER
            recipient_list = [current_user.email]
            message = EmailMessage(subject, html_message,
                                   email_from, recipient_list)
            message.content_subtype = 'html'
            message.send()

            messages.add_message(request, messages.SUCCESS,
                                 'Your withdrawal will be processed immediately')

            return redirect('dashboard')
    return render(request, 'international-transfer.html', context)





@login_required
def transaction(request):
    current_user = request.user
    transactions = Transaction.objects.filter(user=current_user)
    context = {
        'user':current_user,
        'transactions': transactions
    }
    return render(request, 'transaction.html', context)

@login_required
def dashboard(request):
    current_user = request.user
    transactions = Transaction.objects.filter(user=current_user)
    context = {
        'user':current_user,
        'transactions': transactions
    }
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

        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        reset_url = request.build_absolute_uri(f'/reset/{uid}/{token}')

        mydict = {'token': token, 'uid': uid, 'reset_url': reset_url }
        html_template = 'emails/password_reset_email.html'
        html_message = render_to_string(html_template, context=mydict)
        subject = 'Reset Password'
        email_from = settings.EMAIL_HOST_USER
        recipient_list = [email]
        message = EmailMessage(subject, html_message,
                                   email_from, recipient_list)
        message.content_subtype = 'html'
        message.send()

        context = {
            'title': "Reset Password"
        }

        return render(request, 'password_reset_link_sent.html')

    return render(request, 'password_reset_form.html', context)
