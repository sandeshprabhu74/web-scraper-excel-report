import csv
import time

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://quotes.toscrape.com"
HEADERS = {"User-Agent": "Mozilla/5.0 (learning-scraper; contact: you@example.com)"}
DELAY_SECONDS = 1  # be polite: pause between requests


def fetch_page(url):
    """Download a page and return it as a BeautifulSoup object."""
    response = requests.get(url, headers=HEADERS, timeout=10)
    response.raise_for_status()  # raises an error for 404, 500, etc.
    return BeautifulSoup(response.text, "html.parser")


def parse_quotes(soup):
    """Extract the data we want from one page."""
    results = []
    for quote in soup.select("div.quote"):
        results.append({
            "text": quote.select_one("span.text").get_text(strip=True),
            "author": quote.select_one("small.author").get_text(strip=True),
            "tags": ", ".join(tag.get_text(strip=True) for tag in quote.select("a.tag")),
        })
    return results


def scrape_all():
    """Walk through every page until there is no 'Next' button."""
    all_quotes = []
    next_path = "/"

    while next_path:
        url = BASE_URL + next_path
        print(f"Scraping {url}")
        soup = fetch_page(url)
        all_quotes.extend(parse_quotes(soup))

        next_link = soup.select_one("li.next a")
        next_path = next_link["href"] if next_link else None
        time.sleep(DELAY_SECONDS)

    return all_quotes


def save_to_csv(rows, filename="quotes.csv"):
    """Write the scraped data to a CSV file."""
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["text", "author", "tags"])
        writer.writeheader()
        writer.writerows(rows)
    print(f"Saved {len(rows)} rows to {filename}")


if __name__ == "__main__":
    data = scrape_all()
    save_to_csv(data)