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
import json
import unicodedata

rs = redis.Redis("localhost")
resolved = rs.get('resolved')
rank = rs.get('rank_url')
rank = ast.literal_eval(rank)
resolved = ast.literal_eval(resolved)

def generate_search_results(key):
	#grab from db and convert to dicts

	results = {}
	grab = []
	searchkey = key.lower()
	print searchkey
	# print "MARKMARKMARK"
	for i in resolved:
		find_val = i.find(searchkey)
		if find_val == 0:
			# print i
			# print "hi"
			# print resolved[i]
			grab = resolved[i]
			break

	

	# print results
	j = 0
	for i in grab:
		# print i
		if i in rank.keys():
			# print " "
			tempvar = i.encode('ascii','ignore')
			# print type(tempvar)
			results[j] = tempvar
			j += 1
			# results[temp[i]] = i
	
	# print results
	# print "------"
	return(results)

def test():
	j = 0
	for i in resolved:

		if j == 20:
			key = i
			key.encode('ascii','ignore')
			# print key
			generate_search_results(key)
			j = 0

		j += 1
		