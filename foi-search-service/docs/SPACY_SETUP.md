# spaCy Setup Guide

This guide explains how to set up spaCy for advanced text processing features in the TextCleaner utility.

## Installation

### 1. Install spaCy

```bash
pip install spacy>=3.8.7
```

### 2. Download English Language Model

```bash
# Download the small English model (recommended for most use cases)
python -m spacy download en_core_web_sm

# Alternative: Download medium model for better accuracy
python -m spacy download en_core_web_md

# Alternative: Download large model for best accuracy (larger download)
python -m spacy download en_core_web_lg
```

## Usage

### Basic Usage

```python
from src.utils.text_cleaning_utils import TextCleaner

# Initialize with default small model
cleaner = TextCleaner()

# Initialize with specific model
cleaner = TextCleaner(spacy_model="en_core_web_md")

# Remove stop words using spaCy
text = "The quick brown fox jumps over the lazy dog"
result = cleaner.remove_stop_words(text, use_spacy=True)
print(result)  # "quick brown fox jumps lazy dog"
```

### Advanced Features with spaCy

When spaCy is available, the TextCleaner provides enhanced functionality:

1. **Better Tokenization**: spaCy's advanced tokenizer handles complex text better than simple whitespace splitting
2. **Lemmatization**: Words are reduced to their base form (e.g., "running" → "run")
3. **Enhanced Stop Word Detection**: Uses spaCy's comprehensive stop word list
4. **Punctuation Handling**: Better detection of punctuation vs. meaningful symbols

### Fallback Behavior

If spaCy is not available or the model isn't found:
- The TextCleaner will use basic text processing methods
- A warning will be displayed during initialization
- All functionality will still work, but with reduced accuracy

### Stop Word Features

```python
# Get stop words (spaCy list if available, fallback otherwise)
stop_words = cleaner.get_stop_words()
print(f"Number of stop words: {len(stop_words)}")

# Add custom stop words
cleaner.add_stop_words(["custom", "domain", "specific"])

# Remove stop words with custom list
custom_stops = {"quick", "brown", "lazy"}
result = cleaner.remove_stop_words(text, custom_stop_words=custom_stops)

# Remove stop words from word list
words = ["the", "quick", "brown", "fox"]
filtered = cleaner.remove_stop_words_from_list(words)
```

### Performance Considerations

- **Small Model (en_core_web_sm)**: ~15MB, fastest processing
- **Medium Model (en_core_web_md)**: ~50MB, includes word vectors
- **Large Model (en_core_web_lg)**: ~750MB, best accuracy

For most text cleaning tasks, the small model is sufficient.

## Troubleshooting

### Model Not Found Error

If you see:
```
OSError: [E050] Can't find model 'en_core_web_sm'
```

Solution:
```bash
python -m spacy download en_core_web_sm
```

### Import Error

If you see:
```
ModuleNotFoundError: No module named 'spacy'
```

Solution:
```bash
pip install spacy
```

### Verification

Test your installation:

```python
import spacy

# Check if spaCy is installed
print(f"spaCy version: {spacy.__version__}")

# Test model loading
try:
    nlp = spacy.load("en_core_web_sm")
    print("✓ English model loaded successfully")
    
    # Test processing
    doc = nlp("The quick brown fox jumps over the lazy dog")
    print(f"Tokens: {[token.text for token in doc]}")
    print(f"Stop words removed: {[token.text for token in doc if not token.is_stop]}")
    
except OSError:
    print("✗ English model not found. Run: python -m spacy download en_core_web_sm")
```

## Integration with Project

The TextCleaner automatically detects spaCy availability:

```python
from src.utils.text_cleaning_utils import TextCleaner, SPACY_AVAILABLE

if SPACY_AVAILABLE:
    print("✓ spaCy features available")
else:
    print("⚠ Using basic text processing (install spaCy for enhanced features)")

# Works regardless of spaCy availability
cleaner = TextCleaner()
result = cleaner.clean_text("Your text here", remove_stop_words=True)
```

## Additional Resources

- [spaCy Documentation](https://spacy.io/usage)
- [spaCy Models Overview](https://spacy.io/models/en)
- [Language Support](https://spacy.io/usage/models#languages)
