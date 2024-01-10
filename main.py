import os
from spotify import Spotify

SPOTIFY_CLIENT_ID = os.environ['SPOTIFY_CLIENT_ID']
SPOTIFY_CLIENT_SECRET = os.environ['SPOTIFY_CLIENT_SECRET']
SPOTIFY_USERNAME = os.environ['SPOTIFY_USERNAME']

spotify = Spotify(user_id=SPOTIFY_USERNAME, client_id=SPOTIFY_CLIENT_ID, client_secret=SPOTIFY_CLIENT_SECRET, first_time=False) 
spotify.shuffle_playlist(os.environ['PLAYLIST_ID'])


