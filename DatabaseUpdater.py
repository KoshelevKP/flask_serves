import peewee
import datetime

database = peewee.SqliteDatabase("MessageDB.db")


class BaseTable(peewee.Model):
    class Meta:
        database = database


class Database(BaseTable):
    id = peewee.CharField()
    text = peewee.CharField()
    messenger = peewee.CharField()
    date = peewee.DateTimeField()


class DatabaseUpdater:

    def __init__(self):
        self.database = Database
        database.create_tables([self.database])

    def save_data(self, data):

        error_list = ''

        try:
            date_str, time_str = data['date'].split(' ')
            day, month, year = date_str.split('.')
            hour, minute = time_str.split(':')
            date = datetime.datetime(year=int(year), month=int(month), day=int(day), hour=int(hour), minute=int(minute))
        except:
            error_list = 'Неправильно указано время'
            return error_list

        if type(data['id']) == list:
            for id in data['id']:
                for messenger in data['messengers']:
                    data_to_save = self.database.create(
                        id=id,
                        text=data.get('text', ''),
                        messenger=messenger,
                        date=date
                    )
                    data_to_save.save()
        else:
            error_list += 'не верно указаны id'

        return error_list

    def load_data(self, date):

        data_list = []

        for data in self.database.select().where(self.database.date <= date):
            data_list.append({
                'id': data.id,
                'text': data.text,
                'messenger': data.messenger
            })

        return data_list

