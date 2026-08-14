
import urllib.request
from collections import Counter
import re
from multiprocessing import Pool
import logging
from urllib.parse import urlparse

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def is_valid_url(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False

def download_and_count(url):
    if not is_valid_url(url):
        logger.error(f"Invalid URL: {url}")
        return Counter()
    try:
        response = urllib.request.urlopen(url, timeout=10)
        text = response.read().decode('utf-8')
        words = re.findall(r"\b[\w\'-]+\b", text.lower())
        return Counter(words)
    except urllib.error.HTTPError as e:
        logger.error(f"HTTP error processing {url}: {e}")
    except urllib.error.URLError as e:
        logger.error(f"URL error processing {url}: {e}")
    except Exception as e:
        logger.error(f"General error processing {url}: {e}")
    return Counter()

def merge_counters(counters):
    total_count = Counter()
    for counter in counters:
        total_count.update(counter)
    return total_count

def main(urls):
    with Pool(processes=8) as pool:
        counters = pool.map(download_and_count, urls)
    total_word_count = merge_counters(counters)
    for word, count in total_word_count.items():
        print(f'{word}: {count}')

if __name__ == "__main__":
    urls = ["http://example.com/some-text-file1.txt", "http://example.com/some-text-file2.txt"]
    main(urls)
