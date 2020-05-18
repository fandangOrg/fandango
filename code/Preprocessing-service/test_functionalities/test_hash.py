import hashlib

data_uuid = ["hgjhfjgjfg", "donald", "trump"]
identifier = ""

if len(data_uuid) == 1:
    hash_fuct = hashlib.sha512
    iter = 1
else:
    hash_fuct = hashlib.sha256
    iter = 2

for i in range(iter):
    identifier += hash_fuct(data_uuid[i].encode('utf-8')).hexdigest()

print(identifier)
print(len(identifier))