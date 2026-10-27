"""
Book Price Scraper + Cleaner
- Scrapes all books from books.toscrape.com (a practice site made for scraping)
- Cleans the data with pandas
- Saves a clean CSV and a chart

Install:  pip install requests beautifulsoup4 pandas matplotlib
Run:      python book_scraper.py
"""

import time

import matplotlib.pyplot as plt
import pandas as pd
import requests
from bs4 import BeautifulSoup

BASE_URL = "https://books.toscrape.com/catalogue/page-{}.html"
RATING_MAP = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}


def scrape_page(page_number):
    """Scrape one listing page and return a list of book dicts."""
    response = requests.get(BASE_URL.format(page_number), timeout=10)
    if response.status_code != 200:
        return []

    response.encoding = "utf-8"  # fixes the "Â£" symbol problem
    soup = BeautifulSoup(response.text, "html.parser")

    books = []
    for item in soup.select("article.product_pod"):
        books.append(
            {
                "title": item.h3.a["title"],
                "price": item.select_one("p.price_color").text.strip(),
                "rating": item.select_one("p.star-rating")["class"][1],
                "availability": item.select_one("p.availability").text.strip(),
            }
        )
    return books


def scrape_all(max_pages=50):
    """Loop through pages until there are no more books."""
    all_books = []
    for page in range(1, max_pages + 1):
        books = scrape_page(page)
        if not books:
            break
        all_books.extend(books)
        print(f"Page {page}: {len(books)} books scraped")
        time.sleep(0.5)  # be polite to the website
    return all_books


def clean(df):
    """Clean the raw scraped data."""
    df = df.drop_duplicates().copy()
    df["price"] = df["price"].str.replace(r"[^\d.]", "", regex=True).astype(float)
    df["rating"] = df["rating"].map(RATING_MAP)
    df["in_stock"] = df["availability"].str.contains("In stock", case=False)
    df = df.drop(columns=["availability"])
    return df


def make_chart(df, filename="avg_price_by_rating.png"):
    """Bar chart: average price for each star rating."""
    avg = df.groupby("rating")["price"].mean()
    ax = avg.plot(kind="bar", color="#4C72B0")
    ax.set_title("Average Book Price by Rating")
    ax.set_xlabel("Rating (stars)")
    ax.set_ylabel("Average price (GBP)")
    plt.tight_layout()
    plt.savefig(filename)
    plt.close()


def main():
    raw_books = scrape_all()
    if not raw_books:
        print("No data scraped. Check your internet connection.")
        return

    df = clean(pd.DataFrame(raw_books))
    df.to_csv("books_clean.csv", index=False)
    make_chart(df)

    print("\n--- Summary ---")
    print(f"Total books: {len(df)}")
    print(f"Average price: {df['price'].mean():.2f}")
    print(f"Cheapest: {df.loc[df['price'].idxmin(), 'title']}")
    print(f"Most expensive: {df.loc[df['price'].idxmax(), 'title']}")
    print("Saved: books_clean.csv, avg_price_by_rating.png")


if __name__ == "__main__":
    main()