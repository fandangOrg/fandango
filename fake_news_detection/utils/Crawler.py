'''
Created on Oct 26, 2018

@author: daniele
'''
from newspaper.article import Article
def crawler_news(url):

        #url = url.encode("utf-8")
        article = Article(url)
        article.download()
        article.parse()
        d=dict()
        d['title']=article.title
        d['authors']=article.authors
        d['body'] =article.text
        d['publisher'] =article.source_url
        return d

        
if __name__ == '__main__':
    d= crawler_news("http://www.ansa.it/puglia/notizie/2018/10/26/bimbi-maltrattati-a-scuola-arrestate-4-maestre_1db48b10-4d5a-461e-832e-be63f66db10a.html")
    print(d)