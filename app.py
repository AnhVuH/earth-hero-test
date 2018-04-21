from flask import *
import mlab
from random import choice
from models.classes import *
mlab.connect()
app = Flask(__name__)
app.secret_key = 'a-useless-key'


# for i in range(15):
#     new_mission = Missions(missions_name="mission"+ str(i),description="abcxyz" + str(i))
#     new_mission.save()

@app.route('/')
def index():
    return "index"

@app.route("/sign_up", methods= ['GET', 'POST'])
def sign_up():
    if request.method == 'GET':
        if "user_id" not in session:
            return render_template('sign_up.html')
        else:
            return "multi login"
    elif request.method == 'POST':
        form = request.form
        email = form['email']
        username = form['username']
        password = form['password']
        all_missions = list(Missions.objects())
        missions=[]
        for i in range(7):
            mission = choice(all_missions)
            missions.append(mission)
        new_user = User(email = email, username = username, password = password, missions= missions)
        new_user.save()
        session['user_id'] = str(new_user.id)
        return redirect(url_for("user_profile"))


@app.route('/login', methods =['GET', 'POST'])
def login():
    if request.method == 'GET':
        if 'user_id' not in session:
            return render_template('login.html')
        else:
            # return render_template('error.html',error_code = "error_multi_login")
            # return redirect(url_for('index', loged_in = "loged_in"))
            return "multi login"
    elif request.method =='POST':
        form = request.form
        username = form['username']
        password = form['password']
        # If can not get a match object, a exception raise => exception handling
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
    user = User.objects.with_id(session['user_id'])
    mission_number = len(user.missions_done)
    session['mission_number'] = mission_number
    return render_template("user_profile.html", user= user, mission_number = session['mission_number'])

@app.route("/mission_detail")
def mission_detail():
    user = User.objects.with_id(session['user_id'])
    if session['mission_number'] < 7:
        detail = user.missions[session['mission_number']]
        return render_template("mission_detail.html",detail= detail, mission_number = session['mission_number'])
    else:
        return redirect(url_for("congratulation"))


@app.route("/finish",methods= ['GET', 'POST'])
def finish():
    user = User.objects.with_id(session['user_id'])
    if request.method == 'GET':
        if session['mission_number'] == len(user.missions_done):
            return render_template('finish.html')
        else:
            return "can not upload 2 images"
    elif request.method == 'POST':
        form = request.form
        caption = form['caption']
        image = form['image']

        list_missions_done = user.missions_done
        list_missions_done.append(image)

        list_captions = user.captions
        list_captions.append(caption)

        user.update(set__missions_done= list_missions_done, set__captions=list_captions)
        #gửi mail:
        if session['mission_number'] <= 7:
            return redirect(url_for("user_profile"))
        else:
            return redirect(url_for("congratulation"))

@app.route('/congratulation')
def congratulation():
    return render_template("congratulation.html", number_mission = session['mission_number'])

@app.route('/logout')
def logout():
    if 'user_id' in session:
        del session['user_id']
        return 'logout'




if __name__ == '__main__':
  app.run(debug=True)
