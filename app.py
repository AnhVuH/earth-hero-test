from flask import *
import mlab
from random import choice
import base64
import os
import gmail
from gmail import GMail, Message
from io import BytesIO
from  werkzeug.utils import secure_filename
from models.classes import *
from PIL import Image
mlab.connect()
app = Flask(__name__)
app.secret_key = 'a-useless-key'


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
        wellcome_hero = """
        <h1 style="text-align: center;">.....Gửi người anh h&ugrave;ng......</h1>
<h3>- Ch&agrave;o mừng {{username}} tham gia v&agrave;o nhiệm vụ giải cứu tr&aacute;i đất&nbsp;</h3>
<p><strong>- H&atilde;y truy cập https://earth-hero-test.herokuapp.com/&nbsp;để bắt đầu cuộc h&agrave;nh tr&igrave;nh đi n&agrave;o !!</strong></p>
<p><img src="https://html-online.com/editor/tinymce4_6_5/plugins/emoticons/img/smiley-laughing.gif" alt="laughing" width="36" height="36" /></p>
            """
        wellcome_hero = wellcome_hero.replace("{{username}}", username)
        gmail = GMail(username="20166635@student.hust.edu.vn",password="quy.dc20166635")
        msg = Message("Gửi người anh hùng", to= email, html = wellcome_hero)
        gmail.send(msg)

        session['user_id'] = str(new_user.id)
        session['first_login'] = True
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
    if 'first_login' in session:
        first_login = True
    else:
        first_login = False
    username = (User.objects.with_id(session['user_id'])).username
    return render_template("user_profile.html", missions_completed = missions_completed,
                                                username = username,
                                                uncompleted = uncompleted , first_login = first_login)

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
        image_size_MB = len(image.read())/1048576
        # print(image_size_MB)
        image_name = image.filename
        if image  and allowed_filed(image_name):

            img = Image.open(image)
            if "png" in image_name:
                img = img.convert('RGB')
            output = BytesIO()

            if image_size_MB < 5:
                img.save(output,format='JPEG',quality = 95)
            else:
                img.save(output,format ='JPEG', quality = 75)
            # if image_size_MB < 5:
            #     img.save("static/media/small.jpg",format='JPEG', quality = 95)
            # else:
            #     img.save("static/media/large1.jpg",format ='JPEG', quality =70)


            image_data = output.getvalue()

            image_bytes = base64.b64encode(image_data)
            image_string = image_bytes.decode()

            mission_updated = UserMission.objects(user = session["user_id"], completed = False).first()
            mission_updated.update(set__caption = caption, set__image = image_string, completed = True)
            session['done'] = True

            save_missions = UserMission.objects(user = session['user_id'],completed= True, saved = False)
            if len(list(save_missions)) == 7:

                user = User.objects.with_id(session['user_id'])
                missions_share = UserMission.objects(user = session['user_id'],completed = True, saved = False)
                new_album = Library(user = user ,user_missions = missions_share)
                new_album.save()
                session['new_album_id'] = str(new_album.id)
                missions_share.update(set__saved=True)


                username = user.username
                email = user.email
                missions_completed = """
                    <h1 style="text-align: center;">.....Gửi người anh h&ugrave;ng......</h1>
<h3>- Mừng v&igrave; được gửi th&ocirc;ng điệp cho bạn 1 l&acirc;n nữa, {{username}} bạn đ&atilde; ho&agrave;n th&agrave;nh 7 nhiệm vụ tr&aacute;i đất ghi c&ocirc;ng bạn, h&atilde;y tiếp t&uacute;c g&oacute;p những h&agrave;nh động tươi đẹp cho m&ocirc;i trường nh&eacute;</h3>
<h3>&nbsp;&nbsp;</h3>
<h3>Heroku.com hận hạnh t&agrave;i trợ trang web n&agrave;y .</h3>
                """
                missions_completed = missions_completed.replace("{{username}}", username)
                print("missions_completed")
                gmail = GMail(username="20166635@student.hust.edu.vn",password="quy.dc20166635")
                msg = Message("Gửi người anh hùng", to= email, html = missions_completed)
                gmail.send(msg)

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
    return render_template("share.html",username = username, caption = caption, image = image, id_mission= id_mission, mission_number =mission_number)

@app.route('/congratulation/')
def congratulation():
    if "new_album_id" in session:
        user_new_album = Library.objects.with_id(session['new_album_id'])
        user = user_new_album.user
        missions_share = user_new_album.user_missions
        return render_template("congratulation.html",missions_share = missions_share, user=user)
    else:
        return "Error"


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
        # del session['user_id']
        session.clear()
        return redirect(url_for("index"))


if __name__ == '__main__':
  app.run(debug=True)
