import typing

from django.utils.deconstruct import deconstructible


class StemmerLanguage:
    (
        "Available stemmers are Arabic, Danish, Dutch, English, Finnish, French, "
        "German, Greek, Hungarian, Italian, Norwegian, Portuguese, Romanian, "
        "Russian, Spanish, Swedish, Tamil, and Turkish."
    )

    ARABIC = "Arabic"
    DANISH = "Danish"
    DUTCH = "Dutch"
    ENGLISH = "English"
    FINNISH = "Finnish"
    FRENCH = "French"
    GERMAN = "German"
    GREEK = "Greek"
    HUNGARIAN = "Hungarian"
    ITALIAN = "Italian"
    NORWEGIAN = "Norwegian"
    PORTUGUESE = "Portuguese"
    ROMANIAN = "Romanian"
    RUSSIAN = "Russian"
    SPANISH = "Spanish"
    SWEDISH = "Swedish"
    TAMIL = "Tamil"
    TURKISH = "Turkish"

    ALL = [
        ARABIC,
        DANISH,
        DUTCH,
        ENGLISH,
        FINNISH,
        FRENCH,
        GERMAN,
        GREEK,
        HUNGARIAN,
        ITALIAN,
        NORWEGIAN,
        PORTUGUESE,
        ROMANIAN,
        RUSSIAN,
        SPANISH,
        SWEDISH,
        TAMIL,
        TURKISH,
    ]


class StopWordLanguage:
    (
        "Available stopword languages are Danish, Dutch, English, Finnish, French, "
        "German, Hungarian, Italian, Norwegian, Portuguese, Russian, Spanish, "
        "and Swedish."
    )

    DANISH = "Danish"
    DUTCH = "Dutch"
    ENGLISH = "English"
    FINNISH = "Finnish"
    FRENCH = "French"
    GERMAN = "German"
    HUNGARIAN = "Hungarian"
    ITALIAN = "Italian"
    NORWEGIAN = "Norwegian"
    PORTUGUESE = "Portuguese"
    RUSSIAN = "Russian"
    SPANISH = "Spanish"
    SWEDISH = "Swedish"

    ALL = [
        DANISH,
        DUTCH,
        ENGLISH,
        FINNISH,
        FRENCH,
        GERMAN,
        HUNGARIAN,
        ITALIAN,
        NORWEGIAN,
        PORTUGUESE,
        RUSSIAN,
        SPANISH,
        SWEDISH,
    ]


@deconstructible
class Tokenizer:
    name = None

    def __init__(
        self,
        stemmer: typing.Optional[str] = None,
        remove_long: typing.Optional[int] = None,
        lowercase: typing.Optional[bool] = None,
        stopwords_language: typing.Optional[str] = None,
        stopwords: typing.Optional[typing.List[str]] = None,
        ascii_folding: typing.Optional[bool] = None,
    ):
        if stemmer is not None and stemmer not in StemmerLanguage.ALL:
            raise ValueError(
                f"Invalid stemmer: {stemmer}. Must be one of {StemmerLanguage.ALL}"
            )

        if (
            stopwords_language is not None
            and stopwords_language not in StopWordLanguage.ALL
        ):
            raise ValueError(
                f"Invalid stopwords_language: {stopwords_language}. Must be one of"
                f" {StopWordLanguage.ALL}"
            )

        self.stemmer = stemmer
        self.remove_long = remove_long
        self.lowercase = lowercase
        self.stopwords_language = stopwords_language
        self.stopwords = stopwords
        self.ascii_folding = ascii_folding

    @property
    def json(self) -> dict:
        raise NotImplementedError

    def sql(self) -> str:
        raise NotImplementedError

    def default_config(self):
        config = {}
        if self.stemmer is not None:
            config["stemmer"] = self.stemmer
        if self.remove_long is not None:
            config["remove_long"] = self.remove_long
        if self.lowercase is not None:
            config["lowercase"] = self.lowercase
        if self.stopwords_language is not None:
            config["stopwords_language"] = self.stopwords_language
        if self.stopwords is not None:
            config["stopwords"] = self.stopwords
        if self.ascii_folding is not None:
            config["ascii_folding"] = self.ascii_folding
        return config


