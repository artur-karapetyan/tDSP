#
import json

from django.core.paginator import Paginator
#
from django.http import JsonResponse, HttpResponse
from django.views import View
from django.views.decorators.http import require_GET

#
from ..models import Campaign, Configuration
from ..tools.admin_authorized import admin_authorized
from ..tools.data_status import data_status
from ..tools.is_authorized import is_authorized


class CampaignView(View):

    @staticmethod
    @admin_authorized
    def post(request):
        data = json.loads(request.body)

        name = data['name']
        budget = data['budget']

        config = Configuration.objects.first()
        min_bid = config.impression_revenue

        campaign = Campaign.objects.create(name=name, budget=budget, min_bid=min_bid)
        campaign.save()

        response_data = {
            'id': campaign.id,
            'name': campaign.name,
            'budget': campaign.budget,
        }

        return JsonResponse(response_data, status=201)

    @staticmethod
    @require_GET
    @is_authorized
    def get(request):
        if request.GET.get('page'):
            page = int(request.GET.get('page'))
            campaigns = Campaign.objects.order_by('-id').all()

            # Set the number of items per page
            items_per_page = 11

            # Create a Paginator object
            paginator = Paginator(campaigns, items_per_page)

            # Get the current page number from the request query parameters
            page_number = page

            # Get the Page object for the current page
            page_obj = paginator.get_page(page_number)

            data = []
            for campaign in page_obj:
                campaign_data = {
                    'is_enabled': campaign.is_enabled,
                    'id': campaign.id,
                    'name': campaign.name,
                    'budget': campaign.budget,
                    'min_bid': campaign.min_bid,
                }
                data.append(campaign_data)

            # Create a dictionary containing the pagination information and the data for the current page
            response_data = {
                'page': page_number,
                'total_pages': paginator.num_pages,
                'total_items': paginator.count,
                'data': data,
            }
            return data_status(response_data)
        else:
            campaign_ids = list(Campaign.objects.order_by('-id').values_list('id', flat=True))
            return data_status(campaign_ids)

    @staticmethod
    @is_authorized
    def patch(request, campaign_id=None):
        if campaign_id:
            # if campaign_id is provided, update only the specified campaign's min_bid
            campaign = Campaign.objects.get(id=campaign_id)

            data = json.loads(request.body)
            if 'min_bid' in data:
                campaign.min_bid = data['min_bid']
            if 'is_enabled' in data:
                campaign.is_enabled = data['is_enabled']

            campaign.save()

        else:
            # if campaign_id is not provided, update all campaigns' min_bid
            data = json.loads(request.body)
            min_bid = data['min_bid']

            Campaign.objects.all().update(min_bid=min_bid)

        return HttpResponse(
            json.dumps({"status": "ok"}), status=200, content_type="application/json"
        )
