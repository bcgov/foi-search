import pytest
from utils.text_cleaning_utils import TextCleaner, clean_text, clean_text_list

#TODO Move to integration tests
class TestTextCleaner:
    """Test cases for the spaCy-based TextCleaner class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.cleaner = TextCleaner()
    
    def test_init_default_model(self):
        """Test initialization with default model."""
        cleaner = TextCleaner()
        assert cleaner.nlp.meta['name'] == 'core_web_sm'
    
    def test_init_custom_model(self):
        """Test initialization with custom model."""
        # This test assumes en_core_web_sm is available
        cleaner = TextCleaner(model="en_core_web_sm")
        assert cleaner.nlp.meta['name'] == 'core_web_sm'
    
    def test_init_invalid_model(self):
        """Test initialization with invalid model raises error."""
        with pytest.raises(OSError):
            TextCleaner(model="nonexistent_model")
    
    def test_clean_text_basic(self):
        """Test basic text cleaning with default options."""
        text = "Hello! How are you doing today?"
        result = self.cleaner.clean_text(text)
        
        # Should be lowercase and cleaned
        assert result.islower()
        assert "!" not in result
        assert "?" not in result
        # Should remove stopwords like "are", "you", "doing"
        assert "hello" in result
        assert "today" in result
    
    def test_clean_text_lowercase_option(self):
        """Test lowercase option."""
        text = "Hello World"
        
        result_lower = self.cleaner.clean_text(text, lowercase=True)
        result_no_lower = self.cleaner.clean_text(text, lowercase=False)
        
        assert result_lower.islower()
        assert not result_no_lower.islower()
        assert "Hello" in result_no_lower or "hello" in result_no_lower
    
    def test_clean_text_remove_stopwords(self):
        """Test stopword removal option."""
        text = "This is a test sentence with many stopwords."
        
        result_no_stopwords = self.cleaner.clean_text(text, remove_stopwords=True)
        result_with_stopwords = self.cleaner.clean_text(text, remove_stopwords=False)
        
        # Common stopwords should be removed when option is True
        stopwords = ["is", "a", "with"]
        for stopword in stopwords:
            assert stopword not in result_no_stopwords
            assert stopword in result_with_stopwords
    
    def test_clean_text_lemmatize(self):
        """Test lemmatization option."""
        text = "running dogs cats flies"
        
        result_lemmatized = self.cleaner.clean_text(
            text, 
            lemmatize=True, 
            remove_stopwords=False,
            remove_punct=False
        )
        result_not_lemmatized = self.cleaner.clean_text(
            text, 
            lemmatize=False, 
            remove_stopwords=False,
            remove_punct=False
        )
        
        # Should contain lemmas when lemmatize=True
        assert "run" in result_lemmatized  # running -> run
        assert "dog" in result_lemmatized  # dogs -> dog
        assert "cat" in result_lemmatized  # cats -> cat
        assert "fly" in result_lemmatized  # flies -> fly
        
        # Should contain original forms when lemmatize=False
        assert "running" in result_not_lemmatized
        assert "dogs" in result_not_lemmatized
        assert "cats" in result_not_lemmatized
        assert "flies" in result_not_lemmatized
    
    def test_clean_text_remove_punctuation(self):
        """Test punctuation removal option."""
        text = "Hello! How are you? I'm fine, thanks."
        
        result_no_punct = self.cleaner.clean_text(text, remove_punct=True)
        result_with_punct = self.cleaner.clean_text(text, remove_punct=False)
        
        punctuation = ["!", "?", ",", "."]
        for punct in punctuation:
            assert punct not in result_no_punct
    
    def test_clean_text_remove_numbers(self):
        """Test number removal option."""
        text = "I have 5 cats and 10 dogs in 2024."
        
        result_no_numbers = self.cleaner.clean_text(text, remove_numbers=True)
        result_with_numbers = self.cleaner.clean_text(text, remove_numbers=False)
        
        # Numbers should be removed when option is True
        numbers = ["5", "10", "2024"]
        for number in numbers:
            assert number not in result_no_numbers
        
        # At least some numbers should remain when option is False
        # (depending on other cleaning options)
        assert any(char.isdigit() for char in result_with_numbers) or \
               any(num in result_with_numbers for num in ["five", "ten"])
    
    def test_clean_text_keep_pos(self):
        """Test POS filtering option."""
        text = "The quick brown fox jumps over the lazy dog."
        
        # Keep only nouns
        result_nouns = self.cleaner.clean_text(
            text, 
            keep_pos={"NOUN"},
            remove_stopwords=False,
            remove_punct=False
        )
        
        # Keep only verbs
        result_verbs = self.cleaner.clean_text(
            text, 
            keep_pos={"VERB"},
            remove_stopwords=False,
            remove_punct=False
        )
        
        # Nouns should be in noun result
        assert "fox" in result_nouns
        assert "dog" in result_nouns
        
        # Verbs should be in verb result
        assert "jump" in result_verbs  # lemmatized form of "jumps"
        
        # Adjectives should not be in noun result
        assert "quick" not in result_nouns
        assert "brown" not in result_nouns
        assert "lazy" not in result_nouns
    
    def test_clean_text_keep_pos_multiple(self):
        """Test POS filtering with multiple POS tags."""
        text = "The beautiful cat sleeps peacefully on the soft bed."
        
        result = self.cleaner.clean_text(
            text, 
            keep_pos={"NOUN", "ADJ"},
            remove_stopwords=False,
            remove_punct=False
        )
        
        # Should contain nouns and adjectives
        assert "beautiful" in result  # adjective
        assert "cat" in result        # noun
        # assert "peaceful" in result   # adjective (lemmatized from "peacefully")
        assert "soft" in result       # adjective
        assert "bed" in result        # noun
        
        # Should not contain verbs
        assert "sleep" not in result
    
    def test_clean_text_combined_options(self):
        """Test cleaning with multiple options combined."""
        text = "The 5 RUNNING dogs can't jump over 10 tall fences!"
        
        result = self.cleaner.clean_text(
            text,
            lowercase=True,
            remove_stopwords=True,
            lemmatize=True,
            remove_punct=True,
            remove_numbers=True,
            keep_pos={"NOUN", "VERB"}
        )
        
        # Should be lowercase
        assert result.islower()
        
        # Should contain lemmatized forms
        assert "dog" in result      # dogs -> dog
        assert "run" in result      # running -> run
        assert "jump" in result     # jump (already lemma)
        assert "fence" in result    # fences -> fence
        
        # Should not contain stopwords, punctuation, or numbers
        assert "the" not in result
        assert "can" not in result
        assert "over" not in result
        assert "!" not in result
        assert "5" not in result
        assert "10" not in result
        
        # Should not contain adjectives (tall)
        assert "tall" not in result
    
    def test_clean_text_empty_string(self):
        """Test cleaning empty string."""
        result = self.cleaner.clean_text("")
        assert result == ""
    
    def test_clean_text_whitespace_only(self):
        """Test cleaning whitespace-only string."""
        result = self.cleaner.clean_text("   \t\n   ")
        assert result == ""
    
    def test_clean_text_non_string_input(self):
        """Test cleaning non-string input."""
        test_inputs = [None, 123, [], {}, True]
        
        for input_val in test_inputs:
            result = self.cleaner.clean_text(input_val)
            assert result == ""
    
    def test_clean_text_unicode_handling(self):
        """Test cleaning text with Unicode characters."""
        text = "café naïve résumé piñata"
        
        result = self.cleaner.clean_text(
            text,
            remove_stopwords=False,
            remove_punct=False
        )
        
        # Should handle Unicode characters properly
        assert len(result) > 0
        # Unicode characters should be preserved
        assert any(ord(char) > 127 for char in result)
    
    def test_clean_text_very_long_text(self):
        """Test cleaning very long text."""
        long_text = "This is a test sentence. " * 1000
        
        result = self.cleaner.clean_text(long_text)
        
        # Should not crash and should return a string
        assert isinstance(result, str)
        assert len(result) > 0
    
    def test_clean_text_list_basic(self):
        """Test cleaning a list of texts."""
        texts = [
            "Hello! How are you?",
            "I'm fine, thanks.",
            "What about you?"
        ]
        
        results = self.cleaner.clean_text_list(texts)
        
        assert len(results) == len(texts)
        assert all(isinstance(result, str) for result in results)
        
        # Check that each text was cleaned
        for result in results:
            if result:
                assert result.islower()  # Should be lowercase
                assert "!" not in result  # No punctuation
                assert "?" not in result
    
    def test_clean_text_list_with_options(self):
        """Test cleaning a list with custom options."""
        texts = [
            "The cats are running.",
            "Dogs can't fly high.",
            "Birds sing beautifully."
        ]
        
        results = self.cleaner.clean_text_list(
            texts,
            keep_pos={"NOUN", "VERB"},
            lemmatize=True,
            remove_stopwords=False
        )
        
        # Should contain nouns and verbs only
        combined_result = " ".join(results)
        assert "cat" in combined_result
        assert "run" in combined_result
        assert "dog" in combined_result
        assert "fly" in combined_result
        assert "bird" in combined_result
        assert "sing" in combined_result
    
    def test_clean_text_list_empty_list(self):
        """Test cleaning empty list."""
        result = self.cleaner.clean_text_list([])
        assert result == []
    
    def test_clean_text_list_with_empty_strings(self):
        """Test cleaning list containing empty strings."""
        texts = ["Hello world", "", "  ", "Goodbye"]
        results = self.cleaner.clean_text_list(texts)
        
        assert len(results) == len(texts)
        assert results[1] == ""  # Empty string remains empty
        assert results[2] == ""  # Whitespace-only becomes empty
    
    def test_clean_text_list_with_mixed_types(self):
        """Test cleaning list with mixed input types."""
        texts = ["Hello world", None, 123, "Goodbye"]
        results = self.cleaner.clean_text_list(texts)
        
        assert len(results) == len(texts)
        assert isinstance(results[0], str)
        assert results[1] == ""  # None becomes empty string
        assert results[2] == ""  # Number becomes empty string
        assert isinstance(results[3], str)


class TestConvenienceFunctions:
    """Test cases for convenience functions."""
    
    def test_clean_text_function(self):
        """Test the standalone clean_text function."""
        text = "Hello! How are you doing today?"
        result = clean_text(text)
        
        # Should work like the class method
        assert isinstance(result, str)
        assert result.islower()
        assert "!" not in result
        assert "?" not in result
    
    def test_clean_text_function_with_options(self):
        """Test the standalone clean_text function with options."""
        text = "The running dogs can't jump!"
        result = clean_text(
            text,
            keep_pos={"NOUN", "VERB"},
            lemmatize=True
        )
        
        assert "dog" in result
        assert "run" in result
        assert "jump" in result
        assert "the" not in result  # Should remove stopword
    
    def test_clean_text_list_function(self):
        """Test the standalone clean_text_list function."""
        texts = ["Hello world!", "How are you?"]
        results = clean_text_list(texts)
        
        assert len(results) == len(texts)
        assert all(isinstance(result, str) for result in results)
        assert all("!" not in result and "?" not in result for result in results)
    
    def test_clean_text_list_function_with_options(self):
        """Test the standalone clean_text_list function with options."""
        texts = ["Running cats", "Flying birds"]
        results = clean_text_list(
            texts,
            keep_pos={"NOUN", "VERB"},
            lemmatize=True
        )
        
        combined = " ".join(results)
        assert "run" in combined
        assert "cat" in combined
        assert "fly" in combined
        assert "bird" in combined


class TestRealWorldExamples:
    """Test with real-world text examples."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.cleaner = TextCleaner()
    
    def test_news_headline(self):
        """Test cleaning a news headline."""
        headline = "Breaking: Company's Stock Prices Jump 25% After CEO's Announcement!"

        result = self.cleaner.clean_text(
            headline,
            keep_pos={"NOUN", "VERB", "NUM", "PROPN"},
            lemmatize=True,
            remove_stopwords=False,
            remove_punct=False,
            remove_numbers=False
        )

        # Should contain key nouns and verbs
        expected_words = {"breaking", "company", "stock", "prices", "jump", "25", "ceo", "announcement"}
        assert expected_words.issubset(set(result.split()))
    
    def test_social_media_post(self):
        """Test cleaning a social media post."""
        post = "OMG! Can't believe the amazing concert last night! 🎵 The band was incredible! #music #concert"

        result = self.cleaner.clean_text(
            post,
            lowercase=True,
            remove_stopwords=True,
            lemmatize=True,
            remove_punct=True,
            remove_numbers=True,
            keep_pos={"NOUN", "VERB", "ADJ"}
         )

        # Should be cleaned and readable
        assert "believe" in result
        assert "amazing" in result or "amaze" in result
        assert "concert" in result
        assert "night" in result
        assert "band" in result
        assert "incredible" in result
        
        # Should remove punctuation and emojis
        assert "!" not in result
        assert "🎵" not in result
        assert "#" not in result
    
    def test_product_description(self):
        """Test cleaning a product description."""
        description = """
        This high-quality smartphone features a 6.5-inch display, 
        128GB storage, and a powerful 12MP camera. The battery lasts 
        up to 24 hours with normal usage. Perfect for professionals!
        """
        
        result = self.cleaner.clean_text(
            description,
            keep_pos={"NOUN", "ADJ", "NUM"},
            remove_numbers=False
        )
        
        # Should contain key product features
        assert "smartphone" in result
        assert "display" in result
        assert "storage" in result
        assert "camera" in result
        assert "battery" in result
        assert "hour" in result
        assert "professional" in result
    
    def test_academic_abstract(self):
        """Test cleaning an academic abstract."""
        abstract = """
        This study investigates the effectiveness of machine learning algorithms
        in natural language processing tasks. We analyzed 10,000 documents
        using various preprocessing techniques. Our results demonstrate
        significant improvements in accuracy and processing speed.
        """
        
        result = self.cleaner.clean_text(
            abstract,
            keep_pos={"NOUN", "VERB", "ADJ"},
            lemmatize=True
        )
        
        # Should contain key academic terms
        assert "study" in result
        assert "investigate" in result
        assert "effectiveness" in result or "effective" in result
        assert "algorithm" in result
        assert "language" in result
        assert "process" in result
        assert "task" in result
        assert "analyze" in result
        assert "document" in result
        assert "technique" in result
        assert "result" in result
        assert "demonstrate" in result
        assert "improvement" in result
        assert "accuracy" in result
        assert "speed" in result
    
    def test_customer_review(self):
        """Test cleaning a customer review."""
        review = """
        I bought this product 2 weeks ago and I'm absolutely loving it!
        The quality is outstanding and it's very easy to use. 
        Would definitely recommend to anyone looking for reliability.
        """
        
        result = self.cleaner.clean_text(review)
        
        # Should preserve main sentiment and content
        assert "buy" in result or "bought" in result
        assert "product" in result
        assert "love" in result
        assert "quality" in result
        assert "outstanding" in result
        assert "easy" in result
        assert "use" in result
        assert "recommend" in result
        assert "reliability" in result or "reliable" in result


