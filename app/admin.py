from django.contrib import admin
from .models import *
from django.contrib.auth.admin import UserAdmin

# Register your models here.
class WithdrawalAdmin(admin.ModelAdmin):
	list_display = ('creation_date', 'creation_time', 'user', 'amount', 'acc_no', 'acc_name', 'status')
	list_editable = ('status',)
	search_fields = ['user__email', 'amount', 'status']
	list_filter = ('user__email', 'amount', 'status')

class TransactionAdmin(admin.ModelAdmin):
	list_display = ('user', 'amount', 'creation_date', 'trans_type', 'status')
	list_editable = ('status', 'amount', 'trans_type')


class LoanApplicationAdmin(admin.ModelAdmin):
	list_display = ('user', 'loan_amount', 'creation_date', 'status')
	list_editable = ('status', 'loan_amount')

admin.site.register(Withdrawal, WithdrawalAdmin)
admin.site.register(Transaction, TransactionAdmin)
admin.site.register(LoanApplication, LoanApplicationAdmin)
