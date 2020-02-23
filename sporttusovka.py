from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
from base64 import b64encode, b64decode
import requests
import json
import secrets
import os, stat
from re import sub
import ssl
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__,
            static_url_path='', 
            static_folder='static',
            template_folder='templates')

app.config['SECRET_KEY'] = os.environ['FLASK_KEY']
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
socketio = SocketIO(app)

db = SQLAlchemy(app)

### Models

pax = db.Table('pax',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
    db.Column('event_id', db.Integer, db.ForeignKey('event.id'))
    )

class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    age = db.Column(db.Integer)
    telegram = db.Column(db.String(64))
    email = db.Column(db.String(64), unique=True, nullable=False)
    photo = db.Column(db.String(64))
    description = db.Column(db.Text, nullable=False)
    events = db.relationship('Event', secondary=pax, backref=db.backref('event', lazy='dynamic'))

    def __init__(self, name, age, telegram, email, photo, description):
        self.name = name
        self.age = age
        self.telegram = telegram 
        self.email = email
        self.photo = photo
        self.description = description

    def __repr__(self):
        return '<User %r>' % self.email
    
    def serialize(self):
        return {
            'id': self.id, 
            'name' : self.name,
            'age' : self.age,
            'telegram' : self.telegram, 
            'email' : self.email,
            'photo' : self.photo,
            'description' : self.description
        }

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    datetime = db.Column(db.Integer)
    startlat = db.Column(db.Float)
    startlon = db.Column(db.Float)
    finishlat = db.Column(db.Float)
    finishlon = db.Column(db.Float)
    level = db.Column(db.Integer)
    length = db.Column(db.Integer)
    creatorid = db.Column(db.Integer)

    def __init__(self, datetime , startlat, length, startlon, finishlon, finishlat, level, creatorid):
        self.datetime = datetime
        self.startlat = startlat
        self.startlon = startlon
        self.finishlat = finishlat
        self.finishlon = finishlon
        self.level = level
        self.length = length
        self.creatorid = creatorid 

    def __repr__(self):
        return '<id {}>'.format(self.id)
    
    def serialize(self):
        return {
            'id': self.id,
            'datetime' : self.datetime,
            'startlat' : self.startlat,
            'startlon' : self.startlon,
            'finishlat' : self.finishlat,
            'finishlon' : self.finishlon,
            'level' : self.level,
            'creatorid' : self.creatorid
        }

### Models

@app.route('/')
def splash():
    return render_template('splash.html')

@app.route('/app')
def map():
    return render_template('map.html')

@app.route('/account')
def account():
    return render_template('account.html')

@socketio.on('login')
def register(data_from_google):
    if Users.query.filter_by(email=data_from_google['email']).first():
        emit('login_response', 'logged in')
    else:
        new_user = Users(name=data_from_google['name'],
            age=20,
            telegram='none',
            email=data_from_google['email'],
            photo=data_from_google['image'],
            description='helloworld'
            )
        db.session.add(new_user)
        db.session.commit()
        emit('login_response', 'signed up')

@socketio.on('create_event')
def create_event(event_details):
    date = int(event_details['datetime'].replace('-', ''))
    new_event = Event(
        datetime=date,
        startlat=float(event_details['startlat']),
        startlon=float(event_details['startlon']),
        finishlon=None,
        finishlat=None,
        length=int(event_details['length']),
        level=int(event_details['level']),
        creatorid=int(event_details['creatorid'])
        )
    db.session.add(new_event)
    db.session.commit()
    emit('event_response', 'created_event')

@socketio.on('fetch_events')
def fetch_events(filters):
    datetime = int(filters['datetime'].replace('-', ''))
    events_at_date = Event.query.filter(Event.datetime==datetime,
        Event.length<=int(filters['length']),
        Event.level<=int(filters['level'])
        ).all()
    events_at_date_list = []
    for each in events_at_date:
        events_at_date_list.append(each.serialize())
    print("[INFO] ", json.dumps(events_at_date_list))
    response = "{"+json.dumps(events_at_date_list)+"}"
    emit('fetch_events', response )

@app.route('/easter_egg')
def easter_egg():
    return "ну вітаю, маладєц, шо скажеш, круто! умєєш, магьош"

if __name__ == '__main__':
    socketio.run(app)