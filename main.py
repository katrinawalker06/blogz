from flask import Flask,request, redirect, render_template,session,flash
from flask_sqlalchemy import SQLAlchemy
import cgi
import os
import jinja2
import sys
from pprint import pprint

template_dir = os.path.join(os.path.dirname(__file__), 'template')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape=True)

app= Flask(__name__)
app.config['DEBUG']= True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:blog@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db=SQLAlchemy(app)
app.secret_key='sunnyday'

class Blog (db.Model):
    id=db.Column(db.Integer,primary_key=True)
    title= db.Column(db.String(1000))
    body = db.Column(db.String(1500))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self,title,body,owner):
        self.title=title
        self.body=body
        self.owner = owner

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120),unique=True)
    password = db.Column(db.String(120))
    blogs=db.relationship('Blog', backref="owner")
    
    def __init__(self, username, password):
        self.username = username
        self.password = password

@app.before_request
def require_login():
    allowed_routes = ['login', 'blog', 'blogpost', 'posts','index', 'signup', 'users', 'singleUser']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect("/login")
  
@app.route ('/', methods=["GET"])
def index():
    if request.method=="GET":
        users= User.query.all()
        return render_template("/main.html",users=users) 


@app.route('/login',methods= ['POST',"GET"])
def login():
    if request.method == "POST":
        username=request.form["username"]
        password=request.form["password"]
        user = User.query.filter_by(username=username).first()
        
        if user and user.password == password:
            session['username'] = username
            return redirect('/newpost')
        if not user:
            flash("Username does not exist")
            return render_template('/login.html', username=username)
        if password=="":  
            flash("Enter Password")
            return render_template('/login.html',password=password)
        
    if request.method=="GET":
         return render_template('/login.html')

@app.route('/singleUser', methods=['GET'])
def singleUser():
        user_id = request.args.get('id')
        user = User.query.filter_by(id=user_id).first()
        blogs= Blog.query.filter_by(owner_id=user_id).all()
        return render_template('/singleUser.html', blogs=blogs, user=user)
    



@app.route('/signup', methods= ['POST',"GET"])
def signup():
    
    if request.method=="POST":
        username=request.form['username']
        username_error=""
        password=request.form['password']
        password_error=""
        verify_password=request.form['verify_password']
        verify_password_error=""
        currentuser=User.query.filter_by(username=username).first()
              
        if username == "":
            username_error = "Please enter a username."
        if currentuser:
            username_error ="username already taken"
        if password == "":
            password_error = "Please enter a password."
        if len(username) <= 3 or len(username) >3:
            username_error = "Username and Password must have at least 3 characters."
        if password != verify_password:
            verify_password_error = "Passwords do not match"    
           
                                               
        if len(username) > 3 and len(password) > 3 and password == verify_password and not currentuser:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] =username
            return redirect('/newpost')
        else:
            return render_template('signup.html',username=username,username_error=username_error,password=password,verify_password_error=verify_password_error)
                                      
        
    if request.method=="GET":            
        return render_template("signup.html")    
  

@app.route('/logout')
def logout():
    del session['username']
    return redirect("/")


@app.route("/blog",methods=['POST', 'GET'])
def blog():
    blog_id= int(request.args.get("id"))
    user_id= request.args.get("id")
    if blog_id:
       blog = Blog.query.filter_by(id=blog_id).first()
       return render_template("blog.html",title=blog.title, body= blog.body,blog=blog,user=body.owner.username, user_id= blog.owner_id)
    if user_id:
        users = User.query.all()    
        return render_template("singleUser.html",users=users)
    return render_template("main.html")


@app.route('/newpost', methods=['POST', 'GET'])
def home():
    if request.method== "GET":
        return render_template("newpost.html")
    if request.method == "POST":
        blogtitle_error=""
        newblog_error=""
        blogtitle=request.form['blogtitle']
        newblog=request.form['newblog']

        if blogtitle == "":
            blogtitle_error = "error title"
        if newblog == "":
            newblog_error = "enter blog"
        if blogtitle_error != "" or newblog_error != "" :
            return render_template("newpost.html",blogtitle_error=blogtitle_error,newblog_error=newblog_error,blogtitle=blogtitle,newblog=newblog)
        
        if not blogtitle_error and not newblog_error:
            new_blog = Blog(blogtitle,newblog,owner)
            db.session.add(new_blog)
            db.session.commit()
            return redirect("/blog?id={0}".format(new_blog.id))
        
           

@app.route("/posts", methods=["GET"])
def posts():
    blogs = Blog.query.all()
    return render_template("/posts.html", blogs=blogs)

#@app.route("/singleUser", methods=["GET"])
#def singleUser():
#        user_id = request.args.get('id')
#        user = User.query.filter_by(id=user_id).first()
#        blogs= Blog.query.filter_by(owner_id=user_id).all()
#        return render_template('blog.html')
    




if __name__=='__main__':
    app.run()