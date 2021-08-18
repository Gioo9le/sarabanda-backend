from flask import Flask, request
from flask_socketio import SocketIO

import enum

class GameStates(enum.Enum):
    day = 1
    night = 2
    vote = 3


app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*")


connectedClient = 0

@socketio.on('connect')
def test_connect(data):
    print(data)
    print(request.sid)
    global connectedClient
    socketio.emit('my response', {'data': 'Connected'})
    connectedClient+=1
    print(f"User connected, connected client: {connectedClient}")

@socketio.on('disconnect')
def test_disconnect():
    global connectedClient
    print(request.sid)
    connectedClient-=1
    print(f'Client disconnected, connected client: {connectedClient}')

@socketio.on('my event')
def user_con(data):
    print(request.sid)
    print(data)

@app.route("/")
def hello_world():
    return '''<script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js" integrity="sha512-q/dWJ3kcmjBLU4Qc47E4A9kTB4m3wuTY7vkFJDTZKjTs8jhyGQnaUrxa0Ytd0ssMZhbNua9hE+E7Qv1j+DyZwA==" crossorigin="anonymous"></script>
<script type="text/javascript" charset="utf-8">
    var socket = io("localhost:5000", {auth : {id: window.localStorage.getItem('sessionId')}});
    socket.on("connect", function() {
        socket.emit("my event", {data: "I connected!"});
    });
</script>'''

if __name__ == '__main__':
    print("Server starting")
    socketio.run(app, debug=True)

