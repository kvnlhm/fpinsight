import streamlit as st
import pandas as pd
from pages.page.Penamaan_Kode import load_data_from_database
from utils.pdf_generator import create_pdf
import os

# Memuat data dari database untuk membuat pemetaan kode item ke nama item
data_kode_obat = load_data_from_database()
item_name_dict = {kode: nama for kode, nama in data_kode_obat}

def calculate_support_for_item_pair(summarized_patterns, unique_tid_count):
    support_pairs = []
    for pattern in summarized_patterns:
        item = pattern['Item']
        filtered_item_counts = pattern['Filtered Item Counts']
        for other_item, count in filtered_item_counts.items():
            if item != other_item:
                support = count / unique_tid_count
                support = round(support, 2)  # Bulatkan ke 2 angka desimal
                support_pairs.append({
                    'Item Pair': f'{{"{other_item}", "{item}"}}',
                    'Support': support
                })
    return support_pairs

def calculate_confidence(summarized_patterns, support_dict, min_confidence, frequency):
    confidence_pairs = []
    for pattern in summarized_patterns:
        item = pattern['Item']
        filtered_item_counts = pattern['Filtered Item Counts']
        for other_item, count in filtered_item_counts.items():
            if item != other_item:
                if other_item in frequency['Kode'].values:
                    confidence = count / frequency.loc[frequency['Kode'] == other_item]['Frekuensi'].values[0]
                    confidence = round(confidence, 2)  # Bulatkan ke 2 angka desimal
                    confidence_pairs.append({
                        'Item Pair': f'{{"{other_item}", "{item}"}}',
                        'Confidence': confidence
                    })
                else:
                    st.write(f"Item '{other_item}' tidak ditemukan dalam kamus frekuensi.")
    return confidence_pairs

def generate_explanation(row):
    items = row['Item'].strip("{}").split(", ")
    item1, item2 = items[0], items[1]
    item1_name = item_name_dict.get(item1.strip('"'), item1)
    item2_name = item_name_dict.get(item2.strip('"'), item2)
    return (f"Jika customer membeli {item1_name} maka juga akan membeli {item2_name} "
            f"dengan nilai Support sebesar {row['Support']} dan nilai Confidence sebesar {row['Confidence']}")

def display_explanations(result_df):
    explanation_df = result_df[['Penjelasan']]
    explanation_df.index = range(1, len(explanation_df) + 1)
    st.table(explanation_df)

def display_association_rules(support_pairs_df, confidence_pairs_df, min_confidence, item_name_dict):
    result_df = support_pairs_df.merge(confidence_pairs_df, on='Item Pair', how='left')
    result_df = result_df.rename(columns={'Support': 'Support'})
    result_df['Item'] = result_df['Item Pair'].apply(lambda x: "{" + ", ".join(x.strip("{}").split(", ")) + "}")
    result_df = result_df.drop(columns=['Item Pair'])
    result_df = result_df[result_df['Confidence'] >= min_confidence]

    # Generate explanations
    result_df['Penjelasan'] = result_df.apply(generate_explanation, axis=1)

    # Tampilkan tabel aturan asosiasi
    st.write("Association Rules Yang Terbentuk")
    result_df.index = range(1, len(result_df) + 1)
    st.write(result_df[['Item', 'Support', 'Confidence']])

    # Tampilkan tabel penjelasan
    st.write("Penjelasan Association Rules yang Terbentuk")
    display_explanations(result_df)

    # Simpan hasil di session state untuk digunakan di laporan
    st.session_state['result_df'] = result_df

    # Buat direktori 'reports' jika belum ada
    if not os.path.exists("reports"):
        os.makedirs("reports")

    # Simpan hasil ke dalam file PDF
    pdf_file_path = os.path.join("reports", f"association_rules_{st.session_state.uploaded_filename}.pdf")
    create_pdf(result_df, pdf_file_path, st.session_state.uploaded_filename)

    # Tambahkan informasi laporan ke dalam session state
    if "reports" not in st.session_state:
        st.session_state.reports = []
    st.session_state.reports.append({
        "uploaded_filename": st.session_state.uploaded_filename,
        "min_support": st.session_state.min_support,
        "min_confidence": st.session_state.min_confidence,
        "pdf_filename": pdf_file_path,
        "timestamp": pd.Timestamp.now().isoformat()
    })

def main():
    st.subheader("Association Rules")

    # Pastikan data yang diperlukan ada di session state
    if 'support_pairs_df' in st.session_state and 'confidence_pairs_df' in st.session_state:
        support_pairs_df = st.session_state['support_pairs_df']
        confidence_pairs_df = st.session_state['confidence_pairs_df']
        min_confidence = st.session_state.get('min_confidence', 0.2)

        display_association_rules(support_pairs_df, confidence_pairs_df, min_confidence, item_name_dict)

if __name__ == '__main__':
    main()