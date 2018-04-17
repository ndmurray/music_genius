import unittest
import model as model
import sqlite3

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

########################################################
#     Test Successful Data Calls and Data Processing

#These calls test both successful requests to the various APIs and 
#web pages used, along with the successful use of classification to 
#handle data.

#########################################################

class TestCalls(unittest.TestCase):


	search1 = model.search_artists("Amy Winehouse")
	search2 = model.search_artists("Danny Brown")
	search3 = model.get_others_in_genre("Amy Winehouse")
	search4 = model.get_top_tracks("Janis Joplin")
	search5 = model.get_headlines("Danny Brown")
	search6 = model.get_wiki_page("Frank Sinatra")


	def testArtistSearch(self):
		#successful artist name
		self.assertEqual(TestCalls.search1[0].name, "Amy Winehouse")
		#successful artist id
		self.assertEqual(TestCalls.search1[0].spotify_id,"6Q192DXotxtaysaqNPy5yR")
		#successful genre
		self.assertEqual(TestCalls.search2[0].genre,"alternative hip hop")

	def testRelated(self):
		#successful related artist count
		self.assertEqual(len(TestCalls.search3),20)
		#succesful related artist accuracy
		self.assertEqual(TestCalls.search3[3].name,"Macy Gray")

	def testTop(self):
		#successful top track count
		self.assertEqual(len(TestCalls.search4),10)
		#successful top track
		self.assertEqual(TestCalls.search4[0].name,"Me and Bobby McGee")
		#successful top track order
		self.assertEqual(TestCalls.search4[2].name,"Maybe")

	def testHeadline(self):
		#successful results
		self.assertEqual(len(TestCalls.search5),20)
		#successful source
		self.assertEqual(TestCalls.search5[0].source,"Deviantart.com")
		#successful description
		self.assertEqual(TestCalls.search5[1].description,"Danny Brown, a rapper from Detroit who has released multiple albums and mixtapes. a music video directed by Jonah Hill, joins Joey Diaz and Lee Syatt live in studio. This podcast is brought to you by: eharmony - Enter code CHURCH at checkout for a free month …")
		#successful title
		self.assertEqual(TestCalls.search5[4].title,"Atrocity Confrontation")

	def testOverview(self):
		#successful results
		self.assertTrue(len(TestCalls.search6) > 20) #Wiki result is greater than 20 characters
		#successful overview
		self.assertEqual(TestCalls.search6[-26:],"before his death in 1998.\n")


########################################################
#     Test Successful Data Storage

#These calls test that data was properly stored in the database

class TestStorage(unittest.TestCase):

	def testArtistStorage(self):
		
		conn = sqlite3.connect(DBNAME)
		cur = conn.cursor()

		statement = "SELECT Name FROM Artists"
		result = cur.execute(statement).fetchone()
		print(result)

		self.assertEqual(str(result[0]),"Amy Winehouse")

		conn.close()

	def testRelatedStorage(self):
		
		conn = sqlite3.connect(DBNAME)
		cur = conn.cursor()

		statement = "SELECT Name FROM RelatedArtists"
		result = cur.execute(statement).fetchone()
		print(result)

		self.assertEqual(str(result[0]),"Duffy")

		conn.close()

	def testTrackStorage(self):
		
		conn = sqlite3.connect(DBNAME)
		cur = conn.cursor()

		statement = "SELECT Name FROM Tracks"
		result = cur.execute(statement).fetchone()
		print(result)

		self.assertEqual(str(result[0]),"Me and Bobby McGee")

		conn.close()

	def testArticleStorage(self):
		
		conn = sqlite3.connect(DBNAME)
		cur = conn.cursor()

		statement = "SELECT Title FROM Articles"
		result = cur.execute(statement).fetchone()
		print(result)

		self.assertEqual(str(result[0]),"Danny Brown")

		conn.close()


clear_cache()




#########################################################

unittest.main(verbosity=2)
