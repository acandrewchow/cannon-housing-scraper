import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd

# Scrapes the latest house listings on thecannon.ca
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
            st.error(f"Failed to retrieve data from page {page}. Status code: {response.status_code}")
            break

    return pd.DataFrame(scraped_data)

def clean_html(description):
    return BeautifulSoup(description, "html.parser").get_text(strip=True)

st.title("TheCannon Housing Listings Scraper")

st.write("""
Scrapes housing listings from [The Cannon](https://thecannon.ca/housing/) and displays them.
""")

num_pages = st.number_input("Number of pages to scrape:", min_value=1, max_value=50, value=5)

if st.button('Scrape Listings'):
    with st.spinner('Scraping the listings...'):
        df = scrape_listings(max_pages=num_pages)
        if df is not None:
            st.success('Scraping complete!')

            df['Link'] = df['Link'].apply(lambda x: f'<a href="{x}" target="_blank">View Listing</a>')
            
            st.write(df.to_html(escape=False), unsafe_allow_html=True)
    
            # CSV Download
            csv = df.to_csv(index=False)
            st.download_button(
                label="Download listings as CSV",
                data=csv,
                file_name='cannon_housing_listings.csv',
                mime='text/csv',
            )
        else:
            st.error("Could not scrape any listings.")