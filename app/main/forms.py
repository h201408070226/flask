#encoding=utf8
import sys
reload(sys)
sys.setdefaultencoding('utf8')
from flask_wtf import FlaskForm,Form
from .. import photos,text,all_file
from wtforms import StringField, TextAreaField, BooleanField, SelectField,\
    SubmitField,IntegerField,PasswordField
from wtforms.validators import Required, Length, Email, Regexp,IPAddress
from flask_wtf.file import FileRequired,FileAllowed,FileField
from wtforms import ValidationError
from wtforms import FieldList
from ..models import Role, User


class NameForm(FlaskForm):
    name = StringField('What is your name?', validators=[Required()])
    submit = SubmitField('Submit')


class EditProfileForm(FlaskForm):
    name = StringField('Real name', validators=[Length(0, 64)])
    location = StringField('Location', validators=[Length(0, 64)])
    about_me = TextAreaField('About me')
    submit = SubmitField('Submit')


class EditProfileAdminForm(FlaskForm):
    email = StringField('Email', validators=[Required(), Length(1, 64),
                                             Email()])
    username = StringField('Username', validators=[
        Required(), Length(1, 64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                                          'Usernames must have only letters, '
                                          'numbers, dots or underscores')])
    confirmed = BooleanField('Confirmed')
    role = SelectField('Role', coerce=int)
    name = StringField('Real name', validators=[Length(0, 64)])
    location = StringField('Location', validators=[Length(0, 64)])
    about_me = TextAreaField('About me')
    submit = SubmitField('Submit')

    def __init__(self, user, *args, **kwargs):
        super(EditProfileAdminForm, self).__init__(*args, **kwargs)
        self.role.choices = [(role.id, role.name)
                             for role in Role.query.order_by(Role.name).all()]
        self.user = user

    def validate_email(self, field):
        if field.data != self.user.email and \
                User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')

    def validate_username(self, field):
        if field.data != self.user.username and \
                User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already in use.')

#用来显示获取到的信息的form
class ShowForm(FlaskForm):
    getData=TextAreaField('get from the openstack!')

#用来新建flasvor的form
class CreateNewFlavorForm(FlaskForm):
    name=StringField("flavor name",validators=[Required()])
    ram=IntegerField(" Flavor ram",validators=[Required()])
    vcpus=IntegerField(" Flavor vcpus",validators=[Required()])
    disk=IntegerField("flavor disk",validators=[Required()])
    id=StringField(" flavor  id",validators=[Required()])
    #description=StringField("flavor description ",validators=[Required()])
    submit=SubmitField("Submit")

#用来新建keypair
class CreateNewKeypairForm(FlaskForm):
    name=StringField(u"请输入keypair的名字",validators=[Required()])
    type=SelectField(u"请选择keypair的类型",validators=[Required()],choices=[("ssh","ssh"),("x509","x509")])
    public_key=TextAreaField(u"如果可以请输入public_key，否则将会自动生成并返回private_key ")
    submit=SubmitField(u"提交")

#用来新建image的form
class CreateNewImageForm(FlaskForm):
    container_format=StringField("please input container_format",validators=[Required()])
    disk_format=StringField("please input disk_format",validators=[Required()])
    name=StringField("please input the image name",validators=[Required()])
    id=StringField('please input the image id',validators=[Required()])
    visibility=SelectField("please choose the visibility",choices=[('private',u'私有'), ('public', u'公开'),("share",u"共享")])

    ImageFile=FileField("please choose your ImageFile")
    submit=SubmitField("Submit")

