#encoding=utf8
from flask import render_template, redirect, url_for, abort, flash,jsonify, request,current_app
from werkzeug import secure_filename
from random import choice
from flask_login import login_required, current_user
from . import main
from .forms import EditProfileForm, EditProfileAdminForm,ShowForm,CreateNewFlavorForm,CreateNewImageForm,\
    CreateNewServerForm,TestField,CreateNewKeypairForm,ChangeServerFlavorForm,CreateNewKeypairForm,AddFloatIpForm,\
    AddSecurityGroupForm,DeleteFloatIpForm,DeleteSecurityGroupForm,ChangeAdministrativePasswordForm,\
    CreateServerBackUpForm,CreateServerImageForm,RebootServerForm,RebuildServerForm,ResureServerForm,AddFixedIpForm,\
    DeleteFixedIpForm,CreateNewSecurityGroupsForm,MigrateServerForm,AttachVolumeToServerForm
from .. import db
from ..models import Role, User,Permission,Server_for_User
from ..decorators import admin_required,permission_required
import requests
import os

from .. import photos,text,all_file
import urllib2
import json

@main.route('/')
def index():
    return render_template('index.html')


@main.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('user.html', user=user)

#定义python中的访问
#1：第一种：post方式
def post_url(url,values,headers):
    parmas=json.dumps(values)
    req = urllib2.Request(url, parmas, headers)
    response = urllib2.urlopen(req)
    return response

#2:第二种：get方式
def get_url(url,Token):
    req = urllib2.Request(url)
    req.add_header("Content-Type", "application/json")
    req.add_header("Accept", "application/json")
    req.add_header("X-Auth-Token", Token)
    response = urllib2.urlopen(req)
    return response

#3：第三种：put方式
def put_url(url,data,Token):
    request = urllib2.Request(url, data=data)
    request.add_header("Content-Type", "application/octet-stream")
    request.add_header("Accept", "application/json")
    request.add_header("X-Auth-Token", Token)
    request.get_method = lambda: 'PUT'
    response = urllib2.urlopen(request)
    return response

#4:第四种：delete方式
def delete_url(url,Token):
    request = urllib2.Request(url)
    request.add_header("X-Auth-Token", Token)
    request.get_method = lambda: 'DELETE'
    response = urllib2.urlopen(request)
    return response

#5:：第五种：update方法
def update_url(url,Token):
    request=urllib2.Request(url)
    request.add_header("X-Auth-Token", Token)
    request.get_method = lambda: 'UPDATE'
    response = urllib2.urlopen(request)
    return response

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
@main.route("/getToken/<project>/<user>/<password>",methods=['POST','GET'])
# @login_required
def getToken(project,user,password):
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
                        "password": password
                }
            }
        },
        "scope": {
            "project": {
                "domain":{
                        "name":"default"
                },
                "name": project
            }
        }
    }
 }
    # parmas=json.dumps(values)
    # print parmas
    headers={"Content-Type":"application/json","Accept":"application/json"}
    # req=urllib2.Request(baseurl,parmas,headers)
    # response=urllib2.urlopen(req)
    response=post_url(baseurl,values,headers)
    #getImageList(response.headers['X-Subject-Token'])
    return response.headers['X-Subject-Token']

#在project中新建user
def create_new_user(domainId,projectId,username,password,email,enabled):
    url="http://192.168.188.132:35357/v3/users"
    values={
    "user": {
        "default_project_id": projectId,
        "domain_id": domainId,
        "enabled": enabled,
        "name": username,
        "password": password,
        "email": email
    }
    }

    Token=getToken("admin")
    headers = {"Content-Type": "application/json", "Accept": "application/json", "X-Auth-Token": Token}
    response=json.loads(post_url(url,values,headers).read())
    user=response["user"]
    d={}
    d["project_id"]=user["default_project_id"]
    d["id"]=user["id"]
    return d#将新创建的user的id和project_id传过去便于openstack赋予角色

#将xxproject中的xxuser符为xxrole的角色
def role_user(project_id,user_id,role_id):
    url="http://192.168.188.132:35357/v3/projects/"+project_id+"/users/"+user_id+"/roles/"+role_id
    Token=getToken("admin")
    data=""
    response=put_url(url,data,Token)

#获取当前存在的所有project
def get_project():
    url="http://192.168.188.132:35357/v3/projects"
    Token=getToken("admin")
    response=json.loads(get_url(url,Token).read())
    #解析返回的数据然后返回project列表
    projects=response["projects"]
    d={}
    for project in projects:
        if project["name"]!="service":
            d[project["name"]]=project["id"]
    return d

##################################glance的范围#################################################
#获取images
@main.route("/GetImageList")
# @login_required
def getImageList():
    Token=getToken('admin')
    data = []
    baseurl="http://192.168.188.132:9292/v2/images"
    headers={"Content-Type":"application/json","Accept":"application/json","X-Auth-Token":Token}
    req=urllib2.Request(baseurl)
    req.add_header("Content-Type","application/json")
    req.add_header("Accept", "application/json")
    req.add_header("X-Auth-Token", Token)
    response=urllib2.urlopen(req)
    json1=json.loads(response.read())
    List1=json1['images']
    for list in List1:
        d = {}
        d["ImageID"]=list["id"]
        d["ImageName"]=list["name"]
        d["status"]=list["status"]
        d["size"]=list["size"]
        d["disk_format"] = list["disk_format"]
        d["owner"] = list["owner"]
        d["visibility"] = list["visibility"]
        data.append(d)
    # data=[{'status': 'active', 'disk_format': 'qcow2', 'visibility': 'private', 'ImageID': 'b2173dd3-7ad6-4362-baa6-a68bce3565cc', 'ImageName': 'cirros', 'owner': '1c9f71edc1304c1ca6754af18f9ac30d', 'size': 12716032}, {'status': 'queued', 'disk_format': 'raw', 'visibility': 'private', 'ImageID': 'b2173dd3-7ad6-4362-baa6-a68bce3565cb', 'ImageName': 'Ubuntu', 'owner': '1c9f71edc1304c1ca6754af18f9ac30d', 'size': 'null'}, {'status': 'active', 'disk_format': 'qcow2', 'visibility': 'public', 'ImageID': '4535270a-4e39-42f9-9612-3eabcb5fabf9', 'ImageName': 'cirros', 'owner': '1c9f71edc1304c1ca6754af18f9ac30d', 'size': 13287936}]

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
# @main.route("/getImagedata")
# def getImagedata():
#     data=[]
#     d={
#             "ImageID": "b2173dd3-7ad6-4362-baa6-a68bce3565cb",
#             "ImageName": "Ubuntu",
#             "status": "queued",
#             "size": 12716032,
#             "disk_format": "qcow2",
#             "owner": "1c9f71edc1304c1ca6754af18f9ac30d",
#             "visibility": "private",
#         }
#     data.append(d)
#     data=[{'status': 'active', 'disk_format': 'qcow2', 'visibility': 'private', 'ImageID': 'b2173dd3-7ad6-4362-baa6-a68bce3565cc', 'ImageName': 'cirros', 'owner': '1c9f71edc1304c1ca6754af18f9ac30d', 'size': 12716032}, {'status': 'queued', 'disk_format': 'raw', 'visibility': 'private', 'ImageID': 'b2173dd3-7ad6-4362-baa6-a68bce3565cb', 'ImageName': 'Ubuntu', 'owner': '1c9f71edc1304c1ca6754af18f9ac30d', 'size': 'null'}, {'status': 'active', 'disk_format': 'qcow2', 'visibility': 'public', 'ImageID': '4535270a-4e39-42f9-9612-3eabcb5fabf9', 'ImageName': 'cirros', 'owner': '1c9f71edc1304c1ca6754af18f9ac30d', 'size': 13287936}]
#     if request.method == 'GET':
#         info = request.values
#         limit = info.get('limit', 10)  # 每页显示的条数
#         offset = info.get('offset', 0)  # 分片数，(页码-1)*limit，它表示一段数据的起点
#         print('get', limit)
#         print('get  offset', offset)
#         return jsonify({'total': len(data), 'rows': data[int(offset):(int(offset) + int(limit))]})

