
class FPNode:

    def __init__(self, product_id, freq, parent):
        self.product_id = product_id
        self.freq = freq
        self.parent = parent
        self.children = {}

    def increment(self, count):
        self.freq += count
    
    