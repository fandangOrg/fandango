# FROM fandangorg/fandango_preprocessing:1.0.29
FROM fandangorg/fandango_preprocessing:1.0.17

RUN python -m spacy download el_core_news_sm

RUN rm -r /app/
copy . /app

RUN pip3 install -r requirements.txt
