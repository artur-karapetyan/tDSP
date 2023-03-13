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
    revenue = models.FloatField(default=0)


class Campaign(models.Model):
    name = models.CharField(max_length=100)
    budget = models.IntegerField(default=0)


class Category(models.Model):
    code = models.CharField(max_length=100)
    name = models.CharField(max_length=100)


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


class CampaignFrequency(models.Model):
    user_id = models.CharField(max_length=100)
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE)
    frequency = models.IntegerField(default=0)
