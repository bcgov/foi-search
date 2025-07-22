from dataclasses import dataclass
import os

@dataclass
class TokenizationConfig:
    max_token_length: int = None
    max_words_length: int = None
    token_char_estimate: int = None
    include_metadata: bool = None
    language: str = None

    def __post_init__(self):
        if not self.max_token_length:
            self.max_token_length = int(os.getenv("MAX_TOKEN_LENGTH", 512))
        if not self.max_words_length:
            self.max_words_length = int(os.getenv("MAX_WORDS_LENGTH", 100))
        if not self.token_char_estimate:
            self.token_char_estimate = int(os.getenv("TOKEN_CHAR_ESTIMATE", 4))
        if not self.include_metadata:
            self.include_metadata = os.getenv("INCLUDE_METADATA", "true").lower() != "false"
        if not self.language:
            self.language = os.getenv("TOKEN_LANGUAGE", "en")
