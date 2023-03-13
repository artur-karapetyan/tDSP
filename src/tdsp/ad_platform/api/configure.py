#
import json

#
from django.views import View
from django.http import JsonResponse

#
from ..models import Configuration, Campaign, Creative, BidRequest, BidResponse, CampaignFrequency, Notify


class ConfigurationView(View):

    @staticmethod
    def post(request):
        Configuration.objects.all().delete()
        # Campaign.objects.all().delete()
        # Creative.objects.all().delete()
        BidRequest.objects.all().delete()
        BidResponse.objects.all().delete()
        CampaignFrequency.objects.all().delete()
        Notify.objects.all().delete()

        data = json.loads(request.body)
        try:
            impressions_total = data.get('impressions_total')
            auction_type = data.get('auction_type')
            mode = data.get('mode')
            budget = data.get('budget')
            impression_revenue = data.get('impression_revenue')
            click_revenue = data.get('click_revenue')
            conversion_revenue = data.get('conversion_revenue')
            freq_capping = data.get('frequency_capping')
        except:
            return JsonResponse({'error': 'Missing fields'})

        config = Configuration.objects.create(
            impressions_total=impressions_total,
            auction_type=False if auction_type == 1 else True,
            mode=False if mode == 'free' else True,
            budget=budget,
            impression_revenue=impression_revenue,
            click_revenue=click_revenue,
            conversion_revenue=conversion_revenue,
            frequency_capping=freq_capping,
        )

        if mode == 'free':
            campaign = Campaign.objects.first()
            campaign.budget = budget
            campaign.save()

        return JsonResponse({}, status=200)
