import sys
import secrets
import sqlite3
from bs4 import BeautifulSoup
import json
import requests
import spotipy
import spotipy.util as util		

#ISSUES
##Clear the cache before you run this thing for real, so that Danny Brown's data is in the db

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
		DROP TABLE IF EXISTS 'Tracks';
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
		'Followers' INTEGER NOT NULL,
		'Image' TEXT NOT NULL,
		"URL" TEXT NOT NULL

	)

	'''

	cur.execute(statement)

	#Tracks
	statement = '''
	CREATE TABLE 'Tracks' (
		'Id' INTEGER PRIMARY KEY AUTOINCREMENT,
		'Spotify_Id' TEXT NOT NULL,
		'Name' TEXT NOT NULL,
		'Artist' TEXT NOT NULL,
		'Popularity' INTEGER NOT NULL,
		'Album' TEXT NOT NULL,
		'Release Date' TEXT NOT NULL,
		'URL' TEXT NOT NULL

	)

	'''

	cur.execute(statement)

	#Insert Articles table creation code here

	conn.commit()
	conn.close()

def update_artists_table(output): #output is a list Artist objects
	conn = sqlite3.connect(DBNAME)
	cur = conn.cursor()
	data = output

	for row in data:
		cur.execute("INSERT INTO Artists VALUES(NULL, ?, ?, ?, ?, ?, ?, ?)",row.db_row())

	conn.commit()
	conn.close()

def update_tracks_table(output):
	conn = sqlite3.connect(DBNAME)
	cur = conn.cursor()
	data = output

	for row in data:
		cur.execute("INSERT INTO Tracks VALUES(NULL, ?, ?, ?, ?, ?, ?, ?)",row.db_row())

	conn.commit()
	conn.close()

create_mg_db()
stand_up_db_tables()


#LOAD CACHE FILES

##file
WIKI_CACHE_FILE_NAME = "wiki_cache.json"
SP_CACHE_FILE_NAME = "spotify_cache.json"
G_CACHE_FILE_NAME = "google_cache.json"


##Load cache files to dictionary
try:
	wiki_cache_file = open(WIKI_CACHE_FILE_NAME, 'r')
	wiki_cache_str = wiki_cache_file.read()
	WIKI_CACHE_DICT = json.loads(wiki_cache_str)
	wiki_cache_file.close() #WIKI
except:
	WIKI_CACHE_DICT = {}

try:
	sp_cache_file = open(SP_CACHE_FILE_NAME, 'r')
	sp_cache_str = sp_cache_file.read()
	SP_CACHE_DICT = json.loads(sp_cache_str)
	sp_cache_file.close()#SPOTIFY
except:
	SP_CACHE_DICT = {}

try:
	g_cache_file = open(G_CACHE_FILE_NAME, 'r')
	g_cache_str = g_cache_file.read()
	G_CACHE_DICT = json.loads(g_cache_str)
	g_cache_file.close() #GOOGLE
except:
	G_CACHE_DICT = {}

##Unique Ids

#Unique Id for request #same for all data sources!

def unique_id(baseurl,artist):
	return baseurl + "--" + artist


#DEFINE CLASSES FOR ARTIST, TRACK, AND ARTICLE

class Artist():
	def __init__(self, spotify_id="None.", name="None.", genre="None.", popularity="None.", followers="None.", image_url="None.", artist_url="None."):
		self.spotify_id = spotify_id	
		self.name = name
		self.genre = genre
		self.popularity = popularity
		self.followers = followers
		self.image_url = image_url
		self.artist_url = artist_url	

	def db_row(self):
		return (self.spotify_id, self.name, self.genre, self.popularity, self.followers, self.image_url, self.artist_url)

	def __str__(self):
		return self.name + ", " + self.genre + ", popularity = " + str(self.popularity)

class Track():
	def __init__(self="None.", spotify_id="None.", name="None.", artist="None.", popularity="None.", album="None.", release_date="",track_url="None."):
		self.spotify_id = spotify_id	
		self.name = name
		self.artist = artist
		self.popularity = popularity
		self.album = album
		self.release_date = release_date
		self.track_url = track_url

	def db_row(self):
		return (self.spotify_id, self.name, self.artist, self.popularity, self.album, self.release_date, self.track_url)

	def __str__(self):
		return '"' + self.name + '" by ' + self.artist + '. Off of "' + self.album + ", " +self.release_date

class Headline():

	pass



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

#SPOTIFY REQUESTS - NEEDS CACHE

# - Uses Spotify Web API Search Endpoint: https://beta.developer.spotify.com/documentation/web-api/reference/search/search/ 
#### - For later, it's in the cache, pull it from the database
#### - Otherwise, write it to the cache and database


#Search based on artist name
def search_artists(artist="Danny Brown"):
	base_url = "https://api.spotify.com/v1"
	artist_clean = artist.replace(" ","_")

	#Decide whether data comes from web or cache
	unique_ident = unique_id(base_url,artist_clean)

	if unique_ident in SP_CACHE_DICT:
		#Get data from cache
		print("Getting cached Spotify data for " + artist)
		results = SP_CACHE_DICT[unique_ident]
		output = []
		for item in results['artists']['items']:
			if len(item['genres']) < 1 and len(item['images']) < 1:
				artist_data = Artist(item['id'],item['name'],"no genre",item['popularity'],item['followers']['total'],"no image",item['external_urls']['spotify'])
			elif len(item['genres']) < 1:
				artist_data = Artist(item['id'],item['name'],"no genre",item['popularity'],item['followers']['total'],item['images'][0]['url'],item['external_urls']['spotify'])
			elif len(item['images']) < 1:
				artist_data = Artist(item['id'],item['name'],item['genres'][0],item['popularity'],item['followers']['total'],"no image",item['external_urls']['spotify'])
			else:
				artist_data = Artist(item['id'],item['name'],item['genres'][0],item['popularity'],item['followers']['total'],item['images'][0]['url'],item['external_urls']['spotify'])
			output.append(artist_data)
		return output
	else:
		#Pull new data and format it
		print("Getting fresh data from Spotify for " + artist)
		results = SP.search(artist,type='artist')
		output = []
		for item in results['artists']['items']:
			if len(item['genres']) < 1 and len(item['images']) < 1:
				artist_data = Artist(item['id'],item['name'],"no genre",item['popularity'],item['followers']['total'],"no image")
			elif len(item['genres']) < 1:
				artist_data = Artist(item['id'],item['name'],"no genre",item['popularity'],item['followers']['total'],item['images'][0]['url'])
			elif len(item['images']) < 1:
				artist_data = Artist(item['id'],item['name'],item['genres'][0],item['popularity'],item['followers']['total'],"no image")
			else:
				artist_data = Artist(item['id'],item['name'],item['genres'][0],item['popularity'],item['followers']['total'],item['images'][0]['url'])
			output.append(artist_data)
		
		#Write new spotify data to the cache
		print("Writing stankin' fresh Spotify data for " + artist + " to the cache.")
		SP_CACHE_DICT[unique_ident] = results
		dumped_sp_data = json.dumps(SP_CACHE_DICT)
		sp_cache_file = open(SP_CACHE_FILE_NAME, 'w')
		sp_cache_file.write(dumped_sp_data)
		sp_cache_file.close()
		print("Fresh data for " + artist + " written to cache.")
		return output

def get_others_in_genre(artist):

	base_url = "https://api.spotify.com/v1"
	artist_clean = artist.replace(" ","_") + "_related"

	#Decide whether data comes from web or cache
	unique_ident = unique_id(base_url,artist_clean)
	
	if unique_ident in SP_CACHE_DICT:
		#Get data from cache
		print("Getting cached related artist data for " + artist)
		results = SP_CACHE_DICT[unique_ident]
		output = []

		for item in results['artists']:
			if len(item['genres']) < 1 and len(item['images']) < 1:
				artist_data = Artist(item['id'],item['name'],"no genre",item['popularity'],item['followers']['total'],"no image",item['external_urls']['spotify'])
			elif len(item['genres']) < 1:
				artist_data = Artist(item['id'],item['name'],"no genre",item['popularity'],item['followers']['total'],item['images'][0]['url'],item['external_urls']['spotify'])
			elif len(item['images']) < 1:
				artist_data = Artist(item['id'],item['name'],item['genres'][0],item['popularity'],item['followers']['total'],"no image",item['external_urls']['spotify'])
			else:
				artist_data = Artist(item['id'],item['name'],item['genres'][0],item['popularity'],item['followers']['total'],item['images'][0]['url'],item['external_urls']['spotify'])
			output.append(artist_data)

		print(output)
		return output

	else:
		print("Getting fresh related artist data from Spotify for " + artist)
		search_results = search_artists(artist)
		artist = search_results[0].spotify_id #id from first artist for now
		artist_display =  search_results[0].name
		results = SP.artist_related_artists(artist)
		output = []

		for item in results['artists']:
			if len(item['genres']) < 1 and len(item['images']) < 1:
				artist_data = Artist(item['id'],item['name'],"no genre",item['popularity'],item['followers']['total'],"no image")
			elif len(item['genres']) < 1:
				artist_data = Artist(item['id'],item['name'],"no genre",item['popularity'],item['followers']['total'],item['images'][0]['url'])
			elif len(item['images']) < 1:
				artist_data = Artist(item['id'],item['name'],item['genres'][0],item['popularity'],item['followers']['total'],"no image")
			else:
				artist_data = Artist(item['id'],item['name'],item['genres'][0],item['popularity'],item['followers']['total'],item['images'][0]['url'])
			output.append(artist_data)

		#Write new spotify data to the cache
		print("Writing related Spotify data for " + artist_display + " to the cache.")
		SP_CACHE_DICT[unique_ident] = results
		dumped_sp_data = json.dumps(SP_CACHE_DICT)
		sp_cache_file = open(SP_CACHE_FILE_NAME, 'w')
		sp_cache_file.write(dumped_sp_data)
		sp_cache_file.close()
		print("Fresh related artist data for " + artist_display + " written to cache.")

		#Update the database
		update_artists_table(output)

		return output

def get_top_tracks(artist):
	base_url = "https://api.spotify.com/v1"
	artist_clean = artist.replace(" ","_"+"_top-tracks")

	#Decide whether data comes from web or cache
	unique_ident = unique_id(base_url,artist_clean)
	
	if unique_ident in SP_CACHE_DICT:
		#Get data from cache
		print("Getting " + artist + "'s top tracks.")
		results = SP_CACHE_DICT[unique_ident]
		output = []
		for item in results['tracks']:
			track_data = Track(item['id'],item['name'],item['artists'][0]['name'],item['popularity'],item['album']['name'],item['album']['release_date'],item['external_urls']['spotify'])
			output.append(track_data)

		return output

	else:
		print("Getting fresh top tracks for " + artist)
		search_results = search_artists(artist)
		artist = search_results[0].spotify_id #id (Artist class) from first artist for now
		artist_display =  search_results[0].name #name, form the Artist class
		results = SP.artist_top_tracks(artist, country="US")
		output = []

		for item in results['tracks']:
			track_data = Track(item['id'],item['name'],item['artists'][0]['name'],item['popularity'],item['album']['name'],item['album']['release_date'],item['external_urls']['spotify'])
			output.append(track_data)



		# #Write new spotify data to the cache
		print("Writing top tracks data for " + artist_display + " to the cache.")
		SP_CACHE_DICT[unique_ident] = results
		dumped_sp_data = json.dumps(SP_CACHE_DICT)
		sp_cache_file = open(SP_CACHE_FILE_NAME, 'w')
		sp_cache_file.write(dumped_sp_data)
		sp_cache_file.close()
		print("Fresh top track data for " + artist_display + " written to cache.")

		#Update the database
		update_tracks_table(output)

		print("TRAKCS OUTPUT")
		print(output)

		return output

get_others_in_genre('Coleman Hawkins')
search_artists('Coleman Hawkins')
get_top_tracks('Coleman Hawkins')


#GOOGLE NEWS 


def get_headlines(artist):
	pass


#WIKIPEDIA - SCRAPE IT

#Scrape code wiki overview
def scrape_wiki_overview(page_text):
	overview = ""
	soup = BeautifulSoup(page_text, 'html.parser')
	container = soup.find('div',attrs={'class':'mw-parser-output'})
	paras = container.find_all('p')

	for p in paras[:2]: #First 2 paragraphs only
		overview += "\n" + p.text + "\n"

	return overview

#Get wiki page and scrape
def get_wiki_page(artist):
	base_url = "https://en.wikipedia.org/wiki/"
	artist_clean = artist.replace(" ","_")
	page_url = base_url + artist_clean

	unique_ident = unique_id(base_url,artist_clean)

	if unique_ident in WIKI_CACHE_DICT:
		#Get data from cache
		print("Getting cached Wiki data for " + artist)
		overview = WIKI_CACHE_DICT[unique_ident]
		return overview
	else:
		#Pull wiki data and soupify
		print("Getting fresh wiki data for " + artist)
		page_text = requests.get(page_url).text
		overview = scrape_wiki_overview(page_text)

		#Write new data to cache
		print("Writing fresh overview of " + artist + " to cache.")
		WIKI_CACHE_DICT[unique_ident] = overview
		dumped_wiki_data = json.dumps(WIKI_CACHE_DICT)
		wiki_cache_file = open(WIKI_CACHE_FILE_NAME, 'w')
		wiki_cache_file.write(dumped_wiki_data)
		wiki_cache_file.close()
		print("Fresh data for " + artist + " written to cache.")
		return overview




get_wiki_page("Coleman Hawkins")





