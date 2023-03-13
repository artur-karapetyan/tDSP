#
import json
import requests

#
from django.views import View
from django.http import JsonResponse, HttpResponse

#
from ..models import BidRequest, Creative, BidResponse, Configuration, Campaign, CampaignFrequency


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
        config = Configuration.objects.first()
        impression_rev = config.impression_revenue
        click_rev = config.click_revenue
        conversion_rev = config.conversion_revenue

        expected_click_revenue = click_rev * click_prob
        expected_conv_revenue = conversion_rev * conv_prob

        price = (expected_click_revenue + expected_conv_revenue) / 2

        if campaign.budget - price < 0:
            price = campaign.budget

        return price

    @staticmethod
    def check_frequency_capping(user_id, campaign):
        # get the campaign frequency for the user and campaign
        campaign_frequency, created = CampaignFrequency.objects.get_or_create(
            user_id=user_id,
            campaign=campaign,
        )

        # check if the campaign has reached its frequency cap for the user
        if campaign_frequency.frequency >= Configuration.objects.first().frequency_capping:
            return False

        # increment the campaign frequency and save
        campaign_frequency.frequency += 1
        campaign_frequency.save()

        return True

    @staticmethod
    def script_mode(request):
        # extract the request body data
        request_data = json.loads(request.body)

        # extract the mandatory fields from the request data
        bid_id = request_data.get('id')
        banner_width = request_data['imp']['banner']['w']
        banner_height = request_data['imp']['banner']['h']
        click_prob = request_data['click']['prob']
        conv_prob = request_data['conv']['prob']
        domain = request_data['site']['domain']
        ssp_id = request_data['ssp']['id']
        user_id = request_data['user']['id']

        authorized = BidView.check_ads_txt(domain, ssp_id)

        if not authorized:
            response_data = HttpResponse(content_type='text/plain;charset=UTF8', status=204)
            response_data.content = "No Bid"
            return response_data

        # check if mandatory fields are present
        if not all([bid_id, banner_width, banner_height, click_prob, conv_prob, domain, ssp_id, user_id]):
            response_data = HttpResponse(content_type='text/plain;charset=UTF8', status=204)
            response_data.content = "No Bid"
            return response_data

        # convert banner dimensions to integers
        try:
            banner_width = int(banner_width)
            banner_height = int(banner_height)
        except ValueError:
            response_data = HttpResponse(content_type='text/plain;charset=UTF8', status=204)
            response_data.content = "No Bid"
            return response_data

        # check if banner dimensions are valid
        if banner_width > 2000 or banner_height > 2000:
            response_data = HttpResponse(content_type='text/plain;charset=UTF8', status=204)
            response_data.content = "No Bid"
            return response_data

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
        )

        # Assume that blocked_categories is a list of blocked category codes
        blocked_categories = request_data.get('bcat', [])

        # Get all creatives that don't belong to blocked categories
        available_creatives = Creative.objects.exclude(categories__code__in=blocked_categories)

        # Select a creative at random from the available list
        creative = available_creatives.order_by('?').first()

        campaign = creative.campaign

        # Check frequency capping
        frequency_capping = BidView.check_frequency_capping(user_id, campaign)

        if creative and frequency_capping:
            url = f"http://{request.get_host()}/creatives/{creative.name}?width={banner_width}&height={banner_height}"

            # calculate price
            price = BidView.calculate_price(float(click_prob), float(conv_prob), campaign)

            # create bid response object
            bid_response = BidResponse.objects.create(
                bid_id=bid_id,
                external_id=creative.external_id,
                price=price,
            )
            print(price)
            # create response body
            response = {
                'external_id': creative.external_id,
                'price': price,
                'image_url': url,
                'cat': list(creative.categories.values_list('code', flat=True)),
            }
            response_data = JsonResponse(response, status=200)
        else:
            response_data = HttpResponse(content_type='text/plain;charset=UTF8', status=204)
            response_data.content = "No Bid"

        # return bid response
        return response_data

    @staticmethod
    def free_mode(request):
        # extract the request body data
        request_data = json.loads(request.body)

        # extract the mandatory fields from the request data
        bid_id = request_data.get('id')
        banner_width = request_data['imp']['banner']['w']
        banner_height = request_data['imp']['banner']['h']
        click_prob = request_data['click']['prob']
        conv_prob = request_data['conv']['prob']
        domain = request_data['site']['domain']
        ssp_id = request_data['ssp']['id']
        user_id = request_data['user']['id']

        authorized = BidView.check_ads_txt(domain, ssp_id)

        if not authorized:
            response_data = HttpResponse(content_type='text/plain;charset=UTF8', status=204)
            response_data.content = "No Bid"
            return response_data

        # check if mandatory fields are present
        if not all([bid_id, banner_width, banner_height, click_prob, conv_prob, domain, ssp_id, user_id]):
            response_data = HttpResponse(content_type='text/plain;charset=UTF8', status=204)
            response_data.content = "No Bid"
            return response_data

        # convert banner dimensions to integers
        try:
            banner_width = int(banner_width)
            banner_height = int(banner_height)
        except ValueError:
            response_data = HttpResponse(content_type='text/plain;charset=UTF8', status=204)
            response_data.content = "No Bid"
            return response_data

        # check if banner dimensions are valid
        if banner_width > 2000 or banner_height > 2000:
            response_data = HttpResponse(content_type='text/plain;charset=UTF8', status=204)
            response_data.content = "No Bid"
            return response_data

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
        )

        # Assume that blocked_categories is a list of blocked category codes
        blocked_categories = request_data.get('bcat', [])

        # Get all creatives that don't belong to blocked categories
        available_creatives = Creative.objects.exclude(categories__code__in=blocked_categories)

        # Select a creative at random from the available list
        creative = available_creatives.order_by('?').first()

        campaign = creative.campaign

        # Check frequency capping
        frequency_capping = BidView.check_frequency_capping(user_id, campaign)

        if creative and frequency_capping:
            url = f"http://{request.get_host()}/creatives/{creative.name}?width={banner_width}&height={banner_height}"

            # calculate price
            price = BidView.calculate_price(float(click_prob), float(conv_prob), campaign)

            # create bid response object
            bid_response = BidResponse.objects.create(
                bid_id=bid_id,
                external_id=creative.external_id,
                price=price,
            )
            print(price)
            # create response body
            response = {
                'external_id': creative.external_id,
                'price': price,
                'image_url': url,
                'cat': list(creative.categories.values_list('code', flat=True)),
            }
            response_data = JsonResponse(response, status=200)
        else:
            response_data = HttpResponse(content_type='text/plain;charset=UTF8', status=204)
            response_data.content = "No Bid"

        # return bid response
        return response_data

    @staticmethod
    def post(request):
        config = Configuration.objects.first()
        mode = config.mode

        if mode:
            return BidView.script_mode(request)
        else:
            return BidView.free_mode(request)
