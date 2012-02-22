#! /usr/bin/env python
#coding=utf-8
"""
    admin.py

    :license: BSD, see LICENSE for more details.
"""
from flask import Module,render_template,request,send_file,redirect,url_for,flash
from bson.objectid import ObjectId

from gaoxiao.form import PostForm
from gaoxiao.models import Post, conn
from gaoxiao.helper import requires_auth

admin = Module(__name__)

@admin.route("/",methods=["POST","GET"])
def index():
    post = list()
    for p in conn.Post.find():
        post.append(p)
    return render_template("admin.html", post=post)


@admin.route("/upload",methods=["POST","GET"])
@requires_auth
def upload():
    #form = PostForm()
    #if form.validate_on_submit():
    if request.method == "POST":
        image = request.files['file']
        title = request.form['title']
        text = request.form['text']
        tags = request.form['tags'].split(',')
        if not (image or text):
            flash(('test/image can not empty!'),'Fail')
            return redirect(url_for('admin.upload'))

        post = conn.Post()
        post.title = title
        post.text = text
        post.tags = tags
        post.save()

        if image:
            imgname = 'image' + str(post.counter)
            id = post.fs.images.put(image,filename=imgname)
            post.counter = post.counter + 1
            if not post.front_page:
                post.front_page = id
        post.save()
        return render_template('upload.html')

    return render_template("upload.html")


@admin.route("/show_post/<file_id>/", methods=["GET","POST"])
@admin.route("/show_post/<file_id>/<image_id>", methods=["GET","POST"])
@requires_auth
def show_post(file_id, image_id=None, action=None):
    if request.method == "POST":
        img = request.files['file']
        description = request.form['description']
        post = conn.Post.one({'_id':ObjectId(file_id)})

        if img:
            imgname = 'image' + str(post.counter)
            id = post.fs.images.put(img,description=description,filename=imgname)
            post.counter = post.counter + 1
            if not post.front_page:
                post.front_page = id
            post.save()
        return redirect(url_for('show_post',file_id=file_id))
    else:
        post = conn.Post.one({'_id':ObjectId(file_id)})
        image = conn.test.fs.files.find({'docid':ObjectId(file_id)})
        img = [ im for im in image ]
        return render_template('admin_post.html', post=post, img=img, image_id=image_id)

@admin.route("/update_post/<file_id>", methods=["GET","POST"])
@requires_auth
def update_post(file_id):
    if request.method == "POST":
        title = request.form['title']
        text = request.form['text']
        conn.test.gaoxiao.update({'_id':ObjectId(file_id)}, {"$set": {'title':title, 'text':text}}, False)
        return redirect(url_for('show_post', file_id=file_id))
    else:
        post = conn.Post.one({'_id':ObjectId(file_id)})
        image = conn.test.fs.files.find({'docid':ObjectId(file_id)})
        img = [ im for im in image ]
        return render_template('admin_post.html', post=post, img=img, action='update')

@admin.route("/delete_post/<file_id>", methods=["GET","POST"])
@requires_auth
def delete_post(file_id):
    if request.method == "POST":
        title = request.form['title']
        text = request.form['text']
        conn.test.gaoxiao.update({'_id':ObjectId(file_id)}, {"$set": {'title':title, 'text':text}}, False)
        return redirect(url_for('show_post', file_id=file_id))
    else:
        conn.test.gaoxiao.remove({'_id':ObjectId(file_id)})
        return redirect(url_for('admin.index'))

@admin.route("/show_image/<file_id>/<image_id>")
@requires_auth
def show_image(file_id, image_id):
    mimetype = 'image/jpeg'
    post = conn.Post()
    img = post.fs.get(ObjectId(image_id))
    #img = post.fs.images.get_last_version(image_name)
    return send_file(img, mimetype=mimetype, add_etags=False)


@admin.route("/delete_image/<file_id>/<image_id>", methods=["GET"])
@requires_auth
def delete_image(file_id, image_id=None):
    post = conn.Post.one({'_id':ObjectId(file_id)})
    #post = conn.Post()
    post.front_page = None 
    post.fs.images.delete(ObjectId(image_id))
    post.save()
    return redirect(url_for('show_post',file_id=file_id))


@admin.route("/update_image/<file_id>/<image_id>", methods=["POST","GET"])
@requires_auth
def update_image(file_id, image_id=None):
    if request.method == "POST":
        #post = conn.test.shq.Post.one({'_id':ObjectId(file_id)})
        conn.test.fs.files.update({'_id':ObjectId(image_id)}, { "$set": {'description':request.form['description']}}, False)
        return redirect(url_for('show_post',file_id=file_id))
    else:
        return redirect(url_for('show_post', file_id=file_id, image_id=image_id))

