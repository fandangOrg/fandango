import PIL
from PIL import Image
import requests
from io import BytesIO


def retrieve_image_by_url(url):
    img = None
    try:
        response = requests.get(url)
        img = Image.open(BytesIO(response.content))
    except Exception as e:
        print(e)
    return img

def filter_by_size(img):
    filter = False
    try:
        filter_size = 100*100
        image_size = img.size[0]*img.size[1]
        # if the image is smaller than the filter size
        if image_size <= filter_size:
            filter = True
    except Exception as e:
        print(e)
    return filter

def filter_by_apect_ratio(img):
    filter = False
    try:

        filter_ratio_h = 5
        filter_ratio_w = 0.5
        image_ratio = img.width / img.height

        # Horizontal banner
        if image_ratio >= filter_ratio_h:
            filter = True
            print("Horizontal banner")

        # Vertical banner
        if image_ratio <= filter_ratio_w:
            filter = True
            print("Vertical banner")
    except Exception as e:
        print(e)
    return filter
"""n=3
# horizontal banner
img2 = img.resize((int(n*img.width), int(img.height/n)), PIL.Image.ANTIALIAS)
print(img2.width / img2.height)
img2.show()
# vertical banner
img3 = img.resize((int(img.width/n), int(img.height*n)), PIL.Image.ANTIALIAS)
print(img3.width / img3.height)
img3.show()

print("Filtering by size ...")
print(filter_by_size(img))
print(filter_by_size(img2))
print(filter_by_size(img3))

print("Filtering by aspect ratio...")
print(filter_by_apect_ratio(img))
print(filter_by_apect_ratio(img2))
print(filter_by_apect_ratio(img3))"""

# ----------------------------
images =  [
    "https://i.guim.co.uk/img/media/f8fcdd0065027e67d0a6b1a9e8e80db1f2d5be37/101_67_1296_777/master/1296.jpg?width"
    "=300&quality=85&auto=format&fit=max&s=e9e96a412c9987abc44c7bfa251c21c3",
    "https://i.guim.co.uk/img/media/1cdbc98a66ce4007ff70c6099d29a1e1e45e4e0d/0_507_4712_2827/master/4712.jpg?width"
    "=300&quality=85&auto=format&fit=max&s=28462bca9963575d0ca347126b0f2778",
    "https://sb.scorecardresearch.com/p?c1=2&c2=6035250&cv=2.0&cj=1&comscorekw=Germany%2CWorld+news%2CEurope",
    "https://i.guim.co.uk/img/media/aef1b0521d0a5501b771b9461cf1b2859d5a0446/0_126_3500_2100/master/3500.jpg?width"
    "=1200&height=630&quality=85&auto=format&fit=crop&overlay-align=bottom%2Cleft&overlay-width=100p&overlay-base64"
    "=L2ltZy9zdGF0aWMvb3ZlcmxheXMvdGctZGVmYXVsdC5wbmc&enable=upscale&s=fd1818acff65da22c7b899488dc6c2db",
    "https://phar.gu-web.net/count/pvg.gif",
    "https://i.guim.co.uk/img/media/a8199fef69432f43b78a4eba0f54c488feb0799e/0_117_3500_2100/master/3500.jpg?width"
    "=300&quality=85&auto=format&fit=max&s=e0e1445b7489d5706731f53974dfff70",
    "https://phar.gu-web.net/count/pv.gif"]

for i, url in enumerate(images):
    print("Analysing image {}/{}".format(i+1, len(images)))
    img = retrieve_image_by_url(url) # width, height
    print(img)
    if img is not None:
        print(img.size[0] / img.size[1])
        #img.show()
        print("Filtering by size ...")
        print(filter_by_size(img))
        print("Filtering by aspect ratio...")
        print(filter_by_apect_ratio(img))


