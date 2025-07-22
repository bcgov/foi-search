import pytest
import numpy as np
from unittest.mock import patch, MagicMock, Mock

from config import ProviderConfig
from providers.huggingface_provider import HuggingFaceProvider
from schemas.models import EmbeddingResult
import math

@pytest.fixture
def provider_config():
    return ProviderConfig(
        provider_name="huggingface",
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        embedding_dimension=384,
        max_tokens=256,
        cost_per_1k_tokens=0.02,
        cost_per_1m_tokens=0.02
    )


@pytest.fixture
def provider_config_custom():
    return ProviderConfig(
        provider_name="huggingface",
        model_name="sentence-transformers/all-MiniLM-L12-v2",
        embedding_dimension=768,
        max_tokens=512,
        cost_per_1k_tokens=0.0
    )


class TestHuggingFaceProviderInitialization:
    """Test initialization and configuration of HuggingFace provider."""

    @patch('torch.cuda.is_available')
    @patch('sentence_transformers.SentenceTransformer')
    @patch('transformers.AutoTokenizer')
    def test_init_with_default_device(self, mock_tokenizer_cls, mock_model_cls, mock_cuda, provider_config):
        """Test initialization with automatic device selection."""
        mock_cuda.return_value = False
        mock_model = MagicMock()
        mock_model_cls.return_value = mock_model
        mock_tokenizer_cls.from_pretrained.return_value = MagicMock()

        provider = HuggingFaceProvider(provider_config)

        assert provider.device == "cpu"
        assert provider.provider_config == provider_config
        assert provider.normalize_embeddings is True
        mock_cuda.assert_called_once()

    @patch('torch.cuda.is_available')
    @patch('sentence_transformers.SentenceTransformer')
    @patch('transformers.AutoTokenizer')
    def test_init_with_cpu_fallback(self, mock_tokenizer_cls, mock_model_cls, mock_cuda, provider_config):
        """Test initialization falls back to CPU when CUDA unavailable."""
        mock_cuda.return_value = False
        mock_model = MagicMock()
        mock_model_cls.return_value = mock_model
        mock_tokenizer_cls.from_pretrained.return_value = MagicMock()

        provider = HuggingFaceProvider(provider_config)

        assert provider.device == "cpu"

    @patch('torch.cuda.is_available')
    @patch('sentence_transformers.SentenceTransformer')
    @patch('transformers.AutoTokenizer')
    def test_init_with_explicit_device(self, mock_tokenizer_cls, mock_model_cls, mock_cuda, provider_config):
        """Test initialization with explicitly set device."""
        mock_model = MagicMock()
        mock_model_cls.return_value = mock_model
        mock_tokenizer_cls.from_pretrained.return_value = MagicMock()

        provider = HuggingFaceProvider(provider_config, device="cpu")

        assert provider.device == "cpu"
        # Should not call cuda.is_available when device is explicitly set
        mock_cuda.assert_not_called()

    @patch('torch.cuda.is_available')
    @patch('sentence_transformers.SentenceTransformer')
    @patch('transformers.AutoTokenizer')
    def test_init_with_normalize_embeddings_false(self, mock_tokenizer_cls, mock_model_cls, mock_cuda, provider_config):
        """Test initialization with normalize_embeddings disabled."""
        mock_cuda.return_value = False
        mock_model = MagicMock()
        mock_model_cls.return_value = mock_model
        mock_tokenizer_cls.from_pretrained.return_value = MagicMock()

        provider = HuggingFaceProvider(provider_config, normalize_embeddings=False)

        assert provider.normalize_embeddings is False

