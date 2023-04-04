from flask import request
from models import db, Image, EXIFData

def get_and_filter_images():
    """ Query and filter images """

    search_term  = request.args.get("searchTerm") # search term or None

    is_filtering_width = request.args.get('isFilteringWidth') == 'true'
    is_filtering_height = request.args.get('isFilteringHeight') == 'true'

    min_width = request.args.get('minWidth') # '' or an integer string e.g. '10'
    min_width = int(min_width) if is_filtering_width and min_width.isnumeric() else 0

    max_width = request.args.get('maxWidth') # '' or an integer string e.g. '10'
    max_width = int(max_width) if is_filtering_width and max_width.isnumeric() else float('inf')

    min_height = request.args.get('minHeight') # '' or an integer string e.g. '10'
    min_height = int(min_height) if is_filtering_height and min_height.isnumeric() else 0

    max_height = request.args.get('maxHeight') # '' or an integer string e.g. '10'
    max_height = int(max_height) if is_filtering_height and max_height.isnumeric() else float('inf')

    # Filter by EXIF data
    images = db.session.query(Image).join(EXIFData)

    images = images.filter(EXIFData.width_px >= min_width)
    images = images.filter(EXIFData.width_px <= max_width)

    images = images.filter(EXIFData.height_px >= min_height)
    images = images.filter(EXIFData.height_px <= max_height)

    if search_term:
        images = images.filter(Image.title.ilike(f"%{search_term}%"))

    images = images.order_by(Image.id).all()

    return images


def serialize_image_with_exif_data(image):
    """ Serialize an image with its exif data and return it """

    image_exif_data = image.exif_data[0]
    serialized_image = image.serialize()
    serialized_exif_data = image_exif_data.serialize()
    serialized_exif_data.pop("image_id")
    serialized_image['exif_data'] = serialized_exif_data

    return serialized_image