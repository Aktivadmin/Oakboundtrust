from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from validate_email import validate_email
import uuid
from cloudinary.models import CloudinaryField
from django.core.validators import RegexValidator



phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password):
        if password is None:
            raise TypeError('Superusers must have a password.')

        user = self.create_user(email, password)
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)
        return user




class CustomUserAccount(AbstractBaseUser, PermissionsMixin):
    
    phone = models.CharField(validators=[phone_regex], max_length=17, blank=True)
    email = models.EmailField(unique=True)
    balance = models.FloatField(default=0.00)
    savings = models.FloatField(default=0.00)
    expenses = models.FloatField(default=0.00)
    pending_checking = models.FloatField(default=0.00)
    date_joined = models.DateTimeField(verbose_name='date joined', auto_now_add=True)
    last_login = models.DateTimeField(verbose_name='last login', auto_now=True)
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    first_name = models.CharField(max_length=200, default="John")
    last_name = models.CharField(max_length=200, default="Doe")
    dob = models.DateField(null=True, blank=True)
    zipcode = models.CharField(max_length=50)
    currency = models.CharField(max_length=10, default="$")
    image = CloudinaryField('image', default="https://res.cloudinary.com/ds8ljaxsa/image/upload/v1677173485/media/default_t3vbot.png")


    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []


    def __str__(self):
        return (self.email)

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"





