#Music Genius - Overview and guide for users

Ever had a friend say something like, oh man, Lena Horne, those were the days, and have no fing clue who Lena Horne is? But know that she's obviously an icon you're embarassed to admit it? Don't you wish you had a tool to quickly look up an artist and get an overview of who they are?

Crave no more! Simply type a name into Music Genius to get their top tracks and related artists on Spotify, their most popular recent headlines, and their overview from Wikipedia!

Click green link on the page to access related artist information, tracks, and headlines!

#How to run the program

Simply run app.py locally or on your server! This is the controller to the MVC framework built on Flask, Jinja, SQLlite. Here's to Python power!

#Limitations

Currently this application only works if you spell the artist name correctly (case insensitive) and if that artist is on spotify, and on wikipedia.

#Data Sources Used

##Spotify top tracks and related artists

Obtained via Spotify Web API Search, Artists, and Tracks endpoints, see documentation from Spotify, and Spotify, an excellent Python library for using the Spotify API. Authenticate with your Spotify account via OAuth2

Spotify Web API: https://developer.spotify.com/web-api/
Spotipy Documentation: http://spotipy.readthedocs.io/en/latest/

##Google News headlines

Obtained via Google News API's 'Everything' endpoint, results sorted in descending oder by popularity ('sortBy':'popularity')

Google News API - Everything: https://newsapi.org/docs/endpoints/everything

##Wikipedia overview

Scraped from the web with Beautiful Soup. Takes the first two paragraphs from the artist's wikipedia page

#Code Structure

##model.py

####Data request functions, these functions either pull data from web or cache, classes them, and then writes them to the database

search_artists - Search artist by name from Spotify's records
get_others_in_genre - Get related artists to the searched artist
get_top_tracks - Get the searched artist's top tracks
get_headlines - Get the searched artist's most popular headlines
get_wiki_page - Scrape wikipeida for the searched artist's overview

##app.py

The controller this runs functions from the model, and queries their results to be passed on to the view.

artist_display - run artists search and query relevant data from the DB to show in the view.

related_dislpay - run related artists query based on searched artist, and query relevant data to show in the view.

track_display - run top tracks query based on searched artist, and query relevant data to show in the view.

article_display - run headlines query based on searched artist, and query relevant data to show in the view.



