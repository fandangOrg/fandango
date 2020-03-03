'''
Created on 27 set 2018

@author: camila
'''
import treetaggerwrapper
import re


class Tagga():
    
    def tag(self, s, lang="en", numlines=True):
        tagger = treetaggerwrapper.TreeTagger(TAGLANG=lang)
        for el in tagger.tag_text(s, numlines=numlines):
            yield el.split("\t")
    
    def multitag(self, ss, lang="en"):
        ss = "\n".join([re.sub("\\s+", " ", x) for x in ss])
        temp = []
        for el in self.tag(ss, lang):
            if el[0].startswith("<ttpw:"):
                if temp:
                    yield temp[:]
                    temp = []
            else:
                temp.append(el)
        if temp:
            yield temp[:]
    
    def lemmatizer(self, ltr):
        return " ".join([k[2] for k in ltr if len(k) == 3])
    
    def trasforms(self, l):
        output = list()
        for k in self.multitag(l):
            # output.append(self.lemmatizer(k))
            output.append(k)
        return output


if __name__ == '__main__':
    a = Tagga()
    p = a.trasforms(["titlo", "descrizione", "accedo a nugo -> menu -> passeggeri -> clicco sull'icona in vbasso nell'angolo dx per inserire un passeggero -> compilo tutti i campi e nel campo email riporto un valore errato,non del tipo utente@dominio.it -> salvo  non mi compare nessun messaggio di errore sulla forma del campo email errata"])
    
    print(p)
