from mongoengine import *


class Missions(Document):
    missions_name = StringField()
    description = StringField()

class User(Document):
    username = StringField(unique=True)
    email = StringField(unique= True)
    password = StringField()
    missions = ListField(ReferenceField(Missions)) #lưu tên các nhiệm vụ
    missions_done = ListField() # lưu ảnh các nhiệm vụ đã hoàn thành
    captions =ListField() #Lưu caption
