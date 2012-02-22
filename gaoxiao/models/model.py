#! /usr/bin/env python
#coding=utf-8
import datetime
from mongokit import Document,Connection
from bson.objectid import ObjectId

#connection = Connection(app.config['MONGODB_HOST'],app.config['MONGODB_PORT'])
conn= Connection('localhost',27017)

class Post(Document):
    __database__ = 'test'
    __collection__ = 'gaoxiao'

    structure = {
            'title': unicode,
            'text': unicode,
            'date_creation': datetime.datetime,
			'counter': int,
            'owner': unicode,
            'front_page': ObjectId,
            'tags': list,
            'comments': [{
                'name': unicode,
                'comment': unicode,
                'comment_datetime': datetime.datetime,
            }]
    }

    gridfs = {
			'containers': ['images']
    }

    use_dot_notation = True
    required_field=['title','text','date_creation']
    default_values={'counter':0,'date_creation':datetime.datetime.utcnow}

conn.register([Post])
