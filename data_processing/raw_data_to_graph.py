import pandas as pd
import re
import matplotlib.pyplot as plt
import logging
import nltk
from nltk import pos_tag
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords, wordnet
from nltk.stem import WordNetLemmatizer
from datetime import datetime, timedelta
from argparse import ArgumentParser
from nltk.sentiment import SentimentIntensityAnalyzer
from matplotlib.patches import Patch

# arguments
parser = ArgumentParser(description="Process a CSV input file.")
parser.add_argument('-i', '--input', type=str, required=True, help='Path to the input CSV file.')
parser.add_argument('-l', '--label', type=str, required=True, help='Label for dataset, used in the graph title.')
args = parser.parse_args()

input_file: str = args.input

# logging init
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
)


# Columns: ['month', 'text0', 'text1', ...] any number of text columns
df = pd.read_csv(input_file).fillna('').astype(str)
months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
months_found = df['month'].unique().tolist()
if months_found != months:
    raise ValueError(f"Expected months in the first column to be:\n\t{months}\nBut got:\n\t{months_found}")
text_cols = df.columns[1:]  # Exclude the first column (month)


# nltk downloads
logging.info("Downloading NLTK data... (this may take a while if not already downloaded)")
for package in [
    'stopwords',
    'punkt_tab',
    'averaged_perceptron_tagger_eng',
    'wordnet',
    'vader_lexicon',
]:
    nltk.download(package, quiet=True)


logging.info("Cleaning, preprocessing, and lemmatizing...")
# Text Cleaning Function
lemmatizer = WordNetLemmatizer()
english_stopwords = set(stopwords.words('english'))
def clean_text_lemmatizer(text: str) -> str:
    """
    Clean the input text by removing URLs, special characters, and extra whitespace, and using
    NLTK's tokenization, stopword removal, lemmatizer.
    """
    # POS tagging for lemmatization
    # Remove URLs
    text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)

    pos_tags = pos_tag(word_tokenize(text))
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

    # Remove special characters and digits
    text = re.sub(r'[^A-Za-z\s]', '', text)
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip().lower()

    return text


# ## Applying Lemmatizer to all Text Columns
for col in text_cols:
    df[col] = df[col].apply(clean_text_lemmatizer)


logging.info("Performing sentiment analysis...")
# ## NLTK Sentiment Analysis
# In this section I'll use NLTK's sentiment analysis to convert all the columns into sentiment scores.
sia = SentimentIntensityAnalyzer()

# Apply the sentiment analysis and create new columns for each score
for col in text_cols:
    df[f'nltk_{col}'] = df[col].apply(lambda x: pd.Series(sia.polarity_scores(x)['compound']))

nltk_cols = ['nltk_' + col for col in text_cols]

def weighted_mean(row: pd.Series, cols: list[str]) -> float:
    def w(i: int) -> float:
        return 2.718281828459045 ** (-3 * i / len(cols))

    return sum([row[col] * w(i) for i, col in enumerate(cols)])

df['nltk_mu'] = df.apply(lambda row: weighted_mean(row, nltk_cols), axis=1)
nltk_month_avg = df.groupby('month', sort=False)['nltk_mu'].mean()

nltk_month_avgs_standardized = (nltk_month_avg - nltk_month_avg.mean()) / nltk_month_avg.std()


logging.info("Creating the graph...")
# stock dataframe
sdf = pd.read_csv('yahoo-sp500-historical.csv')

# Convert 'Date' column to datetime format
sdf['Date'] = pd.to_datetime(sdf['Date'])
sdf_2024 = sdf[sdf['Date'].dt.year == 2024]
sdf_2024 = sdf_2024.sort_values(by=['Date'])
sdf_2024 = sdf_2024.reset_index(drop=True)

sdf_2024 = sdf_2024[['Date', 'Close/Last']]

start_price = sdf_2024.iloc[0]['Close/Last']
end_price = sdf_2024.iloc[-1]['Close/Last']
baseline_slope = - (start_price - end_price) / len(sdf_2024)

sdf_2024['Baseline'] = start_price + (baseline_slope * sdf_2024.index)
sdf_2024['Deviation'] = sdf_2024['Close/Last'] - sdf_2024['Baseline']

# convert month names to datetime objects
def month_to_datetime(month):
    return datetime.strptime(f"2024-{month}-01", "%Y-%b-%d")

nltk_month_avgs_standardized.index = nltk_month_avgs_standardized.index.map(month_to_datetime)

fig, ax = plt.subplots(figsize=(12, 6))
ax.plot(sdf_2024['Date'], sdf_2024['Deviation'], linestyle='-', color='purple', label='2024 S&P 500 Deviation from Trendline')
mag = sdf_2024['Deviation'].max()
mag += mag / 12

colors = ['green' if val > 0 else 'red' for val in nltk_month_avgs_standardized]
widths = [delta.days for delta in (nltk_month_avgs_standardized.index[1:] - nltk_month_avgs_standardized.index[:-1])] + [31]
standard_abs_max = nltk_month_avgs_standardized.abs().max()
bar_scalar = (mag / standard_abs_max) * (2/3)
ax.bar(nltk_month_avgs_standardized.index, nltk_month_avgs_standardized * bar_scalar, color=colors, width=widths, align='edge', alpha=0.7)

ax.set_title(f'2024 Adjusted S&P 500 w/ Sentiment Correlation of {args.label}')
ax.set_xlabel('Month')

ax_secondary = ax.twinx()
ax_secondary.set_ylabel('Standardized Sentiment Score (Unitless)')
ax_secondary.set_ylim(-1, 1)

ax.grid(True)
ax.set_ylabel('Price Deviation from Trendline ($)')
ax.set_ylim(-mag, mag)

ax.set_xticks(nltk_month_avgs_standardized.index)
ax.set_xticklabels(months, rotation=15, ha='left')
ax.tick_params(axis='x')
ax.set_xlim(sdf_2024['Date'].iloc[0] - timedelta(days=1), sdf_2024['Date'].iloc[-1])

ax.legend(loc='best')
green_patch = Patch(color='green', label='Positive Standardized Sentiment Score')
red_patch = Patch(color='red', label='Negative Standardized Sentiment Score')
ax.legend(handles=ax.get_legend_handles_labels()[0] + [green_patch, red_patch], loc='best')

img_filename = args.input.split('/')[-1].split('.')[0] + '_graph.png'
fig.savefig(img_filename)
logging.info(f"Graph saved as {img_filename}. Exiting.")
