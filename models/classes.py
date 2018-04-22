from mongoengine import *


class Missions(Document):
    mission_name = StringField()
    description = StringField()



class User(Document):
    username = StringField(unique=True)
    email = StringField(unique= True)
    password = StringField()
    # missions = ListField(ReferenceField(Missions)) #lưu tên các nhiệm vụ
    # missions_done = ListField() # lưu ảnh các nhiệm vụ đã hoàn thành
    # captions =ListField() #Lưu caption

# document
class UserMission(Document):
    user =  ReferenceField(User)
    mission = ReferenceField(Missions)
    completed = BooleanField()
    image = StringField()
    caption = StringField()
