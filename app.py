from flask import *
import mlab
from random import choice
import base64
import os
import gmail
from  werkzeug.utils import secure_filename
from models.classes import *
mlab.connect()
app = Flask(__name__)
app.secret_key = 'a-useless-key'


# for i in range(15):
#     new_mission = Missions(missions_name="mission"+ str(i),description="abcxyz" + str(i))
#     new_mission.save()

@app.route('/')
def index():
    if "user_id" in session:
        loged_in = True
    else:
        loged_in = False
    return render_template("index.html", loged_in= loged_in)

@app.route("/sign_up", methods= ['GET', 'POST'])
def sign_up():
    if request.method == 'GET':
        return render_template('sign_up.html')
    elif request.method == 'POST':
        form = request.form
        email = form['email']
        username = form['username']
        password = form['password']
        new_user = User(email = email, username = username, password = password)
        new_user.save()
        session['user_id'] = str(new_user.id)
        missions = Missions.objects()
        for i in range(0,7):
            mission= choice(missions)
            new_user_mission = UserMission(user =new_user.id, mission =mission,completed= False)
            new_user_mission.save()
        return redirect(url_for("user_profile"))

@app.route('/login', methods =['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    elif request.method =='POST':
        form = request.form
        username = form['username']
        password = form['password']
        try:
            user = User.objects.get(username__exact = username, password__exact= password)
        except:
            user = None
        if user is not None:
            user = User.objects.get(username__exact = username, password__exact= password)
            session["user_id"] = str(user.id)
            return redirect(url_for("user_profile"))
        else:
            return "error login"

@app.route("/user_profile")
def user_profile():
    missions_completed = UserMission.objects(user = session['user_id'],completed= True)
    username = (User.objects.with_id(session['user_id'])).username
    return render_template("user_profile.html", missions_completed = missions_completed, username = username)

@app.route("/mission_detail")
def mission_detail():
    mission_detail = (UserMission.objects(user = session['user_id'],completed= False)).first()
    if mission_detail != None:
        return render_template("mission_detail.html",mission_detail = mission_detail)
    else:
        return redirect(url_for("congratulation"))

ALLOWED_EXTENSIONS = set(['txt', 'jpg','png', 'jpeg', 'gif', 'pdf' ])
def allowed_filed(filename):
    check_1 = "." in filename
    check_2 = filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    return check_1 and check_2

@app.route("/finish",methods= ['GET', 'POST'])
def finish():
    if request.method == 'GET':
        return render_template('finish.html')
    elif request.method == 'POST':
        form = request.form
        caption = form['caption']

        image = request.files['image']
        image_name = image.filename
        image_bytes = base64.b64encode(image.read())
        image_string = image_bytes.decode()

        if image  and allowed_filed(image_name):
            mission_updated = UserMission.objects(user = session["user_id"], completed = False).first()
            mission_updated.update(set__caption = caption, set__image = image_string, completed = True)
            return redirect(url_for("share",id = str(mission_updated.id)))

@app.route("/share/<id>")
def share(id):
    mission_share = UserMission.objects.with_id(id)
    username = mission_share.user.username
    caption = mission_share.caption
    image = mission_share.image
    return render_template("share.html",username = username, caption = caption, image = image, id= id)

@app.route('/congratulation')
def congratulation():
    return render_template("congratulation.html")

@app.route('/logout')
def logout():
    if 'user_id' in session:
        del session['user_id']
        return redirect(url_for("index"))

@app.route('/continue_challenge')
def continue_challenge():
    missions = Missions.objects()
    for i in range(0,7):
        mission= choice(missions)
        new_user_mission = UserMission(user =session['user_id'], mission =mission,completed= False)
        new_user_mission.save()
    return redirect(url_for("user_profile"))

if __name__ == '__main__':
  app.run(debug=True)