class TestHuggingFaceProviderModelLoading:
    """Test model loading and validation."""

    @patch('torch.cuda.is_available')
    @patch('providers.huggingface_provider.SentenceTransformer')
    @patch('providers.huggingface_provider.AutoTokenizer')
    def test_initialize_provider_success(self, mock_tokenizer_cls, mock_model_cls, mock_cuda, provider_config):
        """Test successful provider initialization."""
        mock_cuda.return_value = False
        mock_model = MagicMock()
        mock_model_cls.return_value = mock_model
        mock_tokenizer = MagicMock()
        mock_tokenizer_cls.from_pretrained.return_value = mock_tokenizer

        provider = HuggingFaceProvider(provider_config)

        assert hasattr(provider, 'model')
        assert provider.model == mock_model
        assert provider.model.max_seq_length == 256
        assert provider.tokenizer == mock_tokenizer
        mock_model_cls.assert_called_once_with("sentence-transformers/all-MiniLM-L6-v2", device="cpu")
        mock_tokenizer_cls.from_pretrained.assert_called_once_with("sentence-transformers/all-MiniLM-L6-v2")

    @patch('torch.cuda.is_available')
    @patch('providers.huggingface_provider.SentenceTransformer')
    @patch('providers.huggingface_provider.AutoTokenizer')
    def test_initialize_provider_tokenizer_failure(self, mock_tokenizer_cls, mock_model_cls, mock_cuda, provider_config):
        """Test provider initialization with tokenizer loading failure."""
        mock_cuda.return_value = False
        mock_model = MagicMock()
        mock_model_cls.return_value = mock_model
        mock_tokenizer_cls.from_pretrained.side_effect = Exception("Tokenizer not found")

        provider = HuggingFaceProvider(provider_config)

        assert provider.tokenizer is None

    @patch('torch.cuda.is_available')
    @patch('providers.huggingface_provider.SentenceTransformer')
    @patch('providers.huggingface_provider.AutoTokenizer')
    def test_load_model_failure(self, mock_tokenizer_cls, mock_model_cls, mock_cuda, provider_config):
        """Test model loading failure."""
        mock_cuda.return_value = False
        mock_model_cls.side_effect = RuntimeError("Model not found")
        mock_tokenizer_cls.from_pretrained.return_value = MagicMock()

        with pytest.raises(RuntimeError, match="Failed to load any Hugging Face model"):
            HuggingFaceProvider(provider_config)

    @patch('torch.cuda.is_available')
    @patch('providers.huggingface_provider.SentenceTransformer')
    @patch('providers.huggingface_provider.AutoTokenizer')
    def test_is_model_loaded(self, mock_tokenizer_cls, mock_model_cls, mock_cuda, provider_config):
        """Test model loaded check."""
        mock_cuda.return_value = False
        mock_model = MagicMock()
        mock_model_cls.return_value = mock_model
        mock_tokenizer_cls.from_pretrained.return_value = MagicMock()

        provider = HuggingFaceProvider(provider_config)

        assert provider.is_model_loaded() is True

        # Test when model is not loaded
        del provider.model
        assert provider.is_model_loaded() is False


class TestHuggingFaceProviderValidation:
    """Test sentence validation functionality."""

    @patch('torch.cuda.is_available')
    @patch('providers.huggingface_provider.SentenceTransformer')
    @patch('providers.huggingface_provider.AutoTokenizer')
    def test_validate_sentences_valid_input(self, mock_tokenizer_cls, mock_model_cls, mock_cuda, provider_config):
        """Test validation with valid sentences."""
        mock_cuda.return_value = False
        mock_model_cls.return_value = MagicMock()
        mock_tokenizer_cls.from_pretrained.return_value = MagicMock()

        provider = HuggingFaceProvider(provider_config)
        sentences = ["Hello world", "This is a test"]
        
        valid_sentences, valid_indices, _, _ = provider.validate_sentences(sentences)
        
        assert valid_sentences == ["Hello world", "This is a test"]
        assert valid_indices == [0, 1]

    @patch('torch.cuda.is_available')
    @patch('providers.huggingface_provider.SentenceTransformer')
    @patch('providers.huggingface_provider.AutoTokenizer')
    def test_validate_sentences_filters_invalid(self, mock_tokenizer_cls, mock_model_cls, mock_cuda, provider_config):
        """Test validation filters out invalid sentences."""
        mock_cuda.return_value = False
        mock_model_cls.return_value = MagicMock()
        mock_tokenizer_cls.from_pretrained.return_value = MagicMock()

        provider = HuggingFaceProvider(provider_config)
        sentences = ["Hello world", "", "   ", None, 123, "Valid sentence"]
        
        valid_sentences, valid_indices, _, _ = provider.validate_sentences(sentences)
        
        assert valid_sentences == ["Hello world", "Valid sentence"]
        assert valid_indices == [0, 5]

    @patch('torch.cuda.is_available')
    @patch('providers.huggingface_provider.SentenceTransformer')
    @patch('providers.huggingface_provider.AutoTokenizer')
    def test_validate_sentences_max_words_filter(self, mock_tokenizer_cls, mock_model_cls, mock_cuda, provider_config):
        """Test validation filters sentences exceeding max words."""
        mock_cuda.return_value = False
        mock_model_cls.return_value = MagicMock()
        mock_tokenizer_cls.from_pretrained.return_value = MagicMock()

        provider = HuggingFaceProvider(provider_config)
        sentences = [
            "Short sentence",
            "This is a very " + "long " * 100 + "sentence"  # > 100 words
        ]
        
        valid_sentences, valid_indices,_,_ = provider.validate_sentences(sentences, max_words_length=50)
        
        assert valid_sentences == ["Short sentence"]
        assert valid_indices == [0]

    @patch('torch.cuda.is_available')
    @patch('providers.huggingface_provider.SentenceTransformer')
    @patch('providers.huggingface_provider.AutoTokenizer')
    def test_validate_sentences_empty_after_validation(self, mock_tokenizer_cls, mock_model_cls, mock_cuda, provider_config):
        """Test validation handles case when all sentences are invalid."""
        mock_cuda.return_value = False
        mock_model_cls.return_value = MagicMock()
        mock_tokenizer_cls.from_pretrained.return_value = MagicMock()

        provider = HuggingFaceProvider(provider_config)
        sentences = ["", "   ", None]
        
        valid_sentences, valid_indices, _, _ = provider.validate_sentences(sentences)
        
        assert valid_sentences == []
        assert valid_indices == []


