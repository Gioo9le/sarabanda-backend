import enum
from random import choice, randint, sample
from typing import Optional, Any, List
import os

import tekore as tk
from flask import Flask, request, redirect
from flask_cors import CORS


class GameStates(enum.Enum):
    day = 1
    night = 2
    vote = 3


app = Flask(__name__)
CORS(app)


cred = tk.RefreshingCredentials(client_id="3d5c756645874d03a6ddb0b5b2e3574c",
                      client_secret="a2ad98b4e0dd4b39bd06a07abb4a7b34",
                      redirect_uri='http://localhost:5000/code')

spotify: tk.Spotify
my_playlist: Optional[List[Any]] = None



@app.route("/")
def hello_world():
    return '''<script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js" integrity="sha512-q/dWJ3kcmjBLU4Qc47E4A9kTB4m3wuTY7vkFJDTZKjTs8jhyGQnaUrxa0Ytd0ssMZhbNua9hE+E7Qv1j+DyZwA==" crossorigin="anonymous"></script>
<script type="text/javascript" charset="utf-8">
    var socket = io("localhost:5000", {auth : {id: window.localStorage.getItem('sessionId')}});
    socket.on("connect", function() {
        socket.emit("my event", {data: "I connected!"});
    });
</script>'''

@app.get("/login")
def login():
    return cred.user_authorisation_url(scope=tk.scope.playlist_read_private)

@app.route("/code")
def get_access_token():
    global spotify
    global my_playlist
    print(request.host)
    # print(request.args.get('code'))
    token = cred.request_user_token(request.args.get('code'))
    # print(token)
    spotify = tk.Spotify(token)
    my_playlist_id = spotify.playlists(spotify.current_user().id).items[1].id
    my_playlist = spotify.playlist(my_playlist_id).tracks.items
    # print(spotify.playlists(spotify.current_user().id).items[0])
    return redirect('http://localhost:3000/play')

@app.get('/song')
def get_songs():
    global spotify
    global my_playlist
    generic_error = False
    if my_playlist is None:
        raise None
    try:
        song_correct_all = choice(my_playlist)
        song_correct = song_correct_all.track
        my_playlist.remove(song_correct_all)
        result = [((song_correct.artists[0].name, True), (song_correct.name, True))]
        related_artists = spotify.artist_related_artists(song_correct.artists[0].id)
        id_top_4_related_artist = [((artist.name, False), (spotify.artist_top_tracks(artist.id, 'IT')[randint(0,4)].name, False)) for artist in sample(related_artists, k=4,)]
        for song in id_top_4_related_artist:
            result.append(song)
        print(result)
    except:
        generic_error = True

    while song_correct.preview_url is None or generic_error:
        generic_error = False
        try:
            song_correct_all = choice(my_playlist)
            song_correct = song_correct_all.track
            my_playlist.remove(song_correct_all)
            result = [((song_correct.artists[0].name, True), (song_correct.name, True))]
            related_artists = spotify.artist_related_artists(song_correct.artists[0].id)
            id_top_4_related_artist = [
                ((artist.name, False), (spotify.artist_top_tracks(artist.id, 'IT')[randint(0, 4)].name, False)) for
                artist in sample(related_artists, k=4, )]
            for song in id_top_4_related_artist:
                result.append(song)
            print(result)
        except Exception as ex:
            print(ex)
            generic_error = True

    return {'songs_artists': result, 'current_playing': song_correct.preview_url}

@app.get('/artist')
def get_artists():
    return None


if __name__ == '__main__':
    print("Server starting")
    app.run(port=(os.getenv('PORT', 5000)))

