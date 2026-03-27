import requests
from bs4 import BeautifulSoup
import json
import os
import re
from datetime import datetime
from urllib.parse import urljoin, urlparse
import time
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def convert_to_quill_delta(content: str, images: list = None) -> dict:
    """Convert article content to Quill Delta JSON format"""
    ops = []
    paragraphs = content.split('\n\n')
    
    for para in paragraphs:
        cleaned = re.sub(r'<[^>]+>', '', para).strip()
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        if cleaned and len(cleaned) > 10:
            ops.append({"insert": cleaned})
            ops.append({"insert": "\n"})
    
    if images:
        for img_path in images:
            ops.append({"insert": "", "attributes": {"image": img_path}})
            ops.append({"insert": "\n"})
    
    return {"ops": ops}


def extract_image_urls(html_content: str) -> list:
    """Extract all image URLs from HTML content"""
    soup = BeautifulSoup(html_content, 'lxml')
    images = soup.find_all('img')
    urls = []
    for img in images:
        src = img.get('src') or img.get('data-src')
        if src and not src.startswith('data:'):
            urls.append(src)
    return urls


def parse_date(date_string: str) -> datetime:
    """Parse date from various string formats"""
    formats = ["%Y-%m-%d %H:%M", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"]
    for fmt in formats:
        try:
            return datetime.strptime(date_string.strip(), fmt)
        except ValueError:
            continue
    return None


def generate_filename(title: str, date: datetime) -> str:
    """Generate filename for news article"""
    date_str = date.strftime("%d-%m-%Y_%H%M%S")
    return f"nyhet_{date_str}.json"


def create_metadata(articles: list) -> dict:
    """Create metadata file for all scraped articles"""
    return {
        "scraped_at": datetime.now().isoformat(),
        "total_articles": len(articles),
        "articles": articles
    }


def download_image(url: str, save_dir: str, article_id: str) -> str:
    """Download image from URL and save to local directory"""
    try:
        os.makedirs(save_dir, exist_ok=True)
        parsed_url = urlparse(url)
        filename = os.path.basename(parsed_url.path)
        
        if not filename or '.' not in filename:
            filename = f"image_{article_id}_{int(time.time())}.jpg"
        
        base, ext = os.path.splitext(filename)
        counter = 1
        while os.path.exists(os.path.join(save_dir, filename)):
            filename = f"{base}_{counter}{ext}"
            counter += 1
        
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        filepath = os.path.join(save_dir, filename)
        with open(filepath, 'wb') as f:
            f.write(response.content)
        
        logger.info(f"Downloaded image: {filename}")
        return filename
    except Exception as e:
        logger.error(f"Failed to download image {url}: {e}")
        return None


def get_news_list(base_url: str) -> list:
    """Get list of news article URLs from the main news page"""
    news_articles = []
    
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(base_url, headers=headers, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'lxml')
        news_divs = soup.find_all(class_='news')
        
        for news_div in news_divs:
            link = news_div.find('a', href=True)
            if link:
                article_url = urljoin(base_url, link.get('href'))
                title = link.get_text(strip=True)
                
                text = news_div.get_text(strip=True)
                date_match = re.search(r'(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2})', text)
                date_str = date_match.group(1) if date_match else datetime.now().strftime("%Y-%m-%d %H:%M")
                
                news_articles.append({'url': article_url, 'title': title, 'date_str': date_str})
                logger.info(f"Found article: {title}")
        
        logger.info(f"Found {len(news_articles)} news articles")
    except Exception as e:
        logger.error(f"Failed to get news list: {e}")
    
    return news_articles


def scrape_article(article_url: str, expected_title: str) -> dict:
    """Scrape full content of a single news article"""
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(article_url, headers=headers, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'lxml')
        
        # Use expected title from news list
        title = expected_title
        
        # Extract date
        date_str = ""
        date_elem = soup.find('time')
        if date_elem:
            date_str = date_elem.get_text(strip=True)
        else:
            text = soup.get_text()
            date_match = re.search(r'(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2})', text)
            if date_match:
                date_str = date_match.group(1)
        
        if not date_str:
            date_str = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        # Extract content - get all text, clean it up
        content = soup.get_text(separator='\n', strip=True)
        
        # Clean content - remove repeated navigation text
        lines = content.split('\n')
        cleaned_lines = []
        seen_lines = set()
        for line in lines:
            line = line.strip()
            if line and line not in seen_lines and len(line) > 5:
                cleaned_lines.append(line)
                seen_lines.add(line)
        content = '\n\n'.join(cleaned_lines)
        
        # Extract images
        image_urls = extract_image_urls(str(soup))
        
        return {
            'title': title,
            'content': content,
            'date_str': date_str,
            'image_urls': image_urls,
            'url': article_url
        }
    except Exception as e:
        logger.error(f"Failed to scrape article {article_url}: {e}")
        return None


def process_and_save_articles(articles: list, uploads_dir: str, data_dir: str) -> list:
    """Process scraped articles: download images, convert to Quill Delta, save JSON files"""
    processed_articles = []
    
    for idx, article in enumerate(articles):
        try:
            article_id = f"{idx + 1}_{int(time.time())}"
            
            # Download images
            downloaded_images = []
            for img_url in article.get('image_urls', []):
                if not img_url.startswith('http'):
                    img_url = urljoin(article['url'], img_url)
                
                saved_filename = download_image(img_url, uploads_dir, article_id)
                if saved_filename:
                    downloaded_images.append(saved_filename)
            
            # Convert to Quill Delta format
            quill_delta = convert_to_quill_delta(
                article['content'],
                [os.path.join("uploads/news", img) for img in downloaded_images]
            )
            
            # Add metadata
            quill_delta['title'] = article['title']
            quill_delta['date'] = article['date_str']
            quill_delta['original_url'] = article.get('url', '')
            quill_delta['images'] = downloaded_images
            
            # Generate filename and save
            article_date = parse_date(article['date_str']) or datetime.now()
            filename = generate_filename(article['title'], article_date)
            filepath = os.path.join(data_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(quill_delta, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Saved article: {filename} - {article['title']}")
            
            processed_articles.append({
                "title": article['title'],
                "date": article['date_str'],
                "filename": filename,
                "images": downloaded_images,
                "image_count": len(downloaded_images),
                "url": article.get('url', '')
            })
        except Exception as e:
            logger.error(f"Error processing article {article.get('title', idx)}: {e}")
            continue
    
    # Create metadata file
    metadata = create_metadata(processed_articles)
    metadata_filepath = os.path.join(data_dir, "news_metadata.json")
    
    with open(metadata_filepath, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)
    
    logger.info(f"Created metadata file: {metadata_filepath}")
    return processed_articles


def main():
    """Main function to run the news scraper"""
    base_url = "https://www.hammarbysupporterklubb.se/nyheter/?ID=381455&NID=1332083"
    base_dir = "/a0/usr/projects/Development/hammarby_website/backend"
    uploads_dir = os.path.join(base_dir, "uploads/news")
    data_dir = os.path.join(base_dir, "data/news")
    
    os.makedirs(uploads_dir, exist_ok=True)
    os.makedirs(data_dir, exist_ok=True)
    
    logger.info(f"Starting news scraper for: {base_url}")
    
    news_list = get_news_list(base_url)
    if not news_list:
        logger.warning("No news articles found")
        return
    
    articles = []
    for idx, news_item in enumerate(news_list):
        logger.info(f"Scraping article {idx + 1}/{len(news_list)}: {news_item['title']}")
        article = scrape_article(news_item['url'], news_item['title'])
        if article:
            articles.append(article)
        time.sleep(1)
    
    if not articles:
        logger.warning("No articles scraped successfully")
        return
    
    processed = process_and_save_articles(articles, uploads_dir, data_dir)
    
    logger.info(f"\n=== Scraping Complete ===")
    logger.info(f"Total articles found: {len(news_list)}")
    logger.info(f"Articles scraped: {len(articles)}")
    logger.info(f"Articles processed: {len(processed)}")
    logger.info(f"Images downloaded: {sum(a['image_count'] for a in processed)}")
    logger.info(f"Files saved to: {data_dir}")
    logger.info(f"Images saved to: {uploads_dir}")


if __name__ == "__main__":
    main()