#用来新建新的实例
class CreateNewServerForm(FlaskForm):
    ipv4address = StringField("please input the ipv4address", validators=[Required(), Length(1, 64),IPAddress()])
    ipv6address = StringField("please input the ipv6address", validators=[Required(), Length(1, 64)])
    name=StringField("please inpute the server name", validators=[Required(), Length(1, 64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                                          'Usernames must have only letters, '
                                          'numbers, dots or underscores')])
    imageRef=StringField("please input a active image id",validators=[Required()])
    flavorRef=StringField("please input a flavor id",validators=[Required()])
    availability_zone=StringField("please input a zone",default="nova")
    diskConfig=StringField("please input a diskconfig",default="AUTO")
    #元数据的键值对那个不是很懂，所以现在先放下，后面再补
    security_groups=StringField("please input the security_group",default="default")
    user_data=StringField("if you have person data ,please input")

    def validate_name(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already in use.')
#新建秘钥对
class CreateNewKeypairForm(FlaskForm):
    name=StringField(u"请填写名称",validators=[Required()])
    rsa=StringField(u'请填写公钥',validators=[Required()])
    submit=SubmitField(u"提交")
#新建安全组
class CreateNewSecurityGroupsForm(FlaskForm):
    name=StringField(u"请填写安全组名称",validators=[Required()])
    description=StringField(u"请填写关于安全组的描述",validators=[Required()])
    submit=SubmitField(u"提交")

#新建安全组规则
class CreateNewSecurityGroupRoules(FlaskForm):
    parent_group_id=SelectField(u"请选择要添加的安全组",validators=[Required()])


#为虚拟机添加卷
class AttachVolumeToServerForm(FlaskForm):
    volumeId=SelectField(u"请选择要添加的卷",validators=[Required()])
    device=StringField(u'请填写设备的名称',validators=[Required()])
    submit = SubmitField(u"提交")

################下面是为了实现server的action新建的Form###########
##添加浮动ip
class AddFloatIpForm(FlaskForm):
    address=StringField("address",validators=[Required(),IPAddress()])
    fixed_address=StringField("fixed_address",validators=[Required(),IPAddress()])
    submit=SubmitField(u"提交更改数据")
##删除浮动ip
class DeleteFloatIpForm(FlaskForm):
    address=StringField("address",validators=[Required(),IPAddress()])
    submit=SubmitField(u"提交更改数据")

#添加安全组
class AddSecurityGroupForm(FlaskForm):
    name=SelectField(u"请选择要添加的安全组",validators=[Required()])
    submit=SubmitField(u"提交更改数据")
#删除安全组
class DeleteSecurityGroupForm(FlaskForm):
    name = StringField(u"请输入要删除的安全组", validators=[Required()])
    submit = SubmitField(u"提交更改数据")

#更改虚拟机密码
class ChangeAdministrativePasswordForm(FlaskForm):
    password=PasswordField(u"请输入要修改虚拟机密码",validators=[Required()])
    submit=SubmitField(u"提交更改数据")

#为虚拟机添加备份
class CreateServerBackUpForm(FlaskForm):
    name=StringField(u"请填写备份的名字",validators=[Required()])
    backup_type=SelectField(u"请选择要备份的类型",validators=[Required()],default="daily")
    submit = SubmitField(u"提交更改数据")

#为虚拟机制作镜像
class CreateServerImageForm(FlaskForm):
    name = StringField(u"请填写镜像的名字", validators=[Required()])
    metadata_key=StringField(u"请输入元数据的键",validators=[Required()])
    metadata_value=StringField(u"请输入元数据的值",validators=[Required()])
    submit = SubmitField(u"提交更改数据")

#重新启动虚拟机
class RebootServerForm(FlaskForm):
    type=SelectField(u"请选择重启的类型",validators=[Required()],choices=[("HARD ","HARD "),("SOFT","SOFT")])
    submit = SubmitField(u"提交更改数据")

#重构虚拟机
class RebuildServerForm(FlaskForm):

    submit = SubmitField(u"提交更改数据")

#救援虚拟机
class ResureServerForm(FlaskForm):
    adminpass=PasswordField(u"请输入虚拟机的密码",validators=[Required()])
    rescue_image_ref=SelectField(u"请选择要救援的image",validators=[Required()])
    submit = SubmitField(u"提交更改数据")

#修改云主机类型
class ChangeServerFlavorForm(FlaskForm):
    flavorRef=SelectField(u"请选择云主机类型",validators=[Required()])
    diskConfig=SelectField(u"请选择diskConfig类型",validators=[Required()],choices=[("AUTO","AUTO"),("MANUAL","MANUAL")],default="AUTO")
    submit = SubmitField(u"提交更改数据")

#添加固定的ip
class AddFixedIpForm(FlaskForm):
    networkId=SelectField(u"请选择固定的网络",validators=[Required()])
    submit = SubmitField(u"提交更改数据")
#删除固定ip
class DeleteFixedIpForm(FlaskForm):
    address=StringField(u"请输入要删除的ip地址",validators=[Required(),IPAddress()])
    submit = SubmitField(u"提交更改数据")

#冷迁移虚拟机
class MigrateServerForm(FlaskForm):
    host=SelectField(u"请选择要迁移的虚拟机",validators=[Required()],default=u"null")
    submit=SubmitField(u"提交数据")

class TestField(FlaskForm):
    photo = FileField(validators=[
        FileAllowed(photos, u'只能上传图片！'),
        FileRequired(u'文件未选择！')])
    text = FileField(validators=[FileAllowed(text, u'只能上传txt文件'), FileRequired(u'文件未选择！')])
    all_file=FileField(validators=[FileAllowed(all_file),FileRequired(u'文件未选择！')])
    submit = SubmitField(u'上传')