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
    is_published = db.Column(db.Boolean, default=False)
    position = db.Column(db.Integer, default=0)

    def to_dict(self):
        return {
            "title": self.title,
            "category": self.category,
            "image": self.image_path,
            "thumb": self.thumb_path,
            "details": f"{self.year}, {self.technique}" if self.year else self.technique,
        }
