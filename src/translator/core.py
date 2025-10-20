"""
Core translation module using NLLB-200-distilled-600M model.
"""
import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline
from typing import Optional, List
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Translator:
    """
    A translator class that uses the NLLB-200-distilled-600M model
    for multilingual translation.
    """

    # Language code mapping for common languages
    LANGUAGE_CODES = {
        'en': 'eng_Latn',  # English
        'ko': 'kor_Hang',  # Korean
        'ja': 'jpn_Jpan',  # Japanese
        'zh': 'zho_Hans',  # Chinese (Simplified)
        'es': 'spa_Latn',  # Spanish
        'fr': 'fra_Latn',  # French
        'de': 'deu_Latn',  # German
        'ru': 'rus_Cyrl',  # Russian
        'ar': 'arb_Arab',  # Arabic
        'pt': 'por_Latn',  # Portuguese
        'it': 'ita_Latn',  # Italian
    }

    def __init__(self, model_name: str = "facebook/nllb-200-distilled-600M", use_gpu: bool = True):
        """
        Initialize the translator with the specified model.

        Args:
            model_name: HuggingFace model identifier
            use_gpu: Whether to use GPU if available (default: True)
        """
        logger.info(f"Loading model: {model_name}")
        self.model_name = model_name

        # Determine device
        if use_gpu and torch.cuda.is_available():
            self.device = 0
            logger.info("Using GPU for translation")
        else:
            self.device = -1
            logger.info("Using CPU for translation")

        # Load model and tokenizer
        try:
            self.model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            logger.info("Model and tokenizer loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise

        self._pipeline = None

    def _get_language_code(self, lang: str) -> str:
        """
        Convert simple language code to NLLB format.

        Args:
            lang: Language code (e.g., 'en', 'ko') or NLLB code (e.g., 'eng_Latn')

        Returns:
            NLLB formatted language code
        """
        # If already in NLLB format, return as is
        if '_' in lang:
            return lang

        # Convert from simple code
        lang_lower = lang.lower()
        if lang_lower in self.LANGUAGE_CODES:
            return self.LANGUAGE_CODES[lang_lower]
        else:
            raise ValueError(
                f"Unsupported language code: {lang}. "
                f"Supported codes: {', '.join(self.LANGUAGE_CODES.keys())}"
            )

    def translate(
        self,
        text: str,
        src_lang: str = 'en',
        tgt_lang: str = 'ko',
        max_length: int = 512
    ) -> str:
        """
        Translate text from source language to target language.

        Args:
            text: Text to translate
            src_lang: Source language code (e.g., 'en', 'ko', or 'eng_Latn')
            tgt_lang: Target language code (e.g., 'en', 'ko', or 'kor_Hang')
            max_length: Maximum length of generated translation

        Returns:
            Translated text
        """
        if not text or not text.strip():
            return ""

        try:
            # Convert language codes
            src_code = self._get_language_code(src_lang)
            tgt_code = self._get_language_code(tgt_lang)

            logger.info(f"Translating from {src_code} to {tgt_code}")

            # Create pipeline with specified languages
            translation_pipeline = pipeline(
                "translation",
                model=self.model,
                tokenizer=self.tokenizer,
                src_lang=src_code,
                tgt_lang=tgt_code,
                max_length=max_length,
                device=self.device
            )

            # Perform translation
            result = translation_pipeline(text)
            translated_text = result[0]['translation_text']

            return translated_text

        except Exception as e:
            logger.error(f"Translation error: {e}")
            raise

    def translate_batch(
        self,
        texts: List[str],
        src_lang: str = 'en',
        tgt_lang: str = 'ko',
        max_length: int = 512,
        batch_size: int = 8
    ) -> List[str]:
        """
        Translate multiple texts in batch.

        Args:
            texts: List of texts to translate
            src_lang: Source language code
            tgt_lang: Target language code
            max_length: Maximum length of generated translation
            batch_size: Batch size for processing

        Returns:
            List of translated texts
        """
        if not texts:
            return []

        try:
            # Convert language codes
            src_code = self._get_language_code(src_lang)
            tgt_code = self._get_language_code(tgt_lang)

            logger.info(f"Batch translating {len(texts)} texts from {src_code} to {tgt_code}")

            # Create pipeline
            translation_pipeline = pipeline(
                "translation",
                model=self.model,
                tokenizer=self.tokenizer,
                src_lang=src_code,
                tgt_lang=tgt_code,
                max_length=max_length,
                device=self.device
            )

            # Perform batch translation
            results = translation_pipeline(texts, batch_size=batch_size)
            translated_texts = [result['translation_text'] for result in results]

            return translated_texts

        except Exception as e:
            logger.error(f"Batch translation error: {e}")
            raise

    def get_supported_languages(self) -> dict:
        """
        Get dictionary of supported language codes.

        Returns:
            Dictionary mapping simple codes to NLLB codes
        """
        return self.LANGUAGE_CODES.copy()
