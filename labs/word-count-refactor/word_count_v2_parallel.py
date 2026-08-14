import urllib.request
from collections import Counter
import re
from multiprocessing import Pool

def download_and_count(url):
    try:
        response = urllib.request.urlopen(url)
        text = response.read().decode('utf-8')
        words = re.findall(r'\b\w+\b', text.lower())
        return Counter(words)
    except Exception as e:
        print(f"Error processing {url}: {e}")
        return Counter()

def merge_counters(counters):
    total_count = Counter()
    for counter in counters:
        total_count.update(counter)
    return total_count

def main(urls):
    with Pool(processes=8) as pool:  # Adjust the number of processes as needed
        counters = pool.map(download_and_count, urls)
    total_word_count = merge_counters(counters)
    for word, count in total_word_count.items():
        print(f'{word}: {count}')

if __name__ == "__main__":
    urls = ["http://example.com/some-text-file1.txt", "http://example.com/some-text-file2.txt"]  # Replace with your list of URLs
    main(urls)