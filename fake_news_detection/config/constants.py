
LANG_MAPPING = {
                 "en" : ["english", "english", 'en_core_web_md'],
                 "it" : ["italian", "italian", "it_core_news_sm"],
                 "es" : ["spanish", "spanish", "es_core_news_md"],
                 "nl" : ["dutch", "dutch", "nl_core_news_sm"]
                }

LANG_SUPPORTED = ["en", "it", "es", "nl"] 

QUOTES = "\"\'`´‘’“”❛❜❝❞‹›«»„‚‛‟「」『』〝〞〟﹁﹂﹃﹄＂＇｢｣"

LABEL_SCORE = {   
     'text_StopwordCounter'    : 'Count stopwords, usually refers to the most common words in a language',
       'text_CharsCounter'       : 'Count all the characters of body\'s article',
         'title_CharsCounter'       : 'Count all the characters of title\'s article',
            'text_PunctuationCounter' : "Count all the punctuation marks of body's article",
                'title_PunctuationCounter': "Count all the punctuation marks of title's article",
        'text_LexicalDiversity'   : "Calculate how different words in body's article are, taking the number of all the unique words in the text and diving for the number all the words in the text", 'text_AveWordxParagraph'       : "Words Average per paragraph", 'text_FleschReadingEase'       : 'Flesch reading ease measures the complexity of a text, The lower the score, the more difficult the text is to read. The Flesch readability score uses the average length of your sentences (measured by the number of words) and the average number of syllables per word in an equation to calculate the reading ease. Text with a very high Flesch reading ease score (about 100) is straightforward and easy to read, with short sentences and no words of more than two syllables. Usually, a reading ease score of 60-70 is considered acceptable/normal for web copy.', 'text_FKGRadeLevel'          : 'The Kincaid readability index indicates how difficult a passage in English is to understandIn,higher scores indicate material that is easier to read; lower numbers mark passages that are more difficult to read.',
             'text_CountAdv'           : 'Count all the adverbs in body\'s article',
                'text_CountAdj'          : 'Count all the adjectives in body\'s article',
                  'text_CountPrep_conj'          : 'Count all the preposition and conjuction in body\'s article',
                    'text_countVerbs'              : 'Count all  verbs in body\'s article' ,
                    'text_AVGSentencesSizeCounter':  'Average article sentences size',
                    'title_StopwordCounter': ' Count stop-words in the title of an article',
                    'title_POSDiversity':  'Count how many unique Part of speech are in the title of an article',
                    "text_AVGWordsCounter": 'words Average  in an article body',
                    'title_AVGWordsCounter': 'words Average  in the title of an article'
                    }
