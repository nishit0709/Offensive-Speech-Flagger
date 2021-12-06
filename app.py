import logging, os, pyrebase, firebase_admin
from flask import Flask, flash, redirect, render_template,request, session, make_response, abort, url_for
from werkzeug.utils import secure_filename
from firebase_admin import credentials
from firebase_admin import firestore
from Detector import offenceDetector
basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)       #Initialze flask constructor
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
config = {
    "apiKey": "AIzaSyDixuOtwlw-ZG36Ttbwxfmke7Azf6fnV5U",
    "authDomain": "offensive-91780.firebaseapp.com",
    "databaseURL": "https://offensive-91780-default-rtdb.firebaseio.com",
    "projectId": "offensive-91780",
    "storageBucket": "offensive-91780.appspot.com",
    "messagingSenderId": "302872635993",
    "appId": "1:302872635993:web:79303d88558b920be05f48"
}

#initialize firebase
firebase = pyrebase.initialize_app(config)
storage = firebase.storage()
auth = firebase.auth()
db = firebase.database()
data = os.path.abspath(os.path.dirname(__file__)) + "/offensive-91780-firebase-adminsdk-j8m9b-d243fd6f01.json"
cred = credentials.Certificate(data)
firebase_admin.initialize_app(cred)
fb = firestore.client()
app.config['SECRET_KEY'] = '565656'

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOADED_PHOTOS_DEST'] = os.path.join(basedir, 'uploads') # you'll need to create a folder named uploads
person = {"is_logged_in": False, "name": "", "email": "", "uid": "","profile_url":""}

from datetime import datetime

now = datetime.now()
app.secret_key = '565656'
current_time = now.strftime("%H:%M:%S")
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')

@app.route("/login")
def login():
    return render_template("login.html")

#Sign up/ Register
@app.route("/signup")
def signup():
    return render_template("signup.html")

@app.route("/create/<user>",methods=["POST","GET"])
def create(user):
    uid=user
    try:
        if request.method == 'POST':
            result = request.form  # Get the data submitted
            caption = result["caption"]
            k=offenceDetector.check_tweet(caption)
            print(k)

            # check if the post request has the file part
            doc_ref = fb.collection(uid).document(str(hash(caption)))
            pub_ref = fb.collection('posts').document(str(hash(caption)))

            # looping through all the tags present in exifdata

            doc_ref.set({

                u'caption': caption,
                u'timestamp': firestore.SERVER_TIMESTAMP,
                u'user': uid,
                u'tag':k

                })
            pub_ref.set({

                u'caption': caption,
                u'timestamp': firestore.SERVER_TIMESTAMP,
                u'user': uid,
                u'tag':k

                })
            success = True
        else:
            success = False


    except:
        #If there is any error, redirect back to login
        return redirect(url_for('welcome',_external=True,user=uid))
    return render_template("create.html", user=uid)


#Welcome page
@app.route("/welcome/<user>",methods=["POST","GET"])
def welcome(user):
    key=[]

    for f in os.listdir('uploads'):
        if f.endswith('.jpg'):
            os.remove(os.path.join('uploads', f))
    filename=""
    path_local=""
    person["is_logged_in"] == True
    if person["is_logged_in"] == True:
        doc_ref = fb.collection(u'users').document(user)
        file_url = storage.child("avtars/" + user + ".jpg").get_url(None)
        users_ref = fb.collection(u'users').document(user)
        profile_url = storage.child("avtars/" + user + ".jpg").get_url(None)
        doc = doc_ref.get()
        # name = u'{}'.format(doc.to_dict()['name'])
        # email=u'{}'.format(doc.to_dict()['email'])
        # profile=u'{}'.format(doc.to_dict()['profile_url'])
        # form = UploadForm()

        if request.method == 'POST':
                # check if the post request has the file part

            file = request.files['file']
                # If the user does not select a file, the browser submits an
                # empty file without a filename.
            if file.filename == '':
                flash('No selected file')
                return redirect(request.url)
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOADED_PHOTOS_DEST'], filename))
                path_local = app.config['UPLOADED_PHOTOS_DEST'] + "/" + filename
                path_on_cloud = "avtars/" + user + ".jpg"

                storage.child(path_on_cloud).put(path_local)
                file_url = storage.child("avtars/" + user + ".jpg").get_url(None)
                doc_ref.update({
                    u'profile_url': file_url

                })

                os.remove(app.config['UPLOADED_PHOTOS_DEST']+"/"+ filename)
                success = True

            else:
                success = False
        u = fb.collection(user)
        d = u.stream()
        a,c,t,m=[],[],[],[]

        for doc in d:
            key.append(str(doc.id))
            c.append(u'{}'.format(doc.to_dict()['caption']))
            t.append(u'{}'.format(doc.to_dict()['timestamp']))
            m.append(u'{}'.format(doc.to_dict()['tag']))

        doc = doc_ref.get()
        name = u'{}'.format(doc.to_dict()['name'])
        email=u'{}'.format(doc.to_dict()['email'])
        profile=u'{}'.format(doc.to_dict()['profile_url'])
        print(name,email,profile)
        return render_template("welcome.html", key=key,email = email, name = name,uid=user,file_url=profile,caption=c,timestamps=t,l=len(c),d=d,tag=m)
    
    else:
        return redirect(url_for('login',_external=True))


