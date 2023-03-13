#
import json
import base64
from io import BytesIO

#
from PIL import Image

#
from django.views import View
from django.http import JsonResponse, HttpResponse

#
from ..models import Creative


class CreativeView(View):

    @staticmethod
    def get(request, name):
        width = int(request.GET.get('width', 0))
        height = int(request.GET.get('height', 0))
        if width > 1000 or height > 1000:
            width = 500
            height = 500
        try:
            creative = Creative.objects.get(name=name)
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
        # Get the data from the request
        data = json.loads(request)
        # Decode the file from base64
        file_data = base64.b64decode(data['file'])
        # Save the creative
        creative = Creative(
            external_id=data['external_id'],
            name=data['name'],
            campaign=data['campaign']['id'],
            file=file_data,
            url='',
        )
        creative.save()
        # Create the file name based on the creative ID
        file_name = f"{creative.id}.png"
        # Write the file to disk
        with open(file_name, 'wb') as f:
            f.write(file_data)
        # Set the file URL and save the creative again
        creative.url = f'creatives/{file_name}'
        creative.save()
        # Create the response data
        response_data = {
            'id': creative.id,
            'external_id': creative.external_id,
            'name': creative.name,
            'categories': [{'code': c.code, 'name': c.name} for c in creative.categories.all()],
            'campaign': {'id': creative.campaign},
            'url': creative.file_url,
        }
        return JsonResponse(response_data)
