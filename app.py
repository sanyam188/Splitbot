from flask import Flask, jsonify, request, render_template, redirect, session, url_for
from splitwise import Splitwise
import config as Config

app = Flask(__name__)
app.secret_key = Config.secret_key

@app.route("/")
def home():
    if 'access_token' in session:
        return redirect(url_for("friends"))
    return render_template("home.html")

@app.route("/login")
def login():

    sObj = Splitwise(Config.consumer_key,Config.consumer_secret)
    print(sObj)
    url, secret = sObj.getAuthorizeURL()
    session['secret'] = secret
    print(url)
    print(secret)
    return redirect(url)


@app.route("/authorize")
def authorize():

    if 'secret' not in session:
        return redirect(url_for("home"))

    oauth_token    = request.args.get('oauth_token')
    oauth_verifier = request.args.get('oauth_verifier')
    print(request.args)
    
    sObj = Splitwise(Config.consumer_key,Config.consumer_secret)
    access_token = sObj.getAccessToken(oauth_token,session['secret'],oauth_verifier)
    session['access_token'] = access_token

    return redirect(url_for("friends"))


@app.route("/friends")
def friends():
    if 'access_token' not in session:
        return redirect(url_for("home"))

    sObj = Splitwise(Config.consumer_key,Config.consumer_secret)
    sObj.setAccessToken(session['access_token'])

    friends = sObj.getFriends()
    friend_list = []
    bal_list = []
    for friend in friends:
        friend_list.append(friend.getFirstName())
        bal_list.append(["".join(x.getAmount()) for x in friend.getBalances()])
    print(bal_list)
    # return jsonify(friends)
    # print("HODSfjosdf ", friends)
    output = {'friends': friend_list, 'balances': bal_list}
    return jsonify(output)
    # friend_dict = {}
    # friend_dict['id'] = [f.getId() for f in friends]
    # print(friend_dict)
    # return friend_dict
    # return render_template("friends.html",friends=friends)

@app.route("/groups")
def groups():
    if 'access_token' not in session:
        return redirect(url_for("home"))

    sObj = Splitwise(Config.consumer_key,Config.consumer_secret)
    sObj.setAccessToken(session['access_token'])
    print("session : ", session)

    groups = sObj.getGroups()
    return render_template("groups.html", groups=groups)

@app.route("/help")
def help():
    return "Hello"

if __name__ == "__main__":
    app.run(threaded=True,debug=True)
