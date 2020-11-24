"""
View - contains the basic structure of data that was
passed on by controller actions, uses it to render
the requested page, which is displayed on the browser
"""
from flask import render_template, session, redirect, request, url_for
from requests import get

from breqwatrapp import app


@app.route('/')
def main_page():
    """
    Render main search page template
    :return: Rendered Template
    """
    return render_template("mainSearch.html")


@app.route('/notfound404')
def not_found():
    """
    Render "404 - Not Found!" template with an error message
    :return: Rendered Template
    """
    return render_template("notFound.html", error=session["error"])


@app.route('/', methods=['POST'])
def search_query():
    """
    Render search result page according
    to user's POST request to the server
    :return: Response Object
    """
    category = request.form["selectCategory"]
    if category == "Username":
        session["username"] = request.form["username"]
        return redirect(url_for('get_user'))
    elif category == "Users":
        session["users"] = {
            "keyword": request.form["keywordUsers"].replace(" ", "+"),
            "type": request.form["userType"],
            "repos": request.form["repoNum"],
            "followers": request.form["followerUsers"],
            "location": request.form.get("countryUsers")
        }
        return redirect(url_for('get_users'))
    elif category == "Repositories":
        session["repos"] = {
            "keyword": request.form["keywordRepo"].replace(" ", "+"),
            "repo": request.form["repoName"],
            "user": request.form["repoOwner"],
            "size": request.form["repoSize"],
            "forks": request.form["forkNum"],
            "stars": request.form["minStar"]
        }
        return redirect(url_for('get_repos'))


@app.route('/user')
def get_user():
    """
    Render search result template with Github API data
    :return: Rendered Template
    """
    url = "https://api.github.com/users/"
    search = session["username"]
    user = get(url + search).json()
    if 'message' in user:
        session["error"] = "No result was found based on your input. Try Again!"
        return redirect(url_for('not_found'))
    else:
        return render_template('searchResult.html', user=user, repo=get(user["repos_url"]).json())


@app.route('/users')
def get_users():
    """
    Render search result template with Github API data
    :return: Rendered Template
    """
    user_input = session["users"]

    user_info = {key: value for key, value in user_input.items() if value}

    if len(list(user_info.keys())) <= 1:
        session["error"] = "Search Result is too large, be more specific!"
        return redirect(url_for('not_found'))

    if "repos" in user_info:
        user_info["repos"] = ">=" + user_info["repos"]

    if "followers" in user_info:
        user_info["followers"] = ">=" + user_info["followers"]

    api = "https://api.github.com/search/users?q=" + user_info.pop("keyword")
    if user_info["type"] != all:
        api += "+" + "type:" + user_info["type"]
        user_info.pop("type")
    for key in user_info:
        if key == "location":
            api += "&" + key + ":" + user_info[key]
        else:
            api += "+" + key + ":" + user_info[key]

    user_json = get(api).json()
    if user_json["total_count"] < 1:
        session["error"] = "No result was found based on your input. Try Again!"
        return redirect(url_for("not_found"))
    user_list = []
    for user in user_json["items"]:
        user_list.append(get(user["url"]).json())
    return render_template('usersResult.html', users=user_list, count=user_json["total_count"])


@app.route('/repos')
def get_repos():
    """
    Render search result template with Github API data
    :return: Rendered Template
    """
    user_input = session["repos"]

    repo_info = {key: value for key, value in user_input.items() if value}

    if len(list(repo_info.keys())) < 1:
        session["error"] = "Search Result is too large, be more specific!"
        return redirect(url_for('not_found'))

    if "size" in repo_info:
        repo_info["size"] = ">=" + repo_info["size"]

    if "forks" in repo_info:
        repo_info["forks"] = ">=" + repo_info["forks"]

    if "stars" in repo_info:
        repo_info["stars"] = ">=" + repo_info["stars"]

    api = "https://api.github.com/search/repositories?q=" + repo_info.pop("keyword")

    for key in repo_info:
        api += "+" + key + ":" + repo_info[key]

    repo_json = get(api).json()
    if "message" in repo_json:
        session["error"] = "No result was found based on your input. Try Again!"
        return redirect(url_for("not_found"))
    repo_list = []
    for repo in repo_json["items"]:
        repo_list.append(repo)
    return render_template('repoResults.html', repos=repo_list, count=repo_json["total_count"])
