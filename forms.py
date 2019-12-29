#Utilizaremos otra libreria de flask,flask_wtf para trabajar todo lo que
#tenga que ver con formularios, con FlaskForm.
#flask_wtf fue instalado anteriormende en la cmd con pip install flask_wtf
#al igual que flask_login y flask_bcrypt.
#Regexp valida expresiones regulares que nosotros indiquemos
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField
from wtforms.validators import (DataRequired, ValidationError, Email, Regexp,
                                Length, EqualTo)
from models import User

                                #Metodos

#Si ya existe el nombre de usuario devolvemos un error
#Query donde el nombre de usuario que hayan escojido sea igual al datos
#que estamos obteniendo de nuestro campo field.
def name_exists(form, field):
    if User.select().where(User.username == field.data).exists():
        raise ValidationError("Ya existe ese nombre de usuario")


def email_exists(form, field):
    if User.select().where(User.email == field.data).exists():
        raise ValidationError("El email ya existe")


                                #Clases

class RegisterForm(FlaskForm):
    username = StringField(
        "Username",
        validators = [
            DataRequired(),
            Regexp(
            r'^[a-zA-Z0-9_]+$'
            #Aceptamos caracteres de la A a la Z en minuscula y mayuscula
            #y numeros del 0 al 9.
            ),
            name_exists
    ])
    email = StringField(
        "Email",
        #Nuevamente definimos los validadores
        validators = [
            DataRequired(),
            Email(),
            email_exists
    ])
    password = PasswordField(
        "Password",
        validators = [
            DataRequired(),
            Length(min=4),
            EqualTo("password2", message = "Los passwords deben coincidir")
    ])
    password2 = PasswordField(
        "Confirm Password",
        validators = [DataRequired()]
    )


class LoginForm(FlaskForm):
    email = StringField(
        "Email",
        validators=[
            DataRequired(),
            Email()
    ])
    password = PasswordField(
        "Password",
        validators = [
            DataRequired()
    ])


class PostForm(FlaskForm):
    content = TextAreaField("Que Piensas?",validators = [DataRequired()])
