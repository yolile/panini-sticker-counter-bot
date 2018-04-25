import csv

from peewee import *

db = SqliteDatabase('panini_stickers_bot.db')


class BaseModel(Model):
    class Meta:
        database = db


class Sticker(BaseModel):
    name = TextField()
    number_version_670 = IntegerField(null=True)
    number_version_682 = IntegerField()


class Album(BaseModel):
    name = TextField()
    telegram_id = TextField()
    album_version = IntegerField(constraints=[Check('album_version = 682 or album_version = 670')])


class AddedSticker(BaseModel):
    sticker_id = ForeignKeyField(Sticker)
    album_id = ForeignKeyField(Album)


def load_sticker_table():
    if not Sticker.table_exists():
        Sticker.create_table(True)
        with open('panini_stickers.csv', 'r') as fin:  # `with` statement available in 2.5+
            # csv.DictReader uses first line in file for column headings by default
            dr = csv.DictReader(fin)  # comma is default delimiter
            for i in dr:
                if i['number_version_670'] == '':
                    Sticker.create(name=i['name'], number_version_670=None,
                                   number_version_682=int(i['number_version_682']))
                else:
                    Sticker.create(name=i['name'], number_version_670=int(i['number_version_670']),
                                   number_version_682=int(i['number_version_682']))
