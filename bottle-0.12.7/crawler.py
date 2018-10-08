
# Copyright (C) 2011 by Peter Goodman
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import urllib2
import urlparse
from BeautifulSoup import *
from collections import defaultdict
import re
import pprint

def attr(elem, attr):
    """An html attribute from an html element. E.g. <a href="">, then
    attr(elem, "href") will get the href or an empty string."""
    try:
        return elem[attr]
    except:
        return ""

WORD_SEPARATORS = re.compile(r'\s|\n|\r|\t|[^a-zA-Z0-9\-_]')

class crawler(object):
    """Represents 'Googlebot'. Populates a database by crawling and indexing
    a subset of the Internet.

    This crawler keeps track of font sizes and makes it simpler to manage word
    ids and document ids."""

    def __init__(self, db_conn, url_file):
        """Initialize the crawler with a connection to the database to populate
        and with the file containing the list of seed URLs to begin indexing."""
        self._url_queue = [ ]
        self._doc_id_cache = { }
        self._word_id_cache = { }

        # functions to call when entering and exiting specific tags
        self._enter = defaultdict(lambda *a, **ka: self._visit_ignore)
        self._exit = defaultdict(lambda *a, **ka: self._visit_ignore)

        # add a link to our graph, and indexing info to the related page
        self._enter['a'] = self._visit_a

        # record the currently indexed document's title an increase
        # the font size
        def visit_title(*args, **kargs):
            self._visit_title(*args, **kargs)
            self._increase_font_factor(7)(*args, **kargs)

        # increase the font size when we enter these tags
        self._enter['b'] = self._increase_font_factor(2)
        self._enter['strong'] = self._increase_font_factor(2)
        self._enter['i'] = self._increase_font_factor(1)
        self._enter['em'] = self._increase_font_factor(1)
        self._enter['h1'] = self._increase_font_factor(7)
        self._enter['h2'] = self._increase_font_factor(6)
        self._enter['h3'] = self._increase_font_factor(5)
        self._enter['h4'] = self._increase_font_factor(4)
        self._enter['h5'] = self._increase_font_factor(3)
        self._enter['title'] = visit_title

        # decrease the font size when we exit these tags
        self._exit['b'] = self._increase_font_factor(-2)
        self._exit['strong'] = self._increase_font_factor(-2)
        self._exit['i'] = self._increase_font_factor(-1)
        self._exit['em'] = self._increase_font_factor(-1)
        self._exit['h1'] = self._increase_font_factor(-7)
        self._exit['h2'] = self._increase_font_factor(-6)
        self._exit['h3'] = self._increase_font_factor(-5)
        self._exit['h4'] = self._increase_font_factor(-4)
        self._exit['h5'] = self._increase_font_factor(-3)
        self._exit['title'] = self._increase_font_factor(-7)

        # never go in and parse these tags
        self._ignored_tags = set([
            'meta', 'script', 'link', 'meta', 'embed', 'iframe', 'frame', 
            'noscript', 'object', 'svg', 'canvas', 'applet', 'frameset', 
            'textarea', 'style', 'area', 'map', 'base', 'basefont', 'param',
        ])

        # set of words to ignore
        self._ignored_words = set([
            '', 'the', 'of', 'at', 'on', 'in', 'is', 'it',
            'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j',
            'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't',
            'u', 'v', 'w', 'x', 'y', 'z', 'and', 'or',
        ])

        ############USER EDIT#####################

        #this will contain the <(word, ID)>
        self._Lexicon = {} #WORKS
        self._inverted_Lexicon = {}
        #keep track of the word cout
        self._in_words = 0;
        #keep the Document ID vs URL
        self._Document_ID_V_URL = {} #WORKS
        self._URL_v_Document_ID = {}
        #Keep _Doc_ID_v_Word_Set
        self._Doc_ID_v_Word_Set_string = {}
        self._Doc_url_v_Word_Set_string = {}
        self._Doc_ID_v_Word_Set_ID = {}
        #changing wordset Variable that will work with dict above
        self._word_Set_ID = []
        self._word_Set_String ={}

        ###########################################


        # TODO remove me in real version
        self._mock_next_doc_id = 1
        self._mock_next_word_id = 1

        # keep track of some info about the page we are currently parsing
        self._curr_depth = 0
        self._curr_url = ""
        self._curr_doc_id = 0
        self._font_size = 0
        self._curr_words = None

        # get all urls into the queue
        try:
            with open(url_file, 'r') as f:
                for line in f:
                    self._url_queue.append((self._fix_url(line.strip(), ""), 0))
        except IOError:
            pass
    
    def _insert_document(self, url):
        """A function that insert a url into a document db table
        and then returns that newly inserted document's id."""
        self._Document_ID_V_URL[self._mock_next_doc_id] = url
        self._URL_v_Document_ID[url] = self._mock_next_doc_id
        ret_id = self._mock_next_doc_id
        self._mock_next_doc_id += 1
        return ret_id
    
    def _insert_word(self, word):
        """A function that inster a word into the lexicon db table
        and then returns that newly inserted word's id."""
        #Lexicon Handle here
        self._Lexicon[self._mock_next_word_id] = word; 
        ret_id = self._mock_next_word_id
        self._mock_next_word_id += 1
        return ret_id
    
    def word_id(self, word):
        """Get the word id of some specific word."""
        if word in self._word_id_cache:
            return self._word_id_cache[word]
        
        #       1) add the word to the lexicon, if that fails, then the
        #          word is in the lexicon 
        #       2) query the lexicon for the id assigned to this word, 
        #          store it in the word id cache, and return the id.

        word_id = self._insert_word(word)
        self._word_id_cache[word] = word_id
        return word_id
    
    def document_id(self, url):
        """Get the document id for some url."""
        if url in self._doc_id_cache:
            return self._doc_id_cache[url]
        
        #       just like word id cache, but for documents. if the document
        #       doesn't exist in the db then only insert the url and leave
        #       the rest to their defaults.
        
        doc_id = self._insert_document(url)
        self._doc_id_cache[url] = doc_id
        return doc_id
    
    def _fix_url(self, curr_url, rel):
        """Given a url and either something relative to that url or another url,
        get a properly parsed url."""

        rel_l = rel.lower()
        if rel_l.startswith("http://") or rel_l.startswith("https://"):
            curr_url, rel = rel, ""
            
        # compute the new url based on import 
        curr_url = urlparse.urldefrag(curr_url)[0]
        parsed_url = urlparse.urlparse(curr_url)
        return urlparse.urljoin(parsed_url.geturl(), rel)

    def add_link(self, from_doc_id, to_doc_id):
        """Add a link into the database, or increase the number of links between
        two pages in the database."""
        # TODO

    def _visit_title(self, elem):
        """Called when visiting the <title> tag."""
        title_text = self._text_of(elem).strip()
        print "document title="+ repr(title_text)

        # TODO update document title for document id self._curr_doc_id
    
    def _visit_a(self, elem):
        """Called when visiting <a> tags."""

        dest_url = self._fix_url(self._curr_url, attr(elem,"href"))

        #print "href="+repr(dest_url), \
        #      "title="+repr(attr(elem,"title")), \
        #      "alt="+repr(attr(elem,"alt")), \
        #      "text="+repr(self._text_of(elem))

        # add the just found URL to the url queue
        self._url_queue.append((dest_url, self._curr_depth))
        
        # add a link entry into the database from the current document to the
        # other document
        self.add_link(self._curr_doc_id, self.document_id(dest_url))

        # TODO add title/alt/text to index for destination url
    
    def _add_words_to_document(self): ################################################################################
        #       knowing self._curr_doc_id and the list of all words and their
        #       font sizes (in self._curr_words), add all the words into the
        #       database for this document
        self._Doc_ID_v_Word_Set_string[self._curr_doc_id] = self._word_Set_String; 
        self._Doc_url_v_Word_Set_string[self._curr_url] = self._word_Set_String
        self._Doc_ID_v_Word_Set_ID[self._curr_doc_id] = self._word_Set_ID
        #self._in_words = 0
        print "    num words="+ str(len(self._curr_words))

    def _increase_font_factor(self, factor):
        """Increade/decrease the current font size."""
        def increase_it(elem):
            self._font_size += factor
        return increase_it
    
    def _visit_ignore(self, elem):
        """Ignore visiting this type of tag"""
        pass

    def _add_text(self, elem):
        """Add some text to the document. This records word ids and word font sizes
        into the self._curr_words list for later processing."""
        words = WORD_SEPARATORS.split(elem.string.lower())
        for word in words:
            word = word.strip()
            if word in self._ignored_words:
                continue
            self._in_words = self.word_id(word)
            self._curr_words.append((self._in_words, self._font_size))
            self._word_Set_String[word] = self._in_words
            self._word_Set_ID.append(self._in_words)
            
        
    def _text_of(self, elem):
        """Get the text inside some element without any tags."""
        if isinstance(elem, Tag):
            text = [ ]
            for sub_elem in elem:
                text.append(self._text_of(sub_elem))
            
            return " ".join(text)
        else:
            return elem.string

    def _index_document(self, soup):
        """Traverse the document in depth-first order and call functions when entering
        and leaving tags. When we come accross some text, add it into the index. This
        handles ignoring tags that we have no business looking at."""
        class DummyTag(object):
            next = False
            name = ''
        
        class NextTag(object):
            def __init__(self, obj):
                self.next = obj
        
        tag = soup.html
        stack = [DummyTag(), soup.html]

        while tag and tag.next:
            tag = tag.next

            # html tag
            if isinstance(tag, Tag):

                if tag.parent != stack[-1]:
                    self._exit[stack[-1].name.lower()](stack[-1])
                    stack.pop()

                tag_name = tag.name.lower()

                # ignore this tag and everything in it
                if tag_name in self._ignored_tags:
                    if tag.nextSibling:
                        tag = NextTag(tag.nextSibling)
                    else:
                        self._exit[stack[-1].name.lower()](stack[-1])
                        stack.pop()
                        tag = NextTag(tag.parent.nextSibling)
                    
                    continue
                
                # enter the tag
                self._enter[tag_name](tag)
                stack.append(tag)

            # text (text, cdata, comments, etc.)
            else:
                self._add_text(tag)


    def test_print_docID_v_URL(self):
        #test function to print the document id v the url attached to it
        # print self._Document_ID_V_URL;
        pprint.pprint(self._Document_ID_V_URL)

    def test_print_Lexicon(self):
        #test the lexicon
        # print self._Lexicon
        pprint.pprint(self._Lexicon)

    def test_print_DocID_to_Word_set(self):

        for i in self._Doc_ID_v_Word_Set_ID.keys():
            print "THIS IS i:%s" % i
            word_id_set = self._Doc_ID_v_Word_Set_ID.itervalues()
            for j in word_id_set:
                print j 
                print " "
            pprint.pprint(" ")

        # pprint.pprint(self._Doc_ID_v_Word_Set_ID)

    def test_print_DocURL_to_Word_Set_String(self):
        pprint.pprint(self._Doc_ID_v_Word_Set_string)

    def test_print_set(self):
        next_set = self._Doc_ID_v_Word_Set_ID.popitem()
        pprint.pprint(next_set)

    def get_inverted_index(self):
        #given a word i need to know all of the documents it is in
        inverted_index = {}
        doc_id_set = []

        #check if each word id is the the word set link to the doc id
        #add it to the final return var

        for i in self._Lexicon.keys():

            for k in self._Doc_ID_v_Word_Set_ID.keys():
 
                next_set = self._Doc_ID_v_Word_Set_ID.itervalues()
                # print next_set
                for j in next_set:
                    if i in j:
                        doc_id_set.append(k)
                        break

            # print doc_id_set
            # pprint.pprint("")
            
            #add to a dict as a set and clear set
            inverted_index[i] = doc_id_set
            doc_id_set = []

        # pprint.pprint(inverted_index)              
        return inverted_index



    def get_resolved_inverted_index(self):
        resolved_index = {}   
        doc_string_set = []
        # go throught every word
        # get the word set per doc id (if avaiable)
        #  check if the word is in the word set
        for i in self._Lexicon.values():
            # print "THIS IS THE WORD:%s \n" % i
            for k in self._Doc_ID_v_Word_Set_string.keys():
                 # print "This the the link:%s" % self._Document_ID_V_URL[k]
                j = self._Doc_ID_v_Word_Set_string[k]
                    # print "THIS IS J:%s \n" % j
                if i in j:
                    # print "THIS IS THE WORD:%s" % i                        
                    # print "THIS IS J:%s" % j
                    # print "This the the link:%s" % k
                    print "This the the link:%s \n" % self._Document_ID_V_URL[k]
                    # print "\n"
                    doc_string_set.append(self._Document_ID_V_URL[k])
                    # break
                # print "\n"
                #add it into a dict as wordId key 
                #doc_string_set is a set
            resolved_index[i] = doc_string_set
                      
            # pprint.pprint(" ")
            # print doc_string_set

            doc_string_set = []

        # print "%s"%self._Doc_url_v_Word_Set_string.keys()[8]

        return resolved_index

    def test_print_DocID_w_wordset(self):

        for i in self._Doc_ID_v_Word_Set_string:
            print "ID i: %s per url:%s \n" % (i , self._Document_ID_V_URL[i])