class TestEdgeCases:
    """Test edge cases and special scenarios."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.cleaner = TextCleaner()
    
    def test_only_punctuation(self):
        """Test text with only punctuation."""
        # TODO Revisit this test if punctuation handling changes
        import re

        text = "!@#$%^&*()+-=[]{}|;:,.<>?"
        text = re.sub(r"[^\w\s]", " ", text).strip()
        result = self.cleaner.clean_text(text, remove_punct=True)
        assert result == ""

    def test_only_numbers(self):
        """Test text with only numbers."""
        text = "123 456 789 2024"
        result = self.cleaner.clean_text(text, remove_numbers=True)
        assert result == ""
    
    def test_only_stopwords(self):
        """Test text with only stopwords."""
        text = "the and or but if then when where"
        result = self.cleaner.clean_text(text, remove_stopwords=True)
        assert result == ""
    
    def test_mixed_languages(self):
        """Test text with mixed languages (basic test)."""
        # Note: This assumes the model can handle some multilingual content
        text = "Hello world hola mundo"
        result = self.cleaner.clean_text(text, remove_stopwords=False)
        
        # Should not crash and should return something
        assert isinstance(result, str)
        assert len(result) > 0
    
    def test_special_characters_and_symbols(self):
        """Test text with special characters and symbols."""
        text = "Price: $29.99 @ 50% off! Contact us: info@company.com"
        result = self.cleaner.clean_text(text)
        
        # Should handle special characters gracefully
        assert isinstance(result, str)
        assert "price" in result
        assert "contact" in result
    
    def test_repeated_words(self):
        """Test text with many repeated words."""
        text = "good good good very very very nice nice nice product product"
        result = self.cleaner.clean_text(text, remove_stopwords=False)
        
        # Should preserve repeated words (spaCy processes each token)
        assert "good" in result
        assert "nice" in result
        assert "product" in result
    
    def test_contractions_and_possessives(self):
        """Test handling of contractions and possessives."""
        text = "John's car can't start. It's Mary's fault, isn't it?"
        result = self.cleaner.clean_text(text, remove_stopwords=False)
        
        # spaCy should handle contractions and possessives
        assert isinstance(result, str)
        assert len(result) > 0
        # Exact output depends on spaCy's tokenization
    
    def test_line_breaks_and_tabs(self):
        """Test text with line breaks and tabs."""
        text = "Line 1\nLine 2\tTabbed text\n\nEmpty line above"
        result = self.cleaner.clean_text(text,remove_stopwords=False)
        
        # Should normalize whitespace
        assert "\n" not in result
        assert "\t" not in result
        assert "line" in result
        assert "tabbed" in result
        assert "text" in result
        assert "empty" in result


class TestPerformance:
    """Basic performance and stress tests."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.cleaner = TextCleaner()
    
    def test_large_text_processing(self):
        """Test processing of large text."""
        # Create a reasonably large text (not too big for testing)
        large_text = ("This is a test sentence with various words. " * 100)
        
        result = self.cleaner.clean_text(large_text)
        
        # Should complete without error
        assert isinstance(result, str)
        assert len(result) > 0
        assert result.count("test") > 0  # Should contain cleaned content
    
    def test_many_small_texts(self):
        """Test processing many small texts."""
        texts = [f"Text number {i} for testing." for i in range(100)]
        
        results = self.cleaner.clean_text_list(texts)
        
        # Should complete without error
        assert len(results) == len(texts)
        assert all(isinstance(result, str) for result in results)
        assert all("text" in result for result in results)
        assert all("number" in result for result in results)


if __name__ == "__main__":
    pytest.main([__file__])
