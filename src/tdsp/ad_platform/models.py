from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.db import models


class BidRequest(models.Model):
    bid_id = models.CharField(max_length=100)
    banner_width = models.IntegerField(default=0)
    banner_height = models.IntegerField(default=0)
    click_probability = models.FloatField(default=0)
    conversion_probability = models.FloatField(default=0)
    domain = models.CharField(max_length=100)
    ssp_id = models.CharField(max_length=100)
    user_id = models.CharField(max_length=100)


class BidResponse(models.Model):
    bid_id = models.CharField(max_length=100, default="")
    external_id = models.CharField(max_length=100)
    price = models.FloatField(default=0)


class Notify(models.Model):
    notify_id = models.CharField(max_length=100)
    win = models.BooleanField(default=False)
    price = models.FloatField(default=0)
    click = models.BooleanField(default=False)
    conversion = models.BooleanField(default=False)
    revenue = models.IntegerField(default=0)


class Campaign(models.Model):
    name = models.CharField(max_length=100)
    budget = models.FloatField(default=0)
    min_bid = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    is_enabled = models.BooleanField(default=True)


class Category(models.Model):
    code = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    parent = models.ForeignKey('self', null=True, blank=True, related_name='subcategories',
                               on_delete=models.CASCADE)

    def get_subcategory_codes(self):
        # Return a list of all subcategory codes for this category.
        subcategory_codes = [subcat.code for subcat in self.subcategories.all()]
        for subcat in self.subcategories.all():
            subcategory_codes.extend(subcat.get_subcategory_codes())
        return subcategory_codes


class Creative(models.Model):
    external_id = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    categories = models.ManyToManyField(Category)
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE)
    file = models.ImageField(upload_to='creatives/')
    url = models.CharField(max_length=255, blank=True)


class Configuration(models.Model):
    impressions_total = models.IntegerField(default=0)
    auction_type = models.BooleanField(default=False)  # False if 1st auction
    mode = models.BooleanField(default=False)  # False if "free" mode
    budget = models.IntegerField(default=0)
    impression_revenue = models.IntegerField(default=0)
    click_revenue = models.IntegerField(default=0)
    conversion_revenue = models.IntegerField(default=0)
    frequency_capping = models.IntegerField(default=0)
    game_goal = models.BooleanField(default=False)  # False if "revenue"
    remaining_rounds = models.IntegerField(default=0)


class CampaignFrequency(models.Model):
    user_id = models.CharField(max_length=100)
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE)
    frequency = models.IntegerField(default=0)


class GenericUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
