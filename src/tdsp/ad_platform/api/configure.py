#
import base64
import json
import logging
from PIL import Image

from django.core.files.base import ContentFile
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
        Campaign.objects.all().delete()
        Creative.objects.all().delete()

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
            game_goal=False if game_goal == 'revenue' else True,
            remaining_rounds=impressions_total + 1,
        )

        if not config.mode:  # If game mode is free
            campaign = Campaign.objects.create(name="TheInterns", budget=budget)
            if impression_revenue < (budget / impressions_total):
                campaign.min_bid = impression_revenue
                campaign.save()
            else:
                campaign.min_bid = budget / impressions_total
                campaign.save()
            if not campaign.is_enabled:
                campaign.is_enabled = True
                campaign.save()
            creative = Creative.objects.create(external_id="test_id", name="TheInterns", campaign=campaign)
            base64_img = "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"
            file_data = base64.b64decode(base64_img)
            file = ContentFile(file_data, name=f'{creative.id}.png')
            img = Image.open(file)
            url = f"http://{request.get_host()}/api/creatives/{creative.id}?width={img.width}&height={img.height}"
            creative.file = file
            creative.url = url
            creative.save()

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
