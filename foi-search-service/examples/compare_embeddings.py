from sklearn.metrics.pairwise import cosine_similarity
from src.config import get_config
from src.utils.text_cleaning_utils import clean_text_list, extract_sentences
from src.sbert_sentence_tokenizer import SBERTSentenceTokenizer

if __name__ == "__main__":
    config = get_config()
    provider_config = config.provider
    token_config = config.tokenization

    # Initialize tokenizer
    tokenizer = SBERTSentenceTokenizer(
        provider_configuration=provider_config,
        max_token_length=token_config.max_token_length,
        max_words_length=token_config.max_words_length,
        token_char_estimate=token_config.token_char_estimate
    )

    raw_text = """
        Artificial intelligence (AI) is revolutionizing the way we live and work.
        Nowadays, AI systems are capable of performing tasks that were once thought to be exclusive to humans.
        In the future, we can expect AI to become even more integrated into our daily lives.
    """

    # Extract sentences
    chunks = extract_sentences(raw_text)

    raw_embeddings = None
    cleaned_embeddings = None
    cleaned_tokenized = None
    raw_tokenized = None
    # Raw embedding
    try:
        raw_tokenized = tokenizer.embedding_sentences(sentences=chunks)
        raw_embeddings = raw_tokenized.embeddings
    except Exception as e:
        print(f"Error during raw text tokenization: {e}")

    try:
        cleaned_texts = clean_text_list(
            chunks,
            keep_pos={"NOUN", "VERB", "ADJ", "PRON", "NUM", "ADP", "ADV"},
            lemmatize=True,
            remove_numbers=False,
            remove_stopwords=False,
            remove_punct=False
        )

        cleaned_tokenized = tokenizer.embedding_sentences(sentences=cleaned_texts)
        cleaned_embeddings = cleaned_tokenized.embeddings
    except Exception as e:
        print(f"Error during cleaned text tokenization: {e}")

    # Compare cosine similarity
    if raw_embeddings is not None and cleaned_embeddings is not None:
        if len(raw_embeddings) != len(cleaned_embeddings):
            print(f"⚠️ Warning: Sentence count mismatch. Raw: {len(raw_embeddings)}, Cleaned: {len(cleaned_embeddings)}")
        else:
            print("\n🧾 Cosine Similarity Results per Sentence\n")
            for idx, (raw_vec, clean_vec) in enumerate(zip(raw_embeddings, cleaned_embeddings)):
                sim = cosine_similarity(raw_vec.reshape(1, -1), clean_vec.reshape(1, -1))[0][0]
                raw_sentence = chunks[idx].strip()
                cleaned_sentence = cleaned_texts[idx].strip()

                raw_token_count = len(raw_sentence.split())
                cleaned_token_count = len(cleaned_sentence.split())
                reduction_pct = (1 - cleaned_token_count / raw_token_count) * 100 if raw_token_count else 0.0

                print(f"Sentence {idx + 1}:")
                print(f"  🔹 Raw     : {raw_sentence}")
                print(f"  🔹 Cleaned : {cleaned_sentence}")
                print(f"  📦 Tokens  : Raw = {raw_token_count}, Cleaned = {cleaned_token_count} ({reduction_pct:.1f}% reduction)")
                print(f"  ✅ Cosine Similarity: {sim:.4f}\n")

    elif raw_embeddings is None:
        print("⚠️ Raw embeddings not generated, cannot compute similarity.")
    else:
        print("⚠️ Cleaned embeddings not generated, cannot compute similarity.")