#If someone clicks on login, they are redirected to /result
@app.route("/result", methods = ["POST", "GET"])
def result():
    trigger=False
    if request.method == "POST":        #Only if data has been posted
        result = request.form           #Get the data
        email = result["email"]
        password = result["pass"]
        try:
            #Try signing in the user with the given information
            user = auth.sign_in_with_email_and_password(email, password)
            session['loggedin'] = True
            session['id'] = user['localId']
            session['username'] = email
            #Insert the user data in the global person
            global person
            person["is_logged_in"] = True
            return redirect(url_for('welcome',_external=True,user=user["localId"]))
        except:
            #If there is any error, redirect back to login
            return redirect(url_for('login',_external=True))


@app.route("/posts/<user>",methods=["POST","GET"])
def posts(user):
    uid=user
    u = fb.collection('posts')
    d = u.stream()
    a,c,t,m = [],[],[],[]
    key,usernames,user_emails,user_profiles=[],[],[],[]


    for doc in d:
        key.append(str(doc.id))
        print(doc.id)
        c.append(u'{}'.format(doc.to_dict()['caption']))
        t.append(u'{}'.format(doc.to_dict()['timestamp']))
        m.append(u'{}'.format(doc.to_dict()['tag']))
        id = u'{}'.format(doc.to_dict()[u'user'])
        users_ref = fb.collection(u'users').document(id)
        user_doc = users_ref.get()
        name = u'{}'.format(user_doc.to_dict()['name'])
        usernames.append(name)
        email = u'{}'.format(user_doc.to_dict()['email'])
        user_emails.append(email)
        profile = u'{}'.format(user_doc.to_dict()['profile_url'])
        user_profiles.append(profile)
    return render_template("posts.html",caption=c,timestamps=t,l=len(c),user=uid,usernames=usernames,user_emails=user_emails,user_profiles=user_profiles,key=key,tag=m)

#If someone clicks on register, they are redirected to /register
@app.route("/register", methods = ["POST", "GET"])
def register():
    if request.method == "POST":        #Only listen to POST
        result = request.form           #Get the data submitted
        email = result["email"]
        password = result["pass"]
        name = result["name"]
        #Try creating the user account using the provided data
        auth.create_user_with_email_and_password(email, password)
        #Login the user
        user = auth.sign_in_with_email_and_password(email, password)
        #Add data to global person
        global person
        person["is_logged_in"] = True
        doc_ref = fb.collection(u'users').document(user["localId"])
        doc_ref.set({
            u'name': name,
            u'email':email,
            u'profile_url':''

        })
        #Go to welcome page
        return redirect(url_for('welcome',_external=True,user=user["localId"]))
    else:
            #If there is any error, redirect to register
        return redirect(url_for('register',_external=True))

@app.route("/logout", methods = ["POST", "GET"])
def logout():
    auth.current_user=None
    person = {"is_logged_in": False, "name": "", "email": "", "uid": "", "profile_url": ""}
    person["is_logged_in"]=False
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    return redirect(url_for('login',_external=True))

if __name__ == '__main__':
    app.run(debug=True)
