import json
import logging
import os
import random
import requests
import string
from flask import Flask, flash, jsonify, make_response, redirect, \
                    render_template, request, send_from_directory, url_for
from flask.logging import create_logger
from flask import session as login_session
from werkzeug.utils import secure_filename
from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import NoResultFound
from db import Base, Category, Item, User, IMAGES_DIRECTORY

# GitHub Application credentials
CLIENT_ID = '88143cc4d646e722384a'
CLIENT_SECRET = '896cbafa5d0ebed1a62c17502ef806e7a911a319'

app = Flask(__name__)

LOG = create_logger(app)
LOG.setLevel(logging.INFO)

# Use PostgreSQL database, local connection
engine = create_engine('postgresql://dbuser:secretPassw0rd@db:5432/catalog')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
db_session = DBSession()


# JSON API endpoint
@app.route('/catalog.json')
def catalog_json():
    categories = db_session.query(Category).all()
    list_of_categories = []
    for c in categories:
        category = c.serialize
        items = db_session.query(Item).filter_by(category_id=c.id).all()
        if len(items) > 0:
            category['Item'] = []
            for i in items:
                item = i.serialize
                if item.get('description') is None:
                    item.pop('description')
                if item.get('picture') is not None:
                    item['picture'] = url_for('show_image', _external=True,
                                              filename=item['picture'])
                else:
                    item.pop('picture')
                category['Item'].append(item)
        list_of_categories.append(category)
    return jsonify(Category=list_of_categories)


# XML API endpoint
@app.route('/catalog.xml')
def catalog_xml():
    categories = db_session.query(Category).all()
    list_of_categories = []
    for c in categories:
        category = c.serialize
        items = db_session.query(Item).filter_by(category_id=c.id).all()
        if len(items) > 0:
            category['Item'] = [i.serialize for i in items]
        list_of_categories.append(category)
    xml_page = render_template('catalog.xml', categories=list_of_categories)
    response = make_response(xml_page)
    response.headers["Content-Type"] = "application/xml"
    return response


# Home page
@app.route('/')
@app.route('/catalog/')
def list_categories():
    categories = db_session.query(Category).all()
    last_items = db_session.query(Item).order_by(desc(Item.id)).limit(10)
    return render_template('categories.html', categories=categories,
                           items=last_items,
                           login=login_session.get('username'))


# List items in category
@app.route('/catalog/<category_name>')
def list_items(category_name):
    categories = db_session.query(Category).all()
    category = db_session.query(Category).filter_by(name=category_name).one()
    items = db_session.query(Item).filter_by(category_id=category.id).all()
    return render_template('items.html', categories=categories,
                           name=category.name, count=len(items),
                           items=items,
                           login=login_session.get('username'))


# View item
@app.route('/catalog/<category_name>/<item_name>')
def show_item(category_name, item_name):
    item = db_session.query(Item).filter_by(name=item_name).one()
    LOG.info('Showing item: %s - %s', category_name, item_name)
    return render_template('show.html', item=item,
                           login=login_session.get('username'))


# Show item image
@app.route('/images/<filename>')
def show_image(filename):
    return send_from_directory(IMAGES_DIRECTORY, filename)


# Add item
@app.route('/catalog/add', methods=['GET', 'POST'])
def add_item():
    # Check if user logged in
    if 'username' not in login_session:
        return redirect(url_for('login'))
    if request.method == 'GET':
        categories = db_session.query(Category).all()
        return render_template('add.html', categories=categories,
                               login=login_session.get('username'))
    elif request.method == 'POST':
        image = request.files['image']
        # Save image if chosen
        if check_image(image):
            filename = secure_filename(image.filename).lower()
            image.save(os.path.join(IMAGES_DIRECTORY, filename))
        else:
            filename = None
        # Description validation
        if request.form['description'] == '':
            description = None
        else:
            description = request.form['description']
        # Name must be non-empty
        if request.form['name'] != '':
            new_item = Item(name=request.form['name'],
                            description=description,
                            picture=filename,
                            category_id=request.form['category_id'],
                            user_id=login_session['user_id'])
        db_session.add(new_item)
        db_session.commit()
        return redirect(url_for('list_categories'))


# Edit item
@app.route('/catalog/<category_name>/<item_name>/edit',
           methods=['GET', 'POST'])
def edit_item(category_name, item_name):
    # Check if user logged in
    if 'username' not in login_session:
        return redirect(url_for('login'))
    item = db_session.query(Item).filter_by(name=item_name).one()
    # If current user is not item creator, forbid item's edition
    if item.user_id != login_session['user_id']:
        return """<script>
                    function myFunction() {
                        alert('You are not authorized to edit this item.');
                        window.location.replace('%s');
                    }
                </script>
                <body onload='myFunction()''>""" % url_for('list_categories')
    if request.method == 'GET':
        categories = db_session.query(Category).all()
        category = db_session.query(Category).\
            filter_by(name=category_name).one()
        return render_template('edit.html', categories=categories,
                               category_id=category.id,
                               item=item,
                               login=login_session.get('username'))
    elif request.method == 'POST':
        image = request.files['image']
        # Save updated image
        if check_image(image):
            filename = secure_filename(image.filename).lower()
            image.save(os.path.join(IMAGES_DIRECTORY, filename))
            item.picture = filename
        # Name must be non-empty
        if request.form['name'] != '':
            item.name = request.form['name']
        # Description validation
        if request.form['description'] == '':
            item.description = None
        else:
            item.description = request.form['description']
        item.category_id = request.form['category_id']
        db_session.add(item)
        db_session.commit()
        category = db_session.query(Category).\
            filter_by(id=request.form['category_id']).one()
        LOG.info('Editing item: %s - %s', category_name, item_name)
        return redirect(url_for('list_items',
                                category_name=category.name))


