import requests

lc = 0
with open("urls_to_check.csv", 'r') as src:
    for line in src:
        lc += 1
        url = line.split(",")[0]
        tpe = line.split(",")[1].strip()  # remove the line break '\n'
        print('Checking URL %d: %s ' % (lc, url))
        try:
            r = requests.get(url).status_code
            if r in requests.status_codes._codes.keys():
                sc_readable = requests.status_codes._codes[r][0]
                chk = ','.join([url, tpe, str(r), sc_readable]) + "\n"
                print('Status: %d - %s' % (r, sc_readable))
            else:
                chk = ','.join([url, tpe, str(r), 'non-standard_error_code']) + "\n"
                print('Status: %d' % r)
        except requests.exceptions.ConnectionError as ce:
            chk = ','.join([url, tpe, str(r), str(type(ce))]) + "\n"
            print('ConnectionError - Website doesn\'t exist or is down')
            continue
        except requests.exceptions.RequestException as e:
            chk = ','.join([url, tpe, str(r), str(type(e))]) + "\n"
            print('RequestException')
            continue
        with open("checked_urls_with_status_codes.csv", "a") as cl:
            cl.write(chk)
