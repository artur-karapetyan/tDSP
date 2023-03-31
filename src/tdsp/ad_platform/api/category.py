#
from django.views import View
from django.core.paginator import Paginator

#
from ..models import Category

#
from ..tools.data_status import data_status
from ..tools.admin_authorized import admin_authorized


class CategoryView(View):

    @staticmethod
    @admin_authorized
    def get(request):
        category_codes = list(Category.objects.order_by('-id').values_list('code', flat=True))
        return data_status(category_codes)

    @staticmethod
    @admin_authorized
    def get_page(request, page):
        categories = Category.objects.order_by('-id').all()

        # Set the number of items per page
        items_per_page = 11

        # Create a Paginator object
        paginator = Paginator(categories, items_per_page)

        # Get the current page number from the request query parameters
        page_number = page

        # Get the Page object for the current page
        page_obj = paginator.get_page(page_number)

        data = []
        for category in page_obj:
            category_data = {
                'id': category.id,
                'code': category.code,
                'name': category.name,
                'parent': category.parent.id if category.parent is not None else "-",
            }
            data.append(category_data)

        # Create a dictionary containing the pagination information and the data for the current page
        response_data = {
            'page': page_number,
            'total_pages': paginator.num_pages,
            'total_items': paginator.count,
            'data': data,
        }
        return data_status(response_data)
