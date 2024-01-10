import os
import json
import base64
import requests
from discord import Discord
from random import randrange
from urllib.parse import urlencode

discord = Discord()


class Spotify:
    def __init__(self, user_id: str, client_id: str, client_secret: str, first_time=False):
        self.user_id = user_id
        self.client_id = client_id
        self.client_secret = client_secret

        if first_time:
            self.get_auth_url()
        else:
            access_token = self.refresh_token() 
            self.headers = {
                'Authorization': 'Bearer '+ access_token, 
            } 
        


    def get_token(self) -> None: 
        print('get_token')
        headers = {'Content-type': 'application/x-www-form-urlencoded'}
        data = {
            'grant_type': 'client_credentials',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
        }
        response = requests.post(url='https://accounts.spotify.com/api/token', data=data, headers=headers) 
        return self.__validate_response(response, 'token.json')['access_token']
    

    def get_auth_url(self) -> None:
        print('get_auth_url')
        redirect_uri = 'https://www.google.com'
        scope = 'user-library-read playlist-read-private playlist-read-collaborative playlist-modify-private playlist-modify-public'
        headers = {
            'client_id': self.client_id,
            'response_type': 'code',
            'redirect_uri': redirect_uri,
            'scope': scope,
        }
        url = 'https://accounts.spotify.com/authorize?' + urlencode(headers)
        print(url)


    def get_auth_token(self, code: str) -> None:
        print('get_auth_token')
        id_bytes = self.client_id + ':' + self.client_secret
        encoded_credentials = base64.b64encode(id_bytes.encode()).decode()

        headers = {
            'Authorization': 'Basic ' + encoded_credentials,
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        data = {
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': 'https://www.google.com'
        }

        response = requests.post(url='https://accounts.spotify.com/api/token', data=data, headers=headers) 
        return self.__validate_response(response, 'oauth.json')['access_token']


    def refresh_token(self) -> str:
        print('refresh_token')

        id_bytes = self.client_id + ':' + self.client_secret
        encoded_credentials = base64.b64encode(id_bytes.encode()).decode()
        headers = {
            'content-type': 'application/x-www-form-urlencoded',
            'Authorization': 'Basic ' + encoded_credentials
        }
        
        discord.get_file(os.environ["DISCORD_CHANNEL_ID_OAUTH"], 'oauth.json') 
        refresh_token = self.jsonify('oauth.json')['refresh_token']    
        data = {
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token
        }
        response = requests.post(url='https://accounts.spotify.com/api/token', data=data, headers=headers) 
        if response.ok:
            response = response.json() 
            # self.jsonify('oauth.json', response)
            # discord.send_file(os.environ["DISCORD_CHANNEL_ID_OAUTH"], 'oauth.json')
            return response['access_token']
        else:
            raise Exception(response.json())


    def get_playlists(self, path: str='playlist.json') -> list:
        print('get_playlists')
        url = f'https://api.spotify.com/v1/users/{self.user_id}/playlists/?offset=0&limit=50'

        playlists = []
        while url:
            response = requests.get(url=url, headers=self.headers) 
            playlists += response.json().get('items')
            url = response.json().get('next') 
    
        self.jsonify(path, playlists)
        return playlists


    def get_tracks(self) -> None:
        print('get_tracks')
        url = 'https://api.spotify.com/v1/me/tracks'
        response = requests.get(url=url, headers=self.headers) 
        print(response.json())


    def get_playlist(self, id: str) -> None:
        url = f'https://api.spotify.com/v1/playlists/{id}' 
        response = requests.get(url=url, headers=self.headers) 
        return self.__validate_response(response)

    
    def shuffle_playlist(self, id: str) -> None: 
        playlist = self.get_playlist(id)
        track_len = playlist.get('tracks').get('total')
        id = playlist.get('id')
        url = f'https://api.spotify.com/v1/playlists/{id}/tracks' 
        
        headers = self.headers | {'Content-Type': 'application/json'} 

        data = {
            'range_start': randrange(track_len),
            'insert_before': 0,
            'range_length': 1
        }       
        
        response = requests.put(url=url, headers=headers, json=data)
        return self.__validate_response(response=response)


    def __validate_response(self, response: requests.Response, filepath: str='temp.json'):
        if response.ok:
            response = response.json()  
            self.jsonify(filepath, response)
            return response
            
        else:
            raise Exception(response.json())

        
    @staticmethod
    def jsonify(filename: str, content: dict=None) -> None|dict:
        if content: 
            with open(filename, 'w') as f:
                json.dump(content, f)

        else:
            with open(filename) as f:
                return json.load(f)
