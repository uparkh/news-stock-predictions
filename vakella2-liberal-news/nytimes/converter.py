import json
import csv
from datetime import datetime

def convert_json_to_csv(input_file, output_file):
    # Read the JSON file
    with open(input_file, 'r', encoding='utf-8') as f:
        articles = json.load(f)
    
    # Prepare data for CSV
    csv_data = []
    for article in articles:
        # Extract month from date
        date_str = article['date']
        date_obj = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S%z")
        month = date_obj.strftime('%b')  # 3-letter month abbreviation
        
        # Get title and snippet
        title = article['title']
        snippet = article['snippet']
        
        # Add to CSV data
        csv_data.append({
            'month': month,
            'article_title': title,
            'article_snippet': snippet
        })
    
    # Write to CSV
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['month', 'article_title', 'article_snippet']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        
        writer.writeheader()
        writer.writerows(csv_data)

# Example usage
input_json_file = 'nytimes_2024_articles_complete.json'  
output_csv_file = 'nytimes_2024_articles.csv'   

convert_json_to_csv(input_json_file, output_csv_file)
print(f"Conversion complete. CSV file saved to {output_csv_file}")
