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
        try:
            new_user = User(email = email, username = username, password = password)
            new_user.save()
        except:
            # print(type(User.objects(email = email)))
            if list(User.objects(email = email)) != []:
                return "email đã được sử dụng"
            elif list(User.objects(username = username)) != []:
                return "username đã được sử dụng"
        session['user_id'] = str(new_user.id)
        missions = Missions.objects()
        for i in range(0,7):
            mission= choice(missions)
            new_user_mission = UserMission(user = new_user, mission = mission)
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

        user = User.objects(username__exact = username, password__exact= password).first()
        if user is not None:
            user = User.objects.get(username__exact = username, password__exact= password)
            session["user_id"] = str(user.id)
            return redirect(url_for("user_profile"))
        else:
            return "error login"

@app.route("/user_profile")
def user_profile():
    missions_completed = UserMission.objects(user= session['user_id'],completed= True)
    num_missions_uncompleted = len(list(UserMission.objects(user = session['user_id'],completed= False)))
    # num_missions_not_saved = len(list(UserMission.objects(user=session['user_id'],completed= True, saved =False, not_save = True)))
    # num_mission_saved = len(list(UserMission.objects(user=session['user_id'],completed= True, saved =True, not_save = False)))
    username = (User.objects.with_id(session['user_id'])).username
    return render_template("user_profile.html", missions_completed = missions_completed,
                                                username = username,
                                                num_missions_uncompleted = num_missions_uncompleted)

@app.route("/mission_detail")
def mission_detail():
    mission_detail = (UserMission.objects(user = session['user_id'],completed= False)).first()
    if mission_detail != None:
        session['done'] = False
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
        if not session['done']:
            return render_template('finish.html')
        else:
            return "your image uploaded!!!"
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
            session['done'] = True
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
    user = User.objects.with_id(session['user_id'])
    for i in range(0,7):
        mission= choice(missions)
        new_user_mission = UserMission(user =user, mission =mission)
        new_user_mission.save()
    return "continue challenge"

@app.route("/save_album/<int:save>")
def save_album(save):
    unsave_missions = UserMission.objects(user =session['user_id'],completed = True, saved = False)
    if save == 0:
        unsave_missions.update(set__not_save= True)
    elif save == 1:
        unsave_missions.update(set__not_save= False)
    save_missions = UserMission.objects(user =session['user_id'],completed = True, saved = False, not_save = False)
    user = User.objects.with_id(session['user_id'])

    if save_missions != None:
        new_album = Library(user = user,user_missions = save_missions)
        new_album.save()
        save_missions.update(set__saved=True)
    return "your album saved"

@app.route('/library')
def library():
    all_albums = Library.objects()
    return render_template("library.html", all_albums= all_albums)


if __name__ == '__main__':
  app.run(debug=True)