#新建Image
@main.route("/CreateNewImage",methods=['POST','GET',"PUT"])
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
        Token = getToken("admin", "admin", "admin")
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
        request.add_header("Content-Type","application/octet-stream")
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

######################################################flavor操作####################################
#新建flavor
@main.route("/CreateNewFlavor",methods=['POST','GET'])
# @login_required
# @admin_required
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

        parmas=json.dumps(values)
        Token=getToken('admin')
        print Token
        headers = {"Content-Type": "application/json", "Accept": "application/json","X-Auth-Token":Token}
        request=urllib2.Request(url,parmas,headers)
        response=urllib2.urlopen(request)
        return redirect("ShowFlavorPage")
    return render_template("main/CreateNewFlavor.html", form=form)

#展示某一个特定的flavor的详细信息
@main.route("/GetFlavor/<flavorid>")
def show_a_flavor_detail(flavorid):
    url = "http://192.168.188.132:8774/v2.1/flavors/"+flavorid
    Token = getToken("admin", "admin", "admin")
    req = urllib2.Request(url)
    req.add_header("Content-Type", "application/json")
    req.add_header("Accept", "application/json")
    req.add_header("X-Auth-Token", Token)
    response = urllib2.urlopen(req)
    flavorsList = json.loads(response.read())["flavors"]


#展示所有的flavor有哪些
@main.route("/ShowFlavorPage")
def show_flavor_page():
    return render_template("main/ShowFlavorPage.html")
#为show_flavor_page提供数据
@main.route("/GetFlavorList")
# @login_required
def show_all_flavor():
    data = []

    # 下面的方法中我们首先通过获取url获取到所有的flavor的id，然后在根据每个id来构造新的url2，
    # 然后获取没有个flavor的Detal，最后将这些信息组织成data返回
    url="http://192.168.188.132:8774/v2.1/flavors"
    Token=getToken('admin',"admin","admin")
    # req=urllib2.Request(url)
    # req.add_header("Content-Type","application/json")
    # req.add_header("Accept","application/json")
    # req.add_header("X-Auth-Token",Token)
    response=get_url(url,Token)

    flavorsList=json.loads(response.read())["flavors"]

    IdList=[]
    for i in range(len(flavorsList)):
        d = {}
        #dict（字典）赋给list的是一个位置，对于第一种代码，dictionary定义在循环外，
        # 每次使用list.append(dictionary)赋给  list的都是相同的位置，而在同一位置的dict的值已经改变了，
        # 所以list取到的之前位置的值改变了，表现出后面数据覆盖前面数据的表象。dict定义在循环内，
        # 相当于每一次循环生成一个dictionary，占用不同的位置存储值，所以可以赋给list不同元素不同的位置，获得不同的值
        id=flavorsList[i]["id"]
        IdList.append(flavorsList[i]["id"])
        url2=url+"/"+id#修改网址为flavors/{flavor_id}，来获取每个flavor的细节
        print url2
        # req = urllib2.Request(url2)
        # req.add_header("Content-Type", "application/json")
        # req.add_header("Accept", "application/json")
        # req.add_header("X-Auth-Token", Token)
        response = get_url(url2,Token)
        flavorDetial=json.loads(response.read())["flavor"]
        d["FlavorID"]=flavorDetial["id"]
        d["FlavorName"]=flavorDetial["name"]
        d["ram"]=flavorDetial["ram"]
        d["vcpus"]=flavorDetial["vcpus"]
        d["disk"]=flavorDetial["disk"]
        d["rxtx_factor"]=flavorDetial["rxtx_factor"]
        data.append(d)
        print data
    # data=[{'FlavorID': '4', 'ram': 200, 'FlavorName': 'flavor2', 'vcpus': 1, 'rxtx_factor': 2, 'disk': 5}]
    # print data

    if request.method == 'GET':
        info = request.values
        limit = info.get('limit', 10)  # 每页显示的条数
        offset = info.get('offset', 0)  # 分片数，(页码-1)*limit，它表示一段数据的起点
        print('get', limit)
        print('get  offset', offset)
        return jsonify({'total': len(data), 'rows': data[int(offset):(int(offset) + int(limit))]})

#为选择框添加提供数据
def get_flavor_name_id():
    data = []
    # 下面的方法中我们首先通过获取url获取到所有的flavor的id，然后在根据每个id来构造新的url2，
    # 然后获取没有个flavor的Detal，最后将这些信息组织成data返回
    url = "http://192.168.188.132:8774/v2.1/flavors"
    Token = getToken("admin", "admin", "admin")
    # req=urllib2.Request(url)
    # req.add_header("Content-Type","application/json")
    # req.add_header("Accept","application/json")
    # req.add_header("X-Auth-Token",Token)
    response = get_url(url, Token)

    flavorsList = json.loads(response.read())["flavors"]

    IdList = []
    for i in range(len(flavorsList)):
        d = {}
        # dict（字典）赋给list的是一个位置，对于第一种代码，dictionary定义在循环外，
        # 每次使用list.append(dictionary)赋给  list的都是相同的位置，而在同一位置的dict的值已经改变了，
        # 所以list取到的之前位置的值改变了，表现出后面数据覆盖前面数据的表象。dict定义在循环内，
        # 相当于每一次循环生成一个dictionary，占用不同的位置存储值，所以可以赋给list不同元素不同的位置，获得不同的值
        d["name"]=flavorsList[i]["name"]
        d["id"]=flavorsList[i]["id"]
        data.append(d)
        print data
    return data
        # data=[{'FlavorID': '4', 'ram': 200, 'FlavorName': 'flavor2', 'vcpus': 1, 'rxtx_factor': 2, 'disk': 5}]
        # print data

#删除某一个flavor
@main.route("/Delete_A_Flavor/<flavor_id>",methods=["DELETE"])
def delete_a_flavor(flavor_id):
    url = "http://192.168.188.132:8774/v2.1/flavors/"+flavor_id
    token=getToken()
    response=delete_url(url,token)
    return render_template("main/ShowFlavorPage.html")


######################################################kypair操作####################################
#显示所有的keypair
@main.route("/ShowKeypairPage")
def show_keypair_page():
    return render_template("main/ShowKeypairPage.html")
#为ShowKeypairPage页面提供数据
@main.route("/GET_All_Keypair")
def get_all_keypair():
    url="http://192.168.188.132:8774/v2.1/os-keypairs"
    ################
    token=getToken("admin","admin","admin")
    ###############token获取未定
    response=json.loads(get_url(url,token).read())
    keypairList=response["keypairs"]
    data=[]
    for keypairDict in keypairList:
        d={}
        keypair=keypairDict["keypair"]
        d["keypair_name"]=keypair["name"]
        # d["type"]=keypair["type"]
        d["public_key"]=keypair["public_key"]
        data.append(d)

    if request.method == 'GET':
        info = request.values
        limit = info.get('limit', 10)  # 每页显示的条数
        offset = info.get('offset', 0)  # 分片数，(页码-1)*limit，它表示一段数据的起点
        print('get', limit)
        print('get  offset', offset)
        return jsonify({'total': len(data), 'rows': data[int(offset):(int(offset) + int(limit))]})

