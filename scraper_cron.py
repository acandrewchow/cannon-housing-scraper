import requests
from bs4 import BeautifulSoup
import sqlite3
from twilio.rest import Client
from dotenv import load_dotenv
import os

load_dotenv()

# Twilio credentials 
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")
RECIPIENT_PHONE_NUMBER = os.getenv("RECIPIENT_PHONE_NUMBER")

# SMS notification using Twilio
def send_sms(message):
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    client.messages.create(
        body=message,
        from_=TWILIO_PHONE_NUMBER,
        to=RECIPIENT_PHONE_NUMBER
    )

# Function to scrape house listings
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

# Cleans HTML tags from description
def clean_html(description):
    return BeautifulSoup(description, "html.parser").get_text(strip=True)

# Inserts into the database and prepares new message if a new listing has been posted
def insert_into_db(scraped_data):
    conn = sqlite3.connect('./listings.db')
    cursor = conn.cursor()
    
    new_listings = []
    for data in scraped_data:
        cursor.execute("""
            INSERT OR IGNORE INTO listings (title, price, posted, link, description)
            VALUES (?, ?, ?, ?, ?)""", (data['Title'], data['Price'], data['Posted'], data['Link'], data['Description']))
        
        # If new listing store it for notification
        if cursor.rowcount > 0:
            new_listings.append(data)
    
    conn.commit()
    conn.close()

    # Send SMS for new listings
    if new_listings:
        for listing in new_listings:
            message = (
                f"New Listing: {listing['Title']}\n"
                f"Price: {listing['Price']}\n"
                f"Posted on: {listing['Posted']}\n"
                f"Link: {listing['Link']}\n"
            )
            send_sms(message)
            print(f"New listing added: {listing['Title']}, {listing['Price']}, {listing['Posted']}")

if __name__ == '__main__':
    listings = scrape_listings()
    if listings:
        insert_into_db(listings)
        print("Scraping complete and data processed.")
    else:
        print("No new listings found.")