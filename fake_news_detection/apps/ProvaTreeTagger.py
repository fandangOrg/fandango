import requests
resp=requests.post("http://localhost:8080/tag?lang=it",json={"text":"Io sono Fulvio"})


print(resp.text)