#为选择框提供数据
def get_keypair_name():
    url="http://192.168.188.132:8774/v2.1/os-keypairs"
    ################
    token=getToken()
    ###############token获取未定
    response = json.loads(get_url(url, token).read())
    keypairList=response["keypairs"]
    data=[]
    for keypairDict in keypairList:
        keypair=keypairDict["keypair"]
        data.append(keypair["name"])
    return data#这里提供的是一个关于keypair名字的列表

#新建keypair，keypair是以user为单位建立的
@main.route("/CreateNewKeypair",methods=["POST","GET"])
def create_new_keypair():
    url = "http://192.168.188.132:8774/v2.1/os-keypairs"
    Token=getToken()
    headers={"Content-Type": "application/json", "Accept": "application/json", "X-Auth-Token": Token}
    form=CreateNewKeypairForm()
    if form.validate_on_submit():
        if form.public_key.data != None:
            values={
    "keypair": {
        "name": form.name.data,
        "public_key":form.public_key.data
    }
}
            post_url(url,values,headers)
        else:#当public_key不存在时需要将自动生成的public_key和private_key保存起来
            values = {
                "keypair": {
                    "name": form.name.data,
                }
            }
            response = json.loads(post_url(url, values, headers).read())
            keypairDict=response["keypair"]
            public_keyString=keypairDict["public_key"]
            private_keyString=keypairDict["private_key"]
            ##############在file中新建文件夹名字为keypair名字并将private_key和public_key保存在文件夹中#####
            filepath=current_app.config["UPLOADED_ALLFILE_DEST"]+form.name.data
            isExit=os.path.exists()
            if not isExit:
                os.mkdir(filepath)
                public_key_file_path=filepath+"/id_rsa.pub"
                private_key_file_path = filepath + "/id_rsa"
                private_key_file=open(private_key_file_path)
                private_key_file.write(private_keyString)
                private_key_file.close()
                public_key_file=open(public_key_file_path)
                public_key_file.write(public_keyString)
                public_key_file.close()
        return render_template("main/ShowKeypairPage.html")
    return render_template("main/CreateNewKeypair.html",form=form)

#删除特定的keypair
@main.route("/Delete_A_Keypair/<keypair_name>",methods=["DELETE"])
def delete_a_keypair(keypair_name):
    url="http://192.168.188.132:8774/v2.1/os-keypairs/"+keypair_name
    token=getToken()
    delete_url(url,token)
    return render_template("main/ShowKeypairPage.html")

######################################################security-groups操作####################################
#新建安全组
@main.route("/CreateNewSecurityGroup",methods=["POST","GET"])
def create_new_security_groups():
    url="http://192.168.188.132:8774/v2.1/os-security-groups"
    Token=getToken()
    form=CreateNewSecurityGroupsForm()
    headers={"Content-Type": "application/json", "Accept": "application/json", "X-Auth-Token": Token}
    if form.validate_on_submit():
        values={
    "security_group": {
        "name": form.name.data,
        "description": form.description.data
    }
}
        return render_template("main/ShowSecurityGroupsPage.html")
    return render_template("main/CreateNewSecurityGroups.html",form=form)

#显示全部的安全组的情况
@main.route("/ShowAllSecurityGroups")
def show_all_security_groups():
    return render_template("main/ShowSecurityGroupsPage.html")
#为显示提供数据
@main.route("/GetSecurityGroupsList")
def get_all_security_groups():
    url = "http://192.168.188.132:8774/v2.1/os-security-groups"
    Token = getToken("admin", "admin", "admin")
    response=json.loads(get_url(url,Token).read())
    security_groups_List=response["security_groups"]
    data=[]
    for security_groups in security_groups_List:
        d={}
        d["id"]=security_groups["id"]
        d["name"]=security_groups["name"]
        d["description"]=security_groups["description"]
        d["tenant_id"]=security_groups["tenant_id"]
        message="<ul><li>"
        for rule in security_groups["rules"]:
            message+=rule["id"]
            message+="</li><li>"
        message+="</li></ul>"
        d["rules"]=message
        data.append(d)
    if request.method == 'GET':
        info = request.values
        limit = info.get('limit', 10)  # 每页显示的条数
        offset = info.get('offset', 0)  # 分片数，(页码-1)*limit，它表示一段数据的起点
        print('get', limit)
        print('get  offset', offset)
        return jsonify({'total': len(data), 'rows': data[int(offset):(int(offset) + int(limit))]})
#为选择安全组提供基本的参数
def get_security_groups_name_id():
    url = "http://192.168.188.132:8774/v2.1/os-security-groups"
    Token = getToken("admin", "admin", "admin")
    response = json.loads(get_url(url, Token).read())
    security_groups_List = response["security_groups"]
    data = []
    for security_groups in security_groups_List:
        d={}
        d["id"]=security_groups["id"]
        d["name"]=security_groups["name"]
        data.append(d)
    return data
#删除某一个安全组
def delete_a_security_groups(security_groups_id):
    url="http://192.168.188.132:8774/v2.1/os-security-groups/"+security_groups_id
    Token=getToken()
    delete_url(url,Token)
    return render_template("main/ShowSecurityGroupsPage.html")

#新建安全组规则
def create_new_roule_for_security_group(security_groups_id):
    url=url="http://192.168.188.132:9696/v2.0/os-security-group-rules"


###################################################关于cinder的虚拟机操作#################################
#为虚拟机添加卷
def attach_volume_to_server(server_id):
    url = "http://192.168.188.132:8774/v2.1/"+server_id+"/os-security-groups"
    Token=getToken("admin","admin","admin")
    form=AttachVolumeToServerForm()
    name="为虚拟机添加卷"
    data=get_volumelist()##########这个函数还没写
    form.volumeId.choices=[(d["id"],d["name"]) for d in data]
    if form.validate_on_submit():
        values={
    "volumeAttachment": {
        "volumeId": form.volumeId.data,
        "device": form.device.data
    }
}
        headers = {"Content-Type": "application/json", "Accept": "application/json", "X-Auth-Token": Token}
        post_url(url,values,headers)
        return redirect(url_for("main.show_server_detial",server_id=server_id))
    return render_template("main/ServerAction.html",name=name,form=form)

######################################################service操作####################################
#诊断虚拟机
def show_server_diagnostics(server_id):
    url="http://192.168.188.132:8774/v2.1/servers/"+server_id+"/diagnostics"
    Token=getToken()
    response=json.loads(get_url(url,Token).read())
    #########这里进行数据的处理和显示##########

#展示虚拟机的详细信息
@main.route("/Show_Server_Detial/<server_id>")
def show_server_detial(server_id):
    return render_template("main/ShowServerDetialPage.html",server_id=server_id)
