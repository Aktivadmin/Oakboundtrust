from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.utils import timezone
from django.utils.html import format_html

from .models import CustomUserAccount

admin.site.site_header = "Oakbound Trust Bank Admin"
admin.site.site_title = "Oakbound Admin"
admin.site.index_title = "Customers, balances and transactions"


class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CustomUserAccount
        fields = ("email", "first_name", "last_name", "zipcode")
        field_classes = {}


class CustomUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = CustomUserAccount
        fields = "__all__"
        field_classes = {}


@admin.register(CustomUserAccount)
class CustomUserAccountAdmin(UserAdmin):
    """Customers and admins. Passwords are hashed correctly when created or changed here."""
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm
    ordering = ("-date_joined",)
    list_display = ("email", "first_name", "last_name", "balance", "savings", "is_suspended", "email_verified_at", "is_active", "view_dashboard")
    list_editable = ("balance", "savings", "is_suspended")
    list_filter = ("is_suspended", "is_staff", "is_superuser", "is_active")
    search_fields = ("email", "first_name", "last_name", "phone")
    readonly_fields = ("date_joined", "last_login", "email_verified_at")
    actions = ["verify_selected"]
    filter_horizontal = ("groups", "user_permissions")
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal info", {"fields": ("first_name", "last_name", "phone", "dob", "zipcode", "currency", "access_code")}),
        ("Balances", {"fields": ("balance", "savings", "pending_checking", "expenses")}),
        ("Status", {"fields": ("is_active", "is_suspended", "email_verified_at")}),
        ("Admin access", {"fields": ("is_staff", "is_superuser", "is_admin", "groups", "user_permissions")}),
        ("Dates", {"fields": ("date_joined", "last_login")}),
    )
    add_fieldsets = ((None, {"classes": ("wide",), "fields": ("email", "first_name", "last_name", "zipcode", "password1", "password2")}),)

    @admin.display(description="Dashboard")
    def view_dashboard(self, obj):
        if obj.is_superuser:
            return "-"
        return format_html('<a href="/console/?q={}">Open</a>', obj.email)

    @admin.action(description="Mark selected as email-verified and activate")
    def verify_selected(self, request, queryset):
        n = queryset.update(is_active=True, email_verified_at=timezone.now())
        self.message_user(request, f"{n} account(s) verified and activated.")
