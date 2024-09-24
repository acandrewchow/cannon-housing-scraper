import requests
from bs4 import BeautifulSoup
import sqlite3

# Cron job that will run every hour to check if there
# are new house listings
def scrape_listings(max_pages=10):
    base_url = "https://thecannon.ca/housing/page/"
    scraped_data = []

    for page in range(1, max_pages + 1):
        url = f"{base_url}{page}/"
        response = requests.get(url)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            listings = soup.find_all('li', class_='housing-item')

            if not listings:  
                break

            for listing in listings:
                title = listing.find('h2').text.strip()
                price = listing.find('li', class_='price').find('dd').text.strip()
                post_date = listing.find('li', class_='post-date').find('dd').text.strip()
                link = listing.find('a', href=True)['href']
                description = listing.find('div', class_='description')

                cleaned_description = clean_html(str(description)) if description else "No description available"
                
                scraped_data.append({
                    'Title': title,
                    'Posted': post_date,
                    'Price': price,
                    'Link': link,
                    'Description': cleaned_description
                })
        else:
            print(f"Failed to retrieve data from page {page}. Status code: {response.status_code}")
            break

    return scraped_data

def clean_html(description):
    return BeautifulSoup(description, "html.parser").get_text(strip=True)

def insert_into_db(scraped_data):
    conn = sqlite3.connect('./listings.db')
    cursor = conn.cursor()
    
    for data in scraped_data:
        cursor.execute("""
            INSERT OR IGNORE INTO listings (title, price, posted, link, description)
            VALUES (?, ?, ?, ?, ?)""", (data['Title'], data['Price'], data['Posted'], data['Link'], data['Description']))

    conn.commit()
    conn.close()

if __name__ == '__main__':
    listings = scrape_listings()
    if listings:
        insert_into_db(listings)
        print("Scraping complete and data inserted into database.")
    else:
        print("No new listings found.")