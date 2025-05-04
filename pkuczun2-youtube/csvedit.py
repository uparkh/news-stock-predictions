import csv

input_csv = "pkuczun2-youtube/youtube_news_comments.csv"
output_csv = "pkuczun2-youtube/parsed_youtube_comments.csv"

with open(input_csv, 'r', encoding='utf-8') as infile, \
     open(output_csv, 'w', newline='', encoding='utf-8') as outfile:
    
    reader = csv.reader(infile)
    writer = csv.writer(outfile)
    
    next(reader, None)
    
    for row in reader:
        month = row[0]
        comment = row[2]
        writer.writerow([month, comment])

      