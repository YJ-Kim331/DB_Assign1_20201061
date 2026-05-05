class BTreeNode:
    def __init__(self, leaf=False):
        self.leaf = leaf
        self.keys = []
        self.rids = []
        self.children = []

class BTree:
    def __init__(self, degree):
        self.degree = degree
        self.root = BTreeNode(leaf=True)
        self.split_count = 0

    def search(self, key):
        curr = self.root
        while True:
            i = 0
            while i < len(curr.keys) and key > curr.keys[i]:
                i += 1
            
            if i < len(curr.keys) and curr.keys[i] == key:
                return curr.rids[i]
            
            if curr.leaf:
                return None
            curr = curr.children[i]

    def insert(self, key, rid):
        root = self.root
        # Split root if full
        if len(root.keys) == self.degree - 1:
            new_root = BTreeNode(leaf=False)
            new_root.children.append(self.root)
            self.root = new_root
            self.split_child(new_root, 0)
            self.insert_non_full(new_root, key, rid)
        else:
            self.insert_non_full(root, key, rid)

    def split_child(self, parent, i):
        self.split_count += 1
        full_child = parent.children[i]
        new_node = BTreeNode(leaf=full_child.leaf)
        mid = (self.degree - 1) // 2
        
        # Split keys and rids to sibling
        new_node.keys = full_child.keys[mid + 1:]
        new_node.rids = full_child.rids[mid + 1:]
        
        if not full_child.leaf:
            new_node.children = full_child.children[mid + 1:]
            full_child.children = full_child.children[:mid + 1]
            
        # Push mid key up to parent
        parent.keys.insert(i, full_child.keys[mid])
        parent.rids.insert(i, full_child.rids[mid])
        parent.children.insert(i + 1, new_node)
        
        full_child.keys = full_child.keys[:mid]
        full_child.rids = full_child.rids[:mid]

    def insert_non_full(self, node, key, rid):
        while not node.leaf:
            i = len(node.keys) - 1
            while i >= 0 and key < node.keys[i]:
                i -= 1
            i += 1
            
            # Split child proactively before moving down
            if len(node.children[i].keys) == self.degree - 1:
                self.split_child(node, i)
                if key > node.keys[i]:
                    i += 1
            node = node.children[i]
            
        # Insert into leaf node
        i = len(node.keys) - 1
        node.keys.append(None)
        node.rids.append(None)
        
        while i >= 0 and key < node.keys[i]:
            node.keys[i + 1] = node.keys[i]
            node.rids[i + 1] = node.rids[i]
            i -= 1
            
        node.keys[i + 1] = key
        node.rids[i + 1] = rid

    def range_query(self, min_key, max_key):
        result = []
        self._range_search(self.root, min_key, max_key, result)
        return result

    def _range_search(self, node, min_key, max_key, result):
        if node is None:
            return
        
        i = 0
        while i < len(node.keys):
            # Traverse left child if it might contain keys in range
            if node.children and min_key < node.keys[i]:
                self._range_search(node.children[i], min_key, max_key, result)
            
            # Append RID if the current key is within the range
            if min_key <= node.keys[i] <= max_key:
                result.append(node.rids[i])
            
            i += 1
        
        # Traverse the rightmost child if max_key exceeds the last key
        if node.children and max_key >= node.keys[-1]:
            self._range_search(node.children[-1], min_key, max_key, result)

    def delete(self, key):
        # TODO: Advanced structural merge/borrow handling is omitted.
        pass