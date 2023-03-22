import openpyxl
from ad_platform.models import Category


def run():
    workbook = openpyxl.load_workbook('scripts/categories.xlsx')

    # Get the first worksheet
    worksheet = workbook.active

    # Loop through each row in the worksheet
    for row in worksheet.iter_rows(values_only=True):
        code = row[0]
        tier = row[1]
        name = row[2]

        # Create or get the category object
        category, created = Category.objects.get_or_create(code=code, name=name)

        # If this is a subcategory, set its parent category
        if tier == 'Tier 2':
            parent_code = code.split('-')[0]
            parent = Category.objects.get(code=parent_code)
            category.parent = parent

        # Save the category
        category.save()
