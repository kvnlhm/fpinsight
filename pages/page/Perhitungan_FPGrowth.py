import streamlit as st
import pandas as pd
import mysql.connector
from mysql.connector import Error
from collections import defaultdict
import graphviz

st.title("Proses Perhitungan")
st.markdown("---")

# Fungsi untuk koneksi ke database
def connect_to_db():
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='',
        database='obat'
    )

# Fungsi untuk mengambil kode item dari database
def get_item_code(cursor, Nama):
    try:
        query = "SELECT kode FROM kode_obat WHERE Nama = %s"
        cursor.execute(query, (Nama.strip(),))
        result = cursor.fetchone()
        cursor.fetchall()  # Mengambil semua hasil untuk memastikan tidak ada hasil yang tidak dibaca
        if result:
            return result[0]
        else:
            st.write(f"Item name '{Nama}' not found in the database.")
            return None
    except Error as e:
        st.error(f"Error fetching item code for '{Nama}': {e}")
        return None

def build_fp_tree(transactions):
    fp_tree = defaultdict(lambda: {'count': 0, 'parent': None, 'children': {}})
    for tid, group in transactions.groupby('TID'):
        transaction = list(group['Item'])
        current_node = fp_tree['root']
        for item in transaction:
            if item not in current_node['children']:
                current_node['children'][item] = {'count': 0, 'parent': current_node, 'children': {}}
            current_node['children'][item]['count'] += 1
            current_node = current_node['children'][item]
    return fp_tree

def draw_fp_tree(fp_tree):
    dot = graphviz.Digraph()
    dot.node('root', 'ROOT')

    def add_nodes(node, parent):
        for item, data in node['children'].items():
            node_name = f"{item} ({data['count']})"
            dot.node(node_name, node_name)
            dot.edge(parent, node_name)
            if data['children']:
                add_nodes(data, node_name)

    add_nodes(fp_tree['root'], 'root')
    dot.render('fp_tree', format='png')

def build_conditional_pattern_base(fp_tree, support_dict):
    patterns = defaultdict(list)
    
    def collect_paths(node, path):
        for item, data in node['children'].items():
            new_path = path + [item]
            patterns[item].append((new_path, data['count']))  # Save path along with its count
            collect_paths(data, new_path)

    collect_paths(fp_tree['root'], [])

    conditional_pattern_base = []
    for item, paths in patterns.items():
        filtered_paths = []
        path_counts = defaultdict(int)
        for path, count in paths:
            if path[-1] == item:
                filtered_paths.append((path[:-1], count))  # Exclude the item itself and keep the count
        for path, count in filtered_paths:
            path_counts[tuple(path)] += count
        
        # Only include non-empty paths
        if path_counts:
            formatted_paths = [f"{list(path)} ({path_count})" for path, path_count in path_counts.items() if path]
            if formatted_paths:  # Check if there are non-empty formatted paths
                conditional_pattern_base.append({
                    'Item': item,
                    'Support': support_dict[item],
                    'Conditional Pattern Base': ', '.join(formatted_paths),
                    'Path Counts': path_counts  # Save raw path counts for further processing
                })

    # Sort the conditional pattern base by the support value
    conditional_pattern_base.sort(key=lambda x: x['Support'])
    
    return conditional_pattern_base

def summarize_conditional_patterns(conditional_pattern_base, support_dict, min_support, unique_tid_count):
    summarized_data = []
    min_support_threshold = min_support * unique_tid_count  # Menghitung nilai ambang minimum baru

    for pattern in conditional_pattern_base:
        item_counts = defaultdict(int)
        for path, count in pattern['Path Counts'].items():
            for sub_item in path:
                item_counts[sub_item] += count

        # Filter item counts berdasarkan min_support_threshold dan count > 1
        filtered_item_counts = {item: count for item, count in item_counts.items() if count >= min_support_threshold and count > 1}

        if filtered_item_counts:
            summarized_data.append({
                'Item': pattern['Item'],
                'Conditional FP-Tree': filtered_item_counts
            })
    
    return summarized_data

def convert_to_frequent_itemset(summarized_patterns):
    frequent_itemsets = []
    for pattern in summarized_patterns:
        item = pattern['Item']
        item_counts = pattern['Conditional FP-Tree']
        frequent_itemset = []
        for other_item, count in item_counts.items():
            frequent_itemset.append(f'{{"{other_item}", "{item}":{count}}}')
        frequent_itemsets.append({
            'Item': item,
            'Frequent Itemset': ", ".join(frequent_itemset)
        })
    return frequent_itemsets

