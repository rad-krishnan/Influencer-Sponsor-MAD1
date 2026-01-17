from datetime import datetime
from app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password = db.Column(db.String(60), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'influencer', 'admin', 'sponsor'
    flagged = db.Column(db.Boolean, default=False)

    # Relationship to InfluencerProfile
    influencer_profile = db.relationship('InfluencerProfile', backref='user', uselist=False)

    def set_password(self, password):
        self.password = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password, password)


class Campaign(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    start_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    end_date = db.Column(db.DateTime, nullable=False)
    budget = db.Column(db.Float, nullable=False)
    visibility = db.Column(db.String(10), nullable=False)  # 'public', 'private'
    goals = db.Column(db.Text, nullable=False)
    sponsor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    sponsor = db.relationship('User', backref='campaigns')
    flagged = db.Column(db.Boolean, default=False)

class AdRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaign.id'), nullable=False)
    influencer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    messages = db.Column(db.Text, nullable=False)
    requirements = db.Column(db.String(50), nullable=False)
    payment_amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(15), nullable=False, default='Pending')  # Set default to 'Pending'  

    # Relationships
    campaign = db.relationship('Campaign', backref='ad_requests')
    influencer = db.relationship('User', backref='ad_requests')                  # Reverse relationship

class InfluencerProfile(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True, nullable=False)
    category = db.Column(db.String(100), nullable=True)
    niche = db.Column(db.String(100), nullable=True)
    reach = db.Column(db.String(25), nullable=True)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
