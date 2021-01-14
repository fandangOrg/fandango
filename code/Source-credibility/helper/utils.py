import re, string
import numpy as np
from helper.settings import logger
from datetime import datetime


def remove_non_alphabetical_symbols(text: str) -> str:
    # Filter numbers
    s1_filtered: str = re.sub(r'\b\d+\b', '', text)
    text_filtered: str = s1_filtered.translate(
        str.maketrans('', '', string.punctuation)).strip()
    return text_filtered


def normalize_value(mu: float = 50, sigma: float = 2, abs: bool = True) -> float:
    normalize_val: float = mu
    try:
        normalize_val: float = np.round(np.random.normal(mu, sigma, 1)[0], 3)
        if abs:
            normalize_val: float = float(np.abs(normalize_val))
    except Exception as e:
        logger.error(e)
    return normalize_val


def preprocess_date(non_formatted_date: datetime,
                    new_format: str = '%Y/%m/%d %H:%M:%S') -> str:
    return non_formatted_date.strftime(new_format)


def relevance_mapping(x: float, alpha: float = .20) -> float:
    return 1 - (1/(1 + alpha * x))