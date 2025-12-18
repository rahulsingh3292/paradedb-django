> - import from  `paradedb.tokenizers` module


## Available Tokenizers

Below are the available tokenizer classes you can use

### Available Stemmer Languages

Arabic, Danish, Dutch, English, Finnish, French, German, Greek, Hungarian, Italian, Norwegian, Portuguese, Romanian, Russian, Spanish, Swedish, Tamil, Turkish

### Available Stopword Languages

Danish, Dutch, English, Finnish, French, German, Hungarian, Italian, Norwegian, Portuguese, Russian, Spanish, Swedish

---

### **WhitespaceTokenizer**

```python
WhitespaceTokenizer(
    stemmer: typing.Optional[str] = None,
    remove_long: typing.Optional[int] = None,
    lowercase: typing.Optional[bool] = None,
    stopwords_language: typing.Optional[str] = None,
    stopwords: typing.Optional[typing.List[str]] = None,
    ascii_folding: typing.Optional[bool] = None,
)
```

see [ParadeDB whitespace tokenizer](https://docs.paradedb.com/legacy/indexing/tokenizers#whitespace)

---

### **RawTokenizer**

```python
RawTokenizer(
    stemmer: typing.Optional[str] = None,
    remove_long: typing.Optional[int] = None,
    lowercase: typing.Optional[bool] = None,
    stopwords_language: typing.Optional[str] = None,
    stopwords: typing.Optional[typing.List[str]] = None,
    ascii_folding: typing.Optional[bool] = None,
)
```

see [ParadeDB raw tokenizer](https://docs.paradedb.com/legacy/indexing/tokenizers#raw)

---

### **KeyWordTokenizer**

```python
KeyWordTokenizer(
    stemmer: typing.Optional[str] = None,
    remove_long: typing.Optional[int] = None,
    lowercase: typing.Optional[bool] = None,
    stopwords_language: typing.Optional[str] = None,
    stopwords: typing.Optional[typing.List[str]] = None,
    ascii_folding: typing.Optional[bool] = None,
)
```

see [ParadeDB keyword tokenizer](https://docs.paradedb.com/legacy/indexing/tokenizers#keyword)

---

### **SourceCodeTokenizer**

```python
SourceCodeTokenizer(
    stemmer: typing.Optional[str] = None,
    remove_long: typing.Optional[int] = None,
    lowercase: typing.Optional[bool] = None,
    stopwords_language: typing.Optional[str] = None,
    stopwords: typing.Optional[typing.List[str]] = None,
    ascii_folding: typing.Optional[bool] = None,
)
```

see [ParadeDB sourcecode tokenizer](https://docs.paradedb.com/legacy/indexing/tokenizers#source-code)

---

### **ChineseCompatibleTokenizer**

```python
ChineseCompatibleTokenizer(
    stemmer: typing.Optional[str] = None,
    remove_long: typing.Optional[int] = None,
    lowercase: typing.Optional[bool] = None,
    stopwords_language: typing.Optional[str] = None,
    stopwords: typing.Optional[typing.List[str]] = None,
    ascii_folding: typing.Optional[bool] = None,
)
```

see [ParadeDB chinese compatible tokenizer](https://docs.paradedb.com/legacy/indexing/tokenizers#chinese-compatible)

---

### **LinderaTokenizer**

```python
LinderaTokenizer(
    stemmer: typing.Optional[str] = None,
    remove_long: typing.Optional[int] = None,
    lowercase: typing.Optional[bool] = None,
    stopwords_language: typing.Optional[str] = None,
    stopwords: typing.Optional[typing.List[str]] = None,
    ascii_folding: typing.Optional[bool] = None,
)
```
see [ParadeDB lindera tokenizer](https://docs.paradedb.com/legacy/indexing/tokenizers#lindera)

---

### **JiebaTokenizer**

```python
JiebaTokenizer(
    stemmer: typing.Optional[str] = None,
    remove_long: typing.Optional[int] = None,
    lowercase: typing.Optional[bool] = None,
    stopwords_language: typing.Optional[str] = None,
    stopwords: typing.Optional[typing.List[str]] = None,
    ascii_folding: typing.Optional[bool] = None,
)
```
see [ParadeDB jieba okenizer](https://docs.paradedb.com/legacy/indexing/tokenizers#jieba)

---

### **ICUTokenizer**

```python
ICUTokenizer(
    stemmer: typing.Optional[str] = None,
    remove_long: typing.Optional[int] = None,
    lowercase: typing.Optional[bool] = None,
    stopwords_language: typing.Optional[str] = None,
    stopwords: typing.Optional[typing.List[str]] = None,
    ascii_folding: typing.Optional[bool] = None,
)
```
see [ParadeDB icu tokenizer](https://docs.paradedb.com/legacy/indexing/tokenizers#icu)

---

### **RegexTokenizer**

```python
RegexTokenizer(
    pattern: str,
    stemmer: typing.Optional[str] = None,
    remove_long: typing.Optional[int] = None,
    lowercase: typing.Optional[bool] = None,
    stopwords_language: typing.Optional[str] = None,
    stopwords: typing.Optional[typing.List[str]] = None,
    ascii_folding: typing.Optional[bool] = None,
)
```

see [ParadeDB regex tokenizer](https://docs.paradedb.com/legacy/indexing/tokenizers#regex)

---

### **NGramTokenizer**

```python
NGramTokenizer(
    min_gram: int,
    max_gram: int,
    prefix_only: bool = False,
    stemmer: typing.Optional[str] = None,
    remove_long: typing.Optional[int] = None,
    lowercase: typing.Optional[bool] = None,
    ascii_folding: typing.Optional[bool] = None,
)
```

see [ParadeDB Ngram tokenizer](https://docs.paradedb.com/legacy/indexing/tokenizers#ngram)

---

### **Example Using Tokenizers with BM25 Index**

```python
from paradedb.indexes import Bm25Index, IndexFieldConfig, TextFieldIndexConfig, JSONFieldIndexConfig
from paradedb.tokenizers import WhitespaceTokenizer, NGramTokenizer

Bm25Index(
    fields=["id", "title", "description", "metadata"],
    name="bm25_idx",
    fields_config=IndexFieldConfig(
        text_fields=[
            TextFieldIndexConfig(
                field="title",
                fast=True,
                tokenizer=WhitespaceTokenizer(),
                normalizer="lowercase",
                record="position"
            ),
            TextFieldIndexConfig(
                field="description",
                fast=True,
                tokenizer=NGramTokenizer(min_gram=2, max_gram=3),
                normalizer="lowercase",
                record="position"
            )
        ],
        json_fields=[
            JSONFieldIndexConfig(
                field="metadata",
                tokenizer=WhitespaceTokenizer(),
                expand_dots=True
            )
        ]
    )
)

```

---
