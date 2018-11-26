'''
Created on 21 nov 2018

@author: camila
'''


import requests
from bs4 import BeautifulSoup



url = r"https://www.politifact.com/"
coda="personalities/"
headers = {"User-Agent" : "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html" }

r = requests.get(url+coda, headers)
lista_persone = []

if r.status_code == requests.codes.ok:
    paginaParsata = BeautifulSoup(r.content, "html.parser")
    lista_grezza = paginaParsata.find_all("a", class_="link")
    for item in lista_grezza:
        lista_persone.append( {"persona": item.text,"url":url + item.get("href")} )
    
    print(lista_persone,"\n")
else:
    
    raise("Houston we've got a problem! : {pr}".format(pr=r.content))



    










