#!/usr/bin/env python3
"""
SQEF Test Files Checksum Generator
Generates SHA256 checksums for all .bin files in directory tree
Outputs to console, CSV, JSON, and Markdown formats
"""

import os
import sys
import json
import csv
import hashlib
from pathlib import Path
from datetime import datetime
import argparse

def calculate_sha256(filepath):
    """Calculate SHA256 hash of a file"""
    sha256_hash = hashlib.sha256()
    try:
        with open(filepath, "rb") as f:
            # Read in chunks for large files
            for chunk in iter(lambda: f.read(4096), b""):
                sha256_hash.update(chunk)
        return sha256_hash.hexdigest().upper()
    except Exception as e:
        print(f"Error hashing {filepath}: {e}")
        return None

def format_bytes(bytes_size):
    """Convert bytes to human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.2f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.2f} PB"

def scan_for_bin_files(root_path):
    """Recursively find all .bin files"""
    bin_files = []
    root = Path(root_path)
    
    print(f"Scanning for .bin files in: {root}")
    
    for file_path in root.rglob("*.bin"):
        if file_path.is_file():
            bin_files.append(file_path)
    
    return bin_files

def generate_checksums(root_path, output_format="both"):
    """Main function to generate checksums"""
    
    print("=" * 60)
    print("SQEF Test Files Checksum Generator")
    print("=" * 60)
    print(f"Root Path: {root_path}")
    print(f"Hash Algorithm: SHA256")
    print()
    
    # Check if path exists
    if not os.path.exists(root_path):
        print(f"Error: Path does not exist: {root_path}")
        return 1
    
    # Find all .bin files
    print("Scanning for .bin files...")
    bin_files = scan_for_bin_files(root_path)
    
    if not bin_files:
        print("No .bin files found!")
        return 0
    
    print(f"Found {len(bin_files)} binary files\n")
    
    # Process each file
    results = []
    total_size = 0
    root = Path(root_path)
    
    for i, file_path in enumerate(bin_files, 1):
        print(f"Processing [{i}/{len(bin_files)}]: {file_path.name}")
        
        # Calculate hash
        sha256 = calculate_sha256(file_path)
        if not sha256:
            continue
        
        # Get file info
        file_size = file_path.stat().st_size
        total_size += file_size
        
        # Get relative path
        try:
            relative_path = file_path.relative_to(root)
        except ValueError:
            relative_path = file_path
        
        # Create result entry
        result = {
            'filename': file_path.name,
            'relative_path': str(relative_path).replace('\\', '/'),
            'full_path': str(file_path),
            'size_bytes': file_size,
            'size_mb': round(file_size / (1024 * 1024), 3),
            'size_human': format_bytes(file_size),
            'sha256': sha256,
            'last_modified': datetime.fromtimestamp(file_path.stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S')
        }
        
        results.append(result)
        
        # Console output
        print(f"  ✓ SHA256: {sha256}")
        print(f"    Size: {result['size_human']}")
        print()
    
    # Summary
    print("=" * 60)
    print("Summary")
    print("=" * 60)
    print(f"Total Files: {len(results)}")
    print(f"Total Size: {format_bytes(total_size)}")
    print()
    
    # Group by directory
    dir_groups = {}
    for result in results:
        dir_name = os.path.dirname(result['relative_path']) or "root"
        if dir_name not in dir_groups:
            dir_groups[dir_name] = 0
        dir_groups[dir_name] += 1
    
    print("Files by Directory:")
    for dir_name in sorted(dir_groups.keys()):
        print(f"  {dir_name}: {dir_groups[dir_name]} files")
    print()
    
    # Generate timestamp for output files
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Export to CSV
    if output_format in ["csv", "both"]:
        csv_path = os.path.join(root_path, f"sqef_checksums_{timestamp}.csv")
        try:
            with open(csv_path, 'w', newline='', encoding='utf-8') as f:
                if results:
                    writer = csv.DictWriter(f, fieldnames=results[0].keys())
                    writer.writeheader()
                    writer.writerows(results)
            print(f"✓ CSV output saved to: {csv_path}")
        except Exception as e:
            print(f"Warning: Failed to save CSV: {e}")
    
    # Export to JSON
    if output_format in ["json", "both"]:
        json_path = os.path.join(root_path, f"sqef_checksums_{timestamp}.json")
        try:
            json_data = {
                'generated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'algorithm': 'SHA256',
                'root_path': str(root_path),
                'total_files': len(results),
                'total_size_gb': round(total_size / (1024**3), 3),
                'files': results
            }
            
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, indent=2)
            print(f"✓ JSON output saved to: {json_path}")
        except Exception as e:
            print(f"Warning: Failed to save JSON: {e}")
    
    # Create Markdown summary
    md_path = os.path.join(root_path, "CHECKSUMS.md")
    try:
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write("# SQEF Test Files Checksums\n\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Algorithm: SHA256\n")
            f.write(f"Total Files: {len(results)}\n")
            f.write(f"Total Size: {format_bytes(total_size)}\n\n")
            
            f.write("## File Checksums\n\n")
            f.write("| File | Size | SHA256 |\n")
            f.write("|------|------|--------|\n")
            
            for result in sorted(results, key=lambda x: x['relative_path']):
                f.write(f"| `{result['relative_path']}` | {result['size_human']} | `{result['sha256']}` |\n")
            
            f.write("\n## Verification\n\n")
            f.write("### Windows PowerShell:\n")
            f.write("```powershell\n")
            f.write('Get-FileHash -Path "filename.bin" -Algorithm SHA256\n')
            f.write("```\n\n")
            f.write("### Windows Command Prompt:\n")
            f.write("```cmd\n")
            f.write('certutil -hashfile "filename.bin" SHA256\n')
            f.write("```\n\n")
            f.write("### Linux/Mac:\n")
            f.write("```bash\n")
            f.write('sha256sum filename.bin\n')
            f.write("```\n\n")
            f.write("### Python:\n")
            f.write("```python\n")
            f.write('import hashlib\n')
            f.write('with open("filename.bin", "rb") as f:\n')
            f.write('    print(hashlib.sha256(f.read()).hexdigest())\n')
            f.write("```\n")
        
        print(f"✓ Markdown summary saved to: {md_path}")
    except Exception as e:
        print(f"Warning: Failed to save Markdown: {e}")
    
    return 0

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Generate SHA256 checksums for SQEF test binary files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                           # Process current directory
  %(prog)s C:\\GitHub\\Luminareware-SQEF-NIST-Evaluation\\sample-outpus\\            # Process specific directory
  %(prog)s --format json            # Output JSON only
  %(prog)s --format csv             # Output CSV only
  %(prog)s . --recursive            # Process recursively (default)
        """
    )
    
    parser.add_argument('path', nargs='?', default=os.getcwd(),
                       help='Root directory containing test files (default: current directory)')
    parser.add_argument('--format', choices=['csv', 'json', 'both'],
                       default='both', help='Output format (default: both)')
    parser.add_argument('--no-recursive', action='store_true',
                       help='Do not scan subdirectories')
    
    args = parser.parse_args()
    
    # Convert path to absolute
    root_path = os.path.abspath(args.path)
    
    # Run checksum generation
    return generate_checksums(root_path, args.format)

if __name__ == '__main__':
    sys.exit(main())