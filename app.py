from flask import *
import mlab
from random import choice
import base64
import os
import gmail
from io import BytesIO
from  werkzeug.utils import secure_filename
from models.classes import *
from PIL import Image
mlab.connect()
app = Flask(__name__)
app.secret_key = 'a-useless-key'

# def save_all_missions(user_id):
#     user = User.objects.with_id(user_id)
#     missions_share = UserMission.objects(user = user_id,completed = True, saved = False)
#     new_album = Library(user = user ,user_missions = missions_share)
#     new_album.save()
#     missions_share.update(set__saved=True)


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
            if list(User.objects(email = email)) != []:
                return render_template("message.html", message = "email exist")
            elif list(User.objects(username = username)) != []:
                return render_template("message.html", message = "username exist")
        session['user_id'] = str(new_user.id)
        missions = Missions.objects()
        for i in range(0,7):
            mission= choice(missions)
            new_user_mission = UserMission(user = new_user, mission = mission, mission_number = i+1)
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
            return render_template("message.html", message = "error login")

@app.route("/user_profile")
def user_profile():
    missions_completed = UserMission.objects(user= session['user_id'],completed= True)
    missions_uncompleted =list(UserMission.objects(user = session['user_id'], completed=False))
    if len(missions_uncompleted) != 0:
        uncompleted = True
    else:
        uncompleted = False
        # save_missions = UserMission.objects(user = session['user_id'],completed= True, saved = False)
        # # if len(list(save_missions)) == 7:
        # new_album = Library(user = session['user_id'],user_missions = save_missions)
        # new_album.save()
        # save_missions.update(set__saved=True)

    username = (User.objects.with_id(session['user_id'])).username
    return render_template("user_profile.html", missions_completed = missions_completed,
                                                username = username,
                                                uncompleted = uncompleted)

@app.route("/mission_detail")
def mission_detail():
    mission_detail = (UserMission.objects(user = session['user_id'],completed= False)).first()
    session['done'] = False
    return render_template("mission_detail.html",mission_detail = mission_detail)



ALLOWED_EXTENSIONS = set([ 'jpg','png', 'jpeg' ])
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
            return render_template("message.html", message = "uploaded")
    elif request.method == 'POST':
        form = request.form
        caption = form['caption']

        image = request.files['image']
        image_name = image.filename
        if image  and allowed_filed(image_name):

            img = Image.open(image)
            if "png" in image_name:
                img = img.convert('RGB')
            output = BytesIO()

            img.save(output,format='JPEG',quality = 20)
            image_data = output.getvalue()

            image_bytes = base64.b64encode(image_data)
            image_string = image_bytes.decode()

            mission_updated = UserMission.objects(user = session["user_id"], completed = False).first()
            mission_updated.update(set__caption = caption, set__image = image_string, completed = True)
            session['done'] = True
            save_missions = UserMission.objects(user = session['user_id'],completed= True, saved = False)
            if len(list(save_missions)) == 7:
                session["all_missions_completed"] = True
                print(session["all_missions_completed"])
            else:
                session["all_missions_completed"] = False
                print(session["all_missions_completed"])
            return redirect(url_for("share",id_mission = str(mission_updated.id)))
        else:
            return render_template("message.html", message = "file not allowed")

@app.route("/share/<id_mission>")
def share(id_mission):
    mission_share = UserMission.objects.with_id(id_mission)
    username = mission_share.user.username
    caption = mission_share.caption
    image = mission_share.image
    mission_number = mission_share.mission_number
    if session["all_missions_completed"]:
        user = User.objects.with_id(session['user_id'])
        missions_share = UserMission.objects(user = session['user_id'],completed = True, saved = False)
        new_album = Library(user = user ,user_missions = missions_share)
        new_album.save()
        missions_share.update(set__saved=True)
        # save_all_missions(session['user_id'])
        session["all_completed"] = False
    return render_template("share.html",username = username, caption = caption, image = image, id_mission= id_mission, mission_number =mission_number)

@app.route('/congratulation')
def congratulation():
    user = User.objects.with_id(session['user_id'])
    missions_share = UserMission.objects(user = session['user_id'],completed = True, saved = False)
    if len(list(missions_share)) == 7:
        # new_album = Library(user = user ,user_missions = missions_share)
        # new_album.save()
        # missions_share.update(set__saved=True)
        return render_template("congratulation.html",missions_share = missions_share, user=user)
    else:
        return "Bạn phải hoàn thành 7 nhiệm vụ đã"



@app.route('/continue_challenge')
def continue_challenge():
    missions = Missions.objects()
    user = User.objects.with_id(session['user_id'])
    for i in range(0,7):
        mission= choice(missions)
        new_user_mission = UserMission(user =user, mission =mission,mission_number = i+1)
        new_user_mission.save()
    return redirect(url_for("mission_detail"))


@app.route('/library')
def library():
    all_albums = Library.objects()
    return render_template("library.html", all_albums= all_albums)

@app.route('/logout')
def logout():
    if 'user_id' in session:
        del session['user_id']
        return redirect(url_for("index"))


if __name__ == '__main__':
  app.run(debug=True)
