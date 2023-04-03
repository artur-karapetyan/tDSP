#
import json
import logging

#
from django.views import View
from django.http import JsonResponse

#
from ..models import Configuration, Campaign, Creative, BidRequest, BidResponse, CampaignFrequency, Notify

#
from ..tools.admin_authorized import admin_authorized
from ..tools.data_status import data_status
from ..tools.is_authorized import is_authorized


class ConfigurationView(View):

    @staticmethod
    @admin_authorized
    def post(request):
        Configuration.objects.all().delete()
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
            game_goal = data.get('game_goal')
        except:
            return JsonResponse({'error': 'Missing fields'}, status=400)

        config = Configuration.objects.create(
            impressions_total=impressions_total,
            auction_type=False if auction_type == 1 else True,
            mode=False if mode == 'free' else True,
            budget=budget,
            impression_revenue=impression_revenue,
            click_revenue=click_revenue,
            conversion_revenue=conversion_revenue,
            frequency_capping=freq_capping,
            game_goal=False if game_goal == 'revenue' else True
        )

        if not config.mode:
            try:
                campaign = Campaign.objects.first()
                campaign.budget = budget
                campaign.min_bid = impression_revenue
                campaign.save()
                Campaign.objects.exclude(id=campaign.id).delete()
                if not campaign.is_enabled:
                    campaign.is_enabled = True
                    campaign.save()
            except Exception as ex:
                logging.exception(ex)

        else:
            Campaign.objects.all().delete()
            Creative.objects.all().delete()

        return JsonResponse({}, status=200)

    @staticmethod
    @is_authorized
    def get(request):
        config = Configuration.objects.first()

        data = {
            'id': config.id,
            'impressions_total': config.impressions_total,
            'auction_type': "1st Auction" if not config.auction_type else "2nd Auction",
            'mode': "Free" if not config.mode else "Script",
            'game_goal': "Revenue" if not config.game_goal else "CPC",
            'budget': config.budget,
            'impression_revenue': config.impression_revenue,
            'click_revenue': config.click_revenue,
            'conversion_revenue': config.conversion_revenue,
            'frequency_capping': config.frequency_capping,
        }

        return data_status(data)
