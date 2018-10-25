from bottle import route, run, template, request, static_file
from collections import Counter
from heapq import nlargest

allinputs = dict()
tt20 = dict()
ttop = dict()
#this dict holds every single input ever entered in on session

@route('/')
def welcome_page():
    return template('indexSearchPage')
#the web famework will launch the above page as the intro page


@route('/static/<filename>')
def server_static(filename):
    return static_file (filename, root='./myfiles')
#this is to specify the picture directory for indexSearchPage


@route('/', method='GET')
def returnResults():
    
    #Take the key word
    #split it
    #count repeats
    hello = 0
    helloo = 0
    ttop = dict()
    
    searchKey = request.query.keywords
    if searchKey == "":
        hello = 1
    if len(allinputs) == 0:
        helloo = 1
    
    if hello and helloo:
        first = 0
        searchKey = "Please Search"
        keyWordCount = dict()
        
        
        return template('searchResultPage.html', searchResult = searchKey,
                        displayArray = keyWordCount, top20 = ttop)
   


    
    searchKey = searchKey.lower()
    splitKey = searchKey.split(" ")
    keyWordCount = {i:splitKey.count(i) for i in splitKey}



#return 2 values the whole search and the split
#return template('{{key}}', key = keyWordCount)


    notshared = dict()
    #this dict holds every word that was not shared between current input and allinputs
    shared = dict()
    #this dict holds every word that was shared between current input and allinputs
    
    #accounting for if the input dict is empty so i dont reach segfault
    if len(allinputs) == 0:
        allinputs.update(keyWordCount)
    #finding whats shared and not shared
    else:
        for key in keyWordCount:
            if key in allinputs:
                temp1 = {key: keyWordCount[key]+allinputs[key]}
                shared.update(temp1)
            else:
                temp2 = {key: keyWordCount[key]}
                notshared.update(temp2)
            #updating allinputs with new arrays
            allinputs.update(shared)
            allinputs.update(notshared)
#by now I have stored every word ever entered and the number of times
#it was repeated over a session in allinputs
#t20 holds the top 20 most shared by finding the biggest valued keys

    counter = 0
    tempp = dict()
    tempp.update(allinputs)
    
    t20 = dict()
    #accounting for segfaults again
    if len(allinputs) < 20:
        t20.update(allinputs)
    else:
        t20 = dict(Counter(tempp).most_common(20))
    
    
    #t20 holds the overall top 20 most searched stuff
    
    
    
    tt20 = t20
    ttop = t20
    
    return template('searchResultPage.html', searchResult = searchKey,
                    displayArray = keyWordCount, top20 = tt20)





run(host='0.0.0.0', port=80, debug=True)

# return template('searchResultPage.html', searchResult = searchKey,
#     displayArray = keyWordCount)
# return keyWordCount


