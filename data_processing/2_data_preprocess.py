import pandas as pd
import nltk
import re
from nltk import pos_tag
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords, wordnet
from nltk.stem import PorterStemmer, WordNetLemmatizer

english_stopwords = set(stopwords.words('english'))
nltk.download('all')

df = pd.concat([
    pd.read_csv('reddit-cryptocurrency-data.csv'),
    pd.read_csv('reddit-wallstreetbets-data.csv'),
    pd.read_csv('reddit-finance-data.csv'),
    pd.read_csv('reddit-investing-data.csv'),
], ignore_index=True)


# Combine `post_title`, `post_selftext` into a column 'headline'
cols_to_combine = ['post_title', 'post_selftext']
df['headline'] = df[cols_to_combine].fillna('').agg(' '.join, axis=1)
df = df.drop(columns=cols_to_combine)


# ## Text Cleaning Function
# I did research the tradeoff between stemming vs. lemmatizing, and in general I got that:
# - Stemming = rules-based, heuristic algorithmic removal of common word endings
#     - faster for larger datasets, loses accuracy and context, can produced nonexistent words
# - Lemmatizing = more accurate, more computationally expensive with Part-of-Speech Tagging required
# 
# But I reason that I'm not training an ML model where accuracy is mission critical, so simply
# stemming should suffice.

def clean_text_stemmer(text: str) -> str:
    """
    Clean the input text by removing URLs, special characters, and extra whitespace, and using
    NLTK's tokenization, stopword removal, stemming.
    """
    # Remove URLs
    text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
    # Remove special characters and digits, keep important punctuation
    text = re.sub(r'[^A-Za-z\s.,!?]', '', text)
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip().lower()

    words = word_tokenize(text)
    # Remove stopwords
    words = [word for word in words if word not in english_stopwords]
    # Stemming
    stemmer = PorterStemmer()
    words = [stemmer.stem(word) for word in words]
    text = ' '.join(words)
    return text + '.'

# example_text = df['text'].iloc[2226]
# example_text

example_text_stemmed = clean_text_stemmer(example_text)
example_text_stemmed

# Okay, maybe lemmatizing is the better strategy, there are just too many nonsense words here that can throw off the sentiment analyzer.

def clean_text_lemmatizer(text: str) -> str:
    """
    Clean the input text by removing URLs, special characters, and extra whitespace, and using
    NLTK's tokenization, stopword removal, lemmatizer.
    """
    # POS tagging for lemmatization
    # Remove URLs
    text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)

    pos_tags = pos_tag(word_tokenize(text))
    lemmatizer = WordNetLemmatizer()
    # Map POS tags to WordNet format
    tag_dict = {
        "J": wordnet.ADJ,  # Adjective
        "N": wordnet.NOUN, # Noun
        "V": wordnet.VERB, # Verb
        "R": wordnet.ADV   # Adverb
    }
    pos_tags = [(word, tag_dict.get(tag[0], 'n')) for word, tag in pos_tags]

    # Lemmatization
    words = [lemmatizer.lemmatize(word, pos).lower() for word, pos in pos_tags]
    # Remove stopwords
    words = [word for word in words if word not in english_stopwords]
    text = ' '.join(words)

    # Remove special characters and digits, keep important punctuation
    text = re.sub(r'[^A-Za-z\s.,!?]', '', text)
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip().lower()

    return text + '.'  # For FinBERT

example_text

example_text_lemmatized = clean_text_lemmatizer(example_text)
print('LEMMATIZED: ' + example_text_lemmatized)
print('STEMMED: ' + example_text_stemmed)

# ## Applying Lemmatizer to Whole Text Column
# Okay the lemmatizer **definitely works a lot better**, it's a whole lot more accurate in its processing. Gonna stick with that! Now to apply it to the whole text column.

# For some reason there are floats in the text data, have to replace those with empty string
cols = ['headline'] + [f'tc{i}' for i in range(10)]
df[cols] = df[cols].astype(str)

for col in cols:
    df[col] = df[col].apply(clean_text_lemmatizer)

df.sample(4)

# Save the cleaned DataFrame to a new CSV file
df.to_csv('reddit-cleaned.csv', index=False)


