import csv
import time
import random
from b_tree import BTree
from bplus_tree import BPlusTree

def load_data(filename="student.csv"):
    # Load records and keys into memory
    records, keys = [], []
    with open(filename, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader) # Skip header
        for row in reader:
            student_id = int(row[0])
            keys.append(student_id)
            records.append({
                'id': student_id,
                'name': row[1],
                'gender': row[2],
                'gpa': float(row[3]),
                'height': float(row[4])
            })
    return records, keys

def test_insertion(keys, degree, tree_type="BTree"):
    # Initialize tree
    tree = BTree(degree) if tree_type == "BTree" else BPlusTree(degree)
    
    # Measure insertion time
    start_time = time.time()
    for rid, key in enumerate(keys):
        tree.insert(key, rid)
    exec_time = time.time() - start_time
    
    print(f"[{tree_type} d={degree:2d}] Insert: {exec_time:.4f}s | Splits: {tree.split_count}")
    return tree

def test_search(tree, sample_keys, tree_type):
    # Measure point search time
    start_time = time.time()
    for key in sample_keys:
        tree.search(key)
    exec_time = time.time() - start_time
    
    mean_time = exec_time / len(sample_keys)
    print(f"[{tree_type}] Search(10k): {exec_time:.4f}s | Mean: {mean_time:.8f}s")

def test_range_query(tree, records, tree_type, start_key=202000000, end_key=202100000):
    # Measure range query time
    start_time = time.time()
    result_rids = tree.range_query(start_key, end_key)
    
    # Calculate stats for target condition (Male)
    count, total_gpa = 0, 0
    for rid in result_rids:
        if records[rid]['gender'].lower() == 'male':
            total_gpa += records[rid]['gpa']
            count += 1
            
    exec_time = time.time() - start_time
    avg_gpa = total_gpa / count if count > 0 else 0
    print(f"[{tree_type}] Range Query: {exec_time:.4f}s | Found: {count} | Avg GPA: {avg_gpa:.2f}")

if __name__ == "__main__":
    records, all_keys = load_data("student.csv")
    print(f"--- Loaded {len(records)} records ---\n")
    
    print("=== [Test 1] Insertion & Parameter Tuning ===")
    b_tree_3 = test_insertion(all_keys, 3, "BTree")
    b_tree_5 = test_insertion(all_keys, 5, "BTree")
    b_tree_10 = test_insertion(all_keys, 10, "BTree")
    bp_tree_3 = test_insertion(all_keys, 3, "BPlusTree")
    bp_tree_5 = test_insertion(all_keys, 5, "BPlusTree")
    bp_tree_10 = test_insertion(all_keys, 10, "BPlusTree")
    print()
    
    print("=== [Test 2] Point Search (10,000 keys) ===")
    sample_keys = random.sample(all_keys, 10000)
    test_search(b_tree_10, sample_keys, "BTree d=10")
    test_search(bp_tree_10, sample_keys, "BPlusTree d=10")
    print()
    
    print("=== [Test 3] Range Query Comparison ===")
    # Compare range query performance between BTree and BPlusTree
    test_range_query(b_tree_10, records, "BTree d=10")
    test_range_query(bp_tree_10, records, "BPlusTree d=10")
    print()
    
    print("=== [Test 4] Deletion Comparison ===")
    # Compare deletion performance (2000 random keys)
    delete_keys = random.sample(all_keys, 2000)
    
    # BTree Deletion
    start_del_btree = time.time()
    for k in delete_keys:
        b_tree_10.delete(k)
    print(f"[BTree d=10] Delete(2k): {time.time() - start_del_btree:.4f}s")
    
    # BPlusTree Deletion
    start_del_bplus = time.time()
    for k in delete_keys:
        bp_tree_10.delete(k)
    print(f"[BPlusTree d=10] Delete(2k): {time.time() - start_del_bplus:.4f}s")