import os, secrets
from flask import  render_template, url_for, flash, redirect, request, abort
from flaskblog.forms import RegistrationForm, LoginForm, UpdateAccountForm, PostForm
from flaskblog.models import User, Posti
from PIL import Image
from flaskblog import app, db, bcrypt
from flask_login import  login_user, current_user, logout_user, login_required
# posts = [
#     {
#         'author': 'Raju Chowdary',
#         'title': 'Blog Post 1',
#         'content': 'First post content',
#         'date_posted': 'May 25, 2020'
#     },
#     {
#         'author': 'fripya',
#         'title': 'Blog Post 2',
#         'content': 'Second post content',
#         'date_posted': 'May 26, 2020'
#     }
# ]

@app.route("/")
@app.route("/home")
def home():
    posts =Posti.query.all()
    return render_template('home.html', posts=posts)


@app.route("/about")
def about():
    return render_template('about.html', title='About')


@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username = form.username.data, email = form.email.data, password =hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your Account  has been created! Now your able to login', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email = form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember= form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route("/logout/")
def logout():
    logout_user()
    return redirect(url_for('home'))


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ex =os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ex
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)
    '''rescaling to 125,125 size , so we wont loose any data'''
    output_size =(125,125)
    i =Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    return picture_fn

@app.route('/account', methods=['GET','POST'])
@login_required
def account():
    form =UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            '''saving the profile pic using the funacyion name, ikada save_picture
            oka argument istundi kada akkda aa argument ee data ni teskoni filename ichi
            then split chestundi a/c to user data--> renames_hex--> then save to profile_pics folder in
            hashable format'''
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        '''ikkada manam databse tho matching chustunam manam em enter chesamo,
        whether it is colliding with the database data or not ani'''
        current_user.email = form.email.data
        db.session.commit()
        flash('Your Account has been Updated!','success' )
        return redirect(url_for('account'))
        '''The above one is post request, the below one is get request'''
    elif request.method == 'GET': 
        #incase POST vadithe its like render kabbati , user data kanipidu
        form.username.data = current_user.username
        '''form data fileds lo curent_user fields veyi ani meaning'''
        form.email.data = current_user.email

    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account', image_file=image_file, form=form)

@app.route("/post/new", methods=['GET','POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post =Posti(title= form.title.data, content =form.content.data, author = current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your post has been created Success!', 'success')
        return redirect(url_for('home'))
    return render_template('create_post.html', title ='New Post', form = form, legend='New Post')

#post overview
@app.route("/post/<int:post_id>")
def post(post_id):
    post = Posti.query.get_or_404(post_id)
    return render_template('post.html', title=post.title, post=post)

#update post
@app.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    post = Posti.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash('Your post has been updated!', 'success')
        return redirect(url_for('post', post_id=post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
    return render_template('create_post.html', title='Update Post', form=form, legend='Update Post')

#delete post
@app.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
    post = Posti.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted!', 'success')
    return redirect(url_for('home'))