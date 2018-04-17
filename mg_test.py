import unittest
import model as model

#################################
#     Test Successful Data Calls
#################################

class TestCalls(unittest.TestCase):


	search1 = model.search_artists("Amy Winehouse")
	search2 = model.search_artists("Danny Brown")
	search3 = model.get_others_in_genre("Amy Winehouse")

	def testArtistSearch(self):

		#successful artist name
		self.assertEqual(TestCalls.search1[0].name, "Amy Winehouse")
		#successful artist id
		self.assertEqual(TestCalls.search1[0].spotify_id,"6Q192DXotxtaysaqNPy5yR")
		#successful genre
		self.assertEqual(TestCalls.search2[0].genre,"alternative hip hop")


	def testRealated(self):
		#successful related artist count
		self.assertEqual(len(TestCalls.search3),20)
		#succesful related artist accuracy
		self.assertEqual(TestCalls.search3[3].name,"Macy Gray")

unittest.main(verbosity=2)
