import pandas as pd
from FPTree import *
import sys

def read_labels(filename):
    # Membaca file Excel
    df = pd.read_excel(filename, header=None)
    
    # Mengonversi DataFrame menjadi dictionary
    labels = dict(df[0].astype(int).zip(df.iloc[:, 1:].astype(str).agg(''.join, axis=1)))
    return labels

# Reads a file into a 2d list
def load_data(filename):
    # Membaca file Excel
    df = pd.read_excel(filename, header=None)
    
    # Mengonversi DataFrame menjadi daftar dua dimensi
    dataset = df.applymap(int).values.tolist()
    return dataset

# Main fpgrowth calculation algorithm
# It constructs and mines tree and returns a dictionary with frequent item list and counts
def fpgrowth(dataset, support):
    #sup = len(dataset) * support
    sup = support
    
    fptree = FPTree()
    tree, headerTable = fptree.ConstructTree(dataset, sup)

    if (tree == None):
        print("No frequent sets")
        return

    freqIt = fptree.MineTree(headerTable, sup)
    freqIt = dict((key, value) for key, value in freqIt.items() if len(key) > 1)
    return freqIt
