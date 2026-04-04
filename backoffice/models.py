from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Artwork(db.Model):
    __tablename__ = "artwork"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    year = db.Column(db.String(4), nullable=True)
    technique = db.Column(db.String(255), default="Acquerello su carta")
    image_path = db.Column(db.String(512), nullable=True)
    thumb_path = db.Column(db.String(512), nullable=True)
    drive_file_id = db.Column(db.String(255), nullable=True)
    drive_thumb_id = db.Column(db.String(255), nullable=True)
    is_published = db.Column(db.Boolean, default=False)
    position = db.Column(db.Integer, default=0)
    descrizione = db.Column(db.Text, nullable=True)

    def to_dict(self):
        from turso_db import _get_optimized_url
        return {
            "title": self.title,
            "category": self.category,
            "image": _get_optimized_url(self.image_path),
            "thumb": _get_optimized_url(self.thumb_path),
            "details": f"{self.year}, {self.technique}" if self.year else self.technique,
            "descrizione": self.descrizione or "",
        }


class Category(db.Model):
    __tablename__ = "category"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=False)
    position = db.Column(db.Integer, default=0)


class Gallery(db.Model):
    __tablename__ = "gallery"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    items = db.relationship(
        "GalleryItem",
        backref="gallery",
        cascade="all, delete-orphan",
        order_by="GalleryItem.position",
    )


class GalleryItem(db.Model):
    __tablename__ = "gallery_item"

    id = db.Column(db.Integer, primary_key=True)
    gallery_id = db.Column(db.Integer, db.ForeignKey("gallery.id"), nullable=False)
    artwork_id = db.Column(db.Integer, db.ForeignKey("artwork.id"), nullable=False)
    position = db.Column(db.Integer, default=0)
    artwork = db.relationship("Artwork")
