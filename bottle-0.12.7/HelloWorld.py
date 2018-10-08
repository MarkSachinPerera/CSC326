from bottle import route, run, template, request, static_file
from collections import Counter
from heapq import nlargest


allinputs = dict()

@route('/')
def welcome_page():
    return template('indexSearchPage')
    #the web famework will launch the above page as the intro page


@route('/static/<filename>')
def server_static(filename):
    return static_file (filename, root='./myfiles')


@route('/results', method='POST')
def returnResults():
   
	#Take the key word 
	#split it
	#count repeats 
	searchKey = request.forms.get('searchKey')
        searchKey = searchKey.lower()
	splitKey = searchKey.split(" ")
	keyWordCount = {i:splitKey.count(i) for i in splitKey}

	#return 2 values the whole search and the split
	#return template('{{key}}', key = keyWordCount)
<<<<<<< HEAD

        notshared = dict()
        shared = dict()

        if len(allinputs) == 0:
            allinputs.update(keyWordCount)

        else:
            for key in keyWordCount:
                if key in allinputs:
                    temp1 = {key: keyWordCount[key]+allinputs[key]}
                    shared.update(temp1)
                else:
                    temp2 = {key: keyWordCount[key]}
                    notshared.update(temp2)

        allinputs.update(shared)
        allinputs.update(notshared)
#by now I have stored every word ever entered and the number of times it was repeated over a session in allinputs

        t20 = dict()
        counter = 0
        tempp = dict()
        tempp.update(allinputs)


        if len(allinputs) < 20:
            t20.update(allinputs)
        else:
            t20 = dict(Counter(tempp).most_common(20))


#t20 holds the overall top 20 most searched stuff





	return template('searchResultPage.html', searchResult = searchKey,
		displayArray = keyWordCount, top20 = t20)

run(host='localhost', port=8080, debug=True)
=======
	# return template('searchResultPage.html', searchResult = searchKey,
	# 	displayArray = keyWordCount)
	return keyWordCount
>>>>>>> f8434e644c23b570ffbcd9a21e02e3e4b94c7b13

