from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login_manager
from flask_login import UserMixin

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(255), nullable=False)
    address = db.Column(db.String(255), nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)  
    category = db.Column(db.String(10), nullable=False)
    role = db.Column(db.String(10), nullable=False, default='supplier')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Method to hash the password
    def set_password(self, password):
        self.password = generate_password_hash(password)

    # Method to check the password
    def check_password(self, password):
        return check_password_hash(self.password, password)
    
class Tender(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    required_experience = db.Column(db.Integer, nullable=False)  
    tender_number = db.Column(db.String(50), unique=True, nullable=False)
    price = db.Column(db.Float, nullable=False)
    delivery_time = db.Column(db.String(50), nullable=False)
    additional_criteria = db.Column(db.String(50), nullable=False) 
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(10), nullable=False, default='open')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Bid(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tender_id = db.Column(db.Integer, db.ForeignKey('tender.id'), nullable=False)
    supplier_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    document_path = db.Column(db.String(255), nullable=False)
    ranking_score = db.Column(db.Float, nullable=True)
    status = db.Column(db.String(10), nullable=False, default='pending')
    decision = db.Column(db.String(10), nullable=False, default='N/A')
    company_name = db.Column(db.String(255), nullable=False, default='N/A')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    submitted_on = db.Column(db.DateTime, default=datetime.utcnow)  

    # Define a relationship to Tender
    tender = db.relationship('Tender', backref='bids')
    supplier = db.relationship('User', backref='bids')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