@deconstructible
class DefaultTokenizer(Tokenizer):
    name = "default"

    def __init__(
        self,
        stemmer: typing.Optional[str] = None,
        remove_long: typing.Optional[int] = None,
        lowercase: typing.Optional[bool] = None,
        stopwords_language: typing.Optional[str] = None,
        stopwords: typing.Optional[typing.List[str]] = None,
        ascii_folding: typing.Optional[bool] = None,
    ):
        super().__init__(
            stemmer,
            remove_long,
            lowercase,
            stopwords_language,
            stopwords,
            ascii_folding,
        )

    @property
    def json(self):
        return {"type": self.name, **self.default_config()}


@deconstructible
class WhitespaceTokenizer(Tokenizer):
    name = "whitespace"

    def __init__(
        self,
        stemmer: typing.Optional[str] = None,
        remove_long: typing.Optional[int] = None,
        lowercase: typing.Optional[bool] = None,
        stopwords_language: typing.Optional[str] = None,
        stopwords: typing.Optional[typing.List[str]] = None,
        ascii_folding: typing.Optional[bool] = None,
    ):
        super().__init__(
            stemmer,
            remove_long,
            lowercase,
            stopwords_language,
            stopwords,
            ascii_folding,
        )

    @property
    def json(self):
        return {"type": self.name, **self.default_config()}


@deconstructible
class RawTokenizer(Tokenizer):
    name = "raw"

    def __init__(
        self,
        stemmer: typing.Optional[str] = None,
        remove_long: typing.Optional[int] = None,
        lowercase: typing.Optional[bool] = None,
        stopwords_language: typing.Optional[str] = None,
        stopwords: typing.Optional[typing.List[str]] = None,
        ascii_folding: typing.Optional[bool] = None,
    ):
        super().__init__(
            stemmer,
            remove_long,
            lowercase,
            stopwords_language,
            stopwords,
            ascii_folding,
        )

    @property
    def json(self):
        return {"type": self.name, **self.default_config()}


@deconstructible
class KeyWordTokenizer(Tokenizer):
    name = "keyword"

    def __init__(
        self,
        stemmer: typing.Optional[str] = None,
        remove_long: typing.Optional[int] = None,
        lowercase: typing.Optional[bool] = None,
        stopwords_language: typing.Optional[str] = None,
        stopwords: typing.Optional[typing.List[str]] = None,
        ascii_folding: typing.Optional[bool] = None,
    ):
        super().__init__(
            stemmer,
            remove_long,
            lowercase,
            stopwords_language,
            stopwords,
            ascii_folding,
        )

    @property
    def json(self):
        return {"type": self.name, **self.default_config()}


@deconstructible
class SourceCodeTokenizer(Tokenizer):
    name = "source_code"

    def __init__(
        self,
        stemmer: typing.Optional[str] = None,
        remove_long: typing.Optional[int] = None,
        lowercase: typing.Optional[bool] = None,
        stopwords_language: typing.Optional[str] = None,
        stopwords: typing.Optional[typing.List[str]] = None,
        ascii_folding: typing.Optional[bool] = None,
    ):
        super().__init__(
            stemmer,
            remove_long,
            lowercase,
            stopwords_language,
            stopwords,
            ascii_folding,
        )

    @property
    def json(self):
        return {"type": self.name, **self.default_config()}


@deconstructible
class ChineseCompatibleTokenizer(Tokenizer):
    name = "chinese_compatible"

    def __init__(
        self,
        stemmer: typing.Optional[str] = None,
        remove_long: typing.Optional[int] = None,
        lowercase: typing.Optional[bool] = None,
        stopwords_language: typing.Optional[str] = None,
        stopwords: typing.Optional[typing.List[str]] = None,
        ascii_folding: typing.Optional[bool] = None,
    ):
        super().__init__(
            stemmer,
            remove_long,
            lowercase,
            stopwords_language,
            stopwords,
            ascii_folding,
        )

    @property
    def json(self):
        return {"type": self.name, **self.default_config()}


