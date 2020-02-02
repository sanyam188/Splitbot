from flask import Flask, jsonify, request, render_template, redirect, session, url_for
from splitwise import Splitwise
import config as Config
import requests

app = Flask(__name__)
app.secret_key = Config.secret_key

#Default route for checking if a user is logged in
@app.route("/")
def home():

    if 'access_token' in session:
        return redirect(url_for('help'))

    #if user is not logged in
    return redirect(url_for('login'))


#Login route
@app.route("/login")
def login():

    sObj = Splitwise(Config.consumer_key,Config.consumer_secret)
    url, secret = sObj.getAuthorizeURL()
    session['secret'] = secret

    #If user is logged in then url redirects to authorize route
    #Else url redirects to splitwise login website
    return redirect(url) 


#Authorize route
@app.route("/authorize")
def authorize():

    if 'secret' not in session:
        return redirect(url_for("home"))

    oauth_token    = request.args.get('oauth_token')
    oauth_verifier = request.args.get('oauth_verifier')
    
    sObj = Splitwise(Config.consumer_key,Config.consumer_secret)
    access_token = sObj.getAccessToken(oauth_token,session['secret'],oauth_verifier)
    print("Access Token ", access_token)
    session['access_token'] = access_token

    return redirect(url_for("help"))


#Get the list of friends along with balances
@app.route("/friends")
def friends():

    if 'access_token' not in session:
        return redirect(url_for("home"))

    sObj = Splitwise(Config.consumer_key,Config.consumer_secret)
    sObj.setAccessToken(session['access_token'])

    friends = sObj.getFriends() #Get a list of friends object using Splitwise API
    
    friend_list = []  #Friends list
    bal_list = []   #Balance list
    
    # li = []
    for friend in friends:
        friend_list.append(friend.getFirstName())
        print(friend.getBalances())
        print(len(friend.getBalances()))

        if len(friend.getBalances())==0:
            bal_list.append("0")
        else:
            for bal in friend.getBalances():
                if len(bal.getAmount()) == 0:
                    bal_list.append("0")
                else:
                    bal_list.append(bal.getAmount())
 
    output = {'friends': friend_list, 'balances': bal_list}
    return jsonify(output)


#Get list of groups with balances
@app.route("/groups")
def groups():

    if 'access_token' not in session:
        return redirect(url_for("home"))

    sObj = Splitwise(Config.consumer_key,Config.consumer_secret)
    sObj.setAccessToken(session['access_token'])

    groups = sObj.getGroups() #Get a list of grpups object
    
    group_list = []  #group list
    bal_list = []   #Balance list
    
    for group in groups:
        group_list.append(group.getName())
        print(group.getName())
        group_bal = []
        for debt in group.getSimplifiedDebts():
            group_bal.append((debt.getFromUser(), debt.getToUser(), debt.getAmount()))
            print(debt.getFromUser(), debt.getToUser(), debt.getAmount())
        bal_list.append(group_bal)

    output = {'groups': group_list, 'balances': bal_list}
    return jsonify(output)


#Default route to display list of options to user
@app.route("/help")
def help():
    return "Hello"

@app.route("/isloggedin")
def isloggedin():
    if('access_token' in session):
        return True
    else:
        return False

if __name__ == "__main__":
    app.run(threaded=True,debug=True)
