from bottle import route, run, template, request, static_file


@route('/')
def welcome_page():
    return template('indexSearchPage')
    #the web famework will launch the above page as the intro page



@route('/results', method='POST')
def returnResults():
	searchKey = request.forms.get('searchKey')
	return template('searchResultPage.html', searchResult = searchKey)

run(host='localhost', port=8080, debug=True)