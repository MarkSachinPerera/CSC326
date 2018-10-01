from bottle import route, run, template, request, static_file
from collections import Counter

@route('/')
def welcome_page():
    return template('indexSearchPage')
    #the web famework will launch the above page as the intro page



@route('/results', method='POST')
def returnResults():
	#Take the key word 
	#split it
	#count repeats 
	searchKey = request.forms.get('searchKey')
	splitKey = searchKey.split(" ")
	keyWordCount = {i:splitKey.count(i) for i in splitKey}

	#return 2 values the whole search and the split
	#return template('{{key}}', key = keyWordCount)
	return template('searchResultPage.html', searchResult = searchKey,
		displayArray = keyWordCount)

run(host='localhost', port=8080, debug=True)