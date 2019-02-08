from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
from forms import CategoryForm, ItemForm
from decorators import login_manager
from functools import wraps
from flask_sqlalchemy import SQLAlchemy
import os
import requests
from flask import (
    Flask,
    render_template,
    url_for,
    request,
    redirect,
    flash,
    jsonify
)
from datetime import datetime
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////var/tmp/test.db'
db = SQLAlchemy(app)

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Dealtime"


# this is class used to save the user data
class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    email = db.Column(db.String(250), nullable=False)
    picture = db.Column(db.String(250))


# this class stores the item categories data
class Category(db.Model):
    __tablename__ = 'category'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    user_id = db.Column(db.String(500), db.ForeignKey('user.id'))
    user = db.relationship(User, backref="category")

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'name': self.name,
            'id': self.id
        }


# this class stores the item data
class Item(db.Model):
    __tablename__ = 'items'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(1050), nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    description = db.Column(db.String(600))
    image = db.Column(db.String(250))
    brand = db.Column(db.String(250))
    price = db.Column(db.String(50))
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    category = db.relationship(
               Category, backref=db.backref('items', cascade='all, delete'))
    user_id = db.Column(db.String(500), db.ForeignKey('user.id'))
    user = db.relationship(User, backref="items")

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'name': self.name,
            'id': self.id,
            'description': self.description,
            'image': self.image,
            'category': self.category.name,
            'date': self.date
        }


# we will call this function from db_create module for creating tables
def create_tables():
    db.create_all()
    print('created tables')


# this decorator injects the categories to all avialable templates


@app.context_processor
def inject_categories():
    categories = Category.query.all()
    return dict(categories=categories)

# it just shows the login page


@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in range(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)

# it helps the user to loggedin and display flash profile


@app.route('/gconnect', methods=['POST', 'GET'])
def gconnect():
    """it handles the gmail authentication
    and get the user basic info from google api
    """
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    code = request.data

    try:
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Checking if the access token is valid or not.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1].decode('utf-8'))
    # If there was an error in the access token info and it will abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this appor not.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print("Token's client ID does not match app's.")
        response.headers['Content-Type'] = 'application/json'
        return response
    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('User is already connected'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id
    # Get user info from google api
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)
    data = answer.json()
    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    image = data['picture']
    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info from google api
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    image = data['picture']
    flash("you are now logged in as %s" % login_session['username'], "success")
    print("done!")
    return render_template('user_profile.html')