# Delete item
@app.route('/catalog/<category_name>/<item_name>/delete',
           methods=['GET', 'POST'])
def delete_item(item_name):
    # Check if user logged in
    if 'username' not in login_session:
        return redirect(url_for('login'))
    item = db_session.query(Item).filter_by(name=item_name).one()
    # If current user is not item creator, forbid item's deletion
    if item.user_id != login_session['user_id']:
        return """<script>
                    function myFunction() {
                        alert('You are not authorized to delete this item.');
                        window.location.replace('%s');
                    }
                </script>
                <body onload='myFunction()''>""" % url_for('list_categories')
    if request.method == 'GET':
        return render_template('delete.html', item=item,
                               login=login_session.get('username'))
    elif request.method == 'POST':
        # Delete image file
        os.remove(os.path.join(IMAGES_DIRECTORY, item.picture))
        db_session.delete(item)
        db_session.commit()
        return redirect(url_for('list_categories'))


# Show login page
@app.route('/login')
def login():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in range(32))
    login_session['state'] = state
    return render_template('login.html', client_id=CLIENT_ID, state=state,
                           login=login_session.get('username'))


# Process GitHub login
@app.route('/glogin')
def github_login():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    state = login_session['state']
    code = request.args.get('code')
    # Check errors for the authorization request
    error = request.args.get('error')
    if error is not None:
        response = make_response(json.dumps(
                    request.args.get('error_description')), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Get access token
    url = 'https://github.com/login/oauth/access_token'
    headers = {'Accept': 'application/json'}
    params = {'client_id': CLIENT_ID, 'client_secret': CLIENT_SECRET,
              'code': code, 'state': state}
    result = requests.post(url, data=params, headers=headers)
    data = result.json()
    # Check errors for the access token request
    error = data.get('error')
    if error is not None:
        response = make_response(json.dumps(
                    data.get('error_description')), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    login_session['access_token'] = data['access_token']
    # Get user info
    url = 'https://api.github.com/user'
    token_param = 'token %s' % login_session['access_token']
    headers = {'Authorization': token_param, 'Accept': 'application/json'}
    result = requests.get(url, headers=headers)
    data = result.json()
    login_session['username'] = data['login']
    login_session['fullname'] = data['name']
    # Check if user exists & create if not found
    user_id = get_user_id(login_session['username'])
    if user_id is None:
        user_id = create_user()
    login_session['user_id'] = user_id
    #
    flash("Welcome, %s!" % login_session['fullname'])
    #
    return redirect(url_for('list_categories'))


# Log user out
@app.route('/logout')
def logout():
    # Delete access token
    url = 'https://api.github.com/applications/%s/tokens/%s' % (
            CLIENT_ID, login_session['access_token'])
    requests.delete(url, auth=(CLIENT_ID, CLIENT_SECRET))
    # result = requests.delete(url, auth=(CLIENT_ID, CLIENT_SECRET))
    # Check result
    # if result.headers['status'] != "204 No Content":
    #     response = make_response(
    #                 json.dumps("Error destroying user session"), 401)
    #     response.headers['Content-Type'] = 'application/json'
    #     return response
    #
    flash("%s logged out!" % login_session['fullname'])
    # Remove the user data from the session if its there
    login_session.pop('access_token', None)
    login_session.pop('state', None)
    login_session.pop('username', None)
    login_session.pop('fullname', None)
    login_session.pop('user_id', None)
    #
    return redirect(url_for('list_categories'))


# User Helper functions
def create_user():
    user = User(username=login_session['username'],
                fullname=login_session['fullname'])
    db_session.add(user)
    db_session.commit()
    user = db_session.query(User).\
        filter_by(username=login_session['username']).one()
    return user.id


def get_user_id(username):
    try:
        user = db_session.query(User).filter_by(username=username).one()
        return user.id
    except NoResultFound:
        return None


def get_user_info(user_id):
    user = db_session.query(User).filter_by(id=user_id).one()
    return user


# Check uploaded image
def check_image(image):
    if image:
        # Read first 10 bytes
        file_signature = image.read(10)
        # Rewind file to begin
        image.seek(0)
        file_extension = os.path.splitext(image.filename)[1].lower()
        # Check conformity between file extension and file signature
        # JPEG image format
        if file_extension == '.jpg' and file_signature[-4:] == 'JFIF':
            return True
        elif file_extension == '.jpeg' and file_signature[-4:] == 'JFIF':
            return True
        # PNG image format
        elif file_extension == '.png' and file_signature[1:4] == 'PNG':
            return True
        # GIF image format
        elif file_extension == '.gif' and file_signature[:6] == 'GIF87a':
            return True
        elif file_extension == '.gif' and file_signature[:6] == 'GIF89a':
            return True
        # We do not support other image formats
        else:
            return False
    else:
        return False


# Main routine
if __name__ == '__main__':
    app.secret_key = 'cgvSdvbFudzOunQFaklmHA=='  # super secret key
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
