from flask import Flask, render_template, request
import model

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
	try:
		if request.method == 'POST':
			artist_input = request.form['artist-entry'] #name attribute of the form in the view, gets the term the user searched on.
			artist = model.search_artists(artist_input)[0][1]#First artist in search results
			overview = model.get_wiki_page(artist)
			related = model.get_others_in_genre(artist) #request data with functions defined in the model
			top_tracks = model.get_top_tracks(artist)
		else:
			artist = "Danny Brown"
			overview = model.get_wiki_page(artist)
			related = model.get_others_in_genre(artist)
			top_tracks = model.get_top_tracks(artist)
		return render_template('index.html',artist=artist,related=related,overview=overview,top_tracks=top_tracks)
	except:
		return render_template('error.html')



if __name__ == '__main__':
	app.run(debug=True)