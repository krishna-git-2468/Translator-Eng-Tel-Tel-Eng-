"""NLP translation engine: English <-> Telugu using Meta's NLLB-200 model."""
import re
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

MODEL_NAME = "facebook/nllb-200-distilled-600M"
LANG_CODES = {"en": "eng_Latn", "te": "tel_Telu"}
TELUGU_RE = re.compile(r"[\u0C00-\u0C7F]")

_tokenizer = None
_model = None


def _load():
    """Load the model once (first request downloads ~2.4 GB, then it's cached)."""
    global _tokenizer, _model
    if _model is None:
        _tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
        _model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME)
    return _tokenizer, _model


def detect_language(text: str) -> str:
    """Return 'te' if the text contains Telugu characters, otherwise 'en'."""
    return "te" if TELUGU_RE.search(text) else "en"


def translate(text: str, source: str = "auto", target: str | None = None) -> dict:
    text = text.strip()
    if not text:
        raise ValueError("Please enter some text to translate.")
    if len(text) > 2000:
        raise ValueError("Text is too long. Keep it under 2000 characters.")

    if source == "auto":
        source = detect_language(text)
    if target is None:
        target = "te" if source == "en" else "en"
    if source == target:
        return {"source": source, "target": target, "translation": text}

    tokenizer, model = _load()
    tokenizer.src_lang = LANG_CODES[source]
    inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
    output = model.generate(
        **inputs,
        forced_bos_token_id=tokenizer.convert_tokens_to_ids(LANG_CODES[target]),
        max_length=512,
        num_beams=4,
    )
    result = tokenizer.batch_decode(output, skip_special_tokens=True)[0]
    return {"source": source, "target": target, "translation": result}
