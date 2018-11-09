from crawler import crawler
import pageranker as pageranker
import redis
import operator

def setup_Read(setserver = False):
    bot = crawler(None, "url-for-test.txt")
    bot.crawl(depth=1)
    link = bot.get_link()

    rank = pageranker.page_rank(link)
    doc_id_v_URL = bot.get_Doc_ID_v_URL()
    lexicon = bot.get_Lexicon()
    inverted_index = bot.get_inverted_index()

    #sort the ranks
    rank = sorted(rank.items(), key=operator.itemgetter(1), reverse=True)
    # print rank
    rank_url = {}
    for i in rank:
        # print type(i)
        doc = doc_id_v_URL[i[0]]
        rank_url[doc] = i[1]
    # print rank_url

    if setserver:
        # print "here"
        rs = redis.Redis("localhost")
        rs.set("rank_url",rank_url)
        rs.set("rank",rank)
        rs.set("doc_id_v_URL",doc_id_v_URL)
        rs.set("lexicon",lexicon)
        rs.set("inverted_index",inverted_index)

def delete_server():
        rs = redis.Redis("localhost")
        rs.delete("rank")
        rs.delete("doc_id_v_URL")
        rs.delete("lexicon")
        rs.delete("inverted_index")


if __name__ == "__main__":
    setup_Read()

