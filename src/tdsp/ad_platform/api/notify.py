#
import json

#
from django.views import View
from django.http import JsonResponse
from django.core.paginator import Paginator

#
from ..models import Notify, BidResponse, Creative, BidRequest, CampaignFrequency

#
from ..tools.data_status import data_status
from ..tools.admin_authorized import admin_authorized
from ..tools.is_authorized import is_authorized


class NotifyView(View):

    @staticmethod
    @admin_authorized
    def post(request):
        data = json.loads(request.body)
        if data.get('win'):
            notifications = Notify.objects.filter(notify_id=data.get('id'))
            if notifications.exists():
                return JsonResponse({'error': 'Wrong id'}, status=400)
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
                bid_request = BidRequest.objects.get(bid_id=notify.notify_id)
                user_id = bid_request.user_id
                campaign = creative.campaign
                freq_cap = CampaignFrequency.objects.get(user_id=user_id, campaign=campaign)
            except:
                return JsonResponse({'error': 'Wrong id'}, status=404)

            # Change frequency capping
            freq_cap.frequency += 1
            freq_cap.save()

            # Change budget
            campaign.budget -= notify.price
            campaign.save()
        else:
            try:
                Notify.objects.create(
                    notify_id=data.get('id'),
                    win=data.get('win'),
                )
            except:
                pass

        return JsonResponse({}, status=200)

    @staticmethod
    @is_authorized
    def get(request, page):
        notifies = Notify.objects.order_by("-id").all()

        # Set the number of items per page
        items_per_page = 11

        # Create a Paginator object
        paginator = Paginator(notifies, items_per_page)

        # Get the current page number from the request query parameters
        page_number = page

        # Get the Page object for the current page
        page_obj = paginator.get_page(page_number)

        data = []
        for notify in page_obj:
            notify_data = {
                'id': notify.id,
                'notify_id': notify.notify_id,
                'win': str(notify.win),
                'price': notify.price if notify.win else "-",
                'click': str(notify.click) if notify.win else "-",
                'conversion': str(notify.conversion) if notify.win else "-",
                'revenue': notify.revenue if notify.win else "-",
            }
            data.append(notify_data)

        # Create a dictionary containing the pagination information and the data for the current page
        response_data = {
                'page': page_number,
                'total_pages': paginator.num_pages,
                'total_items': paginator.count,
                'data': data,
            }
        return data_status(response_data)
