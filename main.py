import sys
import time
import requests
import xml.etree.ElementTree as ET
from collections import defaultdict

class CrawlerStatistics:
    def __init__(self):
        self.start_time = time.time()
        self.stats = defaultdict(int)
        self.status_codes = defaultdict(int)
        self.errors = defaultdict(list)
        self.content_types = defaultdict(int)
    
    def record_success(self, url, status_code, content_type):
        self.stats['total'] += 1
        self.stats['successful'] += 1
        self.status_codes[status_code] += 1
        if content_type:
            self.content_types[content_type] += 1
    
    def record_error(self, url, error):
        self.stats['total'] += 1
        self.stats['failed'] += 1
        self.errors[str(error)].append(url)
    
    def generate_summary(self):
        duration = time.time() - self.start_time
        success_rate = (self.stats['successful'] / self.stats['total'] * 100) if self.stats['total'] > 0 else 0
        
        summary = [
            "\n Scraping summary -",
            f"Time taken: {duration:.2f}s",
            f"URLs Processed: {self.stats['total']}",
            f"Successful: {self.stats['successful']}",
            f"Failed: {self.stats['failed']}",
            f"Success Rate: {success_rate:.1f}%",
            
            "\nStatus Codes:",
            *[f"{code}: {count}" for code, count in sorted(self.status_codes.items())],
            
            "\nContent types:",
            *[f"{ctype}: {count}" for ctype, count in sorted(self.content_types.items())],
            
            "\nErrors encountered:"
        ]
        
        if self.errors:
            for error_type, urls in self.errors.items():
                summary.append(f"{error_type}:")
                for url in urls[:3]:
                    summary.append(f"- {url}")
                if len(urls) > 3:
                    summary.append(f"... and {len(urls) - 3} more")
        else:
            summary.append("None")
            
        return "\n".join(summary)

def crawl_url(url, headers, stats):
    try:
        print(f"\nScraping: {url}")
        print("Request headers:") # Only the user agent for now
        for key, value in headers.items():
            print(f"{key}: {value}")
        
        response = requests.get(url, headers=headers, timeout=10)
        content_type = response.headers.get('Content-Type', '').split(';')[0]
        
        print(f"Response Status: {response.status_code}")
        print("Response Headers:")
        for key, value in response.headers.items():
            print(f"{key}: {value}")
            
        stats.record_success(url, response.status_code, content_type)
        print(f"Completed: {url}")
            
    except Exception as e:
        stats.record_error(url, e)
        print(f"Error: {url} - {str(e)}")

def main():
    if len(sys.argv) != 2:
        print("Usage: python main.py <sitemap.xml_url>")
        sys.exit(1)
        
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.6556.192 Safari/537.36'
    }
    
    try:
        print("Starting the scraper...")
        stats = CrawlerStatistics()
        
        sitemap = requests.get(sys.argv[1], headers=headers)
        urls = [elem.text for elem in ET.fromstring(sitemap.content).findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}loc')]
        
        for url in urls:
            crawl_url(url, headers, stats)
        
        print(stats.generate_summary())
            
    except Exception as e:
        print(f"Critical error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()