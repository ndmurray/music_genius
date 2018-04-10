import sys
import secrets
from flask import Flask, render_template

from bs4 import BeautifulSoup

import requests

import spotipy
import spotipy.util as util		

# app = Flask(__name__)

# @app.route('/')
# def home():
# 	return '<h1>Welcome!</h1>'


#SPOTIFY AUTHENTICATION

#OAuth with Spotify Web API, based on Spotipy's 'Authorization Code Flow'
##http://spotipy.readthedocs.io/en/latest/#installation


username = "ND_Murray"
scope = "user-library-read"
redirect_uri = "https://accounts.spotify.com/authorize" #this will become the URL your app landing page
S_CLIENT_ID = secrets.SPOTIFY_CLIENT_ID
S_CLIENT_SECRET = secrets.SPOTIFY_CLIENT_SECRET

print(S_CLIENT_ID)
print(S_CLIENT_SECRET)

token = util.prompt_for_user_token(username, scope, client_id=S_CLIENT_ID,client_secret=S_CLIENT_SECRET,redirect_uri=redirect_uri)

if token:
	print("Token good!")
	SP = spotipy.Spotify(auth=token)
	# results = sp.current_user_saved_tracks()
	# for item in results['items']:
	#     track = item['track']
	#     print(track['name'] + ' - ' + track['artists'][0]['name'])
else:
    print("Can't get token for", username)






#SPOTIFY REQESTS ARTIST DATA
# - Uses Spotify Web API Search Endpoint: https://beta.developer.spotify.com/documentation/web-api/reference/search/search/ 
#### - For later, it's in the cache, pull it from the database
#### - Otherwise, write it to the cache and database


def get_artist_info(artist):
	# base_url = "https://api.spotify.com/v1/search/"
	# params_dict = {
	# 	'q': artist,
	# 	'type': 'artist'
	# }
	results = SP.search(artist,type='artist')
	print(results)



get_artist_info('Kendrick Lamar')


# if __name__ == '__main__':
# 	app.run(debug=True)