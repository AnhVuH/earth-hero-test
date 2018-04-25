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
                return render_template("message.html", message = "email exist")
            elif list(User.objects(username = username)) != []:
                return render_template("message.html", message = "username exist")
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
            return render_template("message.html", message = "error login")

@app.route("/user_profile")
def user_profile():
    missions_completed = UserMission.objects(user= session['user_id'],completed= True)
    if len(list(missions_completed)) % 7 != 0:
        missions_uncompleted = True
    else:
        missions_uncompleted = False
        num_missions_unprocessed = len(list(UserMission.objects(user = session['user_id'], not_save= None)))
    username = (User.objects.with_id(session['user_id'])).username
    return render_template("user_profile.html", missions_completed = missions_completed,
                                                username = username,
                                                missions_uncompleted = missions_uncompleted,
                                                num_missions_unprocessed = num_missions_unprocessed)

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
            return render_template("message.html", message = "uploaded")
    elif request.method == 'POST':
        form = request.form
        caption = form['caption']
        # username = (User.objects.with_id(session["user_id"])).username
        # mission_id = str((UserMission.objects(user = session["user_id"], completed = False).first()).id)
        # name_image = username + mission_id


        image = request.files['image']
        image_name = image.filename
        if image  and allowed_filed(image_name):
        # im = Image.open(image)
        # im.save("static/media/"+name_image+".jpg", format = "JPEG", quality = 20)
        # image = Image.open("static/media/"+name_image+".jpg")

            img = Image.open(image)
            img.save(format='JPEG',quality = 20)
            output = BytesIO()
            img.save(output)
            image_data = output.getvalue()


            image_bytes = base64.b64encode(image_data)
            image_string = image_bytes.decode()


            mission_updated = UserMission.objects(user = session["user_id"], completed = False).first()
            mission_updated.update(set__caption = caption, set__image = image_string, completed = True)
            session['done'] = True
            return redirect(url_for("share",id_mission = str(mission_updated.id)))
        else:
            return render_template("message.html", message = "file not allowed")

@app.route("/share/<id_mission>")
def share(id_mission):
    mission_share = UserMission.objects.with_id(id_mission)
    username = mission_share.user.username
    caption = mission_share.caption
    image = mission_share.image
    return render_template("share.html",username = username, caption = caption, image = image, id_mission= id_mission)

@app.route('/congratulation')
def congratulation():
    user = User.objects.with_id(session["user_id"])
    return render_template("congratulation.html",user = user)


@app.route('/continue_challenge')
def continue_challenge():
    missions = Missions.objects()
    user = User.objects.with_id(session['user_id'])
    for i in range(0,7):
        mission= choice(missions)
        new_user_mission = UserMission(user =user, mission =mission)
        new_user_mission.save()
    return render_template("message.html", message = "continue challenge")

@app.route("/save_album/<int:save>")
def save_album(save):
    unsave_missions = UserMission.objects(user =session['user_id'],completed = True, saved = False)
    if save == 0:
        unsave_missions.update(set__not_save= True)
    elif save == 1:
        unsave_missions.update(set__not_save= False)
    save_missions = UserMission.objects(user =session['user_id'],completed = True, saved = False, not_save = False)
    user = User.objects.with_id(session['user_id'])

    if list(save_missions) != [] :
        new_album = Library(user = user,user_missions = save_missions)
        new_album.save()
        save_missions.update(set__saved=True)
    return render_template("message.html", message = "processed")

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
