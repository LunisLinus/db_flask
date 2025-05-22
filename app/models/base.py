from datetime import datetime
from app import db


class BaseModel:
    """Base model class that includes common functionality"""

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def save(self):
        """Save the model instance"""
        db.session.add(self)
        db.session.commit()
        return self

    def delete(self):
        """Delete the model instance"""
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def get_by_id(cls, id):
        """Get a model instance by id"""
        return cls.query.get(id)

    @classmethod
    def get_all(cls):
        """Get all model instances"""
        return cls.query.all()

    def to_dict(self):
        """Convert model instance to dictionary"""
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
