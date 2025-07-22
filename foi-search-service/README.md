#  FOI Search Service

**FOI Search Service** is a sophisticated Python library for generating high-quality sentence and document embeddings using multiple providers including Hugging Face Transformers, OpenAI, and others. Designed for NLP researchers and developers, it provides a unified interface for tokenization, embedding generation, and text preprocessing with comprehensive analytics and cost optimization.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

---

## 🌟 Key Features

### 🔌 **Multi-Provider Architecture**
- **Hugging Face Transformers**: Local models with GPU/CPU support
- **OpenAI Embeddings**: Commercial API with batch processing
- **Extensible Factory Pattern**: Easy to add new providers

### 🧹 **Advanced Text Preprocessing**
- **spaCy-powered NLP**: POS filtering, lemmatization, entity recognition
- **Smart Cleaning**: Contraction expansion, stopword removal, token optimization
- **Semantic Preservation**: Maintain meaning while reducing token count by 25-40%

### 📊 **Comprehensive Analytics**
- **Cost Estimation**: Real-time API cost tracking and optimization
- **Token Analysis**: Detailed usage metrics and reduction statistics
- **Quality Metrics**: Cosine similarity analysis for preprocessing validation

### ⚡ **Performance & Efficiency**
- **Batch Processing**: Optimized for large-scale text processing
- **Smart Validation**: Input sanitization and length management
- **Configurable Limits**: Token length, batch size, and retry logic

### 🔧 **Developer Experience**
- **Type-Safe**: Full typing support with dataclasses
- **Comprehensive Testing**: 95%+ test coverage
- **Rich Configuration**: Environment-based settings with validation
- **Detailed Logging**: Structured JSON logging for monitoring

---

## 🚀 Quick Start

### Running the Service


### Basic Usage

```python
from src.config import get_config
from src.sbert_sentence_tokenizer import SBERTSentenceTokenizer

# Initialize with default configuration
config = get_config()
tokenizer = SBERTSentenceTokenizer(
    provider_configuration=config.provider,
    max_token_length=config.tokenization.max_token_length,
    max_words_length=config.tokenization.max_words_length,
    token_char_estimate=config.tokenization.token_char_estimate,
)

# Generate embeddings
sentences = [
    "Artificial intelligence is transforming industries.",
    "Machine learning enables intelligent automation.",
    "Natural language processing improves human-computer interaction."
]

result = tokenizer.embedding_sentences(sentences)

print(f"Generated {result.num_sentences} embeddings")
print(f"Embedding dimensions: {result.embedding_dimension}")
print(f"Total tokens used: {result.tokens_used}")
print(f"Estimated cost: {result.formatted_cost}")
```

### Provider Configuration

#### Hugging Face (Local Models)
```python
from src.config import ProviderConfig

config = ProviderConfig(
    provider_name="huggingface",
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    embedding_dimension=384,
    max_tokens=256,
    supports_batch=True
)
```

#### OpenAI (API)
```python
config = ProviderConfig(
    provider_name="openai",
    model_name="text-embedding-3-small",
    embedding_dimension=1536,
    max_tokens=8192,
    cost_per_1k_tokens=0.02,
    api_key="your-openai-api-key",
    supports_batch=True
)
```

---

## 🧹 Advanced Text Preprocessing

FOI Search Service includes sophisticated text cleaning capabilities that can reduce token usage by 25-40% while preserving semantic meaning:

```python
from src.utils.text_cleaning_utils import clean_text_list

# Original text
raw_sentences = [
    "Artificial intelligence (AI) is revolutionizing the way we live and work.",
    "Nowadays, AI systems are capable of performing tasks that were once thought to be exclusive to humans."
]

# Apply intelligent cleaning
cleaned_sentences = clean_text_list(
    raw_sentences,
    keep_pos={"NOUN", "VERB", "ADJ", "PRON", "NUM", "ADP", "ADV"},
    lemmatize=True,
    remove_numbers=False,
    remove_stopwords=False,
    remove_punct=False
)

# Results:
# Original: "Artificial intelligence (AI) is revolutionizing the way we live and work."
# Cleaned:  "artificial intelligence revolutionize way we live work"
# Token reduction: 36.4%, Semantic similarity: 85.48%
```

### Text Cleaning Features

- **Part-of-Speech Filtering**: Keep only semantically meaningful words
- **Lemmatization**: Reduce words to base forms (`revolutionizing` → `revolutionize`)
- **Contraction Expansion**: Convert contractions (`we're` → `we are`)
- **Smart Preservation**: Maintain numbers and critical punctuation
- **Configurable Processing**: Customize cleaning parameters per use case

---

## 📊 Cost Optimization & Analytics

### Real-time Cost Tracking
```python
# Estimate costs before processing
tokens, cost = tokenizer.provider.estimate_tokens_and_cost(sentences)
print(f"Estimated tokens: {tokens}")
print(f"Estimated cost: ${cost:.6f}")

# Compare raw vs cleaned text costs
raw_result = tokenizer.embedding_sentences(raw_sentences)
cleaned_result = tokenizer.embedding_sentences(cleaned_sentences)

savings = raw_result.cost_estimate - cleaned_result.cost_estimate
print(f"Cost savings: ${savings:.6f} ({savings/raw_result.cost_estimate*100:.1f}%)")
```

