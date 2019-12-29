import datetime
from peewee import *
#flask_login libreria que ya contiene metedos para logeo de usuarios
from flask_login import UserMixin
#Importamos de flask la libreria que nos ayudara a hashear los passwords
from flask_bcrypt import generate_password_hash

DATABASE = SqliteDatabase("social.db")

#Mixin es una clase que esta ya definida que se utiliza para apoyar a las demas
#User hereda de UserMixin de flask_login y Model de peewee
class User(UserMixin,Model):
    username = CharField(unique = True)
    email = CharField(unique = True)
    password = CharField(max_length = 60)
    joined_at = DateTimeField(default = datetime.datetime.now)

    class Meta:
        database = DATABASE
        order_by = ("-joined_at",)

    def get_post(self):
        return Post.select().where(Post.user == self)

    def get_stream(self):
        return Post.select().where(
            (Post.user << self.following()) |
            (Post.user == self)
        )

    def following(self):
        """Los Usuarios que estamos siguiendo"""
        return (
            User.select().join(
                Relationship, on= Relationship.to_user
                ).where(
                    Relationship.from_user == self
                )
            )

    def followers(self):
        """Obtener los usuarios que me siguen"""
        return (
            User.select().join(
                Relationship, on= Relationship.from_user
                ).where(
                    Relationship.to_user == self
                )
            )


    @classmethod
    def create_user(cls, username, email, password):
        try:
            with DATABASE.transaction():
            #cls le indica que es de la clase User
                cls.create(
                    username = username,
                    email = email,
                    password = generate_password_hash(password)
                    )
        #si  indican mal la informacion en username, email o password nos
        #devolvera un IntegrityError
        except IntegrityError:
            #raise ValueError("User already exists")
            raise ValueError("User are ready exists")


class Post(Model):
    user = ForeignKeyField(
        User,
        related_name = "post",
    )
    timestamp = DateTimeField(default = datetime.datetime.now)
    content = TextField()

    class Meta():
        database = DATABASE
        order_by = ("-joined_at",)


class Relationship(Model):
    from_user = ForeignKeyField(User, related_name = "Relationship")
    to_user = ForeignKeyField(User, related_name = "Related to")

    class Meta():
        database = DATABASE
        idexes= (
            (("from_user" , "to_user"), True),
        )



def initialize():
    DATABASE.connect()
    DATABASE.create_tables([User, Post, Relationship],safe = True)
    DATABASE.close()