class TestHuggingFaceProviderEncoding:
    """Test encoding functionality."""

    @patch('torch.cuda.is_available')
    @patch('providers.huggingface_provider.SentenceTransformer')
    @patch('providers.huggingface_provider.AutoTokenizer')
    def test_encode_sentences_success(self, mock_tokenizer_cls, mock_model_cls, mock_cuda, provider_config):
        """Test successful sentence encoding."""
        mock_cuda.return_value = False
        mock_model = MagicMock()
        mock_embeddings = np.random.rand(2, 384)
        mock_model.encode.return_value = mock_embeddings
        mock_model.tokenizer = MagicMock()
        mock_model_cls.return_value = mock_model
        
        mock_tokenizer = MagicMock()
        
        # Create mock tensor-like objects
        mock_tensor_input_ids = MagicMock()
        mock_tensor_input_ids.tolist.return_value = [[1, 2, 3], [1, 2]]
        mock_tensor_attention_mask = MagicMock()
        mock_tensor_attention_mask.tolist.return_value = [[1, 1, 1], [1, 1]]
        
        mock_tokenized = {
            "input_ids": mock_tensor_input_ids,
            "attention_mask": mock_tensor_attention_mask
        }
        mock_tokenizer.return_value = mock_tokenized
        mock_tokenizer.tokenize.side_effect = lambda s: s.split()
        mock_model.tokenizer = mock_tokenizer
        mock_tokenizer_cls.from_pretrained.return_value = mock_tokenizer

        provider = HuggingFaceProvider(provider_config)
        sentences = ["Hello world!", "Test sentence."]
        
        result = provider.encode_sentences(sentences)

        assert isinstance(result, EmbeddingResult)
        assert result.embeddings.shape == (2, 384)
        assert result.model_name == "sentence-transformers/all-MiniLM-L6-v2"
        assert result.provider_name == "huggingface"
        assert result.embedding_dimension == 384
        assert result.num_sentences == 2
        assert result.tokens_used == 7
        assert math.isclose(result.cost_estimate, 0.00014, rel_tol=1e-3)
        # assert result.metadata["device"] == "cpu"
        # assert result.metadata["normalize_embeddings"] is True

        mock_model.encode.assert_called_once_with(
            sentences,
            batch_size=32,
            show_progress_bar=True,
            normalize_embeddings=True
        )

    @patch('torch.cuda.is_available')
    @patch('providers.huggingface_provider.SentenceTransformer')
    @patch('providers.huggingface_provider.AutoTokenizer')
    def test_encode_sentences_dimension_mismatch(self, mock_tokenizer_cls, mock_model_cls, mock_cuda, provider_config):
        """Test encoding with dimension mismatch raises error."""
        mock_cuda.return_value = False
        mock_model = MagicMock()
        # Wrong dimension (512 instead of 384)
        mock_embeddings = np.random.rand(2, 512)
        mock_model.encode.return_value = mock_embeddings
        mock_model.tokenizer = MagicMock()
        mock_model_cls.return_value = mock_model
        mock_tokenizer_cls.from_pretrained.return_value = MagicMock()

        provider = HuggingFaceProvider(provider_config)
        sentences = ["Hello world!", "Test sentence."]
        
        with pytest.raises(ValueError, match="Embedding dimension mismatch"):
            provider.encode_sentences(sentences)

    @patch('torch.cuda.is_available')
    @patch('providers.huggingface_provider.SentenceTransformer')
    @patch('providers.huggingface_provider.AutoTokenizer')
    def test_encode_sentences_no_valid_sentences(self, mock_tokenizer_cls, mock_model_cls, mock_cuda, provider_config):
        """Test encoding with no valid sentences raises error."""
        mock_cuda.return_value = False
        mock_model_cls.return_value = MagicMock()
        mock_tokenizer_cls.from_pretrained.return_value = MagicMock()

        provider = HuggingFaceProvider(provider_config)
        sentences = ["", "   ", None]
        
        with pytest.raises(ValueError, match="No valid sentences to encode after validation"):
            provider.encode_sentences(sentences)

    @patch('torch.cuda.is_available')
    @patch('providers.huggingface_provider.SentenceTransformer')
    @patch('providers.huggingface_provider.AutoTokenizer')
    def test_encode_sentence_dimension_mismatch(self, mock_tokenizer_cls, mock_model_cls, mock_cuda, provider_config):
        """Test encoding with dimension mismatch raises error."""
        mock_cuda.return_value = False
        mock_model = MagicMock()
        # Wrong dimension (512 instead of 384)
        mock_embeddings = np.random.rand(2, 512)
        mock_model.encode.return_value = mock_embeddings
        mock_model.tokenizer = MagicMock()
        mock_model_cls.return_value = mock_model
        mock_tokenizer_cls.from_pretrained.return_value = MagicMock()

        provider = HuggingFaceProvider(provider_config)
        sentences = "Hello world!"

        with pytest.raises(ValueError, match="Embedding dimension mismatch"):
            provider.encode_sentence(sentences)

    @patch('torch.cuda.is_available')
    @patch('providers.huggingface_provider.SentenceTransformer')
    @patch('providers.huggingface_provider.AutoTokenizer')
    def test_encode_sentences_no_sentence(self, mock_tokenizer_cls, mock_model_cls, mock_cuda, provider_config):
        """Test encoding with no sentence raises error."""
        mock_cuda.return_value = False
        mock_model_cls.return_value = MagicMock()
        mock_tokenizer_cls.from_pretrained.return_value = MagicMock()

        provider = HuggingFaceProvider(provider_config)
        sentences = ""

        with pytest.raises(ValueError, match="No valid sentence to encode after validation"):
            provider.encode_sentence(sentences)

    @patch('torch.cuda.is_available')
    @patch('providers.huggingface_provider.SentenceTransformer')
    @patch('providers.huggingface_provider.AutoTokenizer')
    def test_encode_single_sentence(self, mock_tokenizer_cls, mock_model_cls, mock_cuda, provider_config):
        """Test single sentence encoding."""
        mock_cuda.return_value = False
        mock_model = MagicMock()
        mock_embeddings = np.random.rand(384)  # Single sentence returns 1D array
        mock_model.encode.return_value = mock_embeddings
        mock_model.tokenizer = MagicMock()
        mock_model_cls.return_value = mock_model
        mock_tokenizer_cls.from_pretrained.return_value = MagicMock()

        provider = HuggingFaceProvider(provider_config)
        sentence = "Hello world!"

        result = provider.encode_sentence(sentence)

        assert isinstance(result, EmbeddingResult)
        assert result.embeddings.shape == (1, 384)  # Should be reshaped to 2D
        assert result.num_sentences == 1

        mock_model.encode.assert_called_once_with(
            sentence,
            batch_size=1,
            show_progress_bar=False,
            normalize_embeddings=True
        )

    @patch('torch.cuda.is_available')
    @patch('providers.huggingface_provider.SentenceTransformer')
    @patch('providers.huggingface_provider.AutoTokenizer')
    def test_encode_without_tokenizer_attribute(self, mock_tokenizer_cls, mock_model_cls, mock_cuda, provider_config):
        """Test encoding when model doesn't have tokenizer attribute."""
        mock_cuda.return_value = False
        mock_model = MagicMock()
        # Remove tokenizer attribute
        del mock_model.tokenizer
        mock_embeddings = np.random.rand(1, 384)
        mock_model.encode.return_value = mock_embeddings
        mock_model_cls.return_value = mock_model
        mock_tokenizer_cls.from_pretrained.return_value = MagicMock()

        provider = HuggingFaceProvider(provider_config)
        sentences = ["Hello world!"]
        
        result = provider.encode_sentences(sentences)

        assert result.tokens_used is 3


