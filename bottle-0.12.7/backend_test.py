from crawler import crawler
import pageranker as pageranker

bot = crawler(None, "url-for-test.txt")
bot.crawl(depth=2)
link = bot.get_link()
rank = pageranker.page_rank(link)
print rank
doc_id = bot.get_Doc_ID_v_URL()

for key,value in rank.items():
    print doc_id[key]

resolved_index = bot.get_resolved_inverted_index()

name = "intel"

if name in resolved_index:
    print resolved_index[name]