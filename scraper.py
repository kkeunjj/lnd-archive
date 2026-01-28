"""
L&D Article Scraper
Collects articles from 7 major L&D and HR websites
Saves data to articles.json for web display
"""

import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import time
import re
from urllib.parse import urljoin

class LDArticleScraper:
    def __init__(self):
        self.articles = []
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def scrape_degreed(self):
        """Scrape Degreed blog"""
        try:
            url = "https://degreed.com/experience/blog/"
            response = requests.get(url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            articles = soup.find_all('article', limit=10)
            
            for article in articles:
                try:
                    title_elem = article.find(['h2', 'h3', 'h1'])
                    link_elem = article.find('a', href=True)
                    
                    if title_elem and link_elem:
                        title = title_elem.get_text(strip=True)
                        link = urljoin(url, link_elem['href'])
                        
                        date_elem = article.find(['time', 'span'], class_=re.compile('date|time', re.I))
                        date = date_elem.get_text(strip=True) if date_elem else datetime.now().strftime('%Y-%m-%d')
                        
                        summary_elem = article.find(['p', 'div'], class_=re.compile('excerpt|summary|description', re.I))
                        summary = summary_elem.get_text(strip=True)[:200] if summary_elem else title
                        
                        self.articles.append({
                            'date': date,
                            'site': 'Degreed',
                            'title': title,
                            'url': link,
                            'summary': summary,
                            'category': 'L&D 전략 및 LX',
                            'tags': ['L&D', 'Degreed']
                        })
                except Exception as e:
                    print(f"Error parsing Degreed article: {e}")
                    continue
                    
        except Exception as e:
            print(f"Error scraping Degreed: {e}")
    
    def scrape_josh_bersin(self):
        """Scrape Josh Bersin blog"""
        try:
            url = "https://joshbersin.com/"
            response = requests.get(url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            articles = soup.find_all(['article', 'div'], class_=re.compile('post|article|entry', re.I), limit=10)
            
            for article in articles:
                try:
                    title_elem = article.find(['h2', 'h3', 'h1', 'a'])
                    if not title_elem:
                        continue
                        
                    title = title_elem.get_text(strip=True)
                    link_elem = article.find('a', href=True) or title_elem.find('a', href=True)
                    link = urljoin(url, link_elem['href']) if link_elem and 'href' in link_elem.attrs else url
                    
                    date_elem = article.find(['time', 'span'], class_=re.compile('date|time', re.I))
                    date = date_elem.get_text(strip=True) if date_elem else datetime.now().strftime('%Y-%m-%d')
                    
                    summary_elem = article.find(['p', 'div'], class_=re.compile('excerpt|summary|content', re.I))
                    summary = summary_elem.get_text(strip=True)[:200] if summary_elem else title
                    
                    self.articles.append({
                        'date': date,
                        'site': 'Josh Bersin',
                        'title': title,
                        'url': link,
                        'summary': summary,
                        'category': 'TD',
                        'tags': ['TD', 'Josh Bersin', 'Talent Management']
                    })
                except Exception as e:
                    print(f"Error parsing Josh Bersin article: {e}")
                    continue
                    
        except Exception as e:
            print(f"Error scraping Josh Bersin: {e}")
    
    def scrape_shrm(self):
        """Scrape SHRM news"""
        try:
            url = "https://www.shrm.org/topics-tools/news"
            response = requests.get(url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            articles = soup.find_all(['article', 'div'], class_=re.compile('article|news|post', re.I), limit=10)
            
            for article in articles:
                try:
                    title_elem = article.find(['h2', 'h3', 'h1'])
                    if not title_elem:
                        continue
                        
                    title = title_elem.get_text(strip=True)
                    link_elem = article.find('a', href=True)
                    link = urljoin(url, link_elem['href']) if link_elem else url
                    
                    date_elem = article.find(['time', 'span'], class_=re.compile('date|time', re.I))
                    date = date_elem.get_text(strip=True) if date_elem else datetime.now().strftime('%Y-%m-%d')
                    
                    summary_elem = article.find(['p', 'div'], class_=re.compile('excerpt|summary|description', re.I))
                    summary = summary_elem.get_text(strip=True)[:200] if summary_elem else title
                    
                    self.articles.append({
                        'date': date,
                        'site': 'SHRM',
                        'title': title,
                        'url': link,
                        'summary': summary,
                        'category': '기타',
                        'tags': ['HR', 'SHRM', 'News']
                    })
                except Exception as e:
                    print(f"Error parsing SHRM article: {e}")
                    continue
                    
        except Exception as e:
            print(f"Error scraping SHRM: {e}")
    
    def scrape_unleash(self):
        """Scrape Unleash L&D"""
        try:
            url = "https://www.unleash.ai/learning-and-development/"
            response = requests.get(url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            articles = soup.find_all(['article', 'div'], class_=re.compile('post|article|card', re.I), limit=10)
            
            for article in articles:
                try:
                    title_elem = article.find(['h2', 'h3', 'h1'])
                    if not title_elem:
                        continue
                        
                    title = title_elem.get_text(strip=True)
                    link_elem = article.find('a', href=True)
                    link = urljoin(url, link_elem['href']) if link_elem else url
                    
                    date_elem = article.find(['time', 'span'], class_=re.compile('date|time', re.I))
                    date = date_elem.get_text(strip=True) if date_elem else datetime.now().strftime('%Y-%m-%d')
                    
                    summary_elem = article.find(['p', 'div'], class_=re.compile('excerpt|summary|description', re.I))
                    summary = summary_elem.get_text(strip=True)[:200] if summary_elem else title
                    
                    self.articles.append({
                        'date': date,
                        'site': 'Unleash',
                        'title': title,
                        'url': link,
                        'summary': summary,
                        'category': 'L&D 전략 및 LX',
                        'tags': ['L&D', 'Unleash', 'HR Tech']
                    })
                except Exception as e:
                    print(f"Error parsing Unleash article: {e}")
                    continue
                    
        except Exception as e:
            print(f"Error scraping Unleash: {e}")
    
    def scrape_ddi(self):
        """Scrape DDI blogs"""
        try:
            url = "https://www.ddi.com/blogs"
            response = requests.get(url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            articles = soup.find_all(['article', 'div'], class_=re.compile('blog|post|article', re.I), limit=10)
            
            for article in articles:
                try:
                    title_elem = article.find(['h2', 'h3', 'h1'])
                    if not title_elem:
                        continue
                        
                    title = title_elem.get_text(strip=True)
                    link_elem = article.find('a', href=True)
                    link = urljoin(url, link_elem['href']) if link_elem else url
                    
                    date_elem = article.find(['time', 'span'], class_=re.compile('date|time', re.I))
                    date = date_elem.get_text(strip=True) if date_elem else datetime.now().strftime('%Y-%m-%d')
                    
                    summary_elem = article.find(['p', 'div'], class_=re.compile('excerpt|summary|description', re.I))
                    summary = summary_elem.get_text(strip=True)[:200] if summary_elem else title
                    
                    self.articles.append({
                        'date': date,
                        'site': 'DDI',
                        'title': title,
                        'url': link,
                        'summary': summary,
                        'category': '리더십',
                        'tags': ['Leadership', 'DDI', 'Development']
                    })
                except Exception as e:
                    print(f"Error parsing DDI article: {e}")
                    continue
                    
        except Exception as e:
            print(f"Error scraping DDI: {e}")
    
    def scrape_wharton(self):
        """Scrape Wharton Knowledge"""
        try:
            url = "https://knowledge.wharton.upenn.edu/category/leadership/"
            response = requests.get(url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            articles = soup.find_all(['article', 'div'], class_=re.compile('post|article', re.I), limit=10)
            
            for article in articles:
                try:
                    title_elem = article.find(['h2', 'h3', 'h1'])
                    if not title_elem:
                        continue
                        
                    title = title_elem.get_text(strip=True)
                    link_elem = article.find('a', href=True)
                    link = urljoin(url, link_elem['href']) if link_elem else url
                    
                    date_elem = article.find(['time', 'span'], class_=re.compile('date|time', re.I))
                    date = date_elem.get_text(strip=True) if date_elem else datetime.now().strftime('%Y-%m-%d')
                    
                    summary_elem = article.find(['p', 'div'], class_=re.compile('excerpt|summary|description', re.I))
                    summary = summary_elem.get_text(strip=True)[:200] if summary_elem else title
                    
                    self.articles.append({
                        'date': date,
                        'site': 'Wharton Knowledge',
                        'title': title,
                        'url': link,
                        'summary': summary,
                        'category': 'OD',
                        'tags': ['OD', 'Wharton', 'Research']
                    })
                except Exception as e:
                    print(f"Error parsing Wharton article: {e}")
                    continue
                    
        except Exception as e:
            print(f"Error scraping Wharton: {e}")
    
    def scrape_kornferry(self):
        """Scrape Korn Ferry insights"""
        try:
            url = "https://www.kornferry.com/insights"
            response = requests.get(url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            articles = soup.find_all(['article', 'div'], class_=re.compile('insight|article|card', re.I), limit=10)
            
            for article in articles:
                try:
                    title_elem = article.find(['h2', 'h3', 'h1'])
                    if not title_elem:
                        continue
                        
                    title = title_elem.get_text(strip=True)
                    link_elem = article.find('a', href=True)
                    link = urljoin(url, link_elem['href']) if link_elem else url
                    
                    date_elem = article.find(['time', 'span'], class_=re.compile('date|time', re.I))
                    date = date_elem.get_text(strip=True) if date_elem else datetime.now().strftime('%Y-%m-%d')
                    
                    summary_elem = article.find(['p', 'div'], class_=re.compile('excerpt|summary|description', re.I))
                    summary = summary_elem.get_text(strip=True)[:200] if summary_elem else title
                    
                    self.articles.append({
                        'date': date,
                        'site': 'Korn Ferry',
                        'title': title,
                        'url': link,
                        'summary': summary,
                        'category': 'TD',
                        'tags': ['TD', 'Korn Ferry', 'Talent']
                    })
                except Exception as e:
                    print(f"Error parsing Korn Ferry article: {e}")
                    continue
                    
        except Exception as e:
            print(f"Error scraping Korn Ferry: {e}")
    
    def scrape_all(self):
        """Scrape all websites"""
        print("Starting to scrape all websites...")
        
        self.scrape_degreed()
        time.sleep(2)
        
        self.scrape_josh_bersin()
        time.sleep(2)
        
        self.scrape_shrm()
        time.sleep(2)
        
        self.scrape_unleash()
        time.sleep(2)
        
        self.scrape_ddi()
        time.sleep(2)
        
        self.scrape_wharton()
        time.sleep(2)
        
        self.scrape_kornferry()
        
        print(f"Scraping completed. Total articles: {len(self.articles)}")
        return self.articles
    
    def save_to_json(self, filename='articles.json'):
        """Save articles to JSON file"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.articles, f, ensure_ascii=False, indent=2)
        print(f"Articles saved to {filename}")


if __name__ == "__main__":
    scraper = LDArticleScraper()
    scraper.scrape_all()
    scraper.save_to_json('articles.json')
    print("✅ Scraping complete! Check articles.json")