class TestHuggingFaceProviderInfo:
    """Test provider information functionality."""

    @patch('torch.cuda.is_available')
    @patch('providers.huggingface_provider.SentenceTransformer')
    @patch('providers.huggingface_provider.AutoTokenizer')
    def test_get_provider_info(self, mock_tokenizer_cls, mock_model_cls, mock_cuda, provider_config):
        """Test getting provider information."""
        mock_cuda.return_value = False
        mock_model_cls.return_value = MagicMock()
        mock_tokenizer_cls.from_pretrained.return_value = MagicMock()

        provider = HuggingFaceProvider(provider_config, device="gpu", normalize_embeddings=False)

        info = provider.get_provider_info()

        assert info.provider_name == "huggingface"
        assert info.model_name == "sentence-transformers/all-MiniLM-L6-v2"
        assert info.embedding_dimension == 384
        assert info.max_tokens == 256
        assert info.additional_params["device"] == "gpu"
        assert info.additional_params["normalize_embeddings"] is False


class TestHuggingFaceProviderProperties:
    """Test provider properties and attributes."""

    @patch('torch.cuda.is_available')
    @patch('providers.huggingface_provider.SentenceTransformer')
    @patch('providers.huggingface_provider.AutoTokenizer')
    def test_model_name_property(self, mock_tokenizer_cls, mock_model_cls, mock_cuda, provider_config):
        """Test model_name property is correctly set."""
        mock_cuda.return_value = False
        mock_model_cls.return_value = MagicMock()
        mock_tokenizer_cls.from_pretrained.return_value = MagicMock()

        provider = HuggingFaceProvider(provider_config)
        
        assert provider.model_name == "sentence-transformers/all-MiniLM-L6-v2"

    @patch('torch.cuda.is_available')
    @patch('providers.huggingface_provider.SentenceTransformer')
    @patch('providers.huggingface_provider.AutoTokenizer')
    def test_provider_name_property(self, mock_tokenizer_cls, mock_model_cls, mock_cuda, provider_config):
        """Test __provider_name__ class attribute."""
        mock_cuda.return_value = False
        mock_model_cls.return_value = MagicMock()
        mock_tokenizer_cls.from_pretrained.return_value = MagicMock()

        provider = HuggingFaceProvider(provider_config)
        
        assert provider.__provider_name__ == "huggingface"

