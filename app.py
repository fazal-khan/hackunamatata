from flask import Flask, request, render_template
from flask_socketio import SocketIO, send, join_room, leave_room, emit
from twilio.rest import Client
import time
from flask_cors import CORS
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = b'_5#y2L"F4Q8z\n\xec]/'
socketio = SocketIO(app, cors_allowed_origins='*')
CORS(app)

account_sid = "AC681bed3ffe53ae808db2cffb358c3344"
auth_token = "9d6f8974817c38d9319e6c803c70a322"
client = Client(account_sid, auth_token)
sessions = {}


# A route to get SMS messages
@app.route('/sms', methods=['POST'])
def inbound_sms():
    from_num = request.form['From']
    to_num = request.form['To']
    body = request.form['Body']
    timestamp = time.strftime('%X %x')

    uid = str(to_num).replace('+', '').strip() + str(from_num).replace('+', '').strip()
    room = sessions[uid]

    emit('response', {'from_num': from_num, 'to_num': to_num, 'body': body, 'timestamp': timestamp}, room=room,
         namespace='/messaging')
    print("Done")
    return 'ok'


# A route to send SMS messages
@socketio.on('send_message', namespace='/messaging')
def outbound_sms(req):
    print(req)
    from_num = req['from']
    to_num = req['to']
    body = req['body']
    timestamp = time.strftime('%X %x')

    uid = str(from_num).replace('+', '').strip() + str(to_num).replace('+', '').strip()
    room = sessions[uid]

    # client.messages.create(
    #     body=body,
    #     from_=from_num,
    #     to="+918618490862"
    # )

    emit('response_sender', {'from_num': from_num, 'to_num': to_num, 'body': body, 'timestamp': timestamp}, room=room)
    print("Done")


@socketio.on('storesession', namespace='/messaging')
def storesession(username):
    sessions[username] = request.sid
    print(sessions)


# A route for default page
@app.route('/', methods=['GET'])
def index():
    from_num = request.args['from']
    to_num = request.args['to']
    uid = str(from_num).replace('+', '').strip() + str(to_num).replace('+', '').strip()
    return render_template('index.html', uid=uid, from_num=from_num, to_num=to_num)


if __name__ == '__main__':
    socketio.run(app)
