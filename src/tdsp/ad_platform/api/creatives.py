#
import json
import base64
from io import BytesIO

#
from PIL import Image
from django.core.paginator import Paginator

#
from django.views import View
from django.core.files.base import ContentFile
from django.http import JsonResponse, HttpResponse

#
from ..models import Creative, Category, Campaign
from ..tools.admin_authorized import admin_authorized
from ..tools.data_status import data_status


class CreativeView(View):

    @staticmethod
    def get_image(request, creative_id):
        width = int(request.GET.get('width', 0))
        height = int(request.GET.get('height', 0))
        if width > 2000 or height > 2000:
            width = 500
            height = 500
        try:
            creative = Creative.objects.get(id=creative_id)
        except Creative.DoesNotExist:
            return HttpResponse(status=404)

        img = Image.open(creative.file)

        image = Image.new("RGB", (width, height), "white")

        scale = min(width / img.width, height / img.height)
        img = img.resize((int(img.width * scale), int(img.height * scale)))

        x_pos = (image.width - img.width) // 2
        y_pos = (image.height - img.height) // 2

        image.paste(img, (x_pos, y_pos))

        buffer = BytesIO()
        image.save(buffer, format='PNG')
        buffer.seek(0)

        return HttpResponse(buffer, content_type='image/png')

    @staticmethod
    @admin_authorized
    def post(request):
        data = json.loads(request.body)

        external_id = data['external_id']
        name = data['name']
        categories = data.get('categories', [])
        campaign_id = data.get('campaign', {}).get('id')
        file_data = data['file']

        # Check if external ID is unique
        if Creative.objects.filter(external_id=external_id).exists():
            return JsonResponse({'error': 'External ID already exists'}, status=400)

        # Decode the file data and create a ContentFile object
        file_data = base64.b64decode(file_data)

        # Create or retrieve the campaign object
        try:
            campaign = Campaign.objects.get(id=campaign_id)
        except Campaign.DoesNotExist:
            return JsonResponse({'error': 'Campaign does not exist'}, status=400)

        # Create the creative object
        creative = Creative.objects.create(external_id=external_id, name=name, campaign=campaign)
        creative.save()
        file = ContentFile(file_data, name=f'{creative.id}.png')
        img = Image.open(file)
        url = f"http://{request.get_host()}/api/creatives/{creative.id}?width={img.width}&height={img.height}"
        creative.file = file
        creative.url = url
        creative.save()

        # Add categories to the creative object
        for category in categories:
            category_obj = Category.objects.get(code=category['code'])
            creative.categories.add(category_obj)

        # Create the response
        response_data = {
            'id': creative.id,
            'external_id': creative.external_id,
            'name': creative.name,
            'categories': [{'id': category.id, 'code': category.code} for category in creative.categories.all()],
            'campaign': {'id': creative.campaign.id, 'name': creative.campaign.name},
            'url': url,
        }

        return JsonResponse(response_data, status=201)

    @staticmethod
    @admin_authorized
    def get(request, page):
        creatives = Creative.objects.order_by('-id').all()

        # Set the number of items per page
        items_per_page = 3

        # Create a Paginator object
        paginator = Paginator(creatives, items_per_page)

        # Get the current page number from the request query parameters
        page_number = page

        # Get the Page object for the current page
        page_obj = paginator.get_page(page_number)

        data = []
        for creative in page_obj:
            url = f"http://{request.get_host()}/api/creatives/{creative.id}?width=280&height=280"
            creative_data = {
                'url': url,
                'id': creative.id,
                'name': creative.name,
                'external_id': creative.external_id,
                'campaign_id': creative.campaign.id,
                'campaign_name': creative.campaign.name,
                'categories': list(creative.categories.values_list('code', flat=True)),
            }
            data.append(creative_data)

        # Create a dictionary containing the pagination information and the data for the current page
        response_data = {
            'page': page_number,
            'total_pages': paginator.num_pages,
            'total_items': paginator.count,
            'data': data,
        }
        return data_status(response_data)
