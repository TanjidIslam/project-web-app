Github Search

### Features
- Search Specific User by Username
- Search Users with one or more of the following criteria:
    -  Keyword
    -  Account Type
    -  Number of Reposoirties Contributed/Owned
    -  Number of Followers
    -  Location
- Search Repositories with one of more of the following criteri:
    -  Keyword
    -  Specific Repository Name
    -  Specific Repository Owner
    -  Stars
    -  Size of the Repository
    -  Number of Forks
- Views: Passed PyLint & Pep8
- Structure: Basic Flask Structure

### Requirements
- Python 3.5.1 (https://www.python.org/downloads/)
- Flask 0.10.1 (http://flask.pocoo.org/)
- Requests 2.10.0 (http://docs.python-requests.org/en/master/)


### Project Quick Start Guide

This guide will walk you through deploying Project locally

#### Usage

```console
$ https://github.com/TanjidIslam/Github-Search.git
$ cd Github-Search
$ pyvenv-3.5 env
$ source env/bin/activate
$ pip3 install -r requirements.txt
```

#### To run on local server
```console
$ python3 runserver.py
```

### TODO
- Code Search
- Issue Search


### Design Choices
Design choices are as important as application implementations. In this section, I will demonstrate on my choice of design and tools and point out how they connect.
I used Model-View-Controller pattern, also known as the famous MVC pattern. I chose Python with Flask framework because it is light and gives me the freedom to use <b>routes, models, views & controllers</b>, the 4 major components of MVC pattern.

#### Routes
A user <b>requests</b> to view a page by entering a URL:
```HTML
http://breqwatr.search.ca/search
```

The application matches the URL pattern with a predefined <b>route</b>:
```
    http://breqwatr.search.ca/'search'
```

With each <b>route</b> is associated with a controller, more specifically a certain function within the controller, also known as the <b>controller action</b>:
```python
@app.route('/user')
def get_user():
    #functionality of getting user..
```

#### Models and Controllers
The <b>controller action</b> uses the models (search result model for this case) to retrieve all of the necessary data from a database, places the data in a data structure (dictionary/json in this case), and loads a view, passing along the data structure:
```python
@app.route('/user')
def login_user():
    url = "https://api.github.com/users/"
    search = session["username"]
    user = get(url + search).json()
    return render_template('searchResult.html', user=user, repo=get(user["repos_url"]).json())
```
It is ideal to create user model but for this case it wasn't necessary.

#### Views
The <b>view</b>, the basic structure of data that was passed on by <b>controller action</b>, uses it to render the requested page, which is then displayed to the user in their browser.
```jinja2
{% for user in users_list %}
  <li>
    <h2>{{ user.name }}</h2>
    <div>{{ user.html_url }}</div>
  </li>
{% if not user %}
  <li><em>No user in the database!</em></li>
{% endfor %}
```
