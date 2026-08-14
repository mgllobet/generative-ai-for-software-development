import urllib.request
from collections import Counter
import re

def download_text(url):
    # Open the URL and read the content
    response = urllib.request.urlopen(url)
    text = response.read().decode('utf-8')
    return text

def count_words(text):
    # Remove punctuation and split the text into words
    words = re.findall(r'\b\w+\b', text.lower())
    # Count the occurrences of each word
    word_count = Counter(words)
    return word_count

def main():
    url = 'https://www.gutenberg.org/cache/epub/4300/pg4300.txt'  # Replace with your URL
    text = download_text(url)
    word_count = count_words(text)
    for word, count in word_count.items():
        print(f'{word}: {count}')
    #print(word_count)
if __name__ == "__main__":
    main()