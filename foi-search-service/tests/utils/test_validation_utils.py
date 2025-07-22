import pytest
from utils.validation_utils import validate_sentences, classify_sentence


@pytest.mark.parametrize("sentence, expected_reason", [
    (None, "not a string"),
    (123, "not a string"),
    ("     ", "empty after stripping"),
    ("a" * 301, "exceeds max char length (301 > 300)"),
    ("word " * 51, "exceeds max word count (51 > 50)"),
])
def test_classify_sentence_invalid(sentence, expected_reason):
    cleaned, error = classify_sentence(sentence, 0, max_chars=300, max_words=50)
    assert cleaned is None
    assert error["reason"].startswith(expected_reason.split(" ")[0])  # allow dynamic details


def test_classify_sentence_valid():
    sentence = "Hello world"
    cleaned, error = classify_sentence(sentence, 1, max_chars=300, max_words=50)
    assert cleaned == "Hello world"
    assert error is None


def test_validate_sentences_mixed():
    sentences = [
        "Valid sentence.",          # OK
        "",                         # empty after stripping
        None,                       # not a string
        "word " * 51,               # exceeds word count
        "a" * 301,                  # exceeds char length
        "  Another valid sentence"  # OK
    ]

    valid, indices, rejected, summary = validate_sentences(
        sentences, max_chars=300, max_words=50
    )

    assert valid == ["Valid sentence.", "Another valid sentence"]
    assert indices == [0, 5]
    assert len(rejected) == 4

    expected_reasons = {
        "empty after stripping": 1,
        "not a string": 1,
        "exceeds max word count (51 > 50)": 1,
        "exceeds max char length (301 > 300)": 1,
    }

    for reason, count in expected_reasons.items():
        assert summary[reason] == count


def test_validate_sentences_all_valid():
    sentences = ["Short one", "Another good line"]
    valid, indices, rejected, summary = validate_sentences(
        sentences, max_chars=1000, max_words=100
    )
    assert valid == sentences
    assert indices == [0, 1]
    assert rejected == []
    assert summary == {}
