import streamlit as st
import pandas as pd
from bs4 import BeautifulSoup
import io

st.title("EMMA Bond Scraper for Water Infrastructure")

uploaded_file = st.file_uploader("Upload your EMMA HTML table file (e.g., pasted from New Issue Calendar)", type="html")

if uploaded_file:
    # Read the uploaded HTML file
    html_content = uploaded_file.read().decode("utf-8")
    soup = BeautifulSoup(html_content, 'html.parser')
    table = soup.find('table')

    if table:
        # Extract headers
        headers = [th.get_text(strip=True) for th in table.find_all('tr')[0].find_all(['th', 'td'])]

        # Extract rows
        rows = []
        for row in table.find_all('tr')[1:]:
            cells = row.find_all('td')
            rows.append([cell.get_text(strip=True) for cell in cells])

        # Convert to DataFrame
        df = pd.DataFrame(rows, columns=headers)

        # Filter relevant bond purposes
        keywords = ['water', 'wastewater', 'sewer', 'stormwater', 'drainage']
        df['Purpose'] = df['Purpose'].str.lower()
        mask = df['Purpose'].apply(lambda x: any(kw in x for kw in keywords))
        filtered_df = df[mask]

        st.subheader("Filtered Bond Issues")
        st.dataframe(filtered_df)

        # Download button for CSV
        csv = filtered_df.to_csv(index=False).encode('utf-8')
        st.download_button("Download Filtered CSV", csv, "filtered_emma_bonds.csv", "text/csv")
    else:
        st.error("No table found in the uploaded HTML file.")
