from django.contrib import admin
from .models import *


class CustomUserAccountAdmin(admin.ModelAdmin):
	list_display = ('email', 'balance', 'zipcode')
	list_editable = ('balance',)
	list_filter = ('first_name', 'email',)
	search_fields = ['email']



admin.site.register(CustomUserAccount, CustomUserAccountAdmin)