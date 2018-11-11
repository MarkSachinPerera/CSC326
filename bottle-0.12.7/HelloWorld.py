from oauth2client.client import OAuth2WebServerFlow
from oauth2client.client import flow_from_clientsecrets
#from googleapiclient.errors import HttpError
from googleapiclient.discovery import build
from bottle import route, run, template, request, static_file
from collections import Counter
import httplib2
from beaker.middleware import SessionMiddleware
import bottle
from bottle import error
import redis
import ast
allinputs = dict()
import json
import unicodedata
usermanager = dict()
searched = "hi"
ar = dict()
s = dict()
mark = dict()

rs = redis.Redis("localhost")
urls = rs.get("rank_url")
urls = ast.literal_eval(urls)
resolved = rs.get("resolved")






# urls = {
#     #rank / url
#     1: "http://www.google.com",
#     3: "http://www.yahoo.com",
#     6: "http://www.facebook.com",
#     2: "http://www.twitter.com",
#     5: "http://www.instagram.com",
#     4: "http://www.linkedin.com",
#     7: "http://www.snapchat.com",
#     10: "http://wwww.github.com",
#     8: "http://www.outlook.com",
#     11: "http://www.q.utoronto.ca",
#     9 : "http://www.youtube.com"
# }


# session setting
session_opts = {
    'session.type': 'file',
    'session.cookie_expires': 300,
    'session.data_dir': './data',
    'session.auto': True
}
app = SessionMiddleware(bottle.app(), session_opts)




@error(404)
def error404(error):
    return 'Nothing here, sorry'



@route('/')
def welcome_page():
    return template('ask.html')
    #the web famework will launch the above page as the intro page

#Lab 3 addition
@route('/nextpage', method='POST')
def nextpage():
    global s
    # s holds all the ranks:urls in increasing order of their ranking

    # i only want to hold the top 5 for each result


    if len(s) <= 5:
        global s
        top5 = s
    else:
        counter = 0
        top5 = dict()
        while counter < 5:
            wantedkey = next(iter(s))
            top5[wantedkey] = s[wantedkey]
            global s
            del s[wantedkey]
            counter = counter + 1

    global searched
    global ar

    return template('anonsearchResultPage.html', searchResult=searched,
                    displayArray=ar, sortedurl=top5)



@route('/aresults', method='POST')
def areturnResults():
    # Take the key word
    # split it
    # count repeats
    global searchKey
    searchKey = request.forms.get('searchKey')
    searchKey = searchKey.lower()
    splitKey = searchKey.split(" ")
    keyWordCount = {i: splitKey.count(i) for i in splitKey}
    word = next(iter(keyWordCount))
    

    #resolved
    global resolved
    resolved = ast.literal_eval(resolved)
    uword = unicode(word, "utf-8")
    listofurl = ()
    if uword in resolved:
        listofurl = resolved[uword]



    
    print urls #the dict with everything 
    print "==================================================="
    print listofurl #list
    for i in range(len(listofurl)):
        if listofurl[i] in urls:
            name = unicodedata.normalize('NFKD', listofurl[i]).encode('ascii','ignore')
            global mark
            mark[urls[listofurl[i]]]  = name
            dne = False 
    print "=============================hiiiiiiiiii======================"
    print mark #list


  
    #LAB 3 : Assuming that the dict with urls and their rank is sent to me here :
    #sort the dictionary, assuming that the dict is called urls

    # for key in urls:
    #     global s
    #     s[key] = urls[key]
    # #s holds all the ranks:urls in increasing order of their ranking
    

    
    if dne:
        global s 
        s = {1: "page does not exist"}
    else: 
        global s 
        s = mark


   
    #i only want to hold the top 5 for each result

    if len(s) <= 5:
        top5 = s
    else:
        counter = 0
        top5 = dict()
        while counter < 5:
            wantedkey = next(iter(s))
            top5[wantedkey] = s[wantedkey]
            global s
            del s[wantedkey]
            counter = counter + 1



    global searched
    searched = searchKey
    global ar
    ar = keyWordCount


    return template('anonsearchResultPage.html', searchResult=searched,
                    displayArray=keyWordCount, sortedurl = top5)



@route('/signedin', method='GET')
def home():
    flow = flow_from_clientsecrets("client_secrets.json", scope='https://www.googleapis.com/auth/plus.me https://www.googleapis.com/auth/userinfo.email', redirect_uri="http://localhost:8080/redirect")

    uri = flow.step1_get_authorize_url()
    bottle.redirect(str(uri))


@route('/redirect')
def redirect_page():
    code = request.query.get('code', '')
    flow = OAuth2WebServerFlow(client_id="948840677754-f88stoe8tud363t61h4t52h5j1nm0gvi.apps.googleusercontent.com", client_secret="QeIRBeqjfXK3WE4jZByRu7sj",
                               scope="https://www.googleapis.com/auth/plus.me https://www.googleapis.com/auth/userinfo.email", redirect_uri="http://localhost:8080/redirect")
    credentials = flow.step2_exchange(code)
    token = credentials.id_token['sub']
    http = httplib2.Http()
    http = credentials.authorize(http)
    session = request.environ.get('beaker.session')
    # Get user email
    users_service = build('oauth2', 'v2', http=http)
    user_document = users_service.userinfo().get().execute()
    session['email'] = user_document['email']
    #if they have a name registered, I also hold their name
    if 'name' in user_document:
        session['name'] = user_document['name']


    user_email = user_document['email']
    global email
    email = user_email
    session.save()
    return template('indexSearchPage.html', EMAIL=session['name'])



#this dict holds every single input ever entered in on session




@route('/static/<filename>')
def server_static(filename):
    return static_file (filename, root='./myfiles')
#this is to specify the picture directory for indexSearchPage

@route('/signout')
def sign_out():
    session = request.environ.get('beaker.session')
    eemail = session.setdefault('email','')
    global usermanager
    global allinputs

    allinputs.clear()
    session.delete()
    # temp = {'hello': {'l':'j'}}

    bottle.redirect('/')



@route('/anon', method = 'GET')
def ahome():
    return template('anonindexSearchPage.html')










@route('/results', method='POST')
def returnResults():
    session = request.environ.get('beaker.session')
    try:
        email = session['user_email']
    except:
        email = ''

	#Take the key word
	#split it
	#count repeats
	searchKey = request.forms.get('searchKey')
        searchKey = searchKey.lower()
	splitKey = searchKey.split(" ")
	keyWordCount = {i:splitKey.count(i) for i in splitKey}
        global allinputs
        eemail = session.setdefault('email', '')

        if eemail in usermanager:
            allinputs = usermanager[eemail]

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
        t20 = dict()
        counter = 0
        tempp = dict()
        tempp.update(allinputs)

#accounting for segfaults again
        if len(allinputs) < 20:
            t20.update(allinputs)
        else:
            t20 = dict(Counter(tempp).most_common(20))


#t20 holds the overall top 20 most searched stuff
        eemail = session.setdefault('email','')
        name = session.setdefault('name','')
        # global email
        # myemail = email
        # print(eemail)
        global usermanager


        usermanager[eemail] = t20


        return template('searchResultPage.html', searchResult = searchKey,
                    displayArray = keyWordCount, top20=t20, EMAIL=name)

run(app = app)
#, host='0.0.0.0', port=80)





    
