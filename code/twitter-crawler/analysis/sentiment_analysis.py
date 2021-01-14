from helper.settings import logger
import numpy as np
from nltk.sentiment import SentimentIntensityAnalyzer
# from nltk import sent_tokenize
from textblob import TextBlob
from flair.data import Sentence, Label
from flair.models import TextClassifier
from segtok.segmenter import split_single
from langdetect import detect
from data_models.api_models import FlairSentOutput, TextBlobSentOutput, NLTKSentOutput
from googletrans import Translator
from googletrans.models import Translated


class SentimentAnalysisAPI(object):
    default_sentence: str = "N/A"
    flair_sent_model: TextClassifier = TextClassifier.load("sentiment")
    nltk_sent_model: SentimentIntensityAnalyzer = SentimentIntensityAnalyzer()

    @staticmethod
    def get_document_language(doc: str) -> str:
        language: str = ""
        try:
            language: str = detect(doc)
        except Exception as e:
            logger.error(e)
        return language

    @staticmethod
    def translate_to_english(src_doc: str, src_lang: str) -> str:
        translation: str = ""
        try:
            eng_translator: Translator = Translator()
            res: Translated = eng_translator.translate(
                src_doc, src=src_lang, dest="en")

            translation: str = res.text
        except Exception as e:
            logger.error(e)
        return translation

    @staticmethod
    def make_sentences(text: str, min_char: int = 3) -> list:
        """ Break apart text into a list of sentences """
        if len(text) > min_char:
            sentences: list = [sent for sent in split_single(text) if len(sent) > min_char]
        else:
            sentences: list = []

        if not sentences:
            logger.warning("Default sentence was added")
            sentences: list = [SentimentAnalysisAPI.default_sentence]
        return sentences

    @staticmethod
    def get_label_decision(score: float, lower_boundary: float = .4,
                           upper_boundary: float = .6) -> str:
        final_label: str = ""
        try:
            if score < lower_boundary:
                final_label: str = "Negative"
            elif lower_boundary <= score < upper_boundary:
                final_label: str = "Neutral"
            else:
                final_label: str = "Positive"
        except Exception as e:
            logger.error(e)
        return final_label

    @staticmethod
    def get_flair_sentiment_analysis(doc: str) -> FlairSentOutput:
        output: FlairSentOutput = FlairSentOutput()
        try:
            was_translated: bool = False
            # 1. Get the language of the document
            lang: str = SentimentAnalysisAPI.get_document_language(doc=doc)
            if lang != "en":
                # Translate
                doc: str = SentimentAnalysisAPI.translate_to_english(
                    src_doc=doc, src_lang=lang)
                was_translated: bool = True

            sentences: list = SentimentAnalysisAPI.make_sentences(text=doc)
            scores: list = []
            for sent in sentences:
                # 2. Load model and predict
                sentence: Sentence = Sentence(sent)
                SentimentAnalysisAPI.flair_sent_model.predict(sentence)
                single_res: Label = sentence.labels[0]
                single_label: str = single_res.value
                single_score: float = single_res.score if single_label == "POSITIVE" else (1 - single_res.score)
                scores.append(single_score)

            final_score: float = round(float(np.mean(scores)), 3)
            final_label: str = SentimentAnalysisAPI.get_label_decision(score=final_score)

            output: FlairSentOutput = FlairSentOutput(
                label=final_label, confidence=final_score,
                translated=was_translated, analysed=True)
        except Exception as e:
            logger.error(e)
        return output

    @staticmethod
    def get_textblob_sentiment_analysis(doc: str) -> TextBlobSentOutput:
        output: TextBlobSentOutput = TextBlobSentOutput()
        try:
            was_translated: bool = False
            # 1. Get the language of the document
            lang: str = SentimentAnalysisAPI.get_document_language(doc=doc)
            if lang != "en":
                # Translate
                doc: str = SentimentAnalysisAPI.translate_to_english(
                    src_doc=doc, src_lang=lang)
                was_translated: bool = True

            sentences: list = SentimentAnalysisAPI.make_sentences(text=doc)
            polarity_scores: list = []
            subjectivity_scores: list = []
            for sent in sentences:
                subjectivity: float = TextBlob(sent).sentiment.subjectivity
                polarity: float = TextBlob(sent).sentiment.polarity
                polarity_scores.append(polarity)
                subjectivity_scores.append(subjectivity)

            final_subjectivity: float = round(float(np.mean(subjectivity_scores)), 3)
            final_polarity: float = round(float(np.mean(polarity_scores)), 3)

            output: TextBlobSentOutput = TextBlobSentOutput(
                analysed=True,
                polarity=final_polarity,
                subjectivity=final_subjectivity,
                translated=was_translated)

        except Exception as e:
            logger.error(e)
        return output

    @staticmethod
    def get_nltk_sentiment_analysis(doc: str) -> NLTKSentOutput:
        output: NLTKSentOutput = NLTKSentOutput()

        try:
            was_translated: bool = False
            # 1. Get the language of the document
            lang: str = SentimentAnalysisAPI.get_document_language(doc=doc)
            if lang != "en":
                # Translate
                doc: str = SentimentAnalysisAPI.translate_to_english(
                    src_doc=doc, src_lang=lang)
                was_translated: bool = True

            sentences: list = SentimentAnalysisAPI.make_sentences(text=doc)
            polarity_scores: list = []

            for sent in sentences:
                polarity_scores.append(SentimentAnalysisAPI.nltk_sent_model.polarity_scores(
                    text=sent))
            neg_prob: float = SentimentAnalysisAPI.get_nltk_scores(
                scores=polarity_scores, key="neg")
            neu_prob: float = SentimentAnalysisAPI.get_nltk_scores(
                scores=polarity_scores, key="neu")
            pos_prob: float = SentimentAnalysisAPI.get_nltk_scores(
                scores=polarity_scores, key="pos")
            compound_prob: float = SentimentAnalysisAPI.get_nltk_scores(
                scores=polarity_scores, key="compound")

            output: NLTKSentOutput = NLTKSentOutput(
                analysed=True,
                negative_prob=neg_prob,
                neutral_prob=neu_prob,
                positive_prob=pos_prob,
                compound_prob=compound_prob,
                translated=was_translated)
        except Exception as e:
            logger.error(e)
        return output

    @staticmethod
    def get_nltk_scores(scores: list, key: str) -> float:
        score: float = 0.0
        try:
            score: float = round(float(np.mean([i.get(key) for i in scores])), 3)
        except Exception as e:
            logger.error(e)
        return score