#
# Integration-style tests
class TestHuggingFaceProviderIntegration:
    """Integration tests for full workflows."""

    @patch('torch.cuda.is_available')
    @patch('providers.huggingface_provider.SentenceTransformer')
    @patch('providers.huggingface_provider.AutoTokenizer')
    def test_full_encoding_workflow(self, mock_tokenizer_cls, mock_model_cls, mock_cuda, provider_config):
        """Test complete encoding workflow from initialization to result."""
        mock_cuda.return_value = True
        mock_model = MagicMock()
        mock_embeddings = np.random.rand(3, 384)
        mock_model.encode.return_value = mock_embeddings
        mock_model.tokenizer = MagicMock()
        mock_model_cls.return_value = mock_model

        mock_tokenizer = MagicMock()
        
        # Create mock tensor-like objects
        mock_tensor_input_ids = MagicMock()
        mock_tensor_input_ids.tolist.return_value = [[1, 2, 3], [1, 2], [1, 2, 3, 4]]
        mock_tensor_attention_mask = MagicMock()
        mock_tensor_attention_mask.tolist.return_value = [[1, 1, 1], [1, 1], [1, 1, 1, 1]]
        
        mock_tokenized = {
            "input_ids": mock_tensor_input_ids,
            "attention_mask": mock_tensor_attention_mask
        }
        mock_tokenizer.return_value = mock_tokenized
        mock_tokenizer.tokenize.side_effect = lambda s: s.split()
        mock_model.tokenizer = mock_tokenizer
        mock_tokenizer_cls.from_pretrained.return_value = mock_tokenizer

        # Initialize provider
        provider = HuggingFaceProvider(
            provider_config,
            device="cpu",
            normalize_embeddings=True
        )

        # Test provider info
        info = provider.get_provider_info()
        assert info.provider_name == "huggingface"

        # Test model loaded check
        assert provider.is_model_loaded()

        # Test sentence validation
        sentences = ["Hello world", "Test sentence", "Another test"]
        valid_sentences, valid_indices,_,_ = provider.validate_sentences(sentences)
        assert len(valid_sentences) == 3

        # Test encoding
        result = provider.encode_sentences(sentences)
        assert result.embeddings.shape == (3, 384)
        assert result.provider_name == "huggingface"
        assert result.tokens_used == 10

        # Test single sentence encoding
        mock_model.encode.return_value = np.random.rand(384)  # 1D array for single sentence
        single_result = provider.encode_sentence("Single test")
        assert single_result.num_sentences == 1

