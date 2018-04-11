import sys
import secrets
import sqlite3
from flask import Flask, render_template
from bs4 import BeautifulSoup
import json
import requests
import spotipy
import spotipy.util as util		

#SET UP THE DATABASE

DBNAME = "mg.sqlite"

def create_mg_db():
	try:
		conn = sqlite3.connect(DBNAME)
		cur = conn.cursor()
	except Exception as e:
		print(e)

	statement = '''
		DROP TABLE IF EXISTS 'Artists';
	'''
	cur.execute(statement)

	statement = '''
		DROP TABLE IF EXISTS 'Articles';
	'''

	cur.execute(statement)
	conn.commit()

def stand_up_db_tables():
	conn = sqlite3.connect(DBNAME)
	cur = conn.cursor()

	#Artists
	statement = '''
	CREATE TABLE 'Artists' (
		'Id' INTEGER PRIMARY KEY AUTOINCREMENT,
		'Spotify_Id' TEXT NOT NULL,
		'Name' TEXT NOT NULL,
		'Genre' TEXT NOT NULL,
		'Popularity' INTEGER NOT NULL,
		'Followers' INTEGER NOT NULL

	)

	'''

	cur.execute(statement)

	#Insert Articles table creation code here

	conn.commit()
	conn.close()

def update_artists_table(output): #output is a list of tuples
	conn = sqlite3.connect(DBNAME)
	cur = conn.cursor()
	data = output

	for row in data:
		cur.execute("INSERT INTO Artists VALUES(NULL, ?, ?, ?, ?, ?)",row)

	conn.commit()
	conn.close()

create_mg_db()
stand_up_db_tables()


#CACHING SYSTEM

WIKI_CACHE_FILE = "wiki_cache.json"


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
			artist_data = (item['id'],item['name'],"no genre",item['popularity'],item['followers']['total'])
		else:
			artist_data = (item['id'],item['name'],item['genres'][0],item['popularity'],item['followers']['total'])
		output.append(artist_data)
	# print(output)
	return output

#Playlist search based on genre from first result in artist search
## - later we'll change this to let the user pick the artist to show results based on 
## - Need to work out how to sort response by popularity, otherwise we might have to toss this

def get_others_in_genre(artist):
	artist = search_artists(artist)[0][0] #id from first artist for now
	results = SP.artist_related_artists(artist)
	output = []

	for item in results['artists']:
		if len(item['genres']) < 1:
			artist_data = (item['id'],item['name'],"no genre",item['popularity'],item['followers']['total'])
		else:
			artist_data = (item['id'],item['name'],item['genres'][0],item['popularity'],item['followers']['total'])
		output.append(artist_data)


	print(output)
	return output


data = get_others_in_genre('James Brown')

update_artists_table(data)


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





