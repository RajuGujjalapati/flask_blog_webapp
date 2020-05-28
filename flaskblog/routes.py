import os, secrets
from flask import  render_template, url_for, flash, redirect, request, abort
from flaskblog.forms import RegistrationForm, LoginForm, UpdateAccountForm, PostForm, RequestResetForm,ResetPasswordForm
from flaskblog.models import User, Posti
from PIL import Image
from flaskblog import app, db, bcrypt, mail
from flask_login import  login_user, current_user, logout_user, login_required
from flask_mail import Message


@app.route("/")
@app.route("/home")
def home():
    page = request.args.get('page',1,type=int)#optional argument
    posts = Posti.query.order_by(Posti.date_posted.desc()).paginate( page=page, per_page=2)
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
        abort(403)#inbulit func. from flask
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted!', 'success')
    return redirect(url_for('home'))

@app.route("/user/<string:username>")
def user_post(username):
    page = request.args.get('page',1,type=int)
    user = User.query.filter_by(username=username).first_or_404()
    posts = Posti.query.filter_by(author = user)\
        .order_by(Posti.date_posted.desc())\
            .paginate( page=page, per_page=2)
    return render_template('user_posts.html', user = user, posts=posts)


def send_reset_email(user):
    #we need to use flaskextension flask-mail to send the emails
    token = user.get_reset_token()
    msg = Message('Password Reset Request',
                  sender='noreply@demo.com',
                  recipients=[user.email])
                  #_external= true to create absolute url 
    msg.body = f'''To reset your password, visit the following link:
{url_for('reset_token', token=token, _external=True)}
If you did not make this request then simply ignore this email and no changes will be made.
'''
    mail.send(msg)


@app.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password.', 'info')
        return redirect(url_for('login'))
    return render_template('reset_request.html', title='Reset Password', form=form)



@app.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    #if the user is logged in send him to home page
    if current_user.is_authenticated:
        return redirect(url_for('home'))
        #else --verify the token,the below verify_reset_token() is written in models.py
        #which takes 'token' as  a argument.
    user = User.verify_reset_token(token)
    if user is None:
        #if user doesnt find token redirect hime to reset_request
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        ''' checking for valid_submition'''
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        '''encoding and hashing the password'''
        user.password = hashed_password#storing it into new password
        db.session.commit()#adding to database
        flash('Your password has been updated! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('reset_token.html', title='Reset Password', form=form)