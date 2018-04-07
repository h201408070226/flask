#encoding=utf8
import sys
reload(sys)
sys.setdefaultencoding('utf8')
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, BooleanField, SelectField,\
    SubmitField,IntegerField,FileField
from wtforms.validators import Required, Length, Email, Regexp,IPAddress
from wtforms import ValidationError
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

#用来新建image的form
class CreateNewImageForm(FlaskForm):
    container_format=StringField("please input container_format",validators=[Required()])
    disk_format=StringField("please input disk_format",validators=[Required()])
    name=StringField("please input the image name",validators=[Required()])
    id=StringField('please input the image id',validators=[Required()])
    visibility=SelectField("please choose the visibility",choices=[('private',u'私有'), ('public', u'公开'),("share","共享")])

    ImageFile=FileField("please choose your ImageFile")
    submit=SubmitField("Submit")

#用来新建新的实例
class CreateNewServer(FlaskForm):
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
