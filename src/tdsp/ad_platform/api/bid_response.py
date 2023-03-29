from django.core.paginator import Paginator
from django.views import View

from ..models import BidResponse

from ..tools.data_status import data_status
from ..tools.admin_authorized import admin_authorized


class BidResponseView(View):

    @staticmethod
    @admin_authorized
    def get(request, page):
        responses = BidResponse.objects.order_by('-id').all()

        # Set the number of items per page
        items_per_page = 11

        # Create a Paginator object
        paginator = Paginator(responses, items_per_page)

        # Get the current page number from the request query parameters
        page_number = page

        # Get the Page object for the current page
        page_obj = paginator.get_page(page_number)

        data = []
        for response in page_obj:
            res_data = {
                'id': response.id,
                'bid_id': response.bid_id,
                'external_id': response.external_id,
                'price': response.price,
            }
            data.append(res_data)

        # Create a dictionary containing the pagination information and the data for the current page
        response_data = {
                'page': page_number,
                'total_pages': paginator.num_pages,
                'total_items': paginator.count,
                'data': data,
            }
        return data_status(response_data)
