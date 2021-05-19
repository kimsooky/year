from flask import Flask,jsonify,make_response,request
from flask_restx import Resource,Api
from security import authenticate, identity
from flask_jwt import JWT,jwt_required
import json
from itertools import islice

app = Flask(__name__)
api = Api(app)
jwt = JWT(app, authenticate, identity)
app.config['BASIC_AUTH_USERNAME'] = 'Admin'
app.config['BASIC_AUTH_PASSWORD'] = 'Admin'


def jsonread() :
    f = open('music.json')
    data_music = json.load(f)
    return data_music


def writejson(music_dict,type):
    music_list = jsonread()
    for key, value in music_list.items(): 
        if type.lower() == key.lower() :
            music_list[key].append(music_dict)
            open_json_file = open('music.json', 'w')
            json.dump(music_list, open_json_file, indent=4) ##สำคัญ
    return 200


def deleteJson(musicname):
    music_list = jsonread()
    response = 0
    for key, value in music_list.items(): 
        count = len(music_list[key])
        for check in range(count): 
            if musicname.lower() in music_list[key][check]['title'].lower() :
                music_list[key].pop(check)
                response = 200
                open_json_file = open('music.json', 'w')
                json.dump(music_list, open_json_file, indent=4)
                break
    if response == 200 : return response
    else : return 500

####################################################################

def updatejson(title,typemusic,new_info):
    music_list = jsonread()
    response = 0
    for key, value in music_list.items(): 
        count = len(music_list[key])
        for check in range(count): 
            if typemusic.lower() == key.lower() :
                if typemusic.lower() == key.lower() :
                    response = 200
                    music_list[key][check].update(new_info)
                    open_json_file = open('music.json', 'w')
                    json.dump(music_list, open_json_file, indent=4) ##สำคัญ
                break
    if response == 200 : return response
    else : return 500

#####################################################################

class video(Resource):
    def get(self):
        music_data = jsonread() #ดึงข้อมูลมาจาก function jsonread
        title = request.args.get('title') #ดึงค่ามาจากที่เขาส่งมา title

        if title != None : #ถ้าเขาส่ง title มาให้เข้าเงื่อนไข
            listcheck = []
            for key, value in music_data.items():
                for check in range(len(music_data[key])): # loop
                    if title.lower() in music_data[key][check]['title'].lower() : #check ค่า
                        addlist = {
                        'title' : music_data[key][check]['title'],
                        'yt_url' : music_data[key][check]['yt_url']
                        }
                        listcheck.append(addlist)
        if (len(listcheck)) != 0: return listcheck,200
        else : return {"message": "Not Found"},500

############################################################################

class Music(Resource):
    def get(self):
        music_data = jsonread() 
        title = request.args.get('title') 
        artist = request.args.get('artist')
        #None not in (title,artist)
        if all(v is not  None for v in [title,artist])  : 
            listcheck = []
            for key, value in music_data.items():
                for check in range(len(music_data[key])):
                    if title.lower() in music_data[key][check]['title'].lower() and artist.lower() in music_data[key][check]['artist'].lower() : #check ค่า
                        addlist = {
                        'title' : music_data[key][check]['title'],
                        'artist' : music_data[key][check]['artist']
                    }
                    listcheck.append(addlist)
            if len(listcheck) != 0: return listcheck,200
            else : return {"message": "Not Found"},500
        else : return {"message": "Missing parameter"},500


################################################################################


class lyrics(Resource):
    def get(self):
        music_data = jsonread() 
        title = request.args.get('title') 
        artist = request.args.get('artist')
        #None not in (title,artist)
        if title != None and artist == None: 
            listcheck = []
            for key, value in music_data.items():
                for check in range(len(music_data[key])):
                    if title.lower() in music_data[key][check]['title'].lower() : #check ค่า
                        addlist = {
                        'title' : music_data[key][check][check]['title'],
                        'artist' : music_data[key][check][check]['artist'],
                        'web_url' : music_data[key][check][check]['web_url']
                    }
                    listcheck.append(addlist)
            if len(listcheck) != 0: return listcheck,200
            else : return {"message": "Not Found"},500
        elif  title == None and artist != None: 
            listcheck = []
            for key, value in music_data.items():
                for check in range(len(music_data[key])):
                    if title.lower() in music_data[key][check]['artist'].lower() : #check ค่า
                        addlist = {
                        'title' : music_data[key][check]['title'],
                        'artist' : music_data[key][check]['artist'],
                        'web_url' : music_data[key][check]['web_url']
                    }
                    listcheck.append(addlist)
            if len(listcheck) != 0: return listcheck,200
            else : return {"message": "Not Found"},500
        elif  title != None and artist != None: 
            listcheck = []
            for key, value in music_data.items():
                for check in range(len(music_data[key])):
                    if title.lower() in music_data[key][check]['title'].lower() and artist.lower() in music_data[key][check]['artist'].lower() : #check ค่า
                        addlist = {
                        'title' : music_data[key][check]['title'],
                        'artist' : music_data[key][check]['artist'],
                        'web_url' : music_data[key][check]['web_url']
                    }
                    listcheck.append(addlist)
            if len(listcheck) != 0: return listcheck,200
            else : return {"message": "Not Found"},500
        else : return {"message": "Missing parameter"},500



#######################################################################################################


class songpost(Resource):
    def post(self,type):
        print(type)
        print(request.get_json())
        status = writejson(request.get_json(),type)
        if status == 200:
            return {"message":"Music has been added."}, 200
        elif status == 404:
            {"message": "มีข้อมูลอยู่แล้ว."}, 404

class song(Resource):
    
    def delete(self,title): #รับ DELETE
        status = deleteJson(title)
        if status == 200:
            return {"message":"Music has been deleted."}, 200
        elif status == 500:
            return {"message":title+" not found."}, 500


class songput(Resource):
    def put(self,type,title):#รับ PUT
        music_dict = api.payload
        status = updatejson(title,type,music_dict)
        if status == 200:
            return {
                "message":"Music HAS BEEN UPDATED."
                }, 200
        elif status == 500:
            return {"message": "FAIL TO UPDATED."}, 500



#############################################################################################

api.add_resource(lyrics,'/lyrics')
api.add_resource(song,'/song/<title>')
api.add_resource(songpost,'/song/<type>')
api.add_resource(songput,'/song/<type>/<title>')
api.add_resource(video,'/video')
api.add_resource(Music,'/music')