@deconstructible
class LinderaTokenizer(Tokenizer):
    name = "chinese_lindera"

    def __init__(
        self,
        stemmer: typing.Optional[str] = None,
        remove_long: typing.Optional[int] = None,
        lowercase: typing.Optional[bool] = None,
        stopwords_language: typing.Optional[str] = None,
        stopwords: typing.Optional[typing.List[str]] = None,
        ascii_folding: typing.Optional[bool] = None,
    ):
        super().__init__(
            stemmer,
            remove_long,
            lowercase,
            stopwords_language,
            stopwords,
            ascii_folding,
        )

    @property
    def json(self):
        return {"type": self.name, **self.default_config()}


@deconstructible
class JiebaTokenizer(Tokenizer):
    name = "jieba"

    def __init__(
        self,
        stemmer: typing.Optional[str] = None,
        remove_long: typing.Optional[int] = None,
        lowercase: typing.Optional[bool] = None,
        stopwords_language: typing.Optional[str] = None,
        stopwords: typing.Optional[typing.List[str]] = None,
        ascii_folding: typing.Optional[bool] = None,
    ):
        super().__init__(
            stemmer,
            remove_long,
            lowercase,
            stopwords_language,
            stopwords,
            ascii_folding,
        )

    @property
    def json(self):
        return {"type": self.name, **self.default_config()}


@deconstructible
class ICUTokenizer(Tokenizer):
    name = "icu"

    def __init__(
        self,
        stemmer: typing.Optional[str] = None,
        remove_long: typing.Optional[int] = None,
        lowercase: typing.Optional[bool] = None,
        stopwords_language: typing.Optional[str] = None,
        stopwords: typing.Optional[typing.List[str]] = None,
        ascii_folding: typing.Optional[bool] = None,
    ):
        super().__init__(
            stemmer,
            remove_long,
            lowercase,
            stopwords_language,
            stopwords,
            ascii_folding,
        )

    @property
    def json(self):
        return {"type": self.name, **self.default_config()}


@deconstructible
class RegexTokenizer(Tokenizer):
    name = "regex"

    def __init__(
        self,
        pattern: str,
        stemmer: typing.Optional[str] = None,
        remove_long: typing.Optional[int] = None,
        lowercase: typing.Optional[bool] = None,
        stopwords_language: typing.Optional[str] = None,
        stopwords: typing.Optional[typing.List[str]] = None,
        ascii_folding: typing.Optional[bool] = None,
    ):
        super().__init__(
            stemmer,
            remove_long,
            lowercase,
            stopwords_language,
            stopwords,
            ascii_folding,
        )
        self.pattern = pattern

    @property
    def json(self):
        return {"type": self.name, "pattern": self.pattern, **self.default_config()}


@deconstructible
class NGramTokenizer(Tokenizer):
    name = "ngram"

    def __init__(
        self,
        min_gram: int,
        max_gram: int,
        prefix_only: bool = False,
        stemmer: typing.Optional[str] = None,
        remove_long: typing.Optional[int] = None,
        lowercase: typing.Optional[bool] = None,
        ascii_folding: typing.Optional[bool] = None,
    ):
        super().__init__(stemmer, remove_long, lowercase, ascii_folding=ascii_folding)
        self.min_gram = min_gram
        self.max_gram = max_gram
        self.prefix_only = prefix_only

    @property
    def json(self):
        return {
            "type": self.name,
            "min_gram": self.min_gram,
            "max_gram": self.max_gram,
            "prefix_only": self.prefix_only,
            **self.default_config(),
        }


@deconstructible
class LiteralTokenizer(Tokenizer):
    name = "literal"

    def __init__(
        self,
        stemmer: typing.Optional[str] = None,
        remove_long: typing.Optional[int] = None,
        lowercase: typing.Optional[bool] = None,
        stopwords_language: typing.Optional[str] = None,
        stopwords: typing.Optional[typing.List[str]] = None,
        ascii_folding: typing.Optional[bool] = None,
    ):
        super().__init__(
            stemmer,
            remove_long,
            lowercase,
            stopwords_language,
            stopwords,
            ascii_folding,
        )

    @property
    def json(self):
        return {"type": self.name, **self.default_config()}
