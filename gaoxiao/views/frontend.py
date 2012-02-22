#! /usr/bin/env python
#coding=utf-8
"""
    frontend.py

    :license: BSD, see LICENSE for more details.
"""
import datetime
from flask import Module,render_template,request,redirect,url_for,send_file,flash,session
from bson.objectid import ObjectId

from gaoxiao.models import Post, conn
from gaoxiao.helper import check_auth

frontend = Module(__name__)

@frontend.route("/",methods=["POST","GET"])
def index():
    post = list()
    for p in conn.Post.find():
        post.append(p)
    return render_template("frontend.html", post=post)

@frontend.route("/about",)
def about():
    return render_template("about.html")

@frontend.route("/login",methods=["POST","GET"])
def login():
    if request.method == "POST":
        if check_auth(request.form['name'], request.form['password']):
            session['name'] = request.form['name']
            return redirect(url_for("admin.index"))
        else:
            flash(("login error"), "ERROR")
            return redirect(url_for("frontend.login"))
    else:
        return render_template('login.html')

@frontend.route("/logout",methods=["POST","GET"])
def logout():
    session.pop('name', None)
    return redirect(url_for("frontend.index"))

@frontend.route("/show_post/<file_id>/", methods=["POST","GET"])
def show_post(file_id):
    post = conn.Post.one({'_id':ObjectId(file_id)})
    image = conn.test.fs.files.find({'docid':ObjectId(file_id)})
    img = [ im for im in image ]
    return render_template('post.html', post=post, img=img)

@frontend.route("/show_image/<file_id>/<image_id>")
def show_image(file_id, image_id):
    mimetype = 'image/jpeg'
    post = conn.Post()
    img = post.fs.get(ObjectId(image_id))
    return send_file(img, mimetype=mimetype, add_etags=False)

@frontend.route("/add_comment/<file_id>/", methods=["POST","GET"])
def add_comment(file_id):
    name = request.form['name']
    comment = request.form['comment']
    if not comment:
        flash(('comments can not empty'),'Warning')
        return redirect(url_for('show_post',file_id=file_id))
    comment_datetime = datetime.datetime.utcnow()
    
    conn.test.gaoxiao.update({'_id':ObjectId(file_id)}, {"$push": {'comments':{'name':name,'comment':comment,'comment_datetime':comment_datetime}}}, False)
    return redirect(url_for('show_post',file_id=file_id))


