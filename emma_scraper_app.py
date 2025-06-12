import streamlit as st
import pandas as pd
from bs4 import BeautifulSoup
import io

st.title("EMMA Bond Scraper for Water Infrastructure")

uploaded_file = st.file_uploader("Upload your EMMA HTML page (e.g., saved from New Issue Calendar)", type="html")

if uploaded_file:
    # Read the uploaded HTML file
    html_content = uploaded_file.read().decode("utf-8")
    soup = BeautifulSoup(html_content, 'html.parser')

    tables = soup.find_all('table')
    st.write(f"Found {len(tables)} table(s) in the uploaded HTML.")

    table_options = []
    for idx, table in enumerate(tables):
        first_row = table.find('tr')
        if first_row:
            headers = [th.get_text(strip=True) for th in first_row.find_all(['th', 'td'])]
            table_options.append((idx, headers))

    if table_options:
        table_idx = st.selectbox("Select a table to preview:", options=[f"Table {idx}: {headers}" for idx, headers in table_options])
        selected_index = int(table_idx.split()[1].strip(':'))
        selected_table = tables[selected_index]

        headers = [th.get_text(strip=True) for th in selected_table.find_all('tr')[0].find_all(['th', 'td'])]
        rows = []
        for row in selected_table.find_all('tr')[1:]:
            cells = row.find_all('td')
            rows.append([cell.get_text(strip=True) for cell in cells])

        df = pd.DataFrame(rows, columns=headers)

        st.subheader("Raw Table Preview")
        st.dataframe(df)

        # Filter relevant bond purposes
        keywords = ['water', 'wastewater', 'sewer', 'stormwater', 'drainage']
        purpose_col = next((col for col in df.columns if 'purpose' in col.lower()), None)

        if purpose_col:
            df[purpose_col] = df[purpose_col].str.lower()
            mask = df[purpose_col].apply(lambda x: any(kw in x for kw in keywords))
            filtered_df = df[mask]

            st.subheader("Filtered Bond Issues")
            st.dataframe(filtered_df)

            csv = filtered_df.to_csv(index=False).encode('utf-8')
            st.download_button("Download Filtered CSV", csv, "filtered_emma_bonds.csv", "text/csv")
        else:
            st.warning("The selected table does not contain a recognizable 'Purpose' column.")
    else:
        st.error("No HTML tables found in the uploaded file.")