#为虚拟机的详细信息提供数据
@main.route("/GetServerList/<server_id>")
def get_server_list(server_id):
    url="http://192.168.188.132:8774/v2.1/servers/"+server_id
    Token=getToken("admin","admin","admin")
    # response=json.loads(get_url(url,Token).read())
    ###########这里使用的指定的数据，后面在测试#########
    response={
    "server": {
        "OS-DCF:diskConfig": "AUTO",
        "OS-EXT-AZ:availability_zone": "nova",
        "OS-EXT-SRV-ATTR:host": "compute",
        "OS-EXT-SRV-ATTR:hostname": "new-server-test",
        "OS-EXT-SRV-ATTR:hypervisor_hostname": "fake-mini",
        "OS-EXT-SRV-ATTR:instance_name": "instance-00000001",
        "OS-EXT-SRV-ATTR:kernel_id": "",
        "OS-EXT-SRV-ATTR:launch_index": 0,
        "OS-EXT-SRV-ATTR:ramdisk_id": "",
        "OS-EXT-SRV-ATTR:reservation_id": "r-ov3q80zj",
        "OS-EXT-SRV-ATTR:root_device_name": "/dev/sda",
        "OS-EXT-SRV-ATTR:user_data": "IyEvYmluL2Jhc2gKL2Jpbi9zdQplY2hvICJJIGFtIGluIHlvdSEiCg==",
        "OS-EXT-STS:power_state": 1,
        "OS-EXT-STS:task_state": "null",
        "OS-EXT-STS:vm_state": "active",
        "OS-SRV-USG:launched_at": "2017-02-14T19:23:59.895661",
        "OS-SRV-USG:terminated_at": "null",
        "accessIPv4": "1.2.3.4",
        "accessIPv6": "80fe::",
        "addresses": {
            "private": [
                {
                    "OS-EXT-IPS-MAC:mac_addr": "aa:bb:cc:dd:ee:ff",
                    "OS-EXT-IPS:type": "fixed",
                    "addr": "192.168.0.3",
                    "version": 4
                }
            ]
        },
        "config_drive": "",
        "created": "2017-02-14T19:23:58Z",
        "description": "null",
        "flavor": {
            "disk": 1,
            "ephemeral": 0,
            "extra_specs": {
                "hw:cpu_model": "SandyBridge",
                "hw:mem_page_size": "2048",
                "hw:cpu_policy": "dedicated"
            },
            "original_name": "m1.tiny.specs",
            "ram": 512,
            "swap": 0,
            "vcpus": 1
        },
        "hostId": "2091634baaccdc4c5a1d57069c833e402921df696b7f970791b12ec6",
        "host_status": "UP",
        "id": "9168b536-cd40-4630-b43f-b259807c6e87",
        "image": {
            "id": "70a599e0-31e7-49b7-b260-868f441e862b",
            "links": [
                {
                    "href": "http://openstack.example.com/6f70656e737461636b20342065766572/images/70a599e0-31e7-49b7-b260-868f441e862b",
                    "rel": "bookmark"
                }
            ]
        },
        "key_name": "null",
        "links": [
            {
                "href": "http://openstack.example.com/v2.1/6f70656e737461636b20342065766572/servers/9168b536-cd40-4630-b43f-b259807c6e87",
                "rel": "self"
            },
            {
                "href": "http://openstack.example.com/6f70656e737461636b20342065766572/servers/9168b536-cd40-4630-b43f-b259807c6e87",
                "rel": "bookmark"
            }
        ],
        "locked": "false",
        "metadata": {
            "My Server Name": "Apache1"
        },
        "name": "new-server-test",
        "os-extended-volumes:volumes_attached": [
            {
                "delete_on_termination": "false",
                "id": "volume_id1"
            },
            {
                "delete_on_termination": "false",
                "id": "volume_id2"
            }
        ],
        "progress": 0,
        "security_groups": [
            {
                "name": "default"
            }
        ],
        "status": "ACTIVE",
        "tags": [],
        "tenant_id": "6f70656e737461636b20342065766572",
        "updated": "2017-02-14T19:24:00Z",
        "user_id": "fake"
    }
}
    response=json.loads(get_url(url,Token).read())
    server=response["server"]
    data=[]
    d={}
    d["title"]=u"名称"
    d["message"]=server["name"]
    data.append(d)
    d={}
    d["title"]=u"状态"
    if server["status"]=="ACTIVE":
        d["message"]='<h4 style="color:green">ACTIVE</h4>'
        data.append(d)
    elif server["status"]=="ERROR" or server["status"]=="DELETED ":
        d["message"] = '<h4 style="color:red">' + d["status"] + '</h4>'
        data.append(d)
        d2={}
        d2["title"]=u"错误详情"
        fault=server["fault"]
        fault_message="<ul>" \
                      "<li>错误码:"+fault["code"]+"</li>" \
                      "<li>时间:"+fault["created"]+"</li>" \
                      "<li>错误信息:"+fault["message"]+"</li>" \
                      "</ul>"
        d2["message"]=fault_message
        data.append(d2)
    else:
        d["message"] = '<h4 style="background-color:red">'+d["status"]+'</h4>'
        data.append(d)
    d={}
    d["title"]=u"可用域"
    d["message"]="<ul><li>"+server["OS-EXT-AZ:availability_zone"]+"</li></ul>"
    data.append(d)

    d={}
    d["title"]=u"主机信息"
    d["message"]="<ul>" \
                 "<li>主机名称:"+server["OS-EXT-SRV-ATTR:host"]+"</li>" \
                 "<li>主机id:"+server["hostId"]+"</li>" \
                 "</ul>"
    data.append(d)
    d={}
    d["title"]=u"主机类型详细信息"
    flavorid=server["flavor"]["id"]
    url2="http://192.168.188.132:8774/v2.1/flavors/"+flavorid
    print url2
    flavor=json.loads(get_url(url2,Token).read())["flavor"]
    print flavor
    flavor_message="<ul>" \
                   "<li>名称:"+flavor["name"]+"</li>" \
                   "<li>虚拟cpu数量:"+str(flavor["vcpus"])+"</li>" \
                   "<li>虚拟内存数量:"+str(flavor["ram"])+"</li>" \
                   "</ul>" \
                   "<h4>磁盘详情</h4>" \
                   "<ul>" \
                    "<li>磁盘结构:" + server["OS-DCF:diskConfig"] + "</li>" \
                    "<li>根磁盘大小:"+str(flavor["disk"])+"GB</li>" \
                    "<li>临时磁盘大小:"+str(flavor["OS-FLV-EXT-DATA:ephemeral"])+"GB</li>" \
                    "<li>交换磁盘大小:"+str(flavor["swap"])+"MB</li>" \
                    "</ul>"
    d["message"]=flavor_message
    data.append(d)
    d={}
    d["title"]=u"镜像详情"
    image=server["image"]
    image_message="<ul><li>ID:"+image["id"]+"</li></ul>"
    d["message"]=image_message
    data.append(d)
    d={}
    d["title"]=u"安全组"
    security_groups_list=server["security_groups"]
    security_groups_message="<ul>"
    for i in range(len(security_groups_list)):
        security_groups_message+="<li>安全组"+str(i+1)+":"+security_groups_list[i]["name"]+"</li>"
    security_groups_message+="</ul>"
    d["message"]=security_groups_message
    data.append(d)

    if request.method == 'GET':
        info = request.values
        limit = info.get('limit', 10)  # 每页显示的条数
        offset = info.get('offset', 0)  # 分片数，(页码-1)*limit，它表示一段数据的起点
        print('get', limit)
        print('get  offset', offset)
        return jsonify({'total': len(data), 'rows': data[int(offset):(int(offset) + int(limit))]})

#展示所有的servers
@main.route('/Show_All_Servers')
# @login_required
# @permission_required(Permission.SHOW_ERERY_SERVER)
def show_all_servers():
    return render_template("main/ShowAllServerPage.html")
