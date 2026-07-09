from django.contrib import admin
from .models import CountrySetting, ProductPrice, UserProfile, SiteSetting, HeroPanel

@admin.register(CountrySetting)
class CountrySettingAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'currency_code', 'currency_symbol', 'default_language', 'shipping_charge')
    search_fields = ('name', 'code', 'currency_code')

@admin.register(ProductPrice)
class ProductPriceAdmin(admin.ModelAdmin):
    list_display = ('product', 'country', 'price')
    list_filter = ('country',)
    search_fields = ('product__name', 'country__name')

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'country', 'preferred_language')
    search_fields = ('user__username', 'user__email')

@admin.register(SiteSetting)
class SiteSettingAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        # We only want one site setting instance
        if self.model.objects.exists():
            return False
        return super().has_add_permission(request)

@admin.register(HeroPanel)
class HeroPanelAdmin(admin.ModelAdmin):
    list_display = ('title', 'order', 'is_active', 'created_at')
    list_editable = ('order', 'is_active')
    search_fields = ('title',)
