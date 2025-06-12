import streamlit as st
import pandas as pd
from bs4 import BeautifulSoup
import io

st.title("EMMA Bond Scraper for Water Infrastructure")

uploaded_file = st.file_uploader("Upload your EMMA HTML page (e.g., saved from New Issue Calendar)", type="html")

if uploaded_file:
    html_content = uploaded_file.read().decode("utf-8")
    soup = BeautifulSoup(html_content, 'html.parser')

    tables = soup.find_all('table')
    st.write(f"Found {len(tables)} table(s) in the uploaded HTML.")

    if not tables:
        st.error("No tables found in the uploaded HTML file.")
    else:
        all_dfs = []
        for idx, table in enumerate(tables):
            headers = [th.get_text(strip=True) for th in table.find_all('tr')[0].find_all(['th', 'td'])]
            rows = []
            for row in table.find_all('tr')[1:]:
                cells = row.find_all('td')
                row_data = [cell.get_text(strip=True) for cell in cells]
                if len(row_data) == len(headers):
                    rows.append(row_data)
            try:
                df = pd.DataFrame(rows, columns=headers)
                all_dfs.append((f"Table {idx}: {headers}", df))
            except Exception as e:
                st.warning(f"Skipping table {idx} due to error: {e}")

        table_labels = [label for label, _ in all_dfs]
        selected_label = st.selectbox("Select a table to process:", table_labels)
        selected_df = next(df for label, df in all_dfs if label == selected_label)

        st.subheader("Raw Table Preview")
        st.dataframe(selected_df)

        # Attempt to identify the Purpose column
        purpose_col = next((col for col in selected_df.columns if 'purpose' in col.lower()), None)

        if purpose_col:
            keywords = ['water', 'wastewater', 'sewer', 'stormwater', 'drainage']
            selected_df[purpose_col] = selected_df[purpose_col].str.lower()
            mask = selected_df[purpose_col].apply(lambda x: any(kw in x for kw in keywords))
            filtered_df = selected_df[mask]

            st.subheader("Filtered Bond Issues")
            st.dataframe(filtered_df)

            csv = filtered_df.to_csv(index=False).encode('utf-8')
            st.download_button("Download Filtered CSV", csv, "filtered_emma_bonds.csv", "text/csv")
        else:
            st.warning("No 'Purpose' column found. Displaying full table only.")