#为展示所有的server提供数据
@main.route("/GetAllServerList")
def get_all_server_data():
    data=[]
    url="http://192.168.188.132:8774/v2.1/servers/detail"
    # Id=User.query.filter_by(username=current_user.username).first().id
    # ServerList=User_for_Server.query.filter_by(id=Id).ServerID
    #通过查询User和Server的关系数据库得到当前数据库的Server的ID,从而将这些Server从服务器中取出来
    Token=getToken("admin","admin","admin")
    # for serverlist in ServerList:

    values ={
    "servers": [
        {
            "id": "22c91117-08de-4894-9aa9-6ef382400985",
            "links": [
                {
                    "href": "http://openstack.example.com/v2/6f70656e737461636b20342065766572/servers/22c91117-08de-4894-9aa9-6ef382400985",
                    "rel": "self"
                },
                {
                    "href": "http://openstack.example.com/6f70656e737461636b20342065766572/servers/22c91117-08de-4894-9aa9-6ef382400985",
                    "rel": "bookmark"
                }
            ],
            "name": "new-server-test"
        }
    ]
}
    # url2=url+"/"+serverlist
    # request = urllib2.Request(url2)
    # request.add_header("Content-Type", "application/json")
    # request.add_header("Accept", "application/json")
    # request.add_header("X-Auth-Token", Token)
    # response = urllib2.urlopen(request)
    values=json.loads(get_url(url,Token).read())
    ServersList=values["servers"]
    for server in ServersList:
        d={}
        d["ServerName"]=server["name"]
        d["ServerID"]=server["id"]
        if server["status"]=="ACTIVE":
            status_message='<h5 style="color:green">ACTIVE</h4>'
        elif server["status"]=="ERROR" or server["status"]=="DELETE":
            status_message='<h5 style="color:red">'+server["status"]+'</h4>'
        else:
            status_message = '<h5 style="color:Gainsboro">' + server["status"] + '</h4>'

        d["status"]=status_message
        power_state={
            0: "NOSTATE",
            1: "RUNNING",
            3: "PAUSED",
            4: "SHUTDOWN",
            6: "CRASHED",
            7: "SUSPENDED"
        }
        d["power"]=power_state[server["OS-EXT-STS:power_state"]]
        d["host"]=server["OS-EXT-SRV-ATTR:hypervisor_hostname"]
        # '<option value="' + 'create_new_server_image|' + d[ "ServerID"] + '" >新建虚拟机备份</option>' \  '<option value="' + 'suspend_server|' + d["ServerID"] + '" >挂起虚拟机</option>' \
        actionMessage='<select style="height:25px;width:160px;" onchange="actions(this)">  ' \
                      '<option value="menu" selected>action</option> ' \
                      '<option value="'+'show_server_detial|'+d["ServerID"]+'">查看虚拟机详情</option> ' \
                      '<option value="'+'add_float_ip|'+d["ServerID"]+'" >添加浮动ip</option>' \
                      '<option value="'+'delte_float_ip|'+d["ServerID"]+'" >删除浮动ip</option>' \
                      '<option value="' + 'Add_security_group|' + d[ "ServerID"] + '" >添加安全组</option>' \
                      '<option value="' + 'delete_secuity_group|' + d[ "ServerID"] + '" >删除安全组</option>' \
                      '<option value="' + 'change_server_password|' + d[ "ServerID"] + '" >修改虚拟机密码</option>' \
                      '<option value="' + 'create_server_image|' + d[ "ServerID"] + '" >将虚拟机做成镜像</option>' \
                      '<option value="' + 'lock_server|' + d["ServerID"] + '" >锁定虚拟机</option>' \
                      '<option value="' + 'pause_server|' + d["ServerID"] + '" >暂停虚拟机</option>' \
                      '<option value="' + 'reboot_server|' + d["ServerID"] + '" >重启虚拟机</option>' \
                      '<option value="' + 'rebuild_server|' + d["ServerID"] + '" >重构虚拟机</option>' \
                      '<option value="' + 'resure_server|' + d["ServerID"] + '" >救援虚拟机</option>' \
                      '<option value="' + 'resize_server|' + d["ServerID"] + '" >更改虚拟机规格</option>' \
                      '<option value="' + 'resume_server|' + d["ServerID"] + '" >恢复虚拟机运行</option>' \
                      '<option value="' + 'revert_resize_server|' + d["ServerID"] + '" >恢复虚拟机规格修改</option>' \
                      '<option value="' + 'start_server|' + d["ServerID"] + '" >启动虚拟机</option>' \
                      '<option value="' + 'stop_server|' + d["ServerID"] + '" >停止虚拟机</option>' \
                      '<option value="' + 'unlock_server|' + d["ServerID"] + '" >解锁虚拟机</option>' \
                      '<option value="' + 'unpause_server|' + d["ServerID"] + '" >解除暂停虚拟机</option>' \
                      '<option value="' + 'add_fixed_ip_server|' + d["ServerID"] + '" >添加固定ip</option>' \
                      '<option value="' + 'delete_fixed_ip_server|' + d["ServerID"] + '" >删除固定ip</option>' \
                      '<option value="' + 'create_new_backup|' + d[ "ServerID"] + '" >新建虚拟机备份</option>' \
                      '<option value="' + 'suspend_server|' + d[ "ServerID"] + '" >挂起虚拟机</option>' \
                       '</select>'
        actionMessage2='<select style="height:25px;width:160px;" onchange="actions(this)">  ' \
                      '<option value="menu" selected>action</option> ' \
                      '<option value="'+'show_server_detial|'+d["ServerID"]+'">查看虚拟机详情</option> ' \
                      '</select>'
        if server["OS-EXT-STS:vm_state"] == "ERROR" or server["OS-EXT-STS:vm_state"] =="DELETED" :
            d["actions"] = actionMessage2
        else:
            d["actions"] = actionMessage

        data.append(d)

    if request.method == 'GET':
        info = request.values
        limit = info.get('limit', 10)  # 每页显示的条数
        offset = info.get('offset', 0)  # 分片数，(页码-1)*limit，它表示一段数据的起点
        print('get', limit)
        print('get  offset', offset)
        return jsonify({'total': len(data), 'rows': data[int(offset):(int(offset) + int(limit))]})



#新建server
@main.route("/Create_New_Servers",methods=["GET","POST"])
# @login_required
def create_new_servers():
    url="http://192.168.188.132:8774/v2.1/servers"
    Token=getToken("admin","admin","admin")
    form = CreateNewServerForm()
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

        headers = {"Content-Type": "application/json", "Accept": "application/json", "X-Auth-Token": Token}
        response = post_url(url,values,headers)
        result=json.loads(response.read())
        ServerId=result["server"]["id"]
        #将用户id和server的id存储在一个数据库中，每次我们查询的时候只能取得的是当前用户所拥有的server
        server_user=Server_for_User(UserID=current_user.id,ServerID=ServerId)
        db.session.add(server_user)
        db.session.commit()
    return render_template("main/CreateNewServer.html",form=form)

# #更新更改虚拟机规格
# @main.route("/ResizeServer/<serverId>",methods=["POST","GET"])
# def resize_server(serverId):
#     form=ResizeServerForm()
#     form.selectFlavor.choices=[("0","没事"),("26","问题"),("28","答案")]
#     if form.validate_on_submit():
#         print form.selectFlavor.data
#     return render_template("main/TestFile.html",form=form)

#删除指定的server
@main.route("/DeleteAServer/<ServerId>",methods=["DELETE"])
def delete_a_server(ServerId):
    url = "http://192.168.188.132:8774/v2.1/servers/"+ServerId
    Token = getToken("admin","admin","admin")
    delete_url(url,Token)
    return render_template("main/ShowAllServerPage.html")


###############################下面是主要的关于server的操作##############
#添加浮动ip
@main.route("/Add_Float_Ip/<server_id>",methods=["POST","GET"])
def add_float_ip(server_id):
    url="http://192.168.188.132:8774/v2.1/servers/"+server_id+"/action"
    Token = getToken("admin", "admin", "admin")
    headers= headers = {"Content-Type": "application/json", "Accept": "application/json", "X-Auth-Token": Token}
    form=AddFloatIpForm()
    name=u"添加浮动ip"
    if form.validate_on_submit():
        values={
    "addFloatingIp" : {
        "address": form.address.data,
        "fixed_address": form.fixed_address.data
    }
}
        post_url(url,values,headers)
        return redirect(url_for("main.show_all_servers"))
    return render_template("main/ServerAction.html",form=form,name=name)

