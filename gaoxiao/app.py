#! /usr/bin/env python
#coding=utf-8
import os,re
import datetime
import pynotify

from werkzeug import Headers,wrap_file
from flask import Flask, render_template,request,Response,redirect,g,send_from_directory,send_file,current_app,url_for
from mongokit import Document,Connection
from bson.objectid import ObjectId
from link import *

ONLINE = 'C:\\Workstation\\lib\\src\\online'
BATCH = 'C:\\Workstation\\lib\\src\\batch\\hozn'
COPY = 'C:\\Workstation\\lib\\cpy'
RESERVE_WORD = set(['EXEC','DCL','CHAR','PIC','TIMESTAMP','FIXED'])

# configuration
MONGODB_HOST = 'localhost'
MONGODB_PORT = 27017

# create the little application object
app = Flask(__name__)
app.config.from_object(__name__)

# connect to the database
conn = Connection(app.config['MONGODB_HOST'],
                        app.config['MONGODB_PORT'])

class Post(Document):
    structure = {
            'title': unicode,
            'body': unicode,
            'date_creation': datetime.datetime,
			'counter': int,
            'comments': [{
                'name': unicode,
                'comment': unicode
                #'date_creation': datetime.datetime
            }]
    }

    gridfs = {
            'files': ['source'],
			'containers': ['images']
    }

    use_dot_notation = True
    required_field=['title','body','date_creation']
    default_values={'counter':0,'date_creation':datetime.datetime.utcnow}

conn.register([Post])

class Column(object):
    def __init__(self, path, pgm, table):
        if path.upper() == 'ONL':
            self.path = ONLINE
        else:
            self.path = BATCH
        self.cppath = COPY
        self.pgm = pgm.upper()
        self.table = table.upper()
        self.pattern = r"\b%s\w*?\.\w*\b"%table.upper()

    def execute(self):
        f = open(os.path.join(self.path, self.pgm)).read()
        #match = re.findall(r'\bMFS_STRUCT\.\w*\b', f, re.S)
        match = re.findall(self.pattern, f, re.S)
        return set(match)

    def copybook_compare(self):
        db2 = 'DL' + self.table + 'DCM'
        db2book = list()
        f = open(os.path.join(self.cppath, db2)).readlines()
        for l in f:
            if not l.lstrip().startswith('/*'):
                match = re.search(r'\b[a-zA-Z]\w*\b', l)
                if match:
                    m = match.group(0).strip()
                    if m not in RESERVE_WORD and m not in db2book:
                        db2book.append(m)

        dcmbook = list()
        dcm = self.table + 'DV1'
        f = open(os.path.join(self.cppath, dcm)).readlines()
        for l in f:
            if not l.lstrip().startswith('/*'):
                match = re.search(r'\b[a-zA-Z]\w*\b[^,]', l[:30])
                if match:
                    m = match.group(0).strip()
                    if m not in RESERVE_WORD and m not in dcmbook:
                        dcmbook.append(m)

        book = []
        for m in dcmbook:
            if m in db2book:
                book.append('MIF_REC.' + m + '=' + 'DLMIFDCM.' + m + '<br>')
            else:
                book.append('MIF_REC.' + m + '=' + '<br>')
        return book

@app.route("/", methods=["GET"])
def index():
    return render_template('index.html')

@app.route("/tools_a/", methods=["POST","GET"])
def a():
    if request.method == "POST":
        try:
            clm = Column(request.form['type'],request.form['program'],request.form['table'])
            data = list(clm.execute())
            data.sort()
            book = clm.copybook_compare()
            return render_template('a.html', data=data, counter=len(data), book=book)
        except:
            redirect("/")
    return render_template('a.html')

@app.route("/tools_b/", methods=["POST","GET"])
def b():
    if request.method == "POST":
        pgms,err,warn = execu([request.form['program'].upper()])
        return render_template('b.html', pgms=pgms, err=err, warn=warn)
    return render_template('b.html')

@app.route("/delete_post/<file_id>/", methods=["POST","GET"])
def delete_post(file_id):
    post = conn.test.shq.Post.one({'_id':ObjectId(file_id)})
    post.delete()
    #conn.test.shq.Post.delete(ObjectId(file_id))
    #post.fs.images.delete(ObjectId(image_id))
    return redirect('/tools_c')

@app.route("/delete_image/<file_id>/<image_id>", methods=["POST","GET"])
def delete_image(file_id, image_id=None):
    post = conn.test.shq.Post.one({'_id':ObjectId(file_id)})
    post.fs.images.delete(ObjectId(image_id))
    return redirect(url_for('show_post',file_id=file_id))

@app.route("/update_image/<file_id>/<image_id>", methods=["POST","GET"])
def update_image(file_id, image_id=None):
    import pdb
    pdb.set_trace()
    #post = conn.test.shq.Post.one({'_id':ObjectId(file_id)})
    conn.test.fs.files.update({'_id':ObjectId(image_id)}, { "$set": {'description':'doit'} }, False)
    return redirect(url_for('show_post',file_id=file_id))

@app.route("/show_post/<file_id>/", methods=["POST","GET"])
def show_post(file_id):
    if request.method == "POST":
        img = request.files['file']
        post = conn.test.shq.Post.one({'_id':ObjectId(file_id)})
        imgname = 'image' + str(post.counter)
        post.fs.images[imgname] = img
        post.counter = post.counter + 1
        post.save()
        return redirect(url_for('show_post',file_id=file_id))

    else:
        post = conn.test.shq.Post.one({'_id':ObjectId(file_id)})
        image = conn.test.fs.files.find({'docid':ObjectId(file_id)})
        img = [ im for im in image]
        return render_template('d.html', post=post, img=img)


@app.route("/show_image/<file_id>/<image_name>")
def show_image(file_id, image_name):
	mimetype = 'image/jpeg'
	post = conn.test.shq.Post.one({'_id':ObjectId(file_id)})
	img = post.fs.images.get_last_version(image_name)
	return send_file(img, mimetype=mimetype, add_etags=False)

def stream_template(template_name, **context):
    app.update_template_context(context)
    t = app.jinja_env.get_template(template_name)
    rv = t.stream(context)
    rv.enable_buffering(5)
    return rv

@app.route("/tools_c/", methods=["POST","GET"])
def upload_file():
    if request.method == "POST":
        img = request.files['file']
        title = request.form['title']
        body = request.form['body']

        post = conn.test.shq.Post()
        post.title = title
        post.body = body
        post.save()

        imgname = 'image' + str(post.counter)
        post.fs.images.put(img,description='xxxxx',filename='tttt')
        #post.fs.images[
        post.counter = post.counter + 1
        post.save()
        #imgname = 'image' + str(post.counter)
		#post.fs.images[imgname] = img
		#post.counter = post.counter + 1

        #headers = Headers()
        #mimetype = 'image/jpeg'
        #img = open('1280.jpg', 'rb')
        #data = wrap_file(request.environ, img)
        #rv = current_app.response_class(data, mimetype=mimetype, headers=headers,
        #                            direct_passthrough=True)
        #f = post.fs.images.get_last_version('1')

        #return send_file(post.body,mimetype=mimetype, add_etags=False)

        return render_template('c.html')
    else:
        post = list()
        for pt in conn.test.shq.Post.find():
			post.append(pt)
        return render_template('c.html', post=post)
    #return send_file(tmp, mimetype='image/jpeg', add_etags=False)

if __name__ == "__main__":
    app.run('127.0.0.1', debug=True)
    #clm = Column('onl','rks1049','mif')
    #clm.copybook_compare()
