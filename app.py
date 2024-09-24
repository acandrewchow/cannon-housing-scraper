import streamlit as st
import pandas as pd
import sqlite3

# Database setup
DB_NAME = './listings.db'  # Path to your SQLite database

# Fetch listings from the database
def fetch_listings():
    with sqlite3.connect(DB_NAME) as conn:
        query = '''
        SELECT title, posted, price, link, description FROM listings
        '''
        df = pd.read_sql_query(query, conn)
    return df

# Streamlit UI
st.title("TheCannon Housing Listings")

st.write("""
Displays housing listings from the database scraped from [The Cannon](https://thecannon.ca/housing/).
""")

# Fetch and display listings when the app loads
with st.spinner('Fetching listings from the database...'):
    df = fetch_listings()

    if not df.empty:
        # st.success('Listings fetched successfully!')

        if 'link' in df.columns:
            df['link'] = df['link'].apply(lambda x: f'<a href="{x}" target="_blank">View Listing</a>')
            df.rename(columns={'link': 'Link'}, inplace=True)
        else:
            st.error("The 'Link' column is missing from the DataFrame.")

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
        st.error("No listings found in the database.")