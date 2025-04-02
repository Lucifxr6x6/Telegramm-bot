import peewee
from peewee import *
from config_data import config

db = peewee.SqliteDatabase(config.DB_NAME)


class BaseModel(Model):
    class Meta:
        database = db


class User(BaseModel):
    id = AutoField(null=False)
    # id = PrimaryKeyField(null=False)
    chat_id = IntegerField(unique=True)
    username = CharField(max_length=150)
    full_name = CharField(max_length=150)

    class Meta:
        db_table = "user"


class Response(BaseModel):
    id = AutoField(null=False)
    # id = PrimaryKeyField(null=False)
    query_id = IntegerField()
    hotel_id = IntegerField()
    name = CharField(max_length=1500)
    address = CharField(max_length=1500)
    price = FloatField()
    distance = FloatField()

    class Meta:
        db_table = "response"


class Images(BaseModel):
    id = AutoField(null=False)
    # id = PrimaryKeyField(null=False)
    hotel_id = ForeignKeyField(Response,
                               to_field=id,
                               on_delete='cascade',
                               on_update='cascade'
                               )
    link = CharField()

    class Meta:
        db_table = "images"


class Query(BaseModel):
    id = AutoField(null=False)
    # id = PrimaryKeyField(null=False)
    user_id = IntegerField()
    date_time = CharField(max_length=1500)
    input_city = CharField(max_length=150)
    destination_id = CharField(max_length=1500)
    photo_need = CharField(max_length=150)
    response_id = ForeignKeyField(Response,
                                  to_field=id,
                                  on_delete='cascade',
                                  on_update='cascade',
                                  null=True
                                  )

    class Meta:
        db_table = "query"


def create_tables():
    with db:
        db.create_tables([User, Query, Response, Images])


db.connect()
create_tables()