@app.route('/gdisconnect')
def gdisconnect():
    """
    it handles the signout functionality for current user
    """
    access_token = login_session.get('access_token')
    if access_token is None:
        print('Access Token is None')
        response = make_response(json.dumps('User not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    print('In gdisconnect access token is %s', access_token)
    print('User name is: ')
    print(login_session['username'])
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s'\
        % login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print('result is ')
    print(result)
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        global logged_in
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        flash("loggedout successfully", "success")
        return redirect('/')
    else:
        response = make_response(json.dumps('Failed to revoke token for user'))
        response.headers['Content-Type'] = 'application/json'
        return response


@app.route('/showprofile')
def showprofile():
    """
    it display the user profile page
    """
    return render_template('user_profile.html', profile=True)


@app.route('/')
def home():
    """
    home page it will show recent items
    """
    items = Item.query.all()
    categories = Category.query.all()
    if 'picture' in login_session:
        user = {'picture': login_session['picture'],
                'name': login_session['username']}
        return render_template('index.html', items=items,
                               categories=categories, user=user)
    return render_template('index.html', items=items,
                           categories=categories, user=None)


@app.route('/category/<int:id>')
def showitems(id):
    """
    this will show items with respective categories

    """
    category = Category.query.get_or_404(id)
    items = Item.query.filter_by(category_id=category.id)
    categories = Category.query.all()
    return render_template('index.html', items=items, categories=categories)


@app.route('/category/<int:id>/edit', methods=["POST", "GET"])
@login_manager
def editcategory(id):
    """
    this allow users to edit categories
    """
    category = Category.query.get_or_404(id)
    form = CategoryForm(request.form)
    user_id = login_session['gplus_id']
    owner_id = category.user_id
    if request.method == 'POST' and form.validate():
        # editing done here
        category.name = request.form['name']
        if user_id == owner_id:
            db.session.commit()
            flash('Category successfully updated', 'success')
        return redirect('/')
    else:
        user_id = login_session['gplus_id']
        owner_id = category.user_id
        if user_id == owner_id:
            form.name.data = category.name
            return render_template('editcategory.html',
                                   form=form, category=category)
        else:
            flash('Sorry you are not a owner of this category', 'danger')
            return redirect('/')


@app.route('/category/<int:id>/delete', methods=["POST", "GET"])
@login_manager
def deletecategory(id):
    """
    this allow users to delete categories
    """
    category = Category.query.get_or_404(id)
    owner_id = category.user_id
    user_id = login_session['gplus_id']
    if user_id == owner_id:
        db.session.delete(category)
        db.session.commit()
        flash('Category successfully deleted', 'success')
    else:
        flash('Sorry you are not a owner of this category', 'danger')
    return redirect('/')


@app.route('/categories/add', methods=['GET', 'POST'])
@login_manager
def addcategory():
    """
    this allow users to add categories
    """
    form = CategoryForm(request.form)
    if request.method == 'POST' and form.validate():
        # saving done here
        category = Category(name=request.form['name'],
                            user_id=login_session['gplus_id'])

        db.session.add(category)
        db.session.commit()
        flash('Category successfully added', 'success')
        return redirect('/')
    else:
        return render_template('addcategory.html', form=form)


# item crud operations
@app.route('/item/add', methods=['GET', 'POST'])
@login_manager
def additem():
    """
    this allow users to add items
    """
    form = ItemForm(request.form)
    categories = Category.query.all()
    form.category.choices = [(c.id, c.name)for c in categories]
    if request.method == 'POST' and form.validate():
        print('\n\n\n\ninside post')
        name = form.name.data
        price = form.price.data
        brand = form.brand.data
        description = form.description.data
        category = form.category.data
        image = form.image.data
        print(name, price, description, image, brand, category)
        item = Item(name=name, price=price,
                    description=description, image=image,
                    brand=brand, category_id=category,
                    user_id=login_session['gplus_id'])
        db.session.add(item)
        db.session.commit()
        flash('item saved successfully', 'success')
        return redirect('/')
    elif form.errors:
        flash(form.errors, 'danger')
        return redirect('/')
    else:
        print('\n\n\n\ninside get')
        return render_template('additem.html', form=form)


@app.route('/item/<int:id>', methods=["POST", "GET"])
def itemdetails(id):
    """
    this allow users to view item details
    """
    item = Item.query.get_or_404(id)
    return render_template('itemdetails.html', item=item)


@app.route('/item/<int:id>/edit', methods=["POST", "GET"])
@login_manager
def edititem(id):
    """
    this allow authorised users to edit items
    """
    item = Item.query.get_or_404(id)
    form = ItemForm(request.form)
    owner_id = item.user_id
    user_id = login_session['gplus_id']
    if request.method == 'POST':
        # editing done here
        print('\n\n\n\ninside post')

        name = form.name.data
        price = form.price.data
        brand = form.brand.data
        description = form.description.data
        category = form.category.data
        print(category, type(category))
        image = form.image.data
        print(name, price, description, image, brand, category)
        try:
            item.name = name
            item.brand = brand
            item.price = price
            item.description = description
            item.category_id = category
            item.user_id = login_session['gplus_id']
            # user_id=login_session['user_id']
            print("category_id", item.category_id)
            db.session.commit()
        except Exception as e:
            print(e)
            # flash(e,'danger')
        else:

            flash('Item successfully updated', 'success')
        return redirect('/')
    else:
        if user_id == owner_id:
            form.name.data = item.name
            form.brand.data = item.brand
            form.price.data = item.price
            form.image.data = item.image
            form.description.data = item.description
            categories = Category.query.all()
            form.category.choices = [(c.id, c.name)for c in categories]
            form.category.data = int(item.category_id)
            return render_template('edititem.html', form=form, item=item)
        else:
            flash('You are not a owner of this item', 'danger')
            return redirect(url_for('itemdetails', id=item.id))


@app.route('/item/<int:id>/delete', methods=["POST", "GET"])
@login_manager
def deleteitem(id):
    """
    this allow users to delete items
    """
    item = Item.query.get_or_404(id)
    user_id = login_session['gplus_id']
    owner_id = item.user_id
    if user_id == owner_id:
        db.session.delete(item)
        db.session.commit()
        flash('Item successfully deleted', 'success')
        return redirect('/')
    else:
        flash("You are not a owner of this item you can't delete", 'danger')
        return redirect(url_for('itemdetails', id=item.id))


# rest-api connections it allows to other apps
# uses this application data to extension


@app.route('/categories/JSON')
def categoriesJSON():
    categories = Category.query.all()
    return jsonify(Categories=[c.serialize for c in categories])


@app.route('/category/<int:category_id>/items/JSON')
def categoryItemsJSON(category_id):
    categories = Category.query.get(category_id)
    items = Item.query.filter_by(category_id=category_id).all()
    return jsonify(Item=[i.serialize for i in items])


@app.route('/items/JSON')
def itemsJSON():
    items = Item.query.all()
    return jsonify(Item=[i.serialize for i in items])


@app.route('/item/<int:id>/JSON')
def itemJSON(id):
    item = Item.query.get(id)
    return jsonify(Item=item.serialize)

# for css styles update without restarting server


@app.context_processor
def override_url_for():
    return dict(url_for=dated_url_for)


def dated_url_for(endpoint, **values):
    if endpoint == 'static':
        filename = values.get('filename', None)
        if filename:
            file_path = os.path.join(app.root_path,
                                     endpoint, filename)
            values['q'] = int(os.stat(file_path).st_mtime)
    return url_for(endpoint, **values)


# this block should be last
if __name__ == '__main__':
    app.secret_key = 'APP_SECRET_KEY'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