def calculate_support_for_item_pair(summarized_patterns, unique_tid_count):
    support_pairs = []
    for pattern in summarized_patterns:
        item = pattern['Item']
        filtered_item_counts = pattern['Conditional FP-Tree']
        for other_item, count in filtered_item_counts.items():
            if item != other_item:
                support = count / unique_tid_count
                support = round(support, 3)  # Bulatkan ke 2 angka desimal
                support_pairs.append({
                    'Item Pair': f'{{"{other_item}", "{item}"}}',
                    'Support': support
                })
    return support_pairs

def calculate_confidence(summarized_patterns, support_dict, min_confidence, frequency):
    confidence_pairs = []
    for pattern in summarized_patterns:
        item = pattern['Item']
        filtered_item_counts = pattern['Conditional FP-Tree']
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

# Fungsi untuk memulai proses konversi secara otomatis
def start_conversion(min_support, min_confidence):
    st.subheader("Transformasi Data")
    # Mendapatkan data yang telah diunggah dari file datatransaksi.py
    if 'data' not in st.session_state:
        st.session_state.data = None

    df = st.session_state.data

    if df is None:
        st.error("Data belum diunggah. Silakan unggah file terlebih dahulu.")
        return
    
    # Membuat salinan DataFrame
    df_copy = df.copy()

    # Koneksi ke database
    conn = connect_to_db()
    if conn:
        try:
            cursor = conn.cursor()

            # Ambil kode untuk setiap item dalam DataFrame
            df_copy['Kode'] = df_copy['Nama'].apply(lambda x: get_item_code(cursor, x))

            cursor.close()
            conn.close()
        except Error as e:
            st.error(f"Database error: {e}")
            if cursor:
                cursor.close()
            if conn:
                conn.close()
            return

        # Debug: Print the resulting dataframe
        st.write(df_copy)
        st.markdown("---")

        # Mencari Frekuensi Kemunculan Masing Masing Item
        # Hitung frekuensi kemunculan untuk masing-masing kode
        frequency = df_copy['Kode'].value_counts().reset_index()
        frequency.columns = ['Kode', 'Frekuensi']

        # Tambahkan kolom 'Nama Item' ke dalam DataFrame frekuensi
        frequency['Nama Item'] = frequency['Kode'].map(df_copy.drop_duplicates('Kode').set_index('Kode')['Nama'])

        # Atur ulang urutan kolom
        frequency = frequency[['Kode', 'Nama Item', 'Frekuensi']]

        st.subheader("Menghitung Frekuensi Kemunculan")
        frequency.index = frequency.index + 1
        st.write(frequency)
        st.markdown("---")

        # Menghitung Nilai Support Masing Masing Item
        # Menghitung jumlah TID unik
        unique_tid_count = df_copy['TID'].nunique()

        # Mengganti pembagi dengan jumlah TID unik
        frequency['Support'] = frequency['Frekuensi'] / unique_tid_count

        # Atur ulang urutan kolom
        support = frequency[['Kode', 'Frekuensi', 'Support']]

        st.subheader("Menentukan Nilai Support Untuk Masing Masing Item")
        st.write("Perhitungan Nilai Support")
        st.write(support)

        # Membuat kamus support
        support_dict = support.set_index('Kode')['Support'].to_dict()

        # Menyeleksi Nilai Support
        # Filter berdasarkan minimum support
        filtered_frequency = frequency[frequency['Support'] >= min_support]

        # Atur ulang urutan kolom
        filtered_frequency = filtered_frequency[['Kode', 'Frekuensi', 'Support']]
        filtered_frequency.index = range(1, len(filtered_frequency) + 1)

        st.write('Hasil Seleksi Nilai Support')
        st.write(filtered_frequency)
        st.markdown("---")

        # Pembangkitan Itemset
        st.subheader("Pembangkitan Itemset")
        sort = df_copy[['TID', 'Kode']]
        merged_df = pd.merge(sort, filtered_frequency, on='Kode')

        # Membuat kolom baru yang berisi bagian numerik dari TID untuk pengurutan yang benar
        merged_df['TID_num'] = merged_df['TID'].str.extract('(\d+)').astype(int)

        # Mengurutkan berdasarkan TID_num dan kemudian Support
        sorted_df = merged_df.sort_values(by=['TID_num', 'Support'], ascending=[True, False])

        # Menghapus kolom sementara TID_num setelah pengurutan
        sorted_df = sorted_df.drop(columns=['TID_num'])

        # Mengatur ulang indeks dan menambah 1 agar indeks dimulai dari 1
        sorted_df = sorted_df.reset_index(drop=True)
        sorted_df.index = sorted_df.index + 1

        # Mengganti nama kolom Kode menjadi Item
        sorted_df = sorted_df.rename(columns={'Kode': 'Item'})
        st.write(sorted_df[['TID', 'Item', 'Support']])
        st.markdown("---")

        fp_tree = build_fp_tree(sorted_df)
        draw_fp_tree(fp_tree)
        st.subheader("Pembentukan FP-Tree")
        st.image('fp_tree.png')
        st.markdown("---")

        st.subheader("Conditional Pattern Base")
        conditional_pattern_base = build_conditional_pattern_base(fp_tree, support_dict)
        conditional_pattern_base_df = pd.DataFrame(conditional_pattern_base)
        conditional_pattern_base_df.index = range(1, len(conditional_pattern_base_df) + 1)
        st.table(conditional_pattern_base_df[['Item', 'Conditional Pattern Base']])
        st.markdown("---")

        st.subheader("Conditional FP Tree")
        summarized_patterns = summarize_conditional_patterns(conditional_pattern_base, support_dict, min_support, unique_tid_count)
        summarized_patterns_df = pd.DataFrame(summarized_patterns)
        summarized_patterns_df.index = range(1, len(summarized_patterns_df) + 1)
        st.write(summarized_patterns_df)
        st.markdown("---")

        st.subheader("Frequent Itemset")
        frequent_itemsets = convert_to_frequent_itemset(summarized_patterns)
        frequent_itemsets_df = pd.DataFrame(frequent_itemsets)
        frequent_itemsets_df.index = range(1, len(frequent_itemsets_df) + 1)
        st.table(frequent_itemsets_df)
        st.markdown("---")

        st.subheader("Menghitung Nilai Support & Nilai Confidence Dua Item")
        st.write("Perhitungan Nilai Support Dua Item")
        support_pairs = calculate_support_for_item_pair(summarized_patterns, unique_tid_count)
        support_pairs_df = pd.DataFrame(support_pairs)
        support_pairs_df.index = range(1, len(support_pairs_df) + 1)
        st.write(support_pairs_df)
        st.markdown("")
        st.markdown("")

        st.write("Perhitungan Nilai Confidence Dua Item")
        confidence_pairs = calculate_confidence(summarized_patterns, support_dict, min_confidence, frequency)
        confidence_pairs_df = pd.DataFrame(confidence_pairs)
        confidence_pairs_df.index = range(1, len(confidence_pairs_df) + 1)
        st.write(confidence_pairs_df)
        st.markdown("---")

        st.subheader("Hasil Aturan Asosiasi")
        # Gabungkan dua DataFrame support_pairs_df dan confidence_pairs_df
        result_df = support_pairs_df.merge(confidence_pairs_df, on='Item Pair', how='left')
        # Ganti nama kolom 'Support' menjadi 'Support Dua Item'
        result_df = result_df.rename(columns={'Support': 'Support'})
        # Buat kolom 'Item' dengan format {"R5", "E7"}
        result_df['Item'] = result_df['Item Pair'].apply(lambda x: "{" + ", ".join(x.strip("{}").split(", ")) + "}")
        # Hapus kolom 'Item Pair'
        result_df = result_df.drop(columns=['Item Pair'])
        # Atur urutan kolom
        result_df = result_df[['Item', 'Support', 'Confidence']]
        # Tampilkan hasil dalam bentuk tabel
        result_df.index = range(1, len(result_df) + 1)
        st.write(result_df)
        st.markdown("---")

        # Simpan hasil ke dalam session state untuk digunakan di file lain
        st.session_state['support_pairs_df'] = support_pairs_df
        st.session_state['confidence_pairs_df'] = confidence_pairs_df

# Fungsi utama untuk menjalankan aplikasi
def main():
    min_support = st.session_state.get('min_support', 0.2)
    min_support = st.number_input('Masukkan Minimum Support', min_value=0.0, max_value=1.0, value=min_support, step=0.001, format="%.3f")
    st.session_state.min_support = min_support

    min_confidence = st.session_state.get('min_confidence', 0.2)
    min_confidence = st.number_input('Masukkan Minimum Confidence', min_value=0.0, max_value=1.0, value=min_confidence, step=0.001, format="%.3f")
    st.session_state.min_confidence = min_confidence

    start_conversion(min_support, min_confidence)

if __name__ == "__main__":
    main()
