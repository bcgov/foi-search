# Examples Directory

This directory contains practical examples demonstrating the capabilities of the SBERTify embedding system. Each example showcases different aspects of text processing and embedding generation.

## 📊 compare_embeddings.py

### Overview

The `compare_embeddings.py` script demonstrates the impact of text preprocessing on embedding quality by comparing embeddings generated from raw text versus cleaned/preprocessed text. This analysis helps you understand how text cleaning affects semantic similarity while potentially reducing token usage.

### What It Does

1. **Text Preprocessing**: Applies advanced NLP-based cleaning using spaCy
2. **Embedding Generation**: Creates embeddings for both raw and cleaned text
3. **Similarity Analysis**: Computes cosine similarity between raw and cleaned embeddings
4. **Token Efficiency**: Analyzes token count reduction through preprocessing

### Key Features

- **Multi-Provider Support**: Works with any configured embedding provider (Hugging Face, OpenAI, etc.)
- **Advanced Text Cleaning**: Leverages spaCy for POS filtering, lemmatization, and contraction expansion
- **Detailed Analytics**: Provides token count analysis and reduction percentages
- **Visual Output**: Color-coded console output for easy interpretation

### Text Cleaning Pipeline

The script applies the following preprocessing steps:

- **POS Filtering**: Keeps only meaningful parts of speech (NOUN, VERB, ADJ, PRON, NUM, ADP, ADV)
- **Lemmatization**: Reduces words to their base forms (e.g., "revolutionizing" → "revolutionize")
- **Contraction Expansion**: Expands contractions (e.g., "we're" → "we are")
- **Case Normalization**: Converts text to lowercase
- **Selective Cleaning**: Preserves numbers and important punctuation

### Usage

```bash
python examples/compare_embeddings.py
```

### Configuration

The script uses your project's configuration from:
- Provider settings (model, API keys, etc.)
- Tokenization parameters (max length, char estimates)

Update your `.env` file or configuration to change providers or models.

### Sample Output Analysis

```
🧾 Cosine Similarity Results per Sentence

Sentence 1:
  🔹 Raw     : Artificial intelligence (AI) is revolutionizing the way we live and work.
  🔹 Cleaned : artificial intelligence revolutionize way we live work
  📦 Tokens  : Raw = 11, Cleaned = 7 (36.4% reduction)
  ✅ Cosine Similarity: 0.8548

Sentence 2:
  🔹 Raw     : Nowadays, AI systems are capable of performing tasks that were once thought to be exclusive to humans.
  🔹 Cleaned : nowadays system capable of perform task that once think exclusive to human
  📦 Tokens  : Raw = 17, Cleaned = 12 (29.4% reduction)
  ✅ Cosine Similarity: 0.7718

Sentence 3:
  🔹 Raw     : In the future, we can expect AI to become even more integrated into our daily lives.
  🔹 Cleaned : in future we expect become even more integrated into our daily life
  📦 Tokens  : Raw = 16, Cleaned = 12 (25.0% reduction)
  ✅ Cosine Similarity: 0.7715
```

### Interpreting Results

#### Cosine Similarity Scores
- **0.8548**: Excellent semantic preservation despite 36.4% token reduction
- **0.7718**: Good semantic preservation with 29.4% token reduction  
- **0.7715**: Good semantic preservation with 25.0% token reduction

#### What This Tells Us

1. **Efficiency Gains**: Text cleaning reduces token usage by 25-36% while maintaining semantic meaning
2. **Cost Optimization**: For paid APIs (like OpenAI), this translates to significant cost savings
3. **Quality Trade-offs**: High cosine similarity (>0.75) indicates that essential semantic information is preserved
4. **Processing Benefits**: Cleaned text focuses on core semantic content, potentially improving downstream tasks

#### Token Reduction Benefits

- **API Cost Savings**: Fewer tokens = lower costs for commercial embedding services
- **Faster Processing**: Reduced token count leads to faster embedding generation
- **Storage Efficiency**: Smaller embeddings and reduced memory footprint
- **Focused Semantics**: Cleaned text emphasizes core meaning over linguistic artifacts

### When to Use Text Cleaning

**Recommended for:**
- Cost-sensitive applications using paid APIs
- Large-scale text processing pipelines
- Applications focused on core semantic content
- Scenarios where slight semantic loss is acceptable

**Avoid when:**
- Preserving exact linguistic nuances is critical
- Working with poetry, creative writing, or stylistic text
- Applications requiring precise grammatical structure
- Legal or medical documents where every word matters

### Customizing the Cleaning Process

You can modify the cleaning parameters in the script:

```python
cleaned_texts = clean_text_list(
    chunks,
    keep_pos={"NOUN", "VERB", "ADJ", "PRON", "NUM", "ADP", "ADV"},  # Parts of speech to keep
    lemmatize=True,          # Apply lemmatization
    remove_numbers=False,    # Keep numbers
    remove_stopwords=False,  # Keep stopwords (since we filter by POS)
    remove_punct=False       # Keep punctuation
)
```

### Prerequisites

Ensure you have the required dependencies installed:

```bash
pip install spacy scikit-learn
python -m spacy download en_core_web_sm
```

### Error Handling

The script includes comprehensive error handling for:
- Provider initialization failures
- Text processing errors
- Embedding generation issues
- Configuration problems

### Extending the Example

Consider these enhancements:
- Test with different cleaning strategies
- Compare multiple embedding models
- Analyze semantic similarity across different text types
- Export results to CSV for further analysis
- Add visualization with matplotlib or plotly

---

## Contributing

Feel free to add more examples that demonstrate other aspects of the SBERTify system:
- Batch processing examples
- Multi-provider comparisons
- Semantic search implementations
- Text clustering and classification demos

Each example should include clear documentation and practical use cases to help users understand the system's capabilities.
