#
import json
import requests
from django.db.models import Q

#
from django.views import View
from django.http import JsonResponse, HttpResponse

#
from ..models import BidRequest, Creative, BidResponse, Configuration, Campaign, CampaignFrequency, Category
from ..tools.admin_authorized import admin_authorized


class BidView(View):

    @staticmethod
    def check_ads_txt(server, site_domain, ssp_id):
        """
        Checks the ads.txt file for the publisher domain and returns True if the ssp_id is authorized to sell traffic
        from the site_domain, False otherwise.
        """
        ads_txt_url = f"http://{server}/ads.txt?publisher={site_domain}"
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
        # impression_rev = config.impression_revenue
        click_rev = config.click_revenue
        conversion_rev = config.conversion_revenue

        expected_click_revenue = click_rev * click_prob
        expected_conv_revenue = click_prob * conversion_rev * conv_prob

        if not config.game_goal:  # If game_goal is "revenue"
            price = (expected_click_revenue + expected_conv_revenue) / 2
        else:  # If game_goal is (spent budget) / (number of clicks)
            if click_prob > 0.5:
                price = expected_click_revenue + (expected_conv_revenue / 2)
            else:
                price = (expected_click_revenue + expected_conv_revenue) / 3

        price = max(campaign.min_bid, price)

        if campaign.budget - price < 0:
            price = campaign.budget

        if price < 0:
            price = 0

        price = round(price, 2)

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

        return True

    @staticmethod
    def return_creatives(bcat, user_id):

        # get all enabled campaigns
        enabled_campaigns = Campaign.objects.filter(is_enabled=True)

        # get all valid campaigns (i.e., enabled campaigns with frequency cap not exceeded)
        valid_campaigns = []
        for campaign in enabled_campaigns:
            if BidView.check_frequency_capping(user_id, campaign):
                valid_campaigns.append(campaign)

        # get all creatives belonging to valid campaigns
        query = Q()
        for campaign in valid_campaigns:
            query |= Q(campaign=campaign)

        valid_creatives = Creative.objects.filter(query)

        forbidden_categories = []
        forbidden_subcategories = []

        # Split the list into categories and subcategories
        for item in bcat:
            if "-" in item:
                forbidden_subcategories.append(item)
            else:
                forbidden_categories.append(item)

        # Construct the query
        query = Q()
        for category in forbidden_categories:
            query |= Q(categories__code=category)

        # Exclude the forbidden subcategories
        for category_code in forbidden_categories:
            category = Category.objects.get(code=category_code)
            forbidden_subcategories += category.get_subcategory_codes()

        # Exclude the forbidden creatives
        creatives = valid_creatives.exclude(query).exclude(categories__code__in=forbidden_subcategories)

        return creatives

    @staticmethod
    def script_mode(request):
        # extract the request body data
        request_data = json.loads(request.body)

        # extract the mandatory fields from the request data
        bid_id = request_data['id']
        banner_width = request_data['imp']['banner']['w']
        banner_height = request_data['imp']['banner']['h']
        click_prob = request_data['click']['prob']
        conv_prob = request_data['conv']['prob']
        domain = request_data['site']['domain']
        ssp_id = request_data['ssp']['id']
        user_id = request_data['user']['id']

        # server = request.META.get('REMOTE_ADDR')
        # authorized = BidView.check_ads_txt(server, domain, ssp_id)
        #
        # if not authorized:
        #     response_data = HttpResponse(content_type='text/plain;charset=UTF8', status=204)
        #     response_data.content = "No Bid"
        #     return response_data

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
            banner_width = 500
            banner_height = 500

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
        available_creatives = BidView.return_creatives(blocked_categories, user_id)

        # Select a creative at random from the available list
        creative = available_creatives.order_by('?').first()

        # Check frequency capping
        # frequency_capping = BidView.check_frequency_capping(user_id, creative.campaign)

        if creative:  # and frequency_capping:
            url = f"http://{request.get_host()}/api/creatives/{creative.id}?width={banner_width}&height={banner_height}"

            # calculate price
            price = BidView.calculate_price(float(click_prob), float(conv_prob), creative.campaign)

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
        bid_id = request_data['id']
        banner_width = request_data['imp']['banner']['w']
        banner_height = request_data['imp']['banner']['h']
        click_prob = request_data['click']['prob']
        conv_prob = request_data['conv']['prob']
        domain = request_data['site']['domain']
        ssp_id = request_data['ssp']['id']
        user_id = request_data['user']['id']

        # server = request.META.get('REMOTE_ADDR')
        # authorized = BidView.check_ads_txt(server, domain, ssp_id)
        #
        # if not authorized:
        #     response_data = HttpResponse(content_type='text/plain;charset=UTF8', status=204)
        #     response_data.content = "No Bid"
        #     return response_data

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
        available_creatives = BidView.return_creatives(blocked_categories, user_id)

        # Select a creative at random from the available list
        creative = available_creatives.order_by('?').first()

        # Check frequency capping
        # frequency_capping = BidView.check_frequency_capping(user_id, campaign)

        if creative:  # and frequency_capping:
            url = f"http://{request.get_host()}/api/creatives/{creative.id}?width={banner_width}&height={banner_height}"

            # calculate price
            price = BidView.calculate_price(float(click_prob), float(conv_prob), creative.campaign)

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
    @admin_authorized
    def post(request):
        config = Configuration.objects.first()

        if config:
            mode = config.mode
        else:
            response_data = HttpResponse(content_type='text/plain;charset=UTF8', status=204)
            response_data.content = "No Bid"
            return response_data

        if mode:
            return BidView.script_mode(request)
        else:
            return BidView.free_mode(request)
