#
import json

#
from django.http import JsonResponse
from django.views import View

#
from ..models import Notify, BidResponse, Creative


class NotifyView(View):

    @staticmethod
    def post(request):
        data = json.loads(request.body)
        if data.get('win'):
            notifications = Notify.objects.filter(notify_id=data.get('id'))
            if notifications.exists():
                return JsonResponse({'error': 'Wrong id'}, status=404)
            notify = Notify.objects.create(
                notify_id=data.get('id'),
                win=data.get('win'),
                price=data.get('price'),
                click=data.get('click'),
                conversion=data.get('conversion'),
                revenue=data.get('revenue'),
            )

            try:
                bid_response = BidResponse.objects.get(bid_id=notify.notify_id)
                creative = Creative.objects.get(external_id=bid_response.external_id)
                campaign = creative.campaign
            except:
                return JsonResponse({'error': 'Wrong id'}, status=404)

            # Change budget
            campaign.budget -= notify.price
            campaign.save()
        else:
            try:
                notify = Notify.objects.create(
                    notify_id=data.get('id'),
                    win=data.get('win'),
                )
            except:
                pass

        return JsonResponse({}, status=200)
