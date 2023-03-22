#
import json
import base64
from urllib.parse import quote
from io import BytesIO

#
from PIL import Image

#
from django.views import View
from django.core.files.base import ContentFile
from django.http import JsonResponse, HttpResponse

#
from ..models import Creative, Category, Campaign


class CreativeView(View):

    @staticmethod
    def get(request, name):
        width = int(request.GET.get('width', 0))
        height = int(request.GET.get('height', 0))
        if width > 2000 or height > 2000:
            width = 500
            height = 500
        try:
            creative = Creative.objects.get(id=name)
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
        # new_name = quote(name)
        # new_name = new_name.replace("%", "")
        # file = ContentFile(file_data, name=f'{new_name}.png')
        #
        # img = Image.open(file)

        # url = f"http://{request.get_host()}/api/creatives/{new_name}?width={img.width}&height={img.height}"

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
