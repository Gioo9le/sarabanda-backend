import os
from dataclasses import dataclass
from random import choice, randint, sample
from typing import Optional, Any, List

import tekore as tk
import uvicorn
from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from redis import Redis

from config import F_HOSTNAME, B_HOSTNAME, REDIS_URL

ROCK_PLAYLIST = '4jOqGKvV7iu0ojea2pt9Te?si=843dc28cc8954a00'
POP_PLAYLIST = '6mtYuOxzl58vSGnEDtZ9uB?si=8f9fe155c5374268'

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


cred = tk.Credentials(
    client_id="3d5c756645874d03a6ddb0b5b2e3574c",
    client_secret="a2ad98b4e0dd4b39bd06a07abb4a7b34",
    redirect_uri=f"{B_HOSTNAME}/code",
)

# spotify: tk.Spotify
# my_playlist: Optional[List[Any]] = None

@dataclass
class User:
    code: str
    client: tk.Spotify
    playlist_id: Optional[str]

async def get_user(code: str) -> User:
    r = Redis.from_url(REDIS_URL)
    token = r.get(code).decode("utf-8")
    playlist_id = r.get(f"{code}:playlist").decode('utf-8') if r.get(f"{code}:playlist") is not None else None
    print(token)
    client = tk.Spotify(token)
    print(client.current_user().display_name)
    return User(
        code=code,
        client=client,
        playlist_id=playlist_id
    )



@app.get("/login")
def login():
    return cred.user_authorisation_url(scope=tk.scope.playlist_read_private)


@app.get("/code")
def get_access_token(code: str):
    # global spotify
    # global my_playlist
    r = Redis.from_url(REDIS_URL)
    token = cred.request_user_token(code).access_token
    r.set(code, token, ex=600)
    # spotify = tk.Spotify(token)
    # my_playlist_id = spotify.playlists(spotify.current_user().id).items[1].id
    # my_playlist = spotify.playlist(my_playlist_id).tracks.items
    return RedirectResponse(f"{F_HOSTNAME}/login/{code}")


@app.get("/song")
def get_songs(user: User = Depends(get_user)):
    my_playlist_id = user.client.playlists(user.client.current_user().id).items[1].id
    my_playlist = user.client.playlist(user.playlist_id).tracks.items

    generic_error = False
    try:
        song_correct_all = choice(my_playlist)
        song_correct = song_correct_all.track
        my_playlist.remove(song_correct_all)
        result = [((song_correct.artists[0].name, True), (song_correct.name, True))]
        related_artists = user.client.artist_related_artists(song_correct.artists[0].id)
        id_top_4_related_artist = [
            (
                (artist.name, False),
                (user.client.artist_top_tracks(artist.id, "IT")[randint(0, 4)].name, False),
            )
            for artist in sample(
                related_artists,
                k=4,
            )
        ]
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
            related_artists = user.client.artist_related_artists(song_correct.artists[0].id)
            id_top_4_related_artist = [
                (
                    (artist.name, False),
                    (
                        user.client.artist_top_tracks(artist.id, "IT")[randint(0, 4)].name,
                        False,
                    ),
                )
                for artist in sample(
                    related_artists,
                    k=4,
                )
            ]
            for song in id_top_4_related_artist:
                result.append(song)
            print(result)
        except Exception as ex:
            print(ex)
            generic_error = True

    return {"songs_artists": result, "current_playing": song_correct.preview_url}

@app.get('/playlists')
def get_playlists():
    return [
        {'name': 'ROCK', 'id': '4jOqGKvV7iu0ojea2pt9Te'},
        {'name': 'POP', 'id': '6mtYuOxzl58vSGnEDtZ9uB'},
        {'name': 'RAP', 'id': '37i9dQZF1DWSxF6XNtQ9Rg'},
        {'name': 'EDM', 'id': '37i9dQZF1DX3Kdv0IChEm9'},
        {'name': 'CANTAUTORI', 'id': '37i9dQZF1DX3EvTrESVmN6'},
        {'name': 'INDIE', 'id': '37i9dQZF1DX6ShdbyN9CkW'},
        {'name': 'ALTERNATIVE', 'id': '37i9dQZF1DX9GRpeH4CL0S'},
        {'name': 'TOP100', 'id': '3IsxzDS04BvejFJcQ0iVyW'},
    ]

@app.get('/setplaylist')
def set_playlist(playlist_id: str, user: User = Depends(get_user)):
    r = Redis.from_url(REDIS_URL)
    r.set(f"{user.code}:playlist", playlist_id)


@app.get("/artist")
def get_artists(request: Request):
    print(request)
    return None


if __name__ == "__main__":
    print("Server starting")
    uvicorn.run("main:app", port=(int(os.getenv("PORT", 5000))))