#删除浮动ip
@main.route("/Delete_Float_Ip/<server_id>",methods=["POST","GET"])
def delte_float_ip(server_id):
    url = "http://192.168.188.132:8774/v2.1/servers/" + server_id + "/action"
    Token = getToken("admin", "admin", "admin")
    headers = headers = {"Content-Type": "application/json", "Accept": "application/json", "X-Auth-Token": Token}
    form = DeleteFloatIpForm()
    name=u"删除浮动ip"
    if form.validate_on_submit():
        values = {
            "removeFloatingIp": {
                "address": form.address.data,
            }
        }
        post_url(url, values, headers)
        return redirect(url_for("main.show_all_servers"))
    return render_template("main/ServerAction.html", form=form, name=name)

#添加安全组
@main.route("/Add_Security_Group/<server_id>",methods=["POST","GET"])
def Add_security_group(server_id):
    url = "http://192.168.188.132:8774/v2.1/servers/" + server_id + "/action"
    Token = getToken("admin", "admin", "admin")
    headers = headers = {"Content-Type": "application/json", "Accept": "application/json", "X-Auth-Token": Token}
    form = AddSecurityGroupForm()
    data=get_security_groups_name_id()
    print data
    form.name.choices=[(d["name"],d["name"]) for d in data]
    name=u"添加安全组"
    if form.validate_on_submit():
        values = {
    "addSecurityGroup": {
        "name": form.name.data
    }
}
        post_url(url, values, headers)
        return redirect(url_for("main.show_all_servers"))
    return render_template("main/ServerAction.html", form=form, name=name)

#删除安全组
@main.route("/Delete_Security_Group/<server_id>",methods=["POST","GET"])
def delete_secuity_group(server_id):
    url = "http://192.168.188.132:8774/v2.1/servers/" + server_id + "/action"
    Token = getToken("admin", "admin", "admin")
    headers = headers = {"Content-Type": "application/json", "Accept": "application/json", "X-Auth-Token": Token}
    form = DeleteSecurityGroupForm()
    name=u"删除安全组"
    if form.validate_on_submit():
        values = {
            "removeSecurityGroup": {
                "name": form.name.data
            }
        }
        post_url(url, values, headers)
        return redirect(url_for("main.show_all_servers"))
    return render_template("main/ServerAction.html", form=form, name=name)

#修改虚拟机密码
@main.route("/Change_Server_Password/<server_id>",methods=["POST","GET"])
def change_server_password(server_id):
    url = "http://192.168.188.132:8774/v2.1/servers/" + server_id + "/action"
    Token = getToken("admin", "admin", "admin")
    headers = headers = {"Content-Type": "application/json", "Accept": "application/json", "X-Auth-Token": Token}
    form = ChangeAdministrativePasswordForm()
    name=u"修改虚拟机密码"
    if form.validate_on_submit():
        values = {
    "changePassword" : {
        "adminPass" : form.password.data
    }
}
        post_url(url, values, headers)
        return redirect(url_for("main.show_all_servers"))
    return render_template("main/ServerAction.html", form=form, name=name)

#新建虚拟机备份
@main.route("/Create_New_Backup/<server_id>",methods=["POST","GET"])
def create_new_backup(server_id):
    url = "http://192.168.188.132:8774/v2.1/servers/" + server_id + "/action"
    Token = getToken("admin", "admin", "admin")
    headers = headers = {"Content-Type": "application/json", "Accept": "application/json", "X-Auth-Token": Token}
    form = CreateServerBackUpForm()
    name=u"新建虚拟机备份"
    if form.validate_on_submit():
        values = {
    "createBackup": {
        "name": form.name.data,
        "backup_type": form.backup_type.data
    }
}
        post_url(url, values, headers)
        return redirect(url_for("main.show_all_servers"))##应该修改成查看备份详情
    return render_template("main/ServerAction.html", form=form, name=name)

#将虚拟机做成镜像
@main.route("/Create_Server_Image/<server_id>",methods=["POST","GET"])
def create_server_image(server_id):
    url = "http://192.168.188.132:8774/v2.1/servers/" + server_id + "/action"
    Token = getToken("admin", "admin", "admin")
    headers = headers = {"Content-Type": "application/json", "Accept": "application/json", "X-Auth-Token": Token}
    form = CreateServerImageForm()
    name=u"将虚拟机做成镜像"
    if form.validate_on_submit():
        values = {
    "createImage" : {
        "name" : form.name.data,
        "metadata": {
            form.metadata_key.data: form.metadata_value.data
        }
    }
}
        post_url(url, values, headers)
        return redirect(url_for("main.show_all_servers"))##应该修改成查看镜像详情
    return render_template("main/ServerAction.html", form=form, name=name)

#锁定虚拟机
@main.route("/Lock_Server/<server_id>",methods=["POST","GET"])
def lock_server(server_id):
    url = "http://192.168.188.132:8774/v2.1/servers/" + server_id + "/action"
    Token = getToken("admin", "admin", "admin")
    headers = headers = {"Content-Type": "application/json", "Accept": "application/json", "X-Auth-Token": Token}

    values = {
    "lock": "null"
}
    post_url(url, values, headers)
    return redirect(url_for("main.show_all_servers"))

#暂停虚拟机
@main.route("/Pause_Server/<server_id>",methods=["POST","GET"])
def pause_server(server_id):
    url = "http://192.168.188.132:8774/v2.1/servers/" + server_id + "/action"
    Token = getToken("admin", "admin", "admin")
    headers = headers = {"Content-Type": "application/json", "Accept": "application/json", "X-Auth-Token": Token}

    values = {
        "pause": "null"
    }
    post_url(url, values, headers)
    return redirect(url_for("main.show_all_servers"))
#重启虚拟机
@main.route("/Reboot_Server/<server_id>",methods=["POST","GET"])
def reboot_server(server_id):
    url = "http://192.168.188.132:8774/v2.1/servers/" + server_id + "/action"
    Token = getToken("admin", "admin", "admin")
    headers = headers = {"Content-Type": "application/json", "Accept": "application/json", "X-Auth-Token": Token}
    form = RebootServerForm()
    name=u"重启虚拟机"
    if form.validate_on_submit():
        values = {
    "reboot" : {
        "type" : form.type.data
    }
}
        post_url(url, values, headers)
        return redirect(url_for("main.show_all_servers"))
    return render_template("main/ServerAction.html", form=form, name=name)

#重构虚拟机
@main.route("/Rebuild_Server/<server_id>",methods=["POST","GET"])
def rebuild_server(server_id):
    return

#救援虚拟机
@main.route("/Resure_Server/<server_id>",methods=["POST","GET"])
def resure_server(server_id):
    url = "http://192.168.188.132:8774/v2.1/servers/" + server_id + "/action"
    Token = getToken("admin", "admin", "admin")
    headers = headers = {"Content-Type": "application/json", "Accept": "application/json", "X-Auth-Token": Token}
    form = ResureServerForm()
    name=u"救援虚拟机"
    if form.validate_on_submit():
        values = {
    "rescue": {
        "adminPass": form.adminpass.data,
        "rescue_image_ref": form.rescue_image_ref.data
    }
}
        post_url(url, values, headers)
        return redirect(url_for("main.show_all_servers"))
    return render_template("main/ServerAction.html", form=form, name=name)

