import requests
from bs4 import BeautifulSoup
import argparse
import json
import time
import logging
import urllib.robotparser

logging.basicConfig(level=logging.INFO)

def can_fetch(url):
    """Check robots.txt before scraping."""
    rp = urllib.robotparser.RobotFileParser()
    base = "/".join(url.split("/")[:3]) + "/robots.txt"
    try:
        rp.set_url(base)
        rp.read()
        return rp.can_fetch("*", url)
    except Exception:
        return True  # fallback if robots.txt not accessible

def fetch_headlines(source, keyword=None, delay=2):
    """Scrape headlines from a single source."""
    results = []
    if not can_fetch(source):
        logging.warning(f"Blocked by robots.txt: {source}")
        return results

    try:
        time.sleep(delay)
        response = requests.get(source, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        # Generic headline extraction (adjust per site)
        for item in soup.find_all("a"):
            title = item.get_text(strip=True)
            href = item.get("href")
            if not title or not href:
                continue
            if keyword and keyword.lower() not in title.lower():
                continue
            results.append({
                "title": title,
                "url": href,
                "time": None  # Add parsing logic if site provides timestamps
            })
    except Exception as e:
        logging.error(f"Error scraping {source}: {e}")
    return results

def save_results(results, output_file):
    """Save results to JSON only."""
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

def main():
    parser = argparse.ArgumentParser(description="Web scraper for news headlines")
    parser.add_argument("-s", "--sources", nargs="+", required=True, help="List of news site URLs")
    parser.add_argument("-o", "--output", required=True, help="Output file (.json)")
    parser.add_argument("-k", "--keyword", help="Filter headlines by keyword")
    parser.add_argument("-d", "--delay", type=int, default=2, help="Delay between requests (seconds)")
    args = parser.parse_args()

    all_results = []
    for src in args.sources:
        headlines = fetch_headlines(src, keyword=args.keyword, delay=args.delay)
        all_results.extend(headlines)

    if all_results:
        save_results(all_results, args.output)
        logging.info(f"Saved {len(all_results)} headlines to {args.output}")
        print("First headline:", all_results[0]["title"])
    else:
        logging.warning("No headlines found.")

if __name__ == "__main__":
    main()
