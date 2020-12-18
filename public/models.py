from datetime import datetime

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
db = SQLAlchemy(app)


class Investor(db.Model):
    """
         Column      |           Type           | Collation | Nullable |               Default
    -----------------+--------------------------+-----------+----------+--------------------------------------
     id              | integer                  |           | not null | nextval('investor_id_seq'::regclass)
     created_at      | timestamp with time zone |           | not null | now()
     updated_at      | timestamp with time zone |           | not null | now()
     name            | text                     |           |          |
     photo_large     | text                     |           |          |
     photo_thumbnail | text                     |           |          |
    """
    __tablename__ = 'investor'

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    name = db.Column(db.String())
    photo_large = db.Column(db.String())
    photo_thumbnail = db.Column(db.String())

    companies = db.relationship("Company", secondary="investment", lazy="joined")

    def __init__(self, name, photo_large=None, photo_thumbnail=None):
        self.name = name
        self.photo_large = photo_large
        self.photo_thumbnail = photo_thumbnail
        self.updated_at = datetime.utcnow()

    def __repr__(self):
        return '<id {}>'.format(self.id)

    def __hash__(self):
        return hash((self.id, ))

    def jsonify(self):
        return {'id': self.id, 'name': self.name}


class Company(db.Model):
    """
       Column   |           Type           | Collation | Nullable |               Default
    ------------+--------------------------+-----------+----------+-------------------------------------
     id         | integer                  |           | not null | nextval('company_id_seq'::regclass)
     name       | text                     |           |          |
     created_at | timestamp with time zone |           |          | now()
     updated_at | timestamp with time zone |           |          | now()
    """
    __tablename__ = 'company'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String())
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    investors = db.relationship("Investor", secondary="investment", lazy="joined")

    def __init__(self, name):
        self.name = name
        self.updated_at = datetime.utcnow()

    def __repr__(self):
        return '<id {}>'.format(self.id)

    def __hash__(self):
        return hash((self.id, ))


class Investment(db.Model):
    """
           Column    |           Type           | Collation | Nullable |                Default
    -------------+--------------------------+-----------+----------+----------------------------------------
     id          | integer                  |           | not null | nextval('investment_id_seq'::regclass)
     created_at  | timestamp with time zone |           | not null | now()
     updated_at  | timestamp with time zone |           | not null | now()
     amount      | numeric                  |           |          |
     investor_id | integer                  |           | not null |
     company_id  | integer                  |           | not null |
    """

    __tablename__ = 'investment'

    id = db.Column(db.Integer, primary_key=True)
    investor_id = db.Column(db.Integer, db.ForeignKey('investor.id'))
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'))

    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    amount = db.Column(db.Float)

    investor = db.relationship("Investor", backref=db.backref("investments"), lazy="joined")
    company = db.relationship("Company", backref=db.backref("investments"), lazy="joined")

    def __init__(self, investor: Investor, company: Company, amount=None):
        self.amount = amount
        self.investor_id = investor.id
        self.company_id = company.id
        self.updated_at = datetime.utcnow()
