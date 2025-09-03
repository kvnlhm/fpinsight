import streamlit as st
import pandas as pd
import json
import os

def load_report_history(file_path="report_history.json"):
    if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
        try:
            with open(file_path, "r") as file:
                return json.load(file)
        except json.JSONDecodeError:
            st.error("Error decoding JSON. File may be corrupted.")
            return []
    return []

def save_report_history(history, file_path="report_history.json"):
    with open(file_path, "w") as file:
        json.dump(history, file)

def main():
    st.title("History Laporan")
    
    # Load report history from JSON file
    report_history = load_report_history()
    
    # Initialize reports in session state
    if "reports" not in st.session_state:
        st.session_state.reports = report_history

    # Display headers
    col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 2, 1])
    col1.markdown("### Nama File")
    col2.markdown("### Min Support")
    col3.markdown("### Min Confidence")
    col4.markdown("### ")
    col5.markdown("### Laporan")

    if st.session_state.reports:
        # Sort reports by the timestamp
        history_df = pd.DataFrame(st.session_state.reports).sort_values(by='timestamp', ascending=False)

        # Display the uploaded filename and link to download the generated PDF
        for index, row in history_df.iterrows():
            col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 2, 1])
            col1.write(row['uploaded_filename'])
            col2.write(f"{row['min_support']:.3f}")
            col3.write(f"{row['min_confidence']:.3f}")
            pdf_file_path = row['pdf_filename']
            if os.path.exists(pdf_file_path):
                with open(pdf_file_path, "rb") as file:
                    col5.download_button(label="Download", data=file, file_name=os.path.basename(pdf_file_path), key=f"download_{index}")
            else:
                col5.write("File not found.")
    else:
        st.write("No reports generated yet.")

    # Save the updated report history
    save_report_history(st.session_state.reports)

if __name__ == "__main__":
    main()