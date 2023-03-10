import json

from django.http import JsonResponse
from django.views import View
from django.views.decorators.http import require_POST

from ..models import Notify, BidRequest, BidResponse, Creative, Campaign


class NotifyView(View):

    @staticmethod
    def post(request):
        data = json.loads(request.body)
        if data.get('win'):
            notify = Notify.objects.create(
                notify_id=data.get('id'),
                win=data.get('win'),
                price=data.get('price'),
                click=data.get('click'),
                conversion=data.get('conversion'),
                revenue=data.get('revenue'),
            )

            bid_response = BidResponse.objects.get(bid_id=notify.notify_id)
            creative = Creative.objects.get(external_id=bid_response.external_id)
            campaign = Campaign.objects.get(id=creative.campaign_id['id'])

            # Change budget
            campaign.budget -= notify.price
        else:
            notify = Notify.objects.create(
                notify_id=data.get('id'),
                win=data.get('win'),
            )

        return JsonResponse({}, status=200)
