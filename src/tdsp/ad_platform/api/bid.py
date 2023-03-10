import json

import requests
from django.http import JsonResponse
from django.views import View
from django.views.decorators.http import require_POST

from ..models import BidRequest, Creative, BidResponse, Configuration, Campaign


class BidView(View):
    server_url = " "  # Replace with given url

    @staticmethod
    def check_ads_txt(site_domain, ssp_id):
        """
        Checks the ads.txt file for the publisher domain and returns True if the ssp_id is authorized to sell traffic
        from the site_domain, False otherwise.
        """
        server = BidView.server_url
        ads_txt_url = f"{server}/ads.txt?publisher={site_domain}"
        try:
            response = requests.get(ads_txt_url)
            if response.status_code == 200:
                for line in response.text.split("\n"):
                    fields = line.strip().split(",")
                    if len(fields) >= 3 and fields[1].strip() == ssp_id:
                        return True
        except:
            pass
        return False

    @staticmethod
    def calculate_price(click_prob, conv_prob, campaign):
        impression_rev = Configuration.impressions_revenue
        click_rev = Configuration.click_revenue
        conversion_rev = Configuration.conversion_revenue

        expected_click_revenue = click_rev*click_prob
        expected_conv_revenue = conversion_rev*conv_prob

        price = (expected_click_revenue + expected_conv_revenue)/2

        if campaign.budget - price < 0:
            price = campaign.budget

        return price

    @staticmethod
    def post(request):
        # extract the request body data
        request_data = request.POST.dict()

        # extract the mandatory fields from the request data
        bid_id = request_data.get('id')
        banner_width = request_data.get('imp.banner.w')
        banner_height = request_data.get('imp.banner.h')
        click_prob = request_data.get('click.prob')
        conv_prob = request_data.get('conv.prob')
        domain = request_data.get('site.domain')
        ssp_id = request_data.get('ssp.id')
        user_id = request_data.get('user.id')

        authorized = BidView.check_ads_txt(domain, ssp_id)

        if not authorized:
            return JsonResponse({'error': 'SSP is not authorized'})

        # check if mandatory fields are present
        if not all([bid_id, banner_width, banner_height, click_prob, conv_prob, domain, ssp_id, user_id]):
            return JsonResponse({'error': 'Missing mandatory fields'})

        # convert banner dimensions to integers
        try:
            banner_width = int(banner_width)
            banner_height = int(banner_height)
        except ValueError:
            return JsonResponse({'error': 'Invalid banner dimensions'})

        # check if banner dimensions are valid
        if banner_width > 1000 or banner_height > 1000:
            return JsonResponse({'error': 'Banner dimensions too large'})

        # create bid request object
        bid_request = BidRequest.objects.create(
            bid_id=bid_id,
            banner_width=banner_width,
            banner_height=banner_height,
            click_probability=float(click_prob),
            conversion_probability=float(conv_prob),
            domain=domain,
            ssp_id=ssp_id,
            user_id=user_id,
            price=0.0,
        )

        # Assume that blocked_categories is a list of blocked category codes
        blocked_categories = request_data.get('bcat', [])

        # Get all creatives that don't belong to blocked categories
        available_creatives = Creative.objects.exclude(categories__code__in=blocked_categories)

        # Select a creative at random from the available list
        creative = available_creatives.order_by('?').first()

        campaign = Campaign.objects.get(id=creative.campaign_id['id'])

        price = BidView.calculate_price(click_prob, conv_prob, campaign)

        if creative:
            # create bid response object
            bid_response = BidResponse.objects.create(
                bid_id=bid_id,
                external_id=creative.external_id,
                price=price,
            )

            # create response body
            response = {
                'external_id': creative.external_id,
                'price': price,
                'image_url': f'{creative.file_url}?width={banner_width}&height={banner_height}',
                'cat': list(creative.categories.values_list('code', flat=True)),
            }
            response_data = JsonResponse(response, status=200)
        else:
            response_data = JsonResponse({}, status=204)

        # return bid response as JSON
        return response_data
