class BPlusNode:
    def __init__(self, leaf=False):
        self.leaf = leaf
        self.keys = []
        self.rids = []        # Leaf only
        self.children = []    # Internal only
        self.next_leaf = None # Leaf linked list

class BPlusTree:
    def __init__(self, degree):
        self.degree = degree
        self.root = BPlusNode(leaf=True)
        self.split_count = 0

    def search(self, key):
        curr = self.root
        # Always traverse to leaf
        while not curr.leaf:
            i = 0
            while i < len(curr.keys) and key >= curr.keys[i]:
                i += 1
            curr = curr.children[i]
            
        for i in range(len(curr.keys)):
            if curr.keys[i] == key:
                return curr.rids[i]
        return None

    def insert(self, key, rid):
        if len(self.root.keys) == self.degree - 1:
            new_root = BPlusNode(leaf=False)
            new_root.children.append(self.root)
            self.root = new_root
            self.split_child(new_root, 0)
            self.insert_non_full(new_root, key, rid)
        else:
            self.insert_non_full(self.root, key, rid)

    def split_child(self, parent, i):
        self.split_count += 1
        full_child = parent.children[i]
        new_node = BPlusNode(leaf=full_child.leaf)
        mid = (self.degree - 1) // 2
        
        if full_child.leaf:
            # Leaf split: copy mid key up
            new_node.keys = full_child.keys[mid:]
            new_node.rids = full_child.rids[mid:]
            full_child.keys = full_child.keys[:mid]
            full_child.rids = full_child.rids[:mid]
            
            new_node.next_leaf = full_child.next_leaf
            full_child.next_leaf = new_node
            
            parent.keys.insert(i, new_node.keys[0])
            parent.children.insert(i + 1, new_node)
        else:
            # Internal split: push mid key up
            new_node.keys = full_child.keys[mid + 1:]
            new_node.children = full_child.children[mid + 1:]
            
            up_key = full_child.keys[mid]
            full_child.keys = full_child.keys[:mid]
            full_child.children = full_child.children[:mid + 1]
            
            parent.keys.insert(i, up_key)
            parent.children.insert(i + 1, new_node)

    def insert_non_full(self, node, key, rid):
        while not node.leaf:
            i = len(node.keys) - 1
            while i >= 0 and key < node.keys[i]:
                i -= 1
            i += 1
            
            if len(node.children[i].keys) == self.degree - 1:
                self.split_child(node, i)
                if key >= node.keys[i]:
                    i += 1
            node = node.children[i]
            
        # Insert into leaf
        i = len(node.keys) - 1
        node.keys.append(None)
        node.rids.append(None)
        
        while i >= 0 and key < node.keys[i]:
            node.keys[i + 1] = node.keys[i]
            node.rids[i + 1] = node.rids[i]
            i -= 1
            
        node.keys[i + 1] = key
        node.rids[i + 1] = rid

    def range_query(self, start_key, end_key):
        curr = self.root
        while not curr.leaf:
            i = 0
            while i < len(curr.keys) and start_key >= curr.keys[i]:
                i += 1
            curr = curr.children[i]
            
        result_rids = []
        while curr is not None:
            for i in range(len(curr.keys)):
                if start_key <= curr.keys[i] <= end_key:
                    result_rids.append(curr.rids[i])
                elif curr.keys[i] > end_key:
                    return result_rids
            curr = curr.next_leaf
        return result_rids
    
    def delete(self, key):
        if self.root is None:
            return
        
        # Top-down traversal to find the target leaf node
        curr = self.root
        while curr.children:
            i = 0
            # Follow routing keys to the appropriate child
            while i < len(curr.keys) and key >= curr.keys[i]:
                i += 1
            curr = curr.children[i]
        
        # Delete key and RID from the leaf (Lazy deletion, no underflow handling)
        if key in curr.keys:
            idx = curr.keys.index(key)
            curr.keys.pop(idx)
            curr.rids.pop(idx)