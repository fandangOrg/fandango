import newspaper


def check_newspaper_parser():
    url_custom = set()

    with open("checked_urls_with_status_codes.csv", 'r') as src:
        with open('checked_urls_with_status_codes_parser.csv', 'a') as out:
            for counter, line in enumerate(src):
                url = line.split(",")[0]
                tpe = line.split(',')[1]
                status_code = line.split(",")[2]
                err_desc = line.split(',')[3].strip()
                if status_code == '200':
                    paper = newspaper.build(url, memoize_articles=False)

                    if len(paper.articles) == 0:
                        parser = 'custom'
                        url_custom.add(url)
                    else:
                        try:
                            paper.articles[0].download()
                            parser = 'newspaper'
                        except newspaper.article.ArticleException:
                            parser = 'ArticleException'
                    print(','.join([str(counter), url, tpe, status_code, err_desc, parser]))
                    out.write(','.join([url, tpe, status_code, err_desc, parser]) + '\n')
                else:
                    print(','.join([str(counter), url, tpe, status_code, err_desc, 'SKIPPED']))

    return url_custom


def count_custom_parser(filename):
    url_custom = set()

    with open(filename, 'r') as src:
        for line in src:
            url = line.split(",")[0]
            tpe = line.split(',')[1]
            status_code = line.split(",")[2]
            err_desc = line.split(',')[3].strip()
            try:
                parser = line.split(',')[4].strip()
            except (ValueError, IndexError):
                pass
            if parser == 'custom':
                url_custom.add(line)

    print(len(url_custom))

    return url_custom


if __name__ == '__main__':

    # check_newspaper_parser()
    file = 'checked_urls_with_status_codes_parser.csv'

    x = sorted(count_custom_parser(file))
    with open('checklist.csv', 'a') as out:
        for i in x:
            out.write(i.split(',')[0] + ',' + i.split(',')[1] + '\n')
    print('Done')
