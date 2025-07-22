# TextCleaner Setup Guide

This guide explains how to set up and use the new spaCy-based TextCleaner implementation.

## Installation

### 1. Install Required Dependencies

```bash
# Install spaCy (already in requirements.txt)
pip install spacy>=3.8.7

# Download the English language model
python -m spacy download en_core_web_sm
```

### 2. Verify Installation

```python
import spacy

# Test that spaCy and the model are working
try:
    nlp = spacy.load("en_core_web_sm")
    print("✓ spaCy setup complete!")
except OSError:
    print("❌ Please run: python -m spacy download en_core_web_sm")
```

## Usage

### Basic Usage

```python
from src.utils.text_cleaning_utils import TextCleaner, clean_text, clean_text_list

# Initialize the cleaner
cleaner = TextCleaner()

# Clean a single text
text = "Hello! I'm running quickly to the beautiful store."
result = cleaner.clean_text(text)
print(result)  # "hello run quickly beautiful store"

# Clean multiple texts
texts = ["Hello world!", "How are you?", "This is amazing!"]
results = cleaner.clean_text_list(texts)
print(results)  # ["hello world", "amaze"]
```

### Advanced Options

```python
# Custom cleaning options
text = "The 5 running dogs can't jump over 10 tall fences!"

# Keep only nouns and verbs
result = cleaner.clean_text(
    text,
    keep_pos={"NOUN", "VERB"},
    remove_numbers=True,
    lemmatize=True
)
print(result)  # "dog run jump fence"

# Preserve numbers and disable lemmatization
result = cleaner.clean_text(
    text,
    remove_numbers=False,
    lemmatize=False,
    lowercase=False
)
print(result)  # "5 running dogs jump 10 tall fences"
```

### All Available Options

```python
result = cleaner.clean_text(
    text,
    lowercase=True,          # Convert to lowercase
    remove_stopwords=True,   # Remove stopwords (the, and, is, etc.)
    lemmatize=True,          # Convert to base forms (running -> run)
    remove_punct=True,       # Remove punctuation
    remove_numbers=True,     # Remove numbers
    keep_pos={"NOUN", "VERB"} # Keep only specific parts of speech
)
```

### Part-of-Speech Filtering

You can filter to keep only specific types of words:

```python
# Keep only nouns
nouns_only = cleaner.clean_text(text, keep_pos={"NOUN"})

# Keep nouns and adjectives
content_words = cleaner.clean_text(text, keep_pos={"NOUN", "ADJ"})

# Keep nouns, verbs, and adjectives
main_words = cleaner.clean_text(text, keep_pos={"NOUN", "VERB", "ADJ"})
```

### ✅ spaCy Universal POS Tags for `keep_pos`

| POS Tag | Meaning             | Example                          |
|---------|---------------------|----------------------------------|
| `ADJ`   | Adjective           | happy, blue, fast                |
| `ADP`   | Adposition          | in, on, at, under                |
| `ADV`   | Adverb              | quickly, very, well              |
| `AUX`   | Auxiliary verb      | is, have, will                   |
| `CONJ`  | Conjunction         | and, or, but                     |
| `CCONJ` | Coordinating conj.  | and, but, or                     |
| `DET`   | Determiner          | a, an, the                       |
| `INTJ`  | Interjection        | wow, hey, oh                     |
| `NOUN`  | Noun                | dog, house, price                |
| `NUM`   | Number              | one, 25, 3rd                     |
| `PART`  | Particle            | not, to                          |
| `PRON`  | Pronoun             | he, she, they, it                |
| `PROPN` | Proper noun         | Canada, John, Google             |
| `PUNCT` | Punctuation         | .,!?                             |
| `SCONJ` | Subordinating conj. | because, although                |
| `SYM`   | Symbol              | $, %, =                          |
| `VERB`  | Main verb           | run, jump, write                 |
| `X`     | Other               | unknown/uncategorized tokens     |
| `SPACE` | Whitespace          | spaces, tabs, newlines           |

### Convenience Functions

```python
# Quick single-use cleaning
result = clean_text("Hello world!", remove_stopwords=True)

# Quick batch cleaning
results = clean_text_list(["Hello!", "World!"], lemmatize=True)
```

### Custom spaCy Model

```python
# Use a different spaCy model
cleaner = TextCleaner(model="en_core_web_md")  # Medium model
cleaner = TextCleaner(model="en_core_web_lg")  # Large model
```

## Real-World Examples

### Social Media Content

```python
post = "OMG! Can't believe the amazing concert last night! 🎵 #music #concert"
cleaned = cleaner.clean_text(post)
# Result: "believe amazing concert night music concert"
```

### Product Reviews

```python
review = "I bought this product 2 weeks ago and I'm absolutely loving it! Quality is outstanding."
cleaned = cleaner.clean_text(
    review,
    keep_pos={"NOUN", "VERB", "ADJ"},
    remove_numbers=True
)
# Result: "buy product week love quality outstanding"
```

### Academic Text

```python
abstract = "This study investigates machine learning algorithms in NLP tasks."
cleaned = cleaner.clean_text(
    abstract,
    keep_pos={"NOUN", "VERB"},
    lemmatize=True
)
# Result: "study investigate machine learning algorithm nlp task"
```

## Performance Notes

- **Small Model (en_core_web_sm)**: ~15MB, fast processing, good for most use cases
- **Medium Model (en_core_web_md)**: ~50MB, includes word vectors
- **Large Model (en_core_web_lg)**: ~750MB, best accuracy

For typical text cleaning tasks, the small model is recommended.

## Troubleshooting

### Model Not Found
```
OSError: [E050] Can't find model 'en_core_web_sm'
```
**Solution**: `python -m spacy download en_core_web_sm`

### Import Error
```
ModuleNotFoundError: No module named 'spacy'
```
**Solution**: `pip install spacy`

### Memory Issues with Large Texts
For very large texts, process in batches:

```python
# Process large text lists in chunks
def process_large_list(texts, batch_size=100):
    results = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        results.extend(cleaner.clean_text_list(batch))
    return results
```
