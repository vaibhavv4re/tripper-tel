from crawl4ai import WebCrawler
import schedule
import time

def crawl_data():
    crawler = WebCrawler()
    result = crawler.crawl(url="https://example-travel-blog.com", output_format="markdown")
    with open(f"travel_data_{time.time()}.md", "w") as file:
        file.write(result)

# Schedule daily crawls
schedule.every().day.at("00:00").do(crawl_data)

while True:
    schedule.run_pending()
    time.sleep(1)