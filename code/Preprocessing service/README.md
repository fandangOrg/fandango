# FANDANGO-preprocessing-release

A Preprocessing service integrated into FANDANGO, an European Project for detecting fake news.


## Offline Process
### Input

- Read data ingested in a kafka queue (JSON fomat)

### Process

- Clean missing information
- Clean and process the name of the authors
- Add the organization or the publisher of the article.
- Remove the non-related images (publicity banners etc.)
- Extract the language of the text
- Extract the country and nationality of the publisher
- Discard articles with bad format or without text

### Output

- Write data ingested into a Kafka queue (JSON format)

## Online Process 

### Input

- HTTP Post Request

### Process

- Clean missing information
- Clean and process the name of the authors
- Add the organization or the publisher of the article.
- Remove the non-related images (publicity banners etc.)
- Extract the language of the text
- Extract the country and nationality of the publisher
- Discard articles with bad format or without text

### Output

- HTTP response with a JSON file.