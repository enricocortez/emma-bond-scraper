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

    # Attempt to find all tables and pick the one with expected structure
    tables = soup.find_all('table')
    table = None
    for t in tables:
        headers = [th.get_text(strip=True).lower() for th in t.find_all('tr')[0].find_all(['th', 'td'])]
        if any(h in headers for h in ['issuer', 'state', 'sale date', 'par amount', 'purpose']):
            table = t
            break

    if table:
        # Extract headers and rows
        headers = [th.get_text(strip=True) for th in table.find_all('tr')[0].find_all(['th', 'td'])]
        rows = []
        for row in table.find_all('tr')[1:]:
            cells = row.find_all('td')
            rows.append([cell.get_text(strip=True) for cell in cells])

        # Convert to DataFrame
        df = pd.DataFrame(rows, columns=headers)

        # Filter relevant bond purposes
        keywords = ['water', 'wastewater', 'sewer', 'stormwater', 'drainage']
        if 'Purpose' in df.columns:
            df['Purpose'] = df['Purpose'].str.lower()
            mask = df['Purpose'].apply(lambda x: any(kw in x for kw in keywords))
            filtered_df = df[mask]

            st.subheader("Filtered Bond Issues")
            st.dataframe(filtered_df)

            # Download button for CSV
            csv = filtered_df.to_csv(index=False).encode('utf-8')
            st.download_button("Download Filtered CSV", csv, "filtered_emma_bonds.csv", "text/csv")
        else:
            st.warning("The uploaded table does not contain a 'Purpose' column.")
    else:
        st.error("No suitable table found in the uploaded HTML file.")

