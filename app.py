import os
from dotenv import load_dotenv
from flask import Flask, jsonify
from flask_debugtoolbar import DebugToolbarExtension
from flask_cors import CORS
from models import db, connect_db, Image
from service import get_images_service, upload_service

BUCKET_THUMBNAILS_FOLDER = 'pixly/images/thumbnails/'
BUCKET_ORIGINALS_FOLDER = 'pixly/images/originals/'

load_dotenv()

app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ['DATABASE_URL'].replace("postgres://", "postgresql://"))
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = os.environ['SECRET_KEY']
toolbar = DebugToolbarExtension(app)

connect_db(app)
db.create_all()


@app.route("/api/images")
def get_images():
    """ grabs all images from the database and returns as json """

    images = get_images_service()
    serialized = [image.serialize() for image in images]

    return jsonify(images=serialized)


@app.route("/api/images/<int:id>")
def get_image(id):
    """ grabs an image from the database and returns as json """

    image = Image.query.get_or_404(id)
    serialized_image = image.serialize_with_exif()

    return jsonify(image=serialized_image)


@app.post("/api/images")
def upload_image():
    """ post route for uploading image from front end """

    image = upload_service()

    if image is None:
        return (jsonify(error="File failed to upload."), 500)

    serialized = image.serialize()

    return (jsonify(image = serialized),201)


@app.patch("/api/images/<int:id>")
def addView(id):
    """ increments view count by 1 for image """

    image = Image.query.get_or_404(id)
    image.views += 1

    db.session.commit()

    return jsonify(views = image.views)