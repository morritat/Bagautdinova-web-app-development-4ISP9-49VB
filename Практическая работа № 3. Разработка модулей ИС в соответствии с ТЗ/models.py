from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash,check_password_hash
from .extensions import db,login_manager
class User(UserMixin,db.Model):
 id=db.Column(db.Integer,primary_key=True); login=db.Column(db.String(50),unique=True,nullable=False,index=True); password_hash=db.Column(db.String(255),nullable=False); email=db.Column(db.String(120),unique=True,nullable=False,index=True); phone=db.Column(db.String(24),nullable=False); role=db.Column(db.String(20),nullable=False,default='participant')
 requests=db.relationship('Request',back_populates='user',cascade='all, delete-orphan')
 def set_password(self,p): self.password_hash=generate_password_hash(p)
 def check_password(self,p): return check_password_hash(self.password_hash,p)
class Event(db.Model):
 id=db.Column(db.Integer,primary_key=True); title=db.Column(db.String(180),nullable=False); event_date=db.Column(db.Date,nullable=False); venue=db.Column(db.String(160),nullable=False); description=db.Column(db.Text,nullable=False,default=''); capacity=db.Column(db.Integer,nullable=False,default=30); is_active=db.Column(db.Boolean,nullable=False,default=True)
 requests=db.relationship('Request',back_populates='event')
class Status(db.Model):
 id=db.Column(db.Integer,primary_key=True); name=db.Column(db.String(40),unique=True,nullable=False)
class Request(db.Model):
 id=db.Column(db.Integer,primary_key=True); user_id=db.Column(db.Integer,db.ForeignKey('user.id',ondelete='CASCADE'),nullable=False); event_id=db.Column(db.Integer,db.ForeignKey('event.id'),nullable=False); status_id=db.Column(db.Integer,db.ForeignKey('status.id'),nullable=False); created_at=db.Column(db.DateTime,default=datetime.utcnow,nullable=False); payment_method=db.Column(db.String(30),nullable=False,default='Без оплаты')
 user=db.relationship('User',back_populates='requests'); event=db.relationship('Event',back_populates='requests'); status=db.relationship('Status'); review=db.relationship('Review',back_populates='request',uselist=False,cascade='all, delete-orphan')
class Review(db.Model):
 id=db.Column(db.Integer,primary_key=True); request_id=db.Column(db.Integer,db.ForeignKey('request.id',ondelete='CASCADE'),unique=True,nullable=False); text=db.Column(db.Text,nullable=False); rating=db.Column(db.Integer,nullable=False); created_at=db.Column(db.DateTime,default=datetime.utcnow,nullable=False); request=db.relationship('Request',back_populates='review')
 __table_args__=(db.CheckConstraint('rating BETWEEN 1 AND 5',name='ck_review_rating'),)
@login_manager.user_loader
def load_user(uid): return db.session.get(User,int(uid))
