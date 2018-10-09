from crawler import crawler
import sys
import random

crawler = crawler(None, "url-for-test.txt")
crawler.crawl(depth=1)

URL_1 = "https://marksachinperera.github.io/"
URL_2 = "https://marksachinperera.github.io/ContactMe.html"
URL_3 = "https://marksachinperera.github.io/AboutMe.html"

###****************####
ID_1 = -1
ID_2 = -1
ID_3 = -1
###****************####

print "getting inverted index"
inverted_index = crawler.get_inverted_index()

print "getting resolved index"
resolved_index = crawler.get_resolved_inverted_index()

print "Setting up"

word_list_1 = {"jpg", "height" , "done" , "have" , "home" , "portfolio" , "alt" , "web" , "le" , 
"img" , "personal" , "mark" , "width" , "1500" , "styles" , "picture" , "resume" , "showing" , "welcome" ,
 "hi" , "img_2315" , "perera" , "projects" , "me" , "src", "about" , "name" , "1800", "this" , "contact" , "my" , "page" }

word_list_2 = {"feedback" , "links", "ca" , "coming" , "soon" , "jpg", "height" , "home" , "portfolio" , 
"alt", "gmail" , "information" , "le" , "img" , "personal" , "section" , "mark" , "width" , "1500" , 
"mail" , "email" , "marksachin12" , "styles" , "picture" , "welcome" , "img_2315" , "perera", "me" ,
 "src", "about" , "1800" , "utoronto" , "work" , "marksa" , "contact" , "quick" , "com" }

Doc_id_v_URL = crawler.get_Doc_ID_v_URL()

for i in Doc_id_v_URL.keys():
	# print i
	# print Doc_id_v_URL[i]
	if URL_1 == Doc_id_v_URL[i]:
		ID_1 = i
	if URL_2 == Doc_id_v_URL[i]:
		ID_2 = i
	if URL_3 == Doc_id_v_URL[i]:
		ID_3 = i



if ID_1 == -1 | ID_2 == -1 | ID_3 == -1 :
	print ID_1
	print ID_2
	print ID_3	
	print "setup failed"
	sys.exit(0) 

# print ID_1
# print ID_2
# print ID_3	

print "Starting Test One"

ID_1_count = 0
ID_2_count = 0
ID_3_count = 0

# this forloop will count how many times each link appears
for i in inverted_index.keys():
	for j in inverted_index[i]:
		if j == ID_1:
			ID_1_count += 1

		if j == ID_2:
			ID_2_count += 1

		if j == ID_3:
			ID_3_count += 1

# print ID_1_count
# print ID_2_count
# print ID_3_count

if ID_1_count != 32 or ID_2_count != 37 or ID_3_count != 198:
	print "test one failed"
	sys.exit(0)

print "Test Successful"


print "Starting Test Two"

#test for url 1

for i in resolved_index.keys():
	if i in word_list_1:
		if URL_1 not in resolved_index[i]:
			print "Failed to find URL_1 for %" % i
			sys.exit(0)

#test for url 2
for i in resolved_index.keys():
	if i in word_list_2:
		if URL_2 not in resolved_index[i]:
			print "failed find URL_2 for %" % i
			sys.exit(0)

print "Test Successful"


print "Starting Test Three"

#Test if the resolved index matches the inverted index
#is it actually resolved

lexicon = crawler.get_Lexicon()
length_lexicon = len(lexicon)


# do 10 tests

for i in range(100):
	k = random.randint(1,length_lexicon)
	
	curr_rand_inverted = inverted_index[k]
	curr_word = lexicon[k]
	curr_rand_resolved = resolved_index[curr_word]

	for j in curr_rand_inverted:
		curr_url = Doc_id_v_URL[j]

		if curr_url not in curr_rand_resolved:
			print "Can not find % in resolved index" % curr_url
			sys.exit(0)

print "Test Successful"








