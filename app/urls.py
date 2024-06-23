from django.urls import path
from .views import *

urlpatterns = [
    path('', home, name="home"),
    path('about/', about, name="about"),
    path('application/', application, name="application"),
    path('beneficiary/', beneficiary, name="beneficiary"),

    path('login/', login_user, name="login"),
    path('signup/', signup, name="signup"),
    path('logout/', logout_user, name="logout"),
    path('password_reset/', reset_password, name='password_reset'),
    path('reset/<uidb64>/<token>/', password_reset_confirm, name='password_reset_confirm'),

    path('credit_card/', credit_card, name="credit-card"),
    path('deposit/', deposit, name="deposit"),
    path('withdraw/', withdraw, name="withdraw"),
    path('international-transfer/', international_transfer, name="international-transfer"),
    path('transactions/', transaction, name="transaction"),
    path('dashboard/', dashboard, name="dashboard"),

    path('mortgage/', mortgage, name="mortgage"),
    path('loans/', loans, name="loans"),
    path('appy-for-loan/', apply_for_loan, name="apply-for-loan"),
    path('small-businesses/', small_businesses, name="small-businesses"),
    path('investment/', investment, name="investment"),
]
