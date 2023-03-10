import json

from django.http import JsonResponse
from django.views import View
from django.views.decorators.http import require_POST

from ..models import Configuration, Campaign, Creative


class ConfigurationView(View):

    @staticmethod
    def post(request):
        Configuration.objects.all().delete()
        Campaign.objects.all().delete()
        Creative.objects.all().delete()

        data = json.loads(request.body)

        try:
            config = Configuration.objects.create(
                impressions_total=data.get('impressions_total'),
                auction_type=False if data.get('auction_type') == 1 else True,
                mode=False if data.get('mode') == 'free' else True,
                budget=data.get('budget'),
                impression_revenue=data.get('impression_revenue'),
                click_revenue=data.get('click_revenue'),
                conversion_revenue=data.get('conversion_revenue'),
                frequency_capping=data.get('frequency_capping'),
            )
        except:
            return JsonResponse({'error': 'Missing mandatory fields'})

        return JsonResponse({}, status=200)
