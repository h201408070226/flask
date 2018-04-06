#encoding=utf8
from flask import render_template, redirect, url_for, abort, flash,jsonify, request
from werkzeug import secure_filename
from random import choice
from flask_login import login_required, current_user
from . import main
from .forms import EditProfileForm, EditProfileAdminForm,ShowForm,CreateNewFlavorForm,CreateNewImageForm,CreateNewServer
from .. import db
from ..models import Role, User,Permission,User_for_Server
from ..decorators import admin_required,permission_required
import requests
import urllib2
import json

@main.route('/sdsf')
def index():
    return render_template('index.html')


@main.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('user.html', user=user)


@main.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        db.session.add(current_user)
        flash('Your profile has been updated.')
        return redirect(url_for('.user', username=current_user.username))
    form.name.data = current_user.name
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', form=form)


@main.route('/edit-profile/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_profile_admin(id):
    user = User.query.get_or_404(id)
    form = EditProfileAdminForm(user=user)
    if form.validate_on_submit():
        user.email = form.email.data
        user.username = form.username.data
        user.confirmed = form.confirmed.data
        user.role = Role.query.get(form.role.data)
        user.name = form.name.data
        user.location = form.location.data
        user.about_me = form.about_me.data
        db.session.add(user)
        flash('The profile has been updated.')
        return redirect(url_for('.user', username=user.username))
    form.email.data = user.email
    form.username.data = user.username
    form.confirmed.data = user.confirmed
    form.role.data = user.role_id
    form.name.data = user.name
    form.location.data = user.location
    form.about_me.data = user.about_me
    return render_template('edit_profile.html', form=form, user=user)


###################################################keystone的范围#####################################
#获取token
@main.route("/getToken/<user>",methods=['POST','GET'])
# @login_required
def getToken(user):
    baseurl="http://192.168.188.132:35357/v3/auth/tokens"
    values={
    "auth": {
        "identity": {
            "methods": [
                "password"
            ],
            "password": {
                "user": {
                        "domain":{
                                "name":"default"
                        },
                        "name": user,
                        "password": user
                }
            }
        },
        "scope": {
            "project": {
                "domain":{
                        "name":"default"
                },
                "name": user
            }
        }
    }
 }
    parmas=json.dumps(values)
    print parmas
    headers={"Content-Type":"application/json","Accept":"application/json"}
    req=urllib2.Request(baseurl,parmas,headers)
    response=urllib2.urlopen(req)
    #getImageList(response.headers['X-Subject-Token'])
    return response.headers['X-Subject-Token']


##################################glance的范围#################################################
#获取images
@main.route("/GetImageList")
# @login_required
def getImageList():
    # Token=getToken('admin')
    data = []
    d = {}
    # baseurl="http://192.168.188.132:9292/v2/images"
    # headers={"Content-Type":"application/json","Accept":"application/json","X-Auth-Token":Token}
    # req=urllib2.Request(baseurl)
    # req.add_header("Content-Type","application/json")
    # req.add_header("Accept", "application/json")
    # req.add_header("X-Auth-Token", Token)
    # response=urllib2.urlopen(req)
    # json1=response.read()
    # List1=json1['images']
    # for list in List1:
    #     d["ImageID"]=list["ImageID"]
    #     d["ImageName"]=list["ImageName"]
    #     d["status"]=list["status"]
    #     d["size"]=list["size"]
    #     d["disk_format"] = list["disk_format"]
    #     d["owner"] = list["owner"]
    #     d["visibility"] = list["visibility"]
    #     data.append(d)
    data=[{'status': 'active', 'disk_format': 'qcow2', 'visibility': 'private', 'ImageID': 'b2173dd3-7ad6-4362-baa6-a68bce3565cc', 'ImageName': 'cirros', 'owner': '1c9f71edc1304c1ca6754af18f9ac30d', 'size': 12716032}, {'status': 'queued', 'disk_format': 'raw', 'visibility': 'private', 'ImageID': 'b2173dd3-7ad6-4362-baa6-a68bce3565cb', 'ImageName': 'Ubuntu', 'owner': '1c9f71edc1304c1ca6754af18f9ac30d', 'size': 'null'}, {'status': 'active', 'disk_format': 'qcow2', 'visibility': 'public', 'ImageID': '4535270a-4e39-42f9-9612-3eabcb5fabf9', 'ImageName': 'cirros', 'owner': '1c9f71edc1304c1ca6754af18f9ac30d', 'size': 13287936}]

    if request.method == 'GET':
        info = request.values
        limit = info.get('limit', 10)  # 每页显示的条数
        offset = info.get('offset', 0)  # 分片数，(页码-1)*limit，它表示一段数据的起点
        print('get', limit)
        print('get  offset', offset)
        return jsonify({'total': len(data), 'rows': data[int(offset):(int(offset) + int(limit))]})

@main.route("/ShowImagePage")
def show_image_page():
    return render_template("main/ShowImagePage.html")
@main.route("/getImagedata")
def getImagedata():
    data=[]
    d={
            "ImageID": "b2173dd3-7ad6-4362-baa6-a68bce3565cb",
            "ImageName": "Ubuntu",
            "status": "queued",
            "size": 12716032,
            "disk_format": "qcow2",
            "owner": "1c9f71edc1304c1ca6754af18f9ac30d",
            "visibility": "private",
        }
    data.append(d)
    data=[{'status': 'active', 'disk_format': 'qcow2', 'visibility': 'private', 'ImageID': 'b2173dd3-7ad6-4362-baa6-a68bce3565cc', 'ImageName': 'cirros', 'owner': '1c9f71edc1304c1ca6754af18f9ac30d', 'size': 12716032}, {'status': 'queued', 'disk_format': 'raw', 'visibility': 'private', 'ImageID': 'b2173dd3-7ad6-4362-baa6-a68bce3565cb', 'ImageName': 'Ubuntu', 'owner': '1c9f71edc1304c1ca6754af18f9ac30d', 'size': 'null'}, {'status': 'active', 'disk_format': 'qcow2', 'visibility': 'public', 'ImageID': '4535270a-4e39-42f9-9612-3eabcb5fabf9', 'ImageName': 'cirros', 'owner': '1c9f71edc1304c1ca6754af18f9ac30d', 'size': 13287936}]
    if request.method == 'GET':
        info = request.values
        limit = info.get('limit', 10)  # 每页显示的条数
        offset = info.get('offset', 0)  # 分片数，(页码-1)*limit，它表示一段数据的起点
        print('get', limit)
        print('get  offset', offset)
        return jsonify({'total': len(data), 'rows': data[int(offset):(int(offset) + int(limit))]})

#新建Image
@main.route("/CreateNewImage",methods=['POST','GET'])
# @login_required
# @permission_required(Permission.CREATE_OR_DELETE_IMAGE)
def create_new_image():
    url="http://192.168.188.132:9292/v2/images"
    form=CreateNewImageForm()
    if form.validate_on_submit():
        values = {
            "container_format":form.container_format.data,
            "disk_format":form.disk_format.data,
            "name":form.name.data,
            "id":form.id.data,
            "visibility":form.visibility.data

        }
        parmas = json.dumps(values)
        Token = getToken('admin')
        print Token
        headers = {"Content-Type": "application/json", "Accept": "application/json", "X-Auth-Token": Token}
        request = urllib2.Request(url, parmas, headers)
        response = urllib2.urlopen(request)

        # 用put的方式将我们选中的.img文件添加到Image的file
        data=form.ImageFile.data
        print type(data)
        url2=url+"/"+form.id.data+"/file"
        print url2
        ################################
        #这地方的文件上传还没搞定
        ###############################
        request=urllib2.Request(url2,data=data)
        request.add_header("Content-Type","application/json")
        request.add_header("Accept", "application/json")
        request.add_header("X-Auth-Token", Token)
        request.get_method = lambda: 'PUT'
        response = urllib2.urlopen(request)

        print response.read()
    return render_template("main/CreateNewImage.html", form=form)

#删除Image
@main.route("/DeleteNewImage/<ImageId>",methods=['POST','GET'])
@login_required
@permission_required(Permission.CREATE_OR_DELETE_IMAGE)
def delete_a_inage(ImageId):
    url="http://192.168.188.132:9292/v2/images/"+ImageId
    Token=getToken("admin")#这地方的user值得商榷
    request=urllib2.Request(url)
    request.add_header("X-Auth-Token",Token)
    request.get_method = lambda: 'DELETE'
    response = urllib2.urlopen(request)
    return "已经成功删除了该Image"



##############################################nova的范围##################################
#新建flavor
@main.route("/CreateNewFlavor",methods=['POST','GET'])
@login_required
@admin_required
def create_new_flavor():
    url="http://192.168.188.132:8774/v2.1/flavors"
    form = CreateNewFlavorForm()
    if form.validate_on_submit():
        values={
        "flavor": {
        "name": form.name.data,
        "ram": form.ram.data,
        "vcpus":form.vcpus.data,
        "disk": form.disk.data,
        "id": form.id.data,
        "rxtx_factor": 2.0,
    }
}
        print form.file.data
        parmas=json.dumps(values)
        Token=getToken('admin')
        print Token
        headers = {"Content-Type": "application/json", "Accept": "application/json","X-Auth-Token":Token}
        request=urllib2.Request(url,parmas,headers)
        response=urllib2.urlopen(request)
        print response.read()
    return render_template("main/CreateNewFlavor.html", form=form)

#展示所有的flavor有哪些
@main.route("/Show_All_Flavor")
@login_required
def show_all_flavor():
    url="http://192.168.188.132:8774/v2.1/flavors"
    Token=getToken('admin')
    request=urllib2.Request(url)
    request.add_header("Content-Type","application/json")
    request.add_header("Accept","application/json")
    request.add_header("X-Auth-Token",Token)
    response=urllib2.urlopen(request)
    print response.read()
    return

#展示所有的servers
@main.route('/Show_All_Servers')
@login_required
@permission_required(Permission.SHOW_ERERY_SERVER)
def show_all_servers():
    url="http://192.168.188.132:8774/v2.1/servers"
    Id=User.query.filter_by(name=current_user.__name__).first().id
    ServerList=User_for_Server.query.filter_by(id=Id).ServerID#通过查询User和Server的关系数据库得到当前数据库的Server的ID,从而将这些Server从服务器中取出来
    Token=getToken(user)
    for serverlist in ServerList:
        url2=url+"/"+serverlist
        request = urllib2.Request(url2)
        request.add_header("Content-Type", "application/json")
        request.add_header("Accept", "application/json")
        request.add_header("X-Auth-Token", Token)
        response = urllib2.urlopen(request)
        print response.read()
    return


#新建server
@main.route("/Create_New_Servers")
@login_required
def create_new_servers():
    url="http://192.168.188.132:8774/v2.1/servers"
    Token=getToken()
    form = CreateNewServer()
    if form.validate_on_submit():
        values={
    "server" : {
        "accessIPv4": form.ipv4address.data,
        "accessIPv6": form.ipv6address.data,
        "name" : form.name.data,
        "imageRef" : form.imageRef.data,
        "flavorRef" : form.flavorRef.data,
        "availability_zone": form.availability_zone.data,
        "OS-DCF:diskConfig": form.diskConfig.data,
        "metadata" : {
            "My Server Name" : "Apache1"
        },
        "personality": [
            {
                "path": "/etc/banner.txt",
                "contents": "ICAgICAgDQoiQSBjbG91ZCBkb2VzIG5vdCBrbm93IHdoeSBp dCBtb3ZlcyBpbiBqdXN0IHN1Y2ggYSBkaXJlY3Rpb24gYW5k IGF0IHN1Y2ggYSBzcGVlZC4uLkl0IGZlZWxzIGFuIGltcHVs c2lvbi4uLnRoaXMgaXMgdGhlIHBsYWNlIHRvIGdvIG5vdy4g QnV0IHRoZSBza3kga25vd3MgdGhlIHJlYXNvbnMgYW5kIHRo ZSBwYXR0ZXJucyBiZWhpbmQgYWxsIGNsb3VkcywgYW5kIHlv dSB3aWxsIGtub3csIHRvbywgd2hlbiB5b3UgbGlmdCB5b3Vy c2VsZiBoaWdoIGVub3VnaCB0byBzZWUgYmV5b25kIGhvcml6 b25zLiINCg0KLVJpY2hhcmQgQmFjaA=="
            }
        ],
        "security_groups": [
            {
                "name": form.security_groups.data
            }
        ],
        "user_data" : form.user_data.data
    }
}
        parmas=json.dumps(values)
        headers = {"Content-Type": "application/json", "Accept": "application/json", "X-Auth-Token": Token}
        request = urllib2.Request(url, parmas, headers)
        response = urllib2.urlopen(request)
        print response.read()

    return render_template("main/CreateNewServer.html",form=form)





# @main.route('/jsondata', methods=['POST', 'GET'])
# def infos():
#     """
#      请求的数据源，该函数模拟数据库中存储的数据，返回以下这种数据的列表：
#     {'name': '香蕉', 'id': 1, 'price': '10'}
#     {'name': '苹果', 'id': 2, 'price': '10'}
#     """
#     data = []
#     names = ['香', '草', '瓜', '果', '桃', '梨', '莓', '橘', '蕉', '苹']
#     for i in range(1, 1001):
#         d = {}
#         d['id'] = i
#         d['name'] = choice(names) + choice(names)  # 随机选取汉字并拼接
#         d['price'] = '10'
#         data.append(d)
#     if request.method == 'POST':
#         print('post')
#     if request.method == 'GET':
#         info = request.values
#         limit = info.get('limit', 10)  # 每页显示的条数
#         offset = info.get('offset', 0)  # 分片数，(页码-1)*limit，它表示一段数据的起点
#         print('get', limit)
#         print('get  offset', offset)
#         return jsonify({'total': len(data), 'rows': data[int(offset):(int(offset) + int(limit))]})
#         # 注意total与rows是必须的两个参数，名字不能写错，total是数据的总长度，rows是每页要显示的数据,它是一个列表
#         # 前端根本不需要指定total和rows这俩参数，他们已经封装在了bootstrap table里了
#
#
# @main.route('/')
# def hi():
#     return render_template('test/table-test1.html')