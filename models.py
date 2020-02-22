from app import db

participants = db.Table('participants',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('event_id', db.Integer, db.ForeignKey('event.id')),
    )

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    age = db.Column(db.Integer)
    telegram = db.Column(db.String(64))
    email = db.Column(db.String(64), unique=True, nullable=False)
    photo = db.Column(db.String(64))
    description = db.Column(db.Text, nullable=False)
    events = db.relationship('Event', secondary=participants, backref=db.backref('participants'), lazy='dynamic')

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
    __tablename__ = 'events'

    id = db.Column(db.Integer, primary_key=True)
    datetime = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    startLat = db.Column(db.FLoat)
    startLon = db.Column(db.Float)
    finishLat = db.Column(db.Float)
    finishLon = db.Column(db.Float)
    level = db.Column(db.Integer)
    creatorID = db.Column(db.Integer)

    def __init__(self, datetime , startLat, startLon, finishLon, finishLat, level, creatorID):
        self.datetime = datetime
        self.startLat = startLat
        self.startLon = startLon
        self.finishLat = finishLat
        self.finishLon = finishLon
        self.level = level
        self.creatorID = creatorID

    def __repr__(self):
        return '<id {}>'.format(self.id)
    
    def serialize(self):
        return {
            'id': self.id,
            'datetime' : datetime,
            'startLat' : startLat,
            'startLon' : startLon,
            'finishLat' : finishLat,
            'finishLon' : finishLon,
            'level' : level,
            'creatorID' : creatorID
        }