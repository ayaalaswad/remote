"""
Check if the entire checkpoint files are identical using file hash
"""
import hashlib
import os

def get_file_hash(filepath):
    """Calculate MD5 hash of file"""
    hash_md5 = hashlib.md5()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def get_file_size(filepath):
    """Get file size in bytes"""
    return os.path.getsize(filepath)

checkpoints = [
    ('Exp #1 Baseline', 'D:/experiments/exp1_baseline/p3_best.pt'),
    ('Exp #3 Full SHARP', 'D:/experiments/exp3_full_sharp/p3_best.pt'),
    ('Exp #4 v2a (Best R@1)', 'D:/experiments/exp4_v2a_matched_epochs/p3_best.pt')
]

print("="*80)
print("Checking if checkpoint FILES are identical (file hash comparison)")
print("="*80)

hashes = {}
sizes = {}

for name, path in checkpoints:
    print(f"\n{name}:")
    print(f"  Path: {path}")
    
    if not os.path.exists(path):
        print(f"  ❌ File not found!")
        continue
    
    file_size = get_file_size(path)
    file_hash = get_file_hash(path)
    
    hashes[name] = file_hash
    sizes[name] = file_size
    
    print(f"  Size: {file_size:,} bytes ({file_size / 1024 / 1024:.2f} MB)")
    print(f"  MD5 Hash: {file_hash}")

print(f"\n{'='*80}")
print("Comparison:")
print(f"{'='*80}")

if len(hashes) >= 2:
    names = list(hashes.keys())
    all_same = len(set(hashes.values())) == 1
    
    if all_same:
        print("\n*** FILES ARE COMPLETELY IDENTICAL! ***")
        print("All three checkpoint files have the same MD5 hash.")
        print("This means they are exact copies of each other.")
        print("\nPossible causes:")
        print("  1. Copy-paste error during checkpoint management")
        print("  2. All experiments saved to the same checkpoint file")
        print("  3. Symbolic links pointing to the same file")
    else:
        print("\n✓ Files are DIFFERENT")
        print("The checkpoint files are not identical.")
        print("The identical cls_token might be a coincidence or initialization artifact.")
        
        # Show which are same/different
        for i in range(len(names)):
            for j in range(i+1, len(names)):
                if hashes[names[i]] == hashes[names[j]]:
                    print(f"\n  {names[i]} == {names[j]}: SAME FILE")
                else:
                    print(f"\n  {names[i]} != {names[j]}: Different files")
