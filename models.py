""" models for pixly """

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def connect_db(app):
    """ connects this database to the provided flask app"""
    app.app_context().push()
    db.app = app
    db.init_app(app)


class Image(db.Model):
    """ model for images table"""

    __tablename__ = "images"

    ###### TABLE COLUMNS ######

    id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True
    )
    file_name = db.Column(
        db.Text,
        nullable=False,
        unique=True
    )
    title = db.Column(
        db.String(50),
        nullable=False
    )
    caption = db.Column(
        db.String(100),
        nullable=True,
    )
    upload_at = db.Column(
        db.DateTime,
        nullable=False,
        default=db.func.now()
    )
    views = db.Column(
        db.Integer,
        default=0,
        nullable=False
    )
    photographer = db.Column(
        db.String(50),
        nullable=True
    )

    ###### RELATIONSHIPS ######

    exif_data = db.relationship('EXIFData', backref='image')
    tags = db.relationship('Tag', secondary='images_tags', backref='images')

    ###### INSTANCE METHOD ######

    def __repr__(self):
        return f'<Image {self.id} {self.title} {self.file_name}>'

    def serialize(self):
        """ serialize to dictionary """
        return {
            "id":self.id,
            "file_name":self.file_name,
            "title":self.title,
            "caption":self.caption,
            "upload_at":self.upload_at,
            "views":self.views,
            "photographer":self.photographer
        }

    def serialize_with_exif(self):
        """ Serial to dictionary with EXIF data """

        image_exif_data = self.exif_data[0]
        serialized_image = self.serialize()
        serialized_exif_data = image_exif_data.serialize()
        serialized_exif_data.pop("image_id")
        serialized_image['exif_data'] = serialized_exif_data

        return serialized_image


class EXIFData(db.Model):
    """ Model for exif_data table """

    __tablename__ = 'exif_data'

    ###### TABLE COLUMNS ######

    image_id = db.Column(
        db.Integer,
        db.ForeignKey('images.id', ondelete='CASCADE'),
        primary_key=True
    )
    height_px = db.Column(
        db.Integer,
        nullable=False
    )
    width_px = db.Column(
        db.Integer,
        nullable=False
    )
    device_manufacturer = db.Column(
        db.String(100),
        nullable=True
    )
    device_model = db.Column(
        db.String(100),
        nullable=True
    )
    focal_length = db.Column(
        db.Integer,
        nullable=True
    )
    f_stop = db.Column(
        db.Float,
        nullable=True
    )
    exposure = db.Column(
        db.Integer,
        nullable=True
    )
    location = db.Column(
        db.String(100),
        nullable=True
    )
    taken_at = db.Column(
        db.String(100),
        nullable=True
    )

    ###### INSTANCE METHODS ######

    def __repr__(self):
        return f'<EXIFData Image {self.image_id}: {self.image.title}>'


    def serialize(self):
        """ serialize to dictionary """
        return {
            "image_id":self.image_id,
            "height_px":self.height_px,
            "width_px":self.width_px,
            "device_manufacturer":self.device_manufacturer,
            "device_model":self.device_model,
            "focal_length":self.focal_length,
            "f_stop":self.f_stop,
            "exposure":self.exposure,
            "location":self.location,
            "taken_at":self.taken_at
        }


class Tag(db.Model):
    """ Model for tags table """

    __tablename__ = 'tags'

    ###### TABLE COLUMNS ######

    name = db.Column(
        db.String(30),
        primary_key = True
    )

    ###### INSTANCE METHODS ######

    def __repr__(self):
        return f'<Tag {self.name}>'


class ImageTag(db.Model):
    """ Model for images - tags association table """

    __tablename__ = 'images_tags'

    ###### TABLE COLUMNS ######

    image_id = db.Column(
        db.Integer,
        db.ForeignKey('images.id', ondelete='CASCADE'),
        primary_key=True
    )
    tag_name = db.Column(
        db.String(30),
        db.ForeignKey('tags.name', ondelete='CASCADE'),
        primary_key=True
    )

    ###### INSTANCE METHODS ######

    def __repr__(self):
        return f'<ImageTag Image {self.image_id}: Tag {self.tag_name}>'
