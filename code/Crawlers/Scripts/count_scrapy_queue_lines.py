

for cnt in range(1):
    f = open("q%05d" % cnt, "rb")
    contents = f.read()
    lines = contents.split("errbackq#Nu.")
    print "q%05d" % cnt, len(lines)
    f.close()

