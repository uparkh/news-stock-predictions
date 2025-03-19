import requests
import csv
from datetime import datetime
from multiprocessing import Process, Pool

months = {
    'Jan': (datetime(2024, 1, 1), datetime(2024, 1, 31)),
    'Feb': (datetime(2024, 2, 1), datetime(2024, 2, 29)),
    'Mar': (datetime(2024, 3, 1), datetime(2024, 3, 31)),
    'Apr': (datetime(2024, 4, 1), datetime(2024, 4, 30)),
    'May': (datetime(2024, 5, 1), datetime(2024, 5, 31)),
    'Jun': (datetime(2024, 6, 1), datetime(2024, 6, 30)),
    'Jul': (datetime(2024, 7, 1), datetime(2024, 7, 31)),
    'Aug': (datetime(2024, 8, 1), datetime(2024, 8, 31)),
    'Sep': (datetime(2024, 9, 1), datetime(2024, 9, 30)),
    'Oct': (datetime(2024, 10, 1), datetime(2024, 10, 31)),
    'Nov': (datetime(2024, 11, 1), datetime(2024, 11, 30)),
    'Dec': (datetime(2024, 12, 1), datetime(2024, 12, 31)),
}

def get_subreddit_data(subreddit: str):
    print(f'[{subreddit}] Starting...')
    filename = f'reddit-{subreddit}-data.csv'
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerow([
            'subreddit',
            'month',
            'post_id',
            'post_title',
            'post_selftext',
        ] + [
            f'tc{i}' for i in range(10)
        ])
        for mo in months.keys():
            print(f'[{subreddit}] Fetching data for {mo}...')
            mo_start, mo_end = months[mo]

            while 1:
                response = requests.get(
                    f'https://api.pullpush.io/reddit/submission/search/?subreddit={subreddit}&after={int(mo_start.timestamp())}&before={int(mo_end.timestamp())}&sort_type=score&size=100'
                )
                if response.status_code == 200:
                    break

            posts = response.json()['data']

            for i, post in enumerate(posts):
                if i % 25 == 0:
                    print(f'[{subreddit}] Processing {mo} post {i+1}/{len(posts)}...')

                while 1:
                    response = requests.get(
                        f"https://api.pullpush.io/reddit/comment/search/?link_id={post['id']}&sort_type=score&sort=desc&size=10"
                    )
                    if response.status_code == 200:
                        break


                top10_comments = response.json()['data']
                t10c_bodies = [comment['body'].replace('\n', ' ').replace('\r', ' ').strip() for comment in top10_comments]
                writer.writerow([
                    subreddit,
                    mo,
                    post['id'],
                    post['title'],
                    post['selftext'].replace('\n', ' ').replace('\r', ' ').strip(),
                ] + t10c_bodies)

                csvfile.flush()



if __name__ == '__main__':
    # Create a process for each subreddit to collect data concurrently
    subreddits = ['wallstreetbets', 'finance', 'cryptocurrency', 'investing']
    processes = []

    with Pool(4) as pool:
        pool.map(get_subreddit_data, subreddits)


