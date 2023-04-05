from flask import request
from models import db, Image, EXIFData
from shortuuid import uuid
from image_processing import (
    get_exif_data, make_thumbnail, convert_to_grayscale, resize_image
)
from pixly_aws import upload_image_to_aws

BUCKET_THUMBNAILS_FOLDER = 'pixly/images/thumbnails/'
BUCKET_ORIGINALS_FOLDER = 'pixly/images/originals/'

def get_images_service():
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


def upload_service():
    """
    Create and upload image and thumbnail to S3

    Returns None if upload fails
    """

    image_file = request.files.get('imgFile')
    file_extension = image_file.filename.split('.')[-1]
    file_name = f'img_{uuid()}.{file_extension}'

    form_data = request.form

    uploaded_image = create_and_upload_image(
        image_file=image_file,
        file_name=file_name,
        form_data=form_data
    )

    if uploaded_image is None:
        return None

    image = Image(
        file_name=file_name,
        title=form_data["title"],
        caption=form_data["caption"],
        photographer=form_data["photographer"])

    db.session.add(image)
    db.session.commit()

    image_data = get_exif_data(uploaded_image)

    image_exif_data = EXIFData(
        image_id = image.id,
        height_px = image_data['height_px'],
        width_px = image_data['width_px'],
        device_manufacturer = image_data['device_manufacturer'],
        device_model = image_data['device_model'],
        focal_length = image_data['focal_length'],
        f_stop = image_data['f_stop'],
        exposure = image_data['exposure'],
        location = image_data['location'],
        taken_at = image_data['taken_at'],
    )

    db.session.add(image_exif_data)
    db.session.commit()

    return image


def create_and_upload_image(image_file, file_name, form_data):
    """
    Create and upload image and thumbnail to S3 with optional edits in form_data

    Returns image file or None if unsuccessful
    """

    filter = form_data['filter'] # '', 'bw'
    resize_percentage = int(form_data['resize']) # 1 - 100

    if filter == 'bw':
        image_file = convert_to_grayscale(image_file)

    if resize_percentage != 100:
        image_file = resize_image(image_file, resize_percentage)

    upload_image_status = upload_image_to_aws(
        image_file,
        BUCKET_ORIGINALS_FOLDER,
        file_name
    )

    thumbnail_file = make_thumbnail(image_file)

    upload_thumbnail_status = upload_image_to_aws(
        thumbnail_file,
        BUCKET_THUMBNAILS_FOLDER,
        file_name
    )

    if not upload_image_status or not upload_thumbnail_status:
        return None

    return image_file