#更改虚拟机的规格
@main.route("/Resize_Server/<server_id>",methods=["POST","GET"])
def resize_server(server_id):
    url = "http://192.168.188.132:8774/v2.1/servers/" + server_id + "/action"
    Token = getToken("admin", "admin", "admin")
    headers = headers = {"Content-Type": "application/json", "Accept": "application/json", "X-Auth-Token": Token}
    form = ChangeServerFlavorForm()
    data=get_flavor_name_id()
    print data
    form.flavorRef.choices=[(d["id"],d["name"]) for d in data]
    name=u"更改虚拟机的规格"
    if form.validate_on_submit():
        print type(form.flavorRef.data)
        values = {
    "resize" : {
        "flavorRef" : form.flavorRef.data,
        "OS-DCF:diskConfig":form.diskConfig.data
    }
}
        post_url(url, values, headers)
        return redirect(url_for("main.show_all_servers"))
    return render_template("main/ServerAction.html", form=form, name=name)

#恢复虚拟机的运行
@main.route("/Resume_Server/<server_id>",methods=["POST","GET"])
def resume_server(server_id):
    url = "http://192.168.188.132:8774/v2.1/servers/" + server_id + "/action"
    Token = getToken("admin", "admin", "admin")
    headers = headers = {"Content-Type": "application/json", "Accept": "application/json", "X-Auth-Token": Token}

    values = {
        "resume": "null"
    }
    post_url(url,values, headers)
    return redirect(url_for("main.show_all_servers"))

#恢复虚拟机的规格修改
@main.route("/Revert_Resize_Server/<server_id>",methods=["POST","GET"])
def revert_resize_server(server_id):
    url = "http://192.168.188.132:8774/v2.1/servers/" + server_id + "/action"
    Token = getToken("admin", "admin", "admin")
    headers = headers = {"Content-Type": "application/json", "Accept": "application/json", "X-Auth-Token": Token}

    values = {
        "revertResize": "null"
    }
    post_url(url, values, headers)
    return redirect(url_for("main.show_all_servers"))

#启动虚拟机
@main.route("/Start_Server/<server_id>",methods=["POST","GET"])
def start_server(server_id):
    url = "http://192.168.188.132:8774/v2.1/servers/" + server_id + "/action"
    Token = getToken("admin", "admin", "admin")
    headers = headers = {"Content-Type": "application/json", "Accept": "application/json", "X-Auth-Token": Token}

    values = {
        "os-start": "null"
    }
    post_url(url, values, headers)
    return redirect(url_for("main.show_all_servers"))

#停止虚拟机
@main.route("/Stop_Server/<server_id>",methods=["POST","GET"])
def stop_server(server_id):
    url = "http://192.168.188.132:8774/v2.1/servers/" + server_id + "/action"
    Token = getToken("admin", "admin", "admin")
    headers = headers = {"Content-Type": "application/json", "Accept": "application/json", "X-Auth-Token": Token}

    values = {
        "os-stop": "null"
    }
    post_url(url, values, headers)
    return redirect(url_for("main.show_all_servers"))

#挂起虚拟机
@main.route("/Suspend_Server/<server_id>",methods=["POST","GET"])
def suspend_server(server_id):
    url = "http://192.168.188.132:8774/v2.1/servers/" + server_id + "/action"
    Token = getToken("admin", "admin", "admin")
    headers = headers = {"Content-Type": "application/json", "Accept": "application/json", "X-Auth-Token": Token}

    values = {
        "suspend": "null"
    }
    post_url(url, values, headers)
    return redirect(url_for("main.show_all_servers"))

#解锁虚拟机
@main.route("/Unlock_Server/<server_id>",methods=["POST","GET"])
def unlock_server(server_id):
    url = "http://192.168.188.132:8774/v2.1/servers/" + server_id + "/action"
    Token = getToken("admin", "admin", "admin")
    headers = headers = {"Content-Type": "application/json", "Accept": "application/json", "X-Auth-Token": Token}
    values = {
    "unlock": "null"
}
    post_url(url, values, headers)
    return redirect(url_for("main.show_all_servers"))

#解除暂停
@main.route("/Unpause_Server/<server_id>",methods=["POST","GET"])
def unpause_server(server_id):
    url = "http://192.168.188.132:8774/v2.1/servers/" + server_id + "/action"
    Token = getToken("admin", "admin", "admin")
    headers = headers = {"Content-Type": "application/json", "Accept": "application/json", "X-Auth-Token": Token}

    values = {
        "unpause": "null"
    }
    post_url(url, values, headers)
    return redirect(url_for("main.show_all_servers"))

#给虚拟机添加固定的ip
@main.route("/Add_Fixed_Ip_Server/<server_id>",methods=["POST","GET"])
def add_fixed_ip_server(server_id):
    url = "http://192.168.188.132:8774/v2.1/servers/" + server_id + "/action"
    Token = getToken("admin", "admin", "admin")
    headers = headers = {"Content-Type": "application/json", "Accept": "application/json", "X-Auth-Token": Token}
    form = AddFixedIpForm()
    data=get_network_name_id()#这个函数还没写
    form.networkId.choices=[(d["id"],d["name"]) for d in data]
    name=u"给虚拟机添加固定的ip"
    if form.validate_on_submit():
        values = {
    "addFixedIp": {
        "networkId": form.networkId.data
    }
}
        post_url(url, values, headers)
        return redirect(url_for("main.show_all_servers"))
    return render_template("main/ServerAction.html", form=form, name=name)

#删除虚拟机的固定ip
@main.route("/Delete_Fixed_Ip_Server/<server_id>",methods=["POST","GET"])
def delete_fixed_ip_server(server_id):
    url = "http://192.168.188.132:8774/v2.1/servers/" + server_id + "/action"
    Token = getToken("admin", "admin", "admin")
    headers = headers = {"Content-Type": "application/json", "Accept": "application/json", "X-Auth-Token": Token}
    form = DeleteFixedIpForm()
    name=u"删除虚拟机的固定ip"
    if form.validate_on_submit():
        values = {
    "removeFixedIp": {
        "address": form.address.data
    }
}
        post_url(url, values, headers)
        return redirect(url_for("main.show_all_servers"))
    return render_template("main/ServerAction.html", form=form, name=name)

#强制删除虚拟机
@main.route("/Force_Delete_Server/<server_id>",methods=["POST","GET"])
def force_delete_server(server_id):
    url = "http://192.168.188.132:8774/v2.1/servers/" + server_id + "/action"
    Token = getToken("admin", "admin", "admin")
    headers = headers = {"Content-Type": "application/json", "Accept": "application/json", "X-Auth-Token": Token}

    values = {
        "forceDelete": "null"
    }
    post_url(url, values, headers)
    return redirect(url_for("main.show_all_servers"))

#显示虚拟机的控制台输出
@main.route("/Get_Console_Output/<server_id>",methods=["POST","GET"])
def get_console_output(server_id):
    url = "http://192.168.188.132:8774/v2.1/servers/" + server_id + "/action"
    Token = getToken("admin", "admin", "admin")
    headers = headers = {"Content-Type": "application/json", "Accept": "application/json", "X-Auth-Token": Token}

    values = {
    "os-getConsoleOutput": {
    }
}
    response=post_url(url, values, headers)
    #将输出的值显示出来
    form=ShowForm()
    form.getData.data=json.loads(response.read())["output"]
    return render_template("main/TestFile.html",form=form)

#获取vnc控制台url
@main.route("/Get_Vnc_Console/<server_id>",methods=["POST","GET"])
def get_vnc_console(server_id):
    url = "http://192.168.188.132:8774/v2.1/servers/" + server_id + "/action"
    Token = getToken("admin", "admin", "admin")
    headers = headers = {"Content-Type": "application/json", "Accept": "application/json", "X-Auth-Token": Token}

    values = {
    "os-getVNCConsole": {
        "type": "novnc"
    }
}
    response=json.loads(post_url(url, values, headers).read())
    form = ShowForm()
    form.getData.data = response["console"]["url"]
    return render_template("main/TestFile.html", form=form)

