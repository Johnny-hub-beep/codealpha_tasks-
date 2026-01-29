import argparse
import logging
from typing import List, Dict

import requests
from bs4 import BeautifulSoup
import pandas as pd


RATING_MAP = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}


def parse_books_from_page(html: str) -> List[Dict[str, object]]:
	soup = BeautifulSoup(html, "html.parser")
	books = soup.find_all("article", class_="product_pod")
	data: List[Dict[str, object]] = []

	for book in books:
		title = book.h3.a.get("title", "").strip()
		price_raw = book.find("p", class_="price_color").text.strip()
		price = price_raw.replace("£", "").strip()
		rating_class = book.p.get("class", [])
		rating_word = rating_class[1] if len(rating_class) > 1 else ""
		rating = RATING_MAP.get(rating_word, None)

		data.append({
			"Title": title,
			"Price": price,
			"Rating": rating,
		})

	return data


def scrape(url: str) -> List[Dict[str, object]]:
	resp = requests.get(url, timeout=10)
	resp.raise_for_status()
	return parse_books_from_page(resp.text)


def main() -> None:
	parser = argparse.ArgumentParser(description="Simple books.toscrape web scraper")
	parser.add_argument(
		"url",
		nargs="?",
		default=(
			"https://books.toscrape.com/catalogue/category/books/travel_2/index.html"
		),
		help="Page URL to scrape (defaults to books.toscrape travel category)",
	)
	parser.add_argument("-o", "--output", default="scraped_books.csv", help="Output CSV file")
	args = parser.parse_args()

	logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
	logging.info("Fetching %s", args.url)

	try:
		data = scrape(args.url)
		if not data:
			logging.warning("No items found on the page.")

		df = pd.DataFrame(data)
		df.to_csv(args.output, index=False)
		logging.info("Scraping completed. Data saved to %s", args.output)
	except Exception as exc:  # pragma: no cover - surface-level error handling
		logging.error("Error during scraping: %s", exc)


if __name__ == "__main__":
	main()