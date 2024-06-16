from .models import CustomUser ,Alert,ContactMessage,OverallAlert,Referral
from django.contrib.auth.admin import UserAdmin
from django.contrib import admin
from .forms import AlertForm
from django.contrib import admin
from .models import Wallet, Transaction


class CustomUserAdmin(admin.ModelAdmin):
  list_display = ('username','first_name', 'last_name','plan','wallet_balance','wallet_id','status',)
  list_filter = ('plan','status','date_joined','wallet_balance',)
  search_fields = ('username','plan',)
  fieldsets = (
        (None, {'fields': ('status','username', 'email', 'password','first_name', 'last_name','plan','wallet_balance','wallet_id','user_referral_id','joined_referral_id','phone_number',)}),  # Show 'status' at the top
        ('Permissions', {'fields': ('is_staff', 'is_superuser','is_active', 'groups', 'user_permissions')}),
    )
  pass
admin.site.register(CustomUser, CustomUserAdmin)


class OverallAlertAdmin(admin.ModelAdmin):
    list_display = ('message', 'timestamp',)
    list_filter = ('timestamp',)

admin.site.register(OverallAlert, OverallAlertAdmin)  # Register the OverallAlert model with the admin site

class AlertAdmin(admin.ModelAdmin):
    list_display = ('message', 'timestamp', 'recipient')  # Add 'recipient' to display in admin list view
    list_filter = ('timestamp', 'recipient')  # Add 'recipient' to filtering options

    def get_form(self, request, obj=None, **kwargs):
        kwargs['form'] = AlertForm
        return super().get_form(request, obj, **kwargs)

admin.site.register(Alert, AlertAdmin)


class NotRespondedFilter(admin.SimpleListFilter):
    title = 'Response Status'
    parameter_name = 'response_status'

    def lookups(self, request, model_admin):
        return (
            ('not_responded', 'Not Responded Yet'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'not_responded':
            return queryset.filter(response='not respond yet')

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('message', 'date_sent', 'response', 'sender',)
    list_filter = ('date_sent', NotRespondedFilter,)
    search_fields = ('message',)



@admin.register(Referral)
class ReferralAdmin(admin.ModelAdmin):
    list_display = ('user', 'user_referral_id', 'joined_referral_id', 'joins')
    list_filter=('joined_referral_id',)
    def joins(self, obj):
        return obj.joins
    joins.short_description = 'Total Joins'
    search_fields = ('user_referral_id', 'joined_referral_id',)


class WalletAdmin(admin.ModelAdmin):
    list_display = ('user', 'wallet_balance', 'wallet_id')

    def wallet_balance(self, obj):
        return obj.user.wallet_balance
    wallet_balance.short_description = 'Wallet Balance'

    def wallet_id(self, obj):
        return obj.user.wallet_id
    wallet_id.short_description = 'Wallet ID'

admin.site.register(Wallet, WalletAdmin)

admin.site.register(Transaction)

class TransactionAdmin(admin.ModelAdmin):
    list_display=('wallet','transaction_type','amount','timestamp',)
    list_filter = ('transaction_type', 'amount',)

    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)
        try:
            search_amount = float(search_term)
            queryset |= self.model.objects.filter(amount=search_amount)
        except ValueError:
            pass
        return queryset, use_distinct

admin.site.unregister(Transaction)
admin.site.register(Transaction, TransactionAdmin)
