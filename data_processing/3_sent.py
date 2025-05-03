import pandas as pd

# # Sentiment Models Comparisons -- Reddit
# In this part (3), I'll be comparing the VADER pretrained model from NLTK's presets, and the FinBERT model from the PyTorch library.
# 
# The idea is that using a sentiment analysis model trained on financial data will allow it to pick up financial terms and keywords from the corpora better than the general purpose NLTK pretrained sentiment model.
# 
# I'm not sure exactly yet how I'll measure this effect, but for each model's results, I'll make a plot of sentiment results for each month of 2024. Then I'll decide from there.
# 
# ## Data Treatment
# The cleaned data consists of lemmatized top comments, and the "headline" column which has the post title + self text
# 
# Here's what I'll do. For each post:
# - Get a sentiment score for the post title + self text (headline), call it $s_0$
# - Get a sentiment score for each top comment, call them $s_1, s_2, ..., s_{10}$
# - Get a weighted aggregate sentiment score for the post. Weighing a score $s_i$ less as $i$ increases. I will just begin with the simple function: $w(s_i) = \frac{1}{100} * (i - 10)^2 + 0.01$ to multiply to a score to weigh it. The $0.01$ is to just avoid weighing the last element at 0.
# 
# For each month, I will take the median score of the post scores of that month as the representation for the entire month, as this statistic is more resistant to outliers.
# 
# I have to do it like this because sentiment analysis really starts to break when the text gets too long, either with NLTK's VADER, or with FinBERT. You will see this in my previous commits if you want to look, but essentially I tried to combine all the info associated with each post into one supertext of the post, and tried to run an analysis ont that, but the models failed spectacularly with incredibly large bodies of text like that.
# 
# 

df = pd.read_csv('reddit-cleaned.csv')

df.sample(3)

df.drop(columns=['post_id'], inplace=True)

df.sample(3)

subreddits = df['subreddit'].unique()
print(subreddits)

months = df['month'].unique()
print(months)

# Average character length of the text in the combined dataframe
cols = ['headline'] + [f'tc{i}' for i in range(10)]
for col in cols:
    avg_length = df[col].str.len().mean()
    print(f"Average character length of '{col}': {avg_length}")

# Some columns are not of the correct data type
df[cols] = df[cols].astype(str)

# Okay these are all reasonable character lengths, so I think the sentiment analyses should be much nicer compared to my previous attempt.

# ## NLTK Sentiment Analysis
# In this section I'll use NLTK's sentiment analysis to convert all the columns into sentiment scores.

sample_headline = df['headline'].sample(1).values[0]
print(sample_headline)

from nltk.sentiment import SentimentIntensityAnalyzer

sia = SentimentIntensityAnalyzer()

sia.polarity_scores(sample_headline)

# ### Compound Scores
# So this mechanism divides it's output into a negative, neutral, positive, and compound score.
# I'll just use compound for now, and see what the scores are.

# Apply the sentiment analysis and create new columns for each score
for col in cols:
    df[f'nltk_{col}'] = df[col].apply(lambda x: pd.Series(sia.polarity_scores(x)['compound']))

nltk_cols = ['nltk_' + col for col in cols]
df[nltk_cols].describe()

# Okay so it seems that a majority of scores are slightly positive. But this is across the columns. Perhaps after I run my special weighted mean on each post and then take the median grouped by month, I'll see a different story.

def weighted_mean(row: pd.Series, cols: list[str]) -> float:
    def w(i: int) -> float:
        return 2.718281828459045 ** (-3 * i / len(cols))

    return sum([row[col] * w(i) for i, col in enumerate(cols)])

df['nltk_mu'] = df.apply(lambda row: weighted_mean(row, nltk_cols), axis=1)
nltk_month_avg = df.groupby('month', sort=False)['nltk_mu'].mean()

nltk_month_avg

# Hmm, still all positive! Note that this isn't a horrible thing, I shouldn't shape the results to my expectation. Looking at the actual S&P 500 graph:
# ![S&P 500 Graph 2024](S&P_500_2024.png)
# 
# Can see that there was a dip in March and July/August of that year, which does correspond to dips in sentiment scores around that time in the data, despite being positive, so perhaps there's something there! Let's standardize to see in detail.

nltk_month_avgs_standardized = (nltk_month_avg - nltk_month_avg.mean()) / nltk_month_avg.std()
nltk_month_avgs_standardized

# Honestly pretty good! If we think out a monthly score of 0 representing a neutral attitude, a negative score seems to correlate to a bearish outlook versus a positive score being a bullish outlook in the short term.

# ## FinBERT Sentiment Analysis
# Let's see how FinBERT does, given that it is specially trained on financial texts and sources.

from transformers import pipeline

finance_sentiment = pipeline("text-classification", model="ProsusAI/finbert")

finance_sentiment([sample_headline, sample_headline])

from nltk import word_tokenize
from tqdm import tqdm

# Trim length of all entries to 256 tokens
# BERT tokens are defined differently to NLTK tokens, so I ran into issues with only accepting
# 512 tokens. I decided to use 256 tokens instead to avoid this issue.
def trim(text: str) -> str:
    tokens = word_tokenize(text)
    text = ' '.join(tokens[:256])
    return text

for col in tqdm(cols):
    df[col] = df[col].apply(trim)

# Batch processing because we are interfacing with an ML model, faster than processing one by one
for col in tqdm(cols):
    df[f'finbert_{col}'] = [result['score'] for result in finance_sentiment(df[col].tolist())]

finbert_cols = ['finbert_' + col for col in cols]
df[finbert_cols].describe()

df['finbert_mu'] = df.apply(lambda row: weighted_mean(row, finbert_cols), axis=1)
fb_month_avg = df.groupby(['month', 'subreddit'], sort=False)['finbert_mu'].mean().unstack()

fb_month_avg

# It seems that all the scores still are quite high, but the subtle patterns are there that correlate to March and July/August dips. Maybe standardizing could be helpful to see the dips.

fb_month_avgs_standardized = (fb_month_avg - fb_month_avg.mean(axis=0)) / fb_month_avg.std(axis=0)

pd.concat([nltk_month_avgs_standardized, fb_month_avgs_standardized], axis=1, keys=['nltk', 'finbert'])

# ![S&P500 2024 Graph](S&P_500_2024.png)
# Little better, it seems that FinBERT follows similar trends to NLTK, but FinBERT's June is way too pessimistic, and FinBERT's July is way too optimistic. Based on the actual S&P500 graph, it seems that NLTK actually performed better, so I will be using NLTK for my plotting and analysis moving forward.

df.to_csv('reddit-sentiment.csv', index=False)




