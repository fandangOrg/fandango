from collections import defaultdict
from six.moves import urllib


urls = defaultdict(set)

with open("dirty.csv", 'r') as src:
    for line in src:
        base = line.split(",")[0]
        tpe = line.split(",")[1].strip()
        url = None
        try:
            sri = "http://" + base.lower()
            html = urllib.request.urlopen(sri).getcode()
            url = sri
        except:
            pass
        try:
            hri = "https://" + base.lower()
            html = urllib.request.urlopen(hri).getcode()
            url = hri
        except:
            pass
        if url:
            urls[tpe].add(url)
            with open("clean.csv", "a") as cl:
                cl.write(",".join([url, tpe]) + "\n")
        print([t + ": " + len(urls[t]) for t in urls.keys()])
