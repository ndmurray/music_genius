import sys
import secrets
import sqlite3
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
		'Followers' INTEGER NOT NULL,
		'Image' TEXT NOT NULL

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
		cur.execute("INSERT INTO Artists VALUES(NULL, ?, ?, ?, ?, ?, ?)",row)

	conn.commit()
	conn.close()

create_mg_db()
stand_up_db_tables()


#LOAD CACHE FILES

##file
WIKI_CACHE_FILE_NAME = "wiki_cache.json"
SP_CACHE_FILE_NAME = "spotify_cache.json"


##Load cache files to dictionary
try:
	wiki_cache_file = open(WIKI_CACHE_FILE_NAME, 'r')
	wiki_cache_str = wiki_cache_file.read()
	WIKI_CACHE_DICT = json.loads(wiki_cache_str)
	wiki_cache_file.close()
except:
	WIKI_CACHE_DICT = {}

try:
	sp_cache_file = open(SP_CACHE_FILE_NAME, 'r')
	sp_cache_str = sp_cache_file.read()
	SP_CACHE_DICT = json.loads(sp_cache_str)
	sp_cache_file.close()
except:
	SP_CACHE_DICT = {}


##Unique Ids

#Unique Id for request #same for all data sources!

def unique_id(baseurl,artist):
	return baseurl + "--" + artist


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
def search_artists(artist):
	base_url = "https://api.spotify.com/v1"
	artist_clean = artist.replace(" ","_")

	#Decide whether data comes from web or cache
	unique_ident = unique_id(base_url,artist_clean)

	if unique_ident in SP_CACHE_DICT:
		#Get data from cache
		print("Getting cached Spotify data for " + artist)
		return SP_CACHE_DICT[unique_ident]
	else:
		#Pull new data and format it
		print("Getting fresh data from Spotify for " + artist)
		results = SP.search(artist,type='artist')
		print(results)
		output = []
		for item in results['artists']['items']:
			if len(item['genres']) < 1:
				artist_data = (item['id'],item['name'],"no genre",item['popularity'],item['followers']['total'],item['images'][0]['url'])
			else:
				artist_data = (item['id'],item['name'],item['genres'][0],item['popularity'],item['followers']['total'],item['images'][0]['url'])
			output.append(artist_data)
		
		#Write new spotify data to the cache
		print("Writing stankin' fresh Spotify data for " + artist + " to the cache.")
		SP_CACHE_DICT[unique_ident] = output
		dumped_sp_data = json.dumps(SP_CACHE_DICT)
		sp_cache_file = open(SP_CACHE_FILE_NAME, 'w')
		sp_cache_file.write(dumped_sp_data)
		sp_cache_file.close()
		print("Fresh data for " + artist + " writtent to cache.")
		return output


#Playlist search based on genre from first result in artist search
## - later we'll change this to let the user pick the artist to show results based on 
## - Need to work out how to sort response by popularity, otherwise we might have to toss this

def get_others_in_genre(artist):

	base_url = "https://api.spotify.com/v1"
	artist_clean = artist.replace(" ","_"+"_related")

	#Decide whether data comes from web or cache
	unique_ident = unique_id(base_url,artist_clean)
	
	if unique_ident in SP_CACHE_DICT:
		#Get data from cache
		print("Getting cached related artist data for " + artist)
		return SP_CACHE_DICT[unique_ident]
	else:
		print("Getting fresh related artist data from Spotify for " + artist)
		artist = search_artists(artist)[0][0] #id from first artist for now
		results = SP.artist_related_artists(artist)
		output = []

		for item in results['artists']:
			if len(item['genres']) < 1:
				artist_data = (item['id'],item['name'],"no genre",item['popularity'],item['followers']['total'],item['images'][0]['url'])
			else:
				artist_data = (item['id'],item['name'],item['genres'][0],item['popularity'],item['followers']['total'],item['images'][0]['url'])
			output.append(artist_data)

		#Write new spotify data to the cache
		print("Writing related Spotify data for " + artist + " to the cache.")
		SP_CACHE_DICT[unique_ident] = output
		dumped_sp_data = json.dumps(SP_CACHE_DICT)
		sp_cache_file = open(SP_CACHE_FILE_NAME, 'w')
		sp_cache_file.write(dumped_sp_data)
		sp_cache_file.close()
		print("Fresh related artist data for " + artist + " written to cache.")

		return output


data = get_others_in_genre('Earl Sweatshirt')

update_artists_table(data)


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
		print("Fresh data for " + artist + " writtent to cache.")
		return overview




get_wiki_page("Earl Sweatshirt")





