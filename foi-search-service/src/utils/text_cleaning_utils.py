import spacy
from typing import Optional, List, Set
import re

# Common contraction mappings
CONTRACTION_MAP = {
    "ain't": "is not",
    "aren't": "are not",
    "can't": "can not",
    "couldn't": "could not",
    "didn't": "did not",
    "doesn't": "does not",
    "don't": "do not",
    "hadn't": "had not",
    "hasn't": "has not",
    "haven't": "have not",
    "he'd": "he would",
    "he'll": "he will",
    "he's": "he is",
    "i'd": "i would",
    "i'll": "i will",
    "i'm": "i am",
    "i've": "i have",
    "isn't": "is not",
    "it'd": "it would",
    "it'll": "it will",
    "it's": "it is",
    "let's": "let us",
    "mustn't": "must not",
    "shan't": "shall not",
    "she'd": "she would",
    "she'll": "she will",
    "she's": "she is",
    "shouldn't": "should not",
    "that's": "that is",
    "there's": "there is",
    "they'd": "they would",
    "they'll": "they will",
    "they're": "they are",
    "they've": "they have",
    "we'd": "we would",
    "we're": "we are",
    "we've": "we have",
    "weren't": "were not",
    "what's": "what is",
    "where's": "where is",
    "who's": "who is",
    "won't": "will not",
    "wouldn't": "would not",
    "you'd": "you would",
    "you'll": "you will",
    "you're": "you are",
    "you've": "you have"
}

_contraction_pattern = re.compile(r'\b(' + '|'.join(re.escape(k) for k in CONTRACTION_MAP.keys()) + r')\b', flags=re.IGNORECASE)


class TextCleaner:
    """
    A spaCy-based text cleaning utility class for preprocessing text data.
    Provides advanced NLP-based cleaning capabilities including lemmatization,
    part-of-speech filtering, and stopword removal.
    """
    
    def __init__(self, model: str = "en_core_web_sm"):
        """
        Initialize the TextCleaner with a spaCy model.
        
        Args:
            model (str): spaCy model name to load. Defaults to "en_core_web_sm".
        """
        self.nlp = spacy.load(model)

    def extract_sentences(self, text: str) -> List[str]:
        """
        Extract individual sentences from a text using spaCy.

        Args:
            text (str): Input text

        Returns:
            List[str]: List of sentence strings
        """
        doc = self.nlp(text)
        return [sent.text.strip() for sent in doc.sents]

    def extract_paragraphs(self, text: str) -> List[str]:
        """
        Extract individual paragraphs from a text by splitting on blank lines.

        Args:
            text (str): Input text

        Returns:
            List[str]: List of paragraph strings
        """
        import re
        paragraphs = [p.strip() for p in re.split(r'\n\s*\n', text) if p.strip()]
        return paragraphs

    def __expand_contractions(self, text: str) -> str:
        def _replace(match):
            contraction = match.group(0).lower()
            expanded = CONTRACTION_MAP.get(contraction)
            return expanded if expanded else contraction

        return _contraction_pattern.sub(_replace, text)

    def clean_text(
        self,
        text: str,
        *,
        lowercase: bool = True,
        remove_stopwords: bool = True,
        lemmatize: bool = True,
        remove_punct: bool = True,
        remove_numbers: bool = True,
        keep_pos: Optional[Set[str]] = None,  # e.g., {"NOUN", "VERB"}
    ) -> str:
        """
        Clean text using spaCy's NLP pipeline.
        
        Args:
            text (str): Input text to clean
            lowercase (bool): Whether to convert text to lowercase
            remove_stopwords (bool): Whether to remove stopwords
            lemmatize (bool): Whether to lemmatize tokens
            remove_punct (bool): Whether to remove punctuation
            remove_numbers (bool): Whether to remove numbers
            keep_pos (Set[str], optional): Set of POS tags to keep. If provided,
                                         only tokens with these POS tags will be kept.
        
        Returns:
            str: Cleaned text
        """
        if not isinstance(text, str):
            return ""

        doc = self.nlp(text)
        cleaned_tokens = []
        
        for token in doc:
            # Skip punctuation if requested
            if remove_punct and token.is_punct:
                continue
            # Skip numbers if requested
            if remove_numbers and token.like_num:
                continue
            # Skip stopwords if requested
            if remove_stopwords and token.is_stop:
                continue
            # Skip tokens not in specified POS tags if keep_pos is provided
            if keep_pos and token.pos_ not in keep_pos:
                continue
            # Choose token text or lemma
            token_text = token.lemma_ if lemmatize else token.text
            # Apply lowercase transformation
            if lowercase:
                token_text = token_text.lower()
            # Only add non-empty tokens
            if token_text.strip():
                cleaned_tokens.append(token_text.strip())

        result = " ".join(cleaned_tokens)
        result = self.__expand_contractions(result)

        return result
    
    def clean_text_list(self, texts: List[str], **kwargs) -> List[str]:
        """
        Clean a list of text strings.
        
        Args:
            texts (List[str]): List of text strings to clean
            **kwargs: Arguments to pass to clean_text method
        
        Returns:
            List[str]: List of cleaned text strings
        """
        return [self.clean_text(text, **kwargs) for text in texts]


# Convenience functions for quick usage
def clean_text(text: str, **kwargs) -> str:
    """
    Quick text cleaning function using default spaCy model.
    
    Args:
        text (str): Input text
        **kwargs: Cleaning options
        
    Returns:
        str: Cleaned text
    """
    cleaner = TextCleaner()
    return cleaner.clean_text(text, **kwargs)


def clean_text_list(text_list: List[str], **kwargs) -> List[str]:
    """
    Quick function to clean a list of text strings using default spaCy model.
    
    Args:
        text_list (List[str]): List of text strings
        **kwargs: Cleaning options
        
    Returns:
        List[str]: List of cleaned text strings
    """
    cleaner = TextCleaner()
    return cleaner.clean_text_list(text_list, **kwargs)

def extract_sentences(text: str) -> List[str]:
    cleaner = TextCleaner()
    return cleaner.extract_sentences(text)

def extract_paragraphs(text: str) -> List[str]:
    cleaner = TextCleaner()
    return cleaner.extract_paragraphs(text)