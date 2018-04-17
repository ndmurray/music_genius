from flask import Flask, render_template, request
import model

app = Flask(__name__)


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

#Process objects for use on the web page

#Arists 

#returns dictionary of artist name : URL
def related_display(artist): 
	related_data = model.get_others_in_genre(artist) #request data with functions defined in the model 
	related_dict = {}
	for item in related_data:
		related_dict[item.name] = item.artist_url
	return related_dict

#Tracks
def track_display(artist):
	track_data = model.get_top_tracks(artist)
	track_dict = {}
	for item in track_data:
		track_dict[item.name] = item.track_url
	return track_dict

#Articles
def article_display(artist):
	article_data =  model.get_headlines(artist)
	article_dict = {}
	for item in article_data:
		article_dict[item.title] = item.url
	return article_dict


#Staging lainding page

@app.route('/index2', methods=['GET', 'POST'])
def staging():
	return render_template('index2.html',artist=artist,related=related,overview=overview,tracks=tracks,articles=articles)

#Landing Page
@app.route('/', methods=['GET', 'POST'])
def index():
	try:
		if request.method == 'POST':
			artist_input = request.form['artist-entry'] #name attribute of the form in the view, gets the term the user searched on.
			artist = model.search_artists(artist_input)[0].name#First artist in search results

			overview = model.get_wiki_page(artist)
			related = related_display(artist)
			tracks = track_display(artist)
			articles = article_display(artist)
				
		else:
			artist = "Danny Brown"
			overview = model.get_wiki_page(artist)
			related = related_display(artist)
			tracks = track_display(artist)
			articles = article_display(artist)



		return render_template('index.html',artist=artist,related=related,overview=overview,tracks=tracks,articles=articles)
	except:
		return render_template('error.html')



if __name__ == '__main__':
	app.run(debug=True)