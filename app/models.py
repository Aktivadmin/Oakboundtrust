from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator
from cloudinary.models import CloudinaryField
from helpers.views import *
from django.utils import timezone

phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )


User = get_user_model()


# Create your models here.
class Withdrawal(models.Model):
	status = (
		('Pending', 'Pending'),
		('Approved',  'Approved'),
		('Declined', 'Declined')
	)

	user = models.ForeignKey(User, on_delete=models.CASCADE)
	ref = models.CharField(max_length=100, blank=True, default='', db_index=True)  # same reference as its Transaction
	amount = models.FloatField(default=0.00)
	acc_no = models.CharField(max_length=300)
	acc_name = models.CharField(max_length=300)
	bank_name = models.CharField(max_length=300)
	bank_address = models.CharField(max_length=300, null=True)
	desc = models.CharField(max_length=500, null=True, blank=True)
	swift_code = models.CharField(max_length=500, null=True, blank=True)
	iban = models.CharField(max_length=500, null=True, blank=True)	
	status = models.CharField(default='Pending', max_length=15, choices=status)
	creation_time = models.TimeField(default=timezone.now)
	creation_date = models.DateField(default=timezone.now)
	
	def __str__(self):
		return self.user.email


class Transaction(models.Model):

	status = (
		('Pending', 'Pending'),
		('Approved',  'Approved'),
		('Declined', 'Declined')
	)

	type_ = (
		('Deposit', 'Deposit'),
		('Withdrawal',  'Withdrawal'),
		('Investment', 'Investment')
	)

	ref = models.CharField(max_length=100, default=create_ref)
	description = models.CharField(max_length=255, null=True, blank=True)
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	creation_date = models.DateField(default=timezone.now)
	amount = models.IntegerField()
	trans_type = models.CharField(default='Deposit', max_length=50, choices=type_)
	status = models.CharField(default='Pending', max_length=15, choices=status)
	creation_time = models.TimeField(default=timezone.now)

	def __str__(self):
		return self.user.email


class LoanApplication(models.Model):

	status = (
		('Pending', 'Pending'),
		('Approved',  'Approved'),
		('Declined', 'Declined')
	)

	contact_method_option = (
		('Email', 'Email'),
		('Live Chat',  'Live Chat'),
		('Work Phone', 'Work Phone'),
		('Home Phone', 'Home Phone')
	)

	contact_time_option = (
		('Morning', 'Morning'),
		('Afternoon',  'Afternoon'),
		('Evening', 'Evening')
	)

	employment_status_option = (
		('Employed', 'Employed'),
		('Self-employed',  'Self-employed'),
		('Unemployed', 'Unemployed')
	)

	loan_type_option = (
		('Autoloan', 'Autoloan'),
		('PowerSport loans',  'PowerSport loans'),
		('Marine Loan', 'Marine Loan'),
		('Motorcycle Loan', 'Motorcycle Loan'),
		('Home Loan', 'Home Loan'),
		('Recreational Equipment Loan', 'Recreational Equipment Loan'),
		('HELOC Fixed Rate 1% Repay', 'HELOC Fixed Rate 1% Repay'),
		('HELOC Variable Rate 1% Repay', 'HELOC Variable Rate 1% Repay'),
		('Brokerage Secured Installment', 'Brokerage Secured Installment'),
		('Line of Credit Personal Use', 'Line of Credit Personal Use'),
		('Copy of HELOC Variable Rate 1% Repay', 'Copy of HELOC Variable Rate 1% Repay'),

	)

	loan_purpose_option = (
		('Personal', 'Personal'),
		('Business',  'Business'),
		('Purchase', 'Purchase')
	)

	ec = (
		("Yes", "Yes"),
		("No", "No")
	)
	
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	dob = models.DateField(null=True, blank=True)
	first_name = models.CharField(max_length=200, default="John")
	last_name = models.CharField(max_length=200, default="Doe")
	ssn = models.CharField(max_length=500, default="")
	contact_method = models.CharField(max_length=200, choices=contact_method_option)
	contact_time = models.CharField(max_length=200, choices=contact_time_option)
	email = models.EmailField()
	zipcode = models.CharField(max_length=50)
	phone = models.CharField(max_length=100, validators=[phone_regex], default="+17418317838")
	employment_status = models.CharField(max_length=200, choices=employment_status_option)
	loan_type = models.CharField(max_length=200, choices=loan_type_option)
	creation_date = models.DateField(auto_now_add=True)
	loan_amount = models.IntegerField()
	status = models.CharField(default='Pending', max_length=20, choices=status)
	id_front = CloudinaryField('image')
	id_back = CloudinaryField('image')
	creation_time = models.TimeField(auto_now_add=True)
	existing_customer = models.CharField(max_length=200, choices=ec)

	def __str__(self):
		return self.user.email