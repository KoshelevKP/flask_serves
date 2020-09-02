from flask import Flask, jsonify, abort, make_response, request
from DatabaseUpdater import DatabaseUpdater, Database
from threading import Timer
import datetime
import Viber
import Telegram
import WhatsApp

app = Flask(__name__)


MESSENGERS = {
    'Viber': Viber,
    'Telegram': Telegram,
    'WhatsApp': WhatsApp
}

DATABASE = DatabaseUpdater()


def send_time_message(data):
    error_list = DATABASE.save_data(data)
    return error_list


def save_message(id, text, messenger):

    date = datetime.datetime.now()

    data = {
        'id': [id],
        'text': text,
        'messenger': [messenger],
        'date': date.strftime('%d.%m.%Y %H:%M')
    }

    send_time_message(data)


@app.route('/messengers/api/v1.0/send_message', methods=['POST'])
def send_message():
    if not request.json:
        abort(400)
    if not 'id' in request.json:
        abort(400)
    if not 'messengers' in request.json:
        abort(400)

    error_list = ''

    if 'date' in request.json:
        error_list = send_time_message(request.json)
        return make_response(error_list, 200)

    if type(request.json['id']) == list:
        for id in request.json['id']:
            for messenger in request.json['messengers']:
                if messenger in MESSENGERS:
                    text = request.json.get('text', "")
                    status = MESSENGERS[messenger].send_message(id, text)
                    if not status:
                        save_message(id, text, messenger)
                else:
                    error_list += 'Попытка отправить сообщение на не доступный мессенджер'
    else:
        error_list += 'не верно указаны id'

    return make_response(error_list, 200)


def check_database():

    date = datetime.datetime.now()

    message_list = DATABASE.load_data(date)

    query = Database.delete().where(Database.date <= date)
    n = query.execute()

    for message in message_list:
        if message['messenger'] in MESSENGERS:
            id = message['id']
            text = message['text']
            MESSENGERS[message['messenger']].send_message(id, text)

    t = Timer(60, check_database)
    t.start()


if __name__ == '__main__':
    t = Timer(60, check_database)
    t.start()
    app.run()
