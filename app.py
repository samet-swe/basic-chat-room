from flask import Flask, render_template, session, request, redirect, url_for
from flask_socketio import SocketIO, emit, join_room, leave_room, send

import database

from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysecret'
socketio = SocketIO(app)

table_sql = ['CREATE TABLE IF NOT EXISTS public.msg_history(msg_index integer NOT NULL GENERATED ALWAYS AS IDENTITY ( CYCLE INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 2147483647 CACHE 1 ), room text COLLATE pg_catalog."default" NOT NULL, username text COLLATE pg_catalog."default" NOT NULL, msg text COLLATE pg_catalog."default" NOT NULL, msg_time timestamp with time zone NOT NULL, CONSTRAINT msg_history_pkey PRIMARY KEY (msg_index))',
             'CREATE TABLE IF NOT EXISTS public.sys_history(msg text COLLATE pg_catalog."default" NOT NULL, msg_time timestamp with time zone NOT NULL)']
db = database.Database('msg_history', table_sql)

rooms = {}
rooms['General'] =  {'members':1, 'messages': []}


@app.route('/', methods=['GET', 'POST'])
def login():
    session.clear()
    
    if request.method == 'POST':
        
        username = request.form.get('username', '')        
        if username == '':
            username = 'Guest' # If no username is entered, default to 'Guest'

        # If requiring user to enter a username, use the following instead of the default value above:
        #if not name:
        #    return render_template('login.html', error='Please enter a username.', username=username, room=room)

        room = request.form.get('room', '')
        if room == '':
            room = 'General' # If no room is entered, default to 'General'
        else:
            if room not in rooms:
                rooms[room] = {'members': 0, 'messages': []} # If room entered does not exist, create it

        session['username'] = username
        session['room'] = room
            
        return redirect(url_for('chat'))
    return render_template('login.html')

@app.route('/chat')
def chat():
    username = session.get('username')
    room = session.get('room')
    
    if room not in rooms:
        return redirect(url_for('login')) # If attempt is made to enter chatroom without logging in, return to login screen
    
    return render_template('chat.html', username=username, room=room, messages=rooms[room]['messages'])

@socketio.on('connect')
def connect(auth):
    room = session.get('room')
    username = session.get('username')
    
    if not room or not username: # If attempt to connect without logging in, return to login screen
        return
    if room not in rooms: # If attempt to connect to non-existent room, make sure socket not connected to room and return to login
        leave_room(room)
        return
    
    join_room(room)
    
    send({'username':username, 'message':'has entered the room.'}, to=room)
    rooms[room]['members'] += 1
    
    dt = datetime.now()
    msg = f'{username} joined room {room}  -  ' + dt.strftime("%a %b %d %Y %X")  
    print(msg)
    
    columns = ['msg', 'msg_time']
    data = [msg, dt]
    db.save_data('sys_history', columns, data)
    
@socketio.on('disconnect')
def disconnect():
    room = session.get('room')
    username = session.get('username')
    leave_room(room)
    send({'username':username, 'message':'has left the room.'}, to=room)
    
    dt = datetime.now()
    msg = f'{username} left the room {room}  -  ' + dt.strftime("%a %b %d %Y %X")  
    print(msg)
    
    columns = ['msg', 'msg_time']
    data = [msg, dt]
    db.save_data('sys_history', columns, data)

    if room in rooms:
        rooms[room]['members'] -= 1
        if rooms[room]['members'] <= 0:
            del rooms[room]
    
@socketio.on('message')
def message(data):
    username = session.get('username')
    room = session.get('room')
    
    if room not in rooms: 
        return

    content = { 
        'username': username,
        'message': data['data']
    }
    
    send(content, to=room) 
    rooms[room]['messages'].append(content) # Add message to the message history
    
    dt = datetime.now()
    msg = f'{username} [{room}] said: {data["data"]}  -  ' + dt.strftime("%a %b %d %Y %X")  
    print(msg)
    
    columns = ['msg', 'msg_time']
    table_data = [msg, dt]
    db.save_data('sys_history', columns, table_data)
    
    columns = ['room', 'username', 'msg', 'msg_time']
    table_data = [room, username, data['data'], dt]
    db.save_data('msg_history', columns, table_data)
            
if __name__ == "__main__":
    socketio.run(app, debug=True)