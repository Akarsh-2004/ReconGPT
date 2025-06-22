# this script scrapes various cybersecurity-related websites and blogs to collect raw data for training a Named Entity Recognition (NER) model.
# It saves the scraped content into text files in a specified directory.
# The script includes error handling to skip problematic pages and continues scraping other pages.  
import os
import re
import requests
from bs4 import BeautifulSoup
from newspaper import Article
import feedparser

# Create output folder
os.makedirs("raw_data", exist_ok=True)

# Helper: clean filename
def clean_filename(text):
    return re.sub(r'[^\w\-_.]', '_', text)

### 1. MITRE ATT&CK ###
def scrape_mitre(limit=20):
    print("[*] Scraping MITRE ATT&CK")
    BASE_URL = "https://attack.mitre.org"
    START_URL = f"{BASE_URL}/techniques/"
    soup = BeautifulSoup(requests.get(START_URL).text, "html.parser")
    links = [BASE_URL + a['href'] for a in soup.select("a[href^='/techniques/T']")]
    
    for i, link in enumerate(links[:limit]):
        try:
            page = requests.get(link)
            s = BeautifulSoup(page.text, "html.parser")
            text = s.select_one("div.col-md-11").get_text(separator="\n").strip()
            with open(f"raw_data/mitre_{i:03}.txt", "w", encoding="utf-8") as f:
                f.write(text)
        except Exception as e:
            print(f"[!] MITRE error at {link}: {e}")

### 2. CISA Alerts ###
def scrape_cisa(limit=20):
    print("[*] Scraping CISA Alerts")
    feed = feedparser.parse("https://www.cisa.gov/news-events/alerts.xml")
    for i, entry in enumerate(feed.entries[:limit]):
        try:
            html = requests.get(entry.link).text
            soup = BeautifulSoup(html, "html.parser")
            content = soup.find("div", class_="region-content").get_text(separator="\n").strip()
            with open(f"raw_data/cisa_{i:03}.txt", "w", encoding="utf-8") as f:
                f.write(content)
        except Exception as e:
            print(f"[!] CISA error at {entry.link}: {e}")

### 3. TheHackerNews ###
def scrape_hackernews(limit=20):
    print("[*] Scraping TheHackerNews")
    homepage = "https://thehackernews.com/"
    soup = BeautifulSoup(requests.get(homepage).text, "html.parser")
    links = [a['href'] for a in soup.select("h2 a.story-link")]

    for i, url in enumerate(links[:limit]):
        try:
            article = Article(url)
            article.download()
            article.parse()
            with open(f"raw_data/hackernews_{i:03}.txt", "w", encoding="utf-8") as f:
                f.write(article.text)
        except Exception as e:
            print(f"[!] THN error at {url}: {e}")

### 4. AlienVault OTX Blog ###
def scrape_otx(limit=20):
    print("[*] Scraping AlienVault OTX blog")
    base_url = "https://www.alienvault.com/blogs/labs-research"
    soup = BeautifulSoup(requests.get(base_url).text, "html.parser")
    links = [a['href'] for a in soup.select("a.card-title[href]")]

    for i, link in enumerate(links[:limit]):
        try:
            res = requests.get(link)
            soup = BeautifulSoup(res.text, "html.parser")
            content = soup.find("article").get_text(separator="\n").strip()
            with open(f"raw_data/otx_{i:03}.txt", "w", encoding="utf-8") as f:
                f.write(content)
        except Exception as e:
            print(f"[!] OTX error at {link}: {e}")

### 5. Cisco Talos Blog ###
def scrape_talos(limit=20):
    print("[*] Scraping Cisco Talos Blog")
    homepage = "https://blog.talosintelligence.com/"
    soup = BeautifulSoup(requests.get(homepage).text, "html.parser")
    
    links = [
        a['href'] if a['href'].startswith('http') 
        else "https://blog.talosintelligence.com" + a['href'] 
        for a in soup.select("h2 a[href]")
    ]

    for i, link in enumerate(links[:limit]):
        try:
            res = requests.get(link)
            soup = BeautifulSoup(res.text, "html.parser")

            # Try old method first
            content_div = soup.find("div", class_="post-body")
            
            # Fallback to <article> tag
            if content_div is None:
                content_div = soup.find("article")
            
            # Fallback to main content wrapper
            if content_div is None:
                content_div = soup.find("div", class_="post-content")

            if content_div is None:
                raise ValueError("No valid content container found")

            content = content_div.get_text(separator="\n").strip()
            with open(f"raw_data/talos_{i:03}.txt", "w", encoding="utf-8") as f:
                f.write(content)
        except Exception as e:
            print(f"[!] Talos error at {link}: {e}")

# Master function to run all
def scrape_all():
    scrape_mitre()
    scrape_cisa()
    scrape_hackernews()
    scrape_otx()
    scrape_talos()

if __name__ == "__main__":
    scrape_all()