#written to test the idea behind the inverted index
    def test_resolved_index(self):
        resolved_index = {}   
        doc_string_set = []

        for i in self._Lexicon.values():
            # print "THIS IS THE WORD:%s \n" % i
            k = self._Doc_ID_v_Word_Set_string.keys()[0]
                 # print "This the the link:%s" % self._Document_ID_V_URL[k]
            j = self._Doc_ID_v_Word_Set_string[k]
                # print "THIS IS J:%s \n" % j
            if i in j:
                print "THIS IS THE WORD:%s" % i                        
                print "THIS IS J:%s" % j
                # print "This the the link:%s" % k
                # print "This the the link:%s \n" % self._Document_ID_V_URL[k]
                # print "\n"
                doc_string_set.append(self._Document_ID_V_URL[k])
            resolved_index[i] = doc_string_set
            
           
            # pprint.pprint(" ")
            # print doc_string_set

            doc_string_set = []
        print "This the the link:%s \n" % self._Document_ID_V_URL[k]

    def crawl(self, depth=2, timeout=3):
        """Crawl the web!"""
        seen = set()

        while len(self._url_queue):

            url, depth_ = self._url_queue.pop()

            # skip this url; it's too deep
            if depth_ > depth:
                continue

            doc_id = self.document_id(url)

            # we've already seen this document
            if doc_id in seen:
                continue

            seen.add(doc_id) # mark this document as haven't been visited
            
            socket = None
            try:
                socket = urllib2.urlopen(url, timeout=timeout)
                soup = BeautifulSoup(socket.read())

                self._curr_depth = depth_ + 1
                self._curr_url = url
                self._curr_doc_id = doc_id
                self._font_size = 0
                self._word_Set_ID = []
                self._word_Set_String = {}
                self._curr_words = [ ]
                self._index_document(soup)
                self._add_words_to_document()
                print "    url="+repr(self._curr_url)

            except Exception as e:
                print e
                pass
            finally:
                if socket:
                    socket.close()