#撤离虚拟机
@main.route("/Evacute_server/<server_id>",methods=["POST","GET"])
def evacuate_server(server_id):
    url = "http://192.168.188.132:8774/v2.1/servers/" + server_id + "/action"
    Token = getToken("admin", "admin", "admin")
    headers = headers = {"Content-Type": "application/json", "Accept": "application/json", "X-Auth-Token": Token}

    values = {
    "evacuate": {
        "host": "b419863b7d814906a68fb31703c0dbd6",#这里需要知道虚拟机在那个主机上
        "adminPass": "MySecretPass",#这里需要知道虚拟机的密码是多少
        "onSharedStorage": "False"
    }
}
    post_url(url, values, headers)
    return redirect(url_for("main.show_all_servers"))

#故障转储
@main.route("/Trigger_Crash_dump/<server_id>",methods=["POST","GET"])
def trigger_crash_dump(server_id):
    url = "http://192.168.188.132:8774/v2.1/servers/" + server_id + "/action"
    Token = getToken("admin", "admin", "admin")
    headers = headers = {"Content-Type": "application/json", "Accept": "application/json", "X-Auth-Token": Token}

    values = {
    "trigger_crash_dump": "null"
}
    post_url(url, values, headers)
    return redirect(url_for("main.show_all_servers"))


##############################################管理员可执行的server action################
#平台冷迁移
def migrate_server(server_id):
    url = "http://192.168.188.132:8774/v2.1/servers/" + server_id + "/action"
    Token = getToken("admin", "admin", "admin")
    headers = headers = {"Content-Type": "application/json", "Accept": "application/json", "X-Auth-Token": Token}
    form=MigrateServerForm()
    ##这里将hosts的name添加到choices
    if form.validate_on_submit():
        if form.host.data=="null":
            values = {
    "migrate":"null"
}
        else:
            values={
    "migrate": {
        "host": form.host.data
    }
}
        post_url(url, values, headers)
    return render_template("main/ServerAction.html")
#重置虚拟机状态
def reset_server_state(server_id):

    return


##########################################查看节点的信息##########################
#查看节点的列表
@main.route("/ShowHypervisorsPage")
def show_hypervisors_page():
    return render_template("main/ShowHypervisorsPage.html")
@main.route("/GetHypervisorsList")
def get_hypervisors_list():
    url = "http://192.168.188.132:8774/v2.1/os-hypervisors"
    Token=getToken("admin","admin","admin")
    response=json.loads(get_url(url,Token).read())
    data=[]
    hypervisorList=response["hypervisors"]
    for hypervisor in hypervisorList:
        d={}
        d["name"]=hypervisor["hypervisor_hostname"]
        d["id"]=hypervisor["id"]
        d["state"]=hypervisor["state"]
        d["status"] = hypervisor["status"]
        d["message"]="<a href="+url_for("main.show_hypervisors_detial_page",hypervisors_id=d["id"])+">查看</a>"
        data.append(d)
    if request.method == 'GET':
        info = request.values
        limit = info.get('limit', 10)  # 每页显示的条数
        offset = info.get('offset', 0)  # 分片数，(页码-1)*limit，它表示一段数据的起点
        print('get', limit)
        print('get  offset', offset)
        return jsonify({'total': len(data), 'rows': data[int(offset):(int(offset) + int(limit))]})

#获取详细信息
@main.route("/ShowHypervisorDetial/<hypervisors_id>")
def show_hypervisors_detial_page(hypervisors_id):
    return render_template("main/ShowHypervisorDetialPage.html",hypervisors_id=hypervisors_id)
@main.route("/GetAHypervisorDetial/<hypervisors_id>")
def show_hypervisors_detial(hypervisors_id):
    url = "http://192.168.188.132:8774/v2.1/os-hypervisors/"+hypervisors_id
    Token = getToken("admin", "admin", "admin")
    response = json.loads(get_url(url, Token).read())
    data=[]#用来显示信息
    hypervisor=response["hypervisor"]
    base_message=""
    d={}
    # "<li>"+u"能否使用："+hypervisor["status"]+"</li>"\+bytes(hypervisor["state"]) +
    print (hypervisor["hypervisor_hostname"])
    print (hypervisor["state"])
    print type("<li>id：")
    print hypervisor["state"]
    print type(hypervisor["hypervisor_hostname"])
    print "<li>"+u"名称："+hypervisor["hypervisor_hostname"]+"</li>"
    d["title"]=u"基本信息"
    print type(str(hypervisor["id"]))

    d["message"]="<div><ul>" \
                "<li>id："+str(hypervisor["id"])+"</li>"\
                "<li>"+u"名称："+hypervisor["hypervisor_hostname"]+"</li>" \
                "<li>"+u"状态：" +hypervisor["state"]+"</li>" \
                "<li>"+u"是否可用："+hypervisor["status"]+"</li>" \
                 "</ul>" \
                "</div>"
    data.append(d)
    d={}
    d["title"]=u"cpu详细信息"
    cpu_info=json.loads(hypervisor["cpu_info"])
    cpu_message="<div><ul>" \
                "<li>arch："+cpu_info["arch"]+"</li>"\
                "<li>"+u"架构："+cpu_info["model"]+"</li>" \
                "<li>"+u"供应商：" + cpu_info["vendor"] + "</li>" \
                 "</ul>" \
                "<h4>拓扑</h4>"\
                "<ul>" \
                "<li>"+u"核心：" + str(cpu_info["topology"]["cores"])+ "</li>" \
                "<li>"+u"处理器：" + str(cpu_info["topology"]["sockets"]) + "</li>" \
                "</ul>"\
                "<h4>vcpu的使用情况</h4>" \
                 "<ul>" \
                 "<li>"+u"总共的vcpu数量：" + str(hypervisor["vcpus"]) + "</li>" \
                  "<li>"+u"已经使用的vcpu：" + str(hypervisor["vcpus_used"]) + "</li>" \
                  "</ul>" \
                "</div>"
    d["message"]=cpu_message
    data.append(d)
    d={}
    d["title"]=u"内存详情"
    d["message"]="<div><ul>" \
                "<li>可用内存：" + str(hypervisor["memory_mb"]) + "</li>" \
                "<li>已用内存："+str(hypervisor["memory_mb_used"])+"</li>"\
                 "</ul>" \
                "</div>"
    data.append(d)
    d={}
    d["title"]=u"磁盘详情"
    d["message"]="<div><ul>" \
                "<li>可用磁盘：" + str(hypervisor["local_gb"]) + "</li>" \
                "<li>已用磁盘："+str(hypervisor["local_gb_used"])+"</li>"\
                 "</ul>" \
                "</div>"
    data.append(d)
    d={}
    d["title"]=u"网址"
    d["message"]="<div><ul>" \
                "<li>节点ip：" + hypervisor["host_ip"] + "</li>" \
                 "</ul>" \
                "</div>"
    data.append(d)

    if request.method == 'GET':
        info = request.values
        limit = info.get('limit', 10)  # 每页显示的条数
        offset = info.get('offset', 0)  # 分片数，(页码-1)*limit，它表示一段数据的起点
        print('get', limit)
        print('get  offset', offset)
        return jsonify({'total': len(data), 'rows': data[int(offset):(int(offset) + int(limit))]})

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
##############################################显示节点的情况################
@main.route("/postFile",methods=["POST","GET"])
def post_file():
    form = TestField()
    if form.validate_on_submit():
        filename = photos.save(form.photo.data)
        file_url = photos.url(filename)
        filename2 = text.save(form.text.data)
        filename3=all_file.save(form.all_file.data)
    else:
        file_url = None
    return render_template('main/TestFile.html', form=form, file_url=file_url)