### Embedding Quality Analysis
```python
from examples.compare_embeddings import compare_embeddings

# Run comprehensive analysis
results = compare_embeddings(sentences)
# Outputs detailed similarity metrics, token reduction stats, and cost analysis
```

---

## 🏗️ Architecture

### Project Structure
```
foi-search-service/
├── src/
│   ├── config/                 # Configuration management
│   │   ├── provider_config.py  # Provider-specific settings
│   │   ├── tokenization_config.py # Tokenization parameters
│   │   └── global_config.py     # Application-wide settings
│   ├── providers/              # Embedding providers
│   │   ├── embedding_provider.py # Base provider interface
│   │   ├── huggingface_provider.py # Hugging Face implementation
│   │   ├── openai_provider.py   # OpenAI implementation
│   │   ├── provider_factory.py  # Provider factory pattern
│   │   └── clients/            # API client wrappers
│   ├── utils/                  # Utility functions
│   │   ├── text_cleaning_utils.py # NLP-based text processing
│   │   ├── validation_utils.py  # Input validation
│   │   └── logging_utils.py     # Structured logging
│   ├── schemas/               # Data models
│   │   └── models.py          # Result and configuration classes
│   └── sbert_sentence_tokenizer.py # Main tokenizer interface
├── tests/                     # Comprehensive test suite
├── examples/                  # Usage examples and demos
├── docs/                     # Documentation
└── scripts/                  # Utility scripts
```

### Provider Factory Pattern
```python
from src.providers.provider_factory import ProviderFactory

# List available providers
providers = ProviderFactory.get_available_providers()
print(providers)  # ['huggingface', 'openai', 'local', ...]

# Create provider dynamically
provider = ProviderFactory.create_provider(
    provider_config=config.provider,
    device="cuda",  # For local models
    normalize_embeddings=True
)
```

---

## ⚙️ Configuration

### Environment Variables
Create a `.env` file (see `.env_sample` for reference):

```bash
# Provider Settings
PROVIDER_NAME=huggingface
MODEL_NAME=sentence-transformers/all-MiniLM-L6-v2
EMBEDDING_DIM=384
COST_PER_1K=0.0

# OpenAI Settings (when using OpenAI provider)
API_KEY=your-openai-api-key
API_BASE_URL=https://api.openai.com/v1

# Tokenization Settings
MAX_TOKEN_LENGTH=512
MAX_WORDS_LENGTH=120
TOKEN_CHAR_ESTIMATE=4

# Performance Settings
MAX_BATCH_SIZE=100
MAX_RETRIES=3
TIMEOUT=30.0
```

### Multiple Environments
```bash
# Development
cp .env_sample .env

# Testing
cp .env_sample .env.test

# OpenAI specific
cp .env_sample .env_openai
```

---

## 🧪 Testing & Development

### Running Tests
```bash
# Full test suite
make test

# With coverage
make test-coverage

# Specific test categories
pytest tests/providers/  # Provider tests
pytest tests/utils/      # Utility tests
pytest tests/test_sbert_sentence_tokenizer.py  # Main tokenizer tests
```

### Development Setup
```bash
# Clone repository
git clone https://github.com/bcgov/foi-search
cd foi-search-service

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
make install
make install-dev  # For development dependencies

# Install spaCy model
make download-models 

# Run tests
make test
```

---

## 📚 Examples

### Basic Embedding Generation
See `examples/compare_embeddings.py` for a comprehensive demonstration of:
- Multi-provider embedding generation
- Text preprocessing comparison
- Cost and quality analysis
- Token reduction metrics

---

## 🤝 Contributing

We welcome contributions! Please see our contribution guidelines:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Make** your changes with tests
4. **Run** the test suite (`make test`)
5. **Commit** your changes (`git commit -m 'Add amazing feature'`)
6. **Push** to the branch (`git push origin feature/amazing-feature`)
7. **Open** a Pull Request

### Development Standards
- **Code Quality**: Black formatting, type hints, comprehensive docstrings
- **Testing**: Maintain 95%+ coverage, add tests for new features
- **Documentation**: Update README and docstrings for new functionality

---

## 📋 Requirements

### Core Dependencies
- **Python**: 3.8+
- **transformers**: 4.52.4+
- **sentence-transformers**: 4.1.0+
- **numpy**: 2.3.0+
- **openai**: 1.88.0+
- **spacy**: 3.8.7+
- **torch**: 2.7.1+ (for local models)

### Optional Dependencies
- **scikit-learn**: For similarity analysis
- **tqdm**: Progress bars
- **pytest**: Testing framework

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **[Hugging Face](https://huggingface.co/)**: For their excellent Transformers library and model hub
- **[OpenAI](https://openai.com/)**: For their powerful embedding APIs
- **[Sentence Transformers](https://www.sbert.net/)**: For semantic similarity models
- **[spaCy](https://spacy.io/)**: For advanced NLP processing capabilities

---

## 📞 Support

- **Documentation**: Check the `docs/` directory for detailed guides
- **Examples**: Review `examples/` for practical implementations
- **Issues**: Report bugs and request features via GitHub Issues
---