if __name__ == "__main__":
    bot = crawler(None, "hello.txt")
    bot.crawl(depth=1)
   
    # bot.test_print_Lexicon()
    # bot.test_print_DocID_to_Word_set()
    # bot.test_print_DocURL_to_Word_Set_String()
    # bot.get_inverted_index()
    # bot.test_print_set()
    bot.get_resolved_inverted_index()
    # bot.test_print_docID_v_URL()
    # bot.test_resolved_index()
    # bot.test_print_DocID_w_wordset()

########this is for testing###################

#     ID i: 1 per url:https://www.google.com 

# ID i: 2 per url:https://www.google.ca/imghp?hl=en&tab=wi 

# ID i: 3 per url:https://maps.google.ca/maps?hl=en&tab=wl 

# ID i: 4 per url:https://play.google.com/?hl=en&tab=w8 

# ID i: 5 per url:https://www.youtube.com/?gl=CA&tab=w1 

# ID i: 6 per url:https://news.google.ca/nwshp?hl=en&tab=wn 

# ID i: 7 per url:https://mail.google.com/mail/?tab=wm 

# ID i: 8 per url:https://drive.google.com/?tab=wo 

# ID i: 9 per url:https://www.google.ca/intl/en/options/ 

# ID i: 10 per url:http://www.google.ca/history/optout?hl=en 

# ID i: 11 per url:https://www.google.com/preferences?hl=en 

# ID i: 12 per url:https://accounts.google.com/ServiceLogin?hl=en&passive=true&continue=https://www.google.com/ 

# ID i: 14 per url:https://www.google.com/advanced_search?hl=en-CA&authuser=0 

# ID i: 16 per url:https://www.google.com/setprefs?sig=0_mIQnM3IUmgoB6MmnOJEh9T0udvQ%3D&hl=fr&source=homepage&sa=X&ved=0ahUKEwiUvZKnz_fdAhVr6oMKHUY1AIoQ2ZgBCAU 

# ID i: 17 per url:https://www.google.com/intl/en/ads/ 

# ID i: 18 per url:https://www.google.com/services/ 

# ID i: 19 per url:https://plus.google.com/108349337900676782287 

# ID i: 20 per url:https://www.google.com/intl/en/about.html 

# ID i: 21 per url:https://www.google.com/setprefdomain?prefdom=CA&prev=https://www.google.ca/&sig=K_g-IXysnXb7jMHWRZhgnZFudDRLs%3D 

# ID i: 22 per url:https://www.google.com/intl/en/policies/privacy/ 

# ID i: 23 per url:https://www.google.com/intl/en/policies/terms/ 
