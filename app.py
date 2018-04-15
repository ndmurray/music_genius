from flask import Flask, render_template, request
import model

app = Flask(__name__)

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


#Landing Page
@app.route('/', methods=['GET', 'POST'])
def index():
	# try:
	if request.method == 'POST':
		artist_input = request.form['artist-entry'] #name attribute of the form in the view, gets the term the user searched on.
		artist = model.search_artists(artist_input)[0].name#First artist in search results

		overview = model.get_wiki_page(artist)
		related = related_display(artist)
		
		#top_track_names

		
		#top_tracks = 
	else:
		artist = "Danny Brown"
		overview = model.get_wiki_page(artist)
		related = related_display(artist)
		#top_tracks = model.get_top_tracks(artist)

	return render_template('index.html',artist=artist,related=related,overview=overview)
	# except:
		# return render_template('error.html')



if __name__ == '__main__':
	app.run(debug=True)