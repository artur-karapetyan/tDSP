from django.contrib import admin
from .models import BidRequest, BidResponse, Notify, Campaign, Category, Creative, Configuration


@admin.register(BidRequest)
class BidRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'domain', 'user_id', 'price')


@admin.register(BidResponse)
class BidResponseAdmin(admin.ModelAdmin):
    list_display = ('external_id', 'price')


@admin.register(Notify)
class NotifyAdmin(admin.ModelAdmin):
    list_display = ('id', 'win', 'price', 'click', 'conversion', 'revenue')


@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = ('name', 'budget')


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('code', 'name')


class CategoryInline(admin.TabularInline):
    model = Creative.categories.through


@admin.register(Creative)
class CreativeAdmin(admin.ModelAdmin):
    list_display = ('external_id', 'name', 'campaign_id', 'file_url')
    inlines = [CategoryInline]


@admin.register(Configuration)
class ConfigurationAdmin(admin.ModelAdmin):
    list_display = (
        'impressions_total',
        'auction_type',
        'mode',
        'budget',
        'impressions_revenue',
        'click_revenue',
        'conversion_revenue',
        'frequency_capping')
