import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd

# Scrapes the latest house listings on thecannon.ca
def scrape_listings():
    url = "https://thecannon.ca/housing/"
    response = requests.get(url)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        listings = soup.find_all('li', class_='housing-item')
        
        scraped_data = []
        
        for listing in listings:
            title = listing.find('h2').text.strip()
            price = listing.find('li', class_='price').find('dd').text.strip()
            link = listing.find('a', href=True)['href']
            
            scraped_data.append({
                'Title': title,
                'Price': price,
                'Link': link
            })
            
        return pd.DataFrame(scraped_data)
    else:
        st.error(f"Failed to retrieve data. Status code: {response.status_code}")
        return None

st.title("TheCannon Housing Listings Scraper")

st.write("""
Scrapes housing listings from [The Cannon](https://thecannon.ca/housing/) and displays them.
""")

if st.button('Scrape Listings'):
    with st.spinner('Scraping the listings...'):
        df = scrape_listings()
        if df is not None:
            st.success('Scraping complete!')
            st.write(df)  # Dataframe within Streamlit

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