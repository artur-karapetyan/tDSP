from django.core.paginator import Paginator
from django.views import View

from ..models import BidRequest

from ..tools.data_status import data_status
from ..tools.admin_authorized import admin_authorized


class BidRequestView(View):

    @staticmethod
    @admin_authorized
    def get(request, page):
        bid_requests = BidRequest.objects.order_by('-id').all()

        # Set the number of items per page
        items_per_page = 11

        # Create a Paginator object
        paginator = Paginator(bid_requests, items_per_page)

        # Get the current page number from the request query parameters
        page_number = page

        # Get the Page object for the current page
        page_obj = paginator.get_page(page_number)

        # Create a list of dictionaries containing the data for each BidRequest object in the current page
        data = []
        for request in page_obj:
            request_data = {
                'id': request.id,
                'bid_id': request.bid_id,
                'banner_width': request.banner_width,
                'banner_height': request.banner_height,
                'click_probability': request.click_probability,
                'conversion_probability': request.conversion_probability,
                'domain': request.domain,
                'ssp_id': request.ssp_id,
                'user_id': request.user_id,
            }
            data.append(request_data)

        # Create a dictionary containing the pagination information and the data for the current page
        response_data = {
            'page': page_number,
            'total_pages': paginator.num_pages,
            'total_items': paginator.count,
            'data': data,
        }

        return data_status(response_data)
