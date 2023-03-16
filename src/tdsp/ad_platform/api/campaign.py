#
import json

#
from django.http import JsonResponse
from django.views import View

#
from ..models import Campaign


class CampaignView(View):

    @staticmethod
    def post(request):
        data = json.loads(request.body)

        name = data['name']
        budget = data['budget']

        campaign = Campaign.objects.create(name=name, budget=budget)
        campaign.save()

        response_data = {
            'id': campaign.id,
            'name': campaign.name,
            'budget': campaign.budget,
        }

        return JsonResponse(response_data, status=201)
