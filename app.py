import sys
import secrets
from flask import Flask, render_template

from bs4 import BeautifulSoup

import requests

import spotipy
import spotipy.util as util		








#SPOTIFY AUTHENTICATION

#OAuth with Spotify Web API, based on Spotipy's 'Authorization Code Flow'
##http://spotipy.readthedocs.io/en/latest/#installation


username = "ND_Murray"
scope = "user-library-read"
redirect_uri = "https://accounts.spotify.com/authorize" #this will become the URL your app landing page
S_CLIENT_ID = secrets.SPOTIFY_CLIENT_ID
S_CLIENT_SECRET = secrets.SPOTIFY_CLIENT_SECRET

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

#SPOTIFY REQUESTS - NEEDS DB Population

# - Uses Spotify Web API Search Endpoint: https://beta.developer.spotify.com/documentation/web-api/reference/search/search/ 
#### - For later, it's in the cache, pull it from the database
#### - Otherwise, write it to the cache and database


#Search based on artist name
def search_artists(artist):
	results = SP.search(artist,type='artist')

	output = []
	for item in results['artists']['items']:
		if len(item['genres']) < 1:
			artist_data = (item['name'],"no genre",item['popularity'],item['id'])
		else:
			artist_data = (item['name'],item['genres'][0],item['popularity'],item['id'])
		output.append(artist_data)
	# print(output)
	return output

#Playlist search based on genre from first result in artist search
## - later we'll change this to let the user pick the artist to show results based on 
## - Need to work out how to sort response by popularity, otherwise we might have to toss this

def get_others_in_genre(artist):
	artist = search_artists(artist)[0][3] #id from first artist for now
	results1 = SP.artist_related_artists(artist)
	output1 = []

	print(results1)

	for item in results1['artists']:
		if len(item['genres']) < 1:
			artist_data = (item['name'],"no genre",item['popularity'],item['id'])
		else:
			artist_data = (item['name'],item['genres'][0],item['popularity'],item['id'])
		output1.append(artist_data)


	results2 = SP.artist_related_artists(artist)
	output2 = []

	for item in results2['artists']:
		if len(item['genres']) < 1:
			artist_data = (item['name'],"no genre",item['popularity'],item['id'])
		else:
			artist_data = (item['name'],item['genres'][0],item['popularity'],item['id'])
		output2.append(artist_data)

	print(output2)

	output = output1

	for item in output2:
		output.append(item)


	output1.append(output2)
	print(output)
	return output


get_others_in_genre('Kendrick')


#WIKIPEDIA - SCRAPE IT - NEEDS CACHE

def get_wiki_page(artist):
	base_url = "https://en.wikipedia.org/wiki/"
	artist_clean = artist.replace(" ","_")
	page_url = base_url + artist_clean

	page_text = requests.get(page_url).text
	print(pull_wiki_overview(page_text))

def pull_wiki_overview(page_text):
	overview = ""
	soup = BeautifulSoup(page_text, 'html.parser')
	container = soup.find('div',attrs={'class':'mw-parser-output'})
	paras = container.find_all('p')

	for p in paras[:2]: #First 2 paragraphs only
		overview += "\n" + p.text + "\n"

	return overview


#get_wiki_page("Michael Jackson")





