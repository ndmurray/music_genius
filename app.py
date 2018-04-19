from flask import Flask, render_template, request
import model
import sqlite3

app = Flask(__name__)

#Import DB reference from model
DBNAME = model.DBNAME

#Clear cache
def clear_cache():
	sp_cache_file = open(model.SP_CACHE_FILE_NAME, 'w')
	sp_cache_file.write("")
	sp_cache_file.close()

	g_cache_file = open(model.G_CACHE_FILE_NAME, 'w')
	g_cache_file.write("")
	g_cache_file.close()

	wiki_cache_file = open(model.WIKI_CACHE_FILE_NAME, 'w')
	wiki_cache_file.write("")
	wiki_cache_file.close()

clear_cache()

#Pull DB data for use on the web page

#Arists 
def artist_display(artist): 

	try:
		conn = sqlite3.connect(DBNAME)
		cur = conn.cursor()
	except Error as e:
		print(e)

	#request data and log it in the DB
	artist_result = model.search_artists(artist) 

	#get id for query matching
	artist_id = (artist_result[0],)

	#Top five related artists that link to the most recent artist added to the artists table (this table contains all artists the user searched)
	statement = """
	SELECT Name, Image
	FROM Artists
	WHERE Spotify_Id = ?
	ORDER BY Id DESC
	LIMIT 1
	"""

	pull = cur.execute(statement,artist_id).fetchall()

	artist_list = []
	for row in pull: 
		artist_list.append(row[0])
		artist_list.append(row[1])
	return artist_list

	conn.close()


#Related Artists

#returns dictionary of artist name : URL
def related_display(artist): 

	try:
		conn = sqlite3.connect(DBNAME)
		cur = conn.cursor()
	except Error as e:
		print(e)

	#request data and log it in the DB
	model.get_others_in_genre(artist) 

	#Top five related artists that link to the most recent artist added to the artists table (this table contains all artists the user searched)
	statement = """
	SELECT r.Name, r.URL
	FROM RelatedArtists as r
	JOIN Artists AS a
		ON r.Searched_Artist_Id = a.Id
	ORDER BY r.Searched_Artist_Id DESC
	LIMIT 5
	"""

	pull = cur.execute(statement).fetchall()

	related_dict = {}
	for row in pull: 
		related_dict[row[0]] = row[1]
	return related_dict

	conn.close()

#Tracks
def track_display(artist):

	try:
		conn = sqlite3.connect(DBNAME)
		cur = conn.cursor()
	except Error as e:
		print(e)

	#Make the reuest and log to db
	model.get_top_tracks(artist)

	#Top five tracks that link to the most recent artist added to the artists table (this table contains all artists the user searched)
	statement = """
	SELECT t.Name, t.URL
	FROM Tracks as t
	JOIN Artists AS a
		ON t.Searched_Artist_Id = a.Id
	ORDER BY t.Searched_Artist_Id DESC
	LIMIT 5
	"""

	pull = cur.execute(statement).fetchall()

	track_dict = {}
	for row in pull: #Only top 5
		track_dict[row[0]] = row[1]
	return track_dict

	conn.close()

#Articles
def article_display(artist):

	try:
		conn = sqlite3.connect(DBNAME)
		cur = conn.cursor()
	except Error as e:
		print(e)

	#Make the request and log it to the DB
	model.get_headlines(artist)

	#Top five articles that link to the most recent artist added to the artists table (this table contains all artists the user searched)
	statement = """
	SELECT h.Title, h.URL, h.Source, h.PublishedAt
	FROM Articles as h
	JOIN Artists AS a
		ON h.Searched_Artist_Id = a.Id
	ORDER BY h.Searched_Artist_Id DESC
	LIMIT 5
	"""

	pull = cur.execute(statement).fetchall()

	article_dict = {}
	for row in pull:#Only top 5
		article_dict[row[0]] = [row[1], row[2], row[3]]
	return article_dict


#Landing Page
@app.route('/', methods=['GET', 'POST'])
def index():
	# try:
	if request.method == 'POST':
		artist_input = request.form['artist-entry'] #name attribute of the form in the view, gets the term the user searched on.
		artist_result = artist_display(artist_input)#First artist in search results
		artist_name = artist_result[0]
		image_url = artist_result[1]


		overview = model.get_wiki_page(artist_name)
		related = related_display(artist_name)
		tracks = track_display(artist_name)
		articles = article_display(artist_name)
			
	else:
		artist_result = artist_display("Amy Winehouse")
		artist_name = artist_result[0]
		image_url = artist_result[1]
		overview = model.get_wiki_page(artist_name)
		related = related_display(artist_name)
		tracks = track_display(artist_name)
		articles = article_display(artist_name)



	return render_template('index.html',artist_name=artist_name,image_url=image_url,related=related,overview=overview,tracks=tracks,articles=articles)
	# except:
		# return render_template('error.html')



if __name__ == '__main__':
	app.run(debug=True)