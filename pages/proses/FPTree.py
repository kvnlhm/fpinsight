from io import DEFAULT_BUFFER_SIZE
from pages.proses.FPNode import *

class FPTree:
    def __init__(self):
        self.freqItems = {}
    
    # - Creates header table according to given dataset
    # - Dataset should be 2D list
    def CreateHeaderTable(self, dataset, freq):
        headerTable = {}

        for i, trans in enumerate(dataset):
            for product in trans:
                if product in headerTable:
                    headerTable[product][0] += freq[i]
                else:
                    headerTable[product] = [freq[i], []]
        return headerTable

    # - Constructs FP-Tree or Conditional FP-Tree. 
    #   To construct conditional FP-Tree, a frequency list must be provided.
    #   otherwise, custom frequency '1' will be used. 
    # - HeaderTable = Product Name: [Freq, [Node List]] 
    def ConstructTree(self, dataset, support, freq=None):
        if (freq == None):
            freq = [1 for i in range(len(dataset))]
        
        # Create the header table
        headerTable = self.CreateHeaderTable(dataset, freq)

        # Delete the items below support
        headerTable = dict((item, sup) for item, sup in headerTable.items() if sup[0] >= support)

        if (len(headerTable) == 0):
            return None, None

        #print(headerTable)

        # Create test file
        #self.print_dict("test.txt" , headerTable)

        # Sorted transactions
        st = self.SortTransactions(dataset, headerTable)
        #print(st)

        #self.test_transactions(st, headerTable)

        tree, ht = self.BuildTree(st, headerTable, freq)

        return tree, ht
    
    # - Constructs FP-Tree or Conditional FP-Tree according to transactions list.
    #   To construct conditional FP-Tree, a frequency list must be provided. 
    def BuildTree(self, transactions, headerTable, freq):
        # Create Tree        
        tree = FPNode(None, None, None)

        for i, trans in enumerate(transactions):
            currentNode = tree
            
            for product in trans:
                if product in currentNode.children:
                    currentNode.children[product].increment(freq[i])
                
                else:
                    newNode = FPNode(product, freq[i], currentNode)
                    currentNode.children[product] = newNode
                    
                    headerTable[product][1].append(newNode)

                currentNode = currentNode.children[product]
        
        return tree, headerTable
    
    def MineTree(self, headerTable, support):
        freqItemList = {}
        self.MineTreeRec(headerTable, support, list(), freqItemList)

        return freqItemList

    def MineTreeRec(self, headerTable, support, pre, freqItemList):
        sortedProductList = [item[0] for item in sorted(list(headerTable.items()), key=lambda p:p[1][0])] 

        # (ItemName, [Freq, [Node_List]])
        for ItemName in sortedProductList:
            newFreq = pre.copy()
            newFreq.append(ItemName)

            # Adds count to the table
            # Key = List, Value = Count
            hashableFreq = tuple(newFreq)
            if ((hashableFreq not in freqItemList) or (freqItemList[hashableFreq] > headerTable[ItemName][0])):
                freqItemList[hashableFreq] = headerTable[ItemName][0]

            nodes = headerTable[ItemName][1]

            # Create conditional pattern base
            condBase, freq = self.CondPatternBase(nodes)

            # Create conditional fp-tree
            tree, newHeader = self.ConstructTree(condBase, support, freq)
            
            if newHeader != None:
                self.MineTreeRec(newHeader, support, newFreq, freqItemList)

    # Creates conditional pattern base lists.
    # For each node, finds the path to node's root.
    def CondPatternBase(self, nodes):
        condBase = []
        freq = []

        for n in nodes:
            path = []
            self.ascendTree(n, path)

            if (len(path) > 1):
                condBase.append(path[1:])
                freq.append(n.freq)
        
        return condBase, freq

    # Finds the path from a node to it's root
    def ascendTree(self, node, path):
        if node.parent != None:
            path.append(node.product_id)
            self.ascendTree(node.parent, path)

    # Sorts transactions according to frequencies (Freq) in the header table
    # - HeaderTable = Product Name: [Freq, [Node List]] 
    def SortTransactions(self, dataset, headerTable):
        sheaderTable = [item[0] for item in sorted(list(headerTable.items()), key=lambda p:p[1][0], reverse=True)] 

        newList = []
        for i in range(len(dataset)):
            newTrans = [x for a in sheaderTable for x in dataset[i] if x == a]
            newList.append(newTrans) if len(newTrans) > 0 else None
            
        return newList


    ### Test Functions ###

    def print_dict(self, filename, dct):
        with open(filename, 'w') as f:
            for item in dct.items():
                f.write(str(item[0]) + ": " + str(item[1]) + "\n")
            
    def test_transactions(self, transactions, header_dict):
        for t in transactions:
            print(str(t))
            for x in t:
                print(str(x) + ": " + str(header_dict[x]))
            
            print("")