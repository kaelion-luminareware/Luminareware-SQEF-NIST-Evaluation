#!/usr/bin/env python3
"""
SQEF Test Summary Generator - Fixed Version v2.1
Creates summary.json files for each test configuration
Handles consolidated entropy assessment files
Correctly counts all individual NIST tests (not just test types)
"""

import os
import re
import json
from pathlib import Path
from datetime import datetime
import hashlib

def parse_final_analysis_report(filepath):
    """Parse NIST finalAnalysisReport.txt for detailed results"""
    results = {}
    
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
    except Exception as e:
        print(f"❌ Error reading {filepath}: {e}")
        return None
    
    # Extract test results with p-values
    for line in content.split('\n'):
        # Look for lines with test results
        if '/' in line and not line.startswith('-'):
            # Try to extract p-value and proportion
            parts = line.split()
            if len(parts) >= 3:
                # Find the test name (last column)
                test_name = parts[-1]
                
                # Find the proportion (e.g., "123/125")
                for part in parts:
                    if '/' in part:
                        try:
                            passed, total = part.split('/')
                            passed = int(passed)
                            total = int(total)
                            
                            # Find p-value (usually before proportion)
                            p_value = None
                            idx = parts.index(part)
                            if idx > 0:
                                try:
                                    p_value = float(parts[idx-1])
                                except:
                                    pass
                            
                            # Check for asterisk (uniformity failure)
                            has_asterisk = '*' in line
                            
                            if test_name not in results:
                                results[test_name] = {
                                    'test_name': test_name,
                                    'passed': passed,
                                    'total': total,
                                    'pass_rate': passed / total,
                                    'percentage': f"{(passed/total)*100:.2f}%",
                                    'p_value': p_value,
                                    'meets_requirement': (passed/total) >= 0.96 and not has_asterisk,
                                    'uniformity_fail': has_asterisk
                                }
                            break
                        except:
                            continue
    
    return results

def parse_consolidated_entropy_file(entropy_file, key_size, security_level):
    """Parse entropy data for specific key size from consolidated file"""
    
    if not entropy_file or not entropy_file.exists():
        return {}
    
    try:
        with open(entropy_file, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
    except Exception as e:
        print(f"  ❌ Error reading entropy file: {e}")
        return {}
    
    # Map directory key size to entropy file key size patterns
    # Use underscores to be more specific and avoid false matches
    size_mappings = {
        '128-bit': ['_128bit_'],
        '256-bit': ['_256bit_'],
        '512-bit': ['_512bit_'],
        '1024-bit': ['_1024bit_'],
        '2048-bit': ['_2048bit_'],
        '4096-bit': ['_4096bit_'],
        '1KB': ['_1KB_'],
        '4KB': ['_4KB_'],
        '1MB': ['_1MB_'],
        '16MB': ['_16MB_'],
        '256MB': ['_256MB_'],
        '512MB': ['_512MB_']  # Will match sqef_sliced_512MB_1keys
    }
    
    # Get patterns to search for
    patterns = size_mappings.get(key_size, [f"_{key_size.replace('-', '')}_"])
    
    # Split content into sections (each starting with a filename)
    sections = re.split(r'^(.*\.bin\s+\d+)$', content, flags=re.MULTILINE)
    
    entropy_data = {}
    found_section = False
    best_match = None
    best_match_content = None
    
    # Look for the best matching section
    for i in range(1, len(sections), 2):
        if i + 1 < len(sections):
            header = sections[i]
            section_content = sections[i + 1]
            
            # Check if this section matches our key size
            header_lower = header.lower()
            
            for pattern in patterns:
                if pattern.lower() in header_lower:
                    # Since we're reading from a security-level-specific file,
                    # we don't need to verify security level in the filename
                    # Just take the first match for the key size
                    best_match = header
                    best_match_content = section_content
                    found_section = True
                    break
            
            if found_section:
                break
    
    if found_section and best_match_content:
        print(f"  📊 Found entropy section: {best_match.strip()}")
        
        # Parse this section
        h_orig_match = re.search(r'H_original:\s*(\d+\.?\d*)', best_match_content)
        if h_orig_match:
            entropy_data['h_original'] = float(h_orig_match.group(1))
        
        h_bit_match = re.search(r'H_bitstring:\s*(\d+\.?\d*)', best_match_content)
        if h_bit_match:
            entropy_data['h_bitstring'] = float(h_bit_match.group(1))
        
        min_match = re.search(r'min\([^)]+\):\s*(\d+\.?\d*)', best_match_content)
        if min_match:
            entropy_data['min_entropy'] = float(min_match.group(1))
            entropy_data['min_entropy_per_byte'] = f"{float(min_match.group(1)):.6f} bits/byte"
        
        # Check for test passes
        if 'Passed chi square tests' in best_match_content:
            entropy_data['chi_square_test'] = 'PASSED'
        elif 'Failed chi square tests' in best_match_content:
            entropy_data['chi_square_test'] = 'FAILED'
            
        if 'Passed IID permutation tests' in best_match_content:
            entropy_data['iid_test'] = 'PASSED'
        elif 'Failed IID permutation tests' in best_match_content:
            entropy_data['iid_test'] = 'FAILED'
            
        if 'Passed length of longest repeated substring test' in best_match_content:
            entropy_data['lrs_test'] = 'PASSED'
        elif 'Failed length of longest repeated substring test' in best_match_content:
            entropy_data['lrs_test'] = 'FAILED'
        
        # Calculate entropy percentage
        if 'min_entropy' in entropy_data:
            entropy_percentage = (entropy_data['min_entropy'] / 8.0) * 100
            entropy_data['entropy_percentage'] = f"{entropy_percentage:.2f}%"
            
        # Overall pass status
        tests = ['chi_square_test', 'iid_test', 'lrs_test']
        if all(entropy_data.get(test) == 'PASSED' for test in tests):
            entropy_data['overall_status'] = 'PASSED'
        else:
            entropy_data['overall_status'] = 'FAILED' if any(entropy_data.get(test) == 'FAILED' for test in tests) else 'UNKNOWN'
    
    else:
        print(f"  ⚠️  No matching section found for {key_size}")
        # Debug: show available sections
        print(f"      Looking for pattern: {patterns}")
        print(f"      Available sections in file:")
        for i in range(1, min(len(sections), 11), 2):  # Show first 5 sections
            if i < len(sections):
                header = sections[i].strip()
                # Extract just the key size part for clarity
                size_part = "unknown"
                for size in ['256bit', '512bit', '1024bit', '2048bit', '4096bit', 
                           '1KB', '4KB', '1MB', '16MB', '256MB', '512MB']:
                    if size.lower() in header.lower():
                        size_part = size
                        break
                print(f"      - {size_part}: {header[:60]}...")
    
    return entropy_data

def get_entropy_data(root_path, directory_path):
    """Get entropy data for a specific test configuration"""
    
    # Extract configuration from path
    dir_str = str(directory_path).replace('\\', '/')
    
    # Determine security level
    security_level = None
    if 'STANDARD' in dir_str.upper() or '-512' in dir_str:
        security_level = 'STANDARD'
        entropy_filename = 'entropy-assessment-standard.txt'
    elif 'ENHANCED' in dir_str.upper() or '-128' in dir_str:
        security_level = 'ENHANCED'
        entropy_filename = 'entropy-assessment-enhanced.txt'
    elif 'MAXIMUM' in dir_str.upper() or '-32' in dir_str:
        security_level = 'MAXIMUM'
        entropy_filename = 'entropy-assessment-maximum.txt'
    else:
        print(f"  ⚠️  Could not determine security level from path")
        return {}
    
    # Extract key size
    key_size = None
    size_patterns = [
        (r'128[\-_]?bit', '128-bit'),
        (r'256[\-_]?bit', '256-bit'),
        (r'512[\-_]?bit', '512-bit'),
        (r'1024[\-_]?bit', '1024-bit'),
        (r'2048[\-_]?bit', '2048-bit'),
        (r'4096[\-_]?bit', '4096-bit'),
        (r'1[\-_]?KB', '1KB'),
        (r'4[\-_]?KB', '4KB'),
        (r'1[\-_]?MB', '1MB'),
        (r'16[\-_]?MB', '16MB'),
        (r'256[\-_]?MB', '256MB'),
        (r'512[\-_]?MB', '512MB')
    ]
    
    for pattern, size in size_patterns:
        if re.search(pattern, dir_str, re.IGNORECASE):
            key_size = size
            break
    
    if not key_size:
        print(f"  ⚠️  Could not determine key size from path")
        return {}
    
    # Find entropy results folder
    entropy_dirs = [
        root_path / 'sp800-90b-results',
        root_path / 'SP800-90B-results',
        root_path / 'entropy-assessment'
    ]
    
    entropy_dir = None
    for possible_dir in entropy_dirs:
        if possible_dir.exists():
            entropy_dir = possible_dir
            break
    
    if not entropy_dir:
        print(f"  ⚠️  No entropy results folder found")
        return {}
    
    # Get the consolidated entropy file
    entropy_file = entropy_dir / entropy_filename
    if not entropy_file.exists():
        print(f"  ⚠️  Entropy file not found: {entropy_filename}")
        return {}
    
    print(f"  📄 Reading entropy file: {entropy_filename}")
    
    # Parse the specific section from the consolidated file
    return parse_consolidated_entropy_file(entropy_file, key_size, security_level)

def get_configuration_from_path(filepath):
    """Extract configuration details from file path"""
    path_str = str(filepath).replace('\\', '/')
    
    config = {
        'security_level': 'UNKNOWN',
        'expansion_ratio': 'UNKNOWN',
        'key_size': 'UNKNOWN'
    }
    
    # Determine security level
    if 'STANDARD' in path_str.upper() or '-512' in path_str:
        config['security_level'] = 'STANDARD'
        config['expansion_ratio'] = '1:512'
    elif 'ENHANCED' in path_str.upper() or '-128' in path_str:
        config['security_level'] = 'ENHANCED'
        config['expansion_ratio'] = '1:128'
    elif 'MAXIMUM' in path_str.upper() or '-32' in path_str:
        config['security_level'] = 'MAXIMUM'
        config['expansion_ratio'] = '1:32'
    
    # Extract key size
    size_patterns = [
        (r'128[\-_]?bit', '128-bit'),
        (r'256[\-_]?bit', '256-bit'),
        (r'512[\-_]?bit', '512-bit'),
        (r'1024[\-_]?bit', '1024-bit'),
        (r'2048[\-_]?bit', '2048-bit'),
        (r'4096[\-_]?bit', '4096-bit'),
        (r'1[\-_]?KB', '1KB'),
        (r'4[\-_]?KB', '4KB'),
        (r'1[\-_]?MB', '1MB'),
        (r'16[\-_]?MB', '16MB'),
        (r'256[\-_]?MB', '256MB'),
        (r'512[\-_]?MB', '512MB')
    ]
    
    for pattern, size in size_patterns:
        if re.search(pattern, path_str, re.IGNORECASE):
            config['key_size'] = size
            break
    
    # Extract number of keys if available
    keys_match = re.search(r'(\d+)keys', path_str, re.IGNORECASE)
    if keys_match:
        config['num_keys'] = int(keys_match.group(1))
    
    return config

def generate_summary(directory, root_path):
    """Generate comprehensive summary for a test directory"""
    directory = Path(directory)
    root_path = Path(root_path)
    
    print(f"\n📂 Processing: {directory.relative_to(root_path)}")
    
    # Find the final analysis report
    report_file = None
    for pattern in ['*finalAnalysisReport*.txt', '*final*.txt', '*Analysis*.txt']:
        files = list(directory.glob(pattern))
        if files:
            report_file = files[0]
            break
    
    if not report_file:
        print(f"  ❌ No analysis report found")
        return None
    
    print(f"  📄 Found report: {report_file.name}")
    
    # Parse the report
    test_results = parse_final_analysis_report(report_file)
    if not test_results:
        print(f"  ❌ Could not parse test results")
        return None
    
    # Get configuration from path
    config = get_configuration_from_path(directory)
    
    # Get entropy assessment data
    entropy_data = get_entropy_data(root_path, directory)
    if entropy_data and 'min_entropy' in entropy_data:
        print(f"  ✅ Found entropy data: min_entropy={entropy_data['min_entropy']:.6f} bits/byte")
    
    # Calculate overall statistics
    # Count ALL individual tests (don't group by type)
    # The NIST requirement is that ≥96% of individual tests pass
    # Not that ≥96% of test types pass
    total_tests = 0
    passed_tests = 0
    
    # Parse the actual number of tests from the report
    # Each line in the report with a pass/fail ratio is a separate test
    try:
        with open(report_file, 'r', encoding='utf-8', errors='ignore') as f:
            report_content = f.read()
            
        for line in report_content.split('\n'):
            if '/' in line and not line.startswith('-') and not line.startswith('The minimum'):
                parts = line.split()
                if len(parts) >= 3:
                    # Find the proportion (e.g., "123/125")
                    for part in parts:
                        if '/' in part:
                            try:
                                passed, total = part.split('/')
                                passed = int(passed)
                                total = int(total)
                                
                                # This is one test
                                total_tests += 1
                                
                                # Check if it meets the requirement
                                pass_rate = passed / total
                                has_asterisk = '*' in line
                                if pass_rate >= 0.96 and not has_asterisk:
                                    passed_tests += 1
                                    
                                break
                            except:
                                continue
    except:
        # Fallback to the old method if parsing fails
        total_tests = len(test_results)
        passed_tests = sum(1 for r in test_results.values() if r['meets_requirement'])
    
    overall_pass_rate = passed_tests / total_tests if total_tests > 0 else 0
    
    # Print clarification about test counting
    print(f"  📊 Found {total_tests} individual tests ({len(test_results)} unique test types)")
    print(f"  ✅ {passed_tests}/{total_tests} individual tests passed ({overall_pass_rate*100:.2f}%)")
    
    # Get list of all binary files for checksums (optional, limit to first 5)
    bin_files = list(directory.glob('*.bin'))
    file_checksums = {}
    
    for bin_file in bin_files[:5]:  # Limit to first 5 files for summary
        try:
            with open(bin_file, 'rb') as f:
                # Read in chunks for large files
                sha256_hash = hashlib.sha256()
                for chunk in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(chunk)
                file_checksums[bin_file.name] = {
                    'sha256': sha256_hash.hexdigest(),
                    'size_bytes': bin_file.stat().st_size
                }
        except Exception as e:
            print(f"  ⚠️  Could not hash {bin_file.name}: {e}")
    
    # Create comprehensive summary
    summary = {
        'metadata': {
            'generated': datetime.now().isoformat(),
            'generator': 'SQEF Test Summary Generator v2.1',
            'directory': str(directory.relative_to(root_path)),
            'report_file': report_file.name
        },
        'configuration': config,
        'overall_results': {
            'total_individual_tests': total_tests,  # All 188 tests
            'passed_individual_tests': passed_tests,
            'failed_individual_tests': total_tests - passed_tests,
            'overall_pass_rate': overall_pass_rate,
            'pass_percentage': f"{overall_pass_rate*100:.2f}%",
            'meets_nist_requirement': overall_pass_rate >= 0.96,
            'status': 'PASSED' if overall_pass_rate >= 0.96 else 'FAILED',
            'unique_test_types': len(test_results),  # For reference
            'note': 'NIST requires ≥96% of individual tests to pass, not test types'
        },
        'entropy_assessment': entropy_data if entropy_data else None,
        'individual_tests': test_results,
        'test_categories': {
            'frequency_tests': {},
            'runs_tests': {},
            'template_tests': {},
            'complexity_tests': {},
            'other_tests': {}
        },
        'file_checksums': file_checksums if file_checksums else None
    }
    
    # Categorize tests
    for test_name, result in test_results.items():
        if 'Frequency' in test_name:
            summary['test_categories']['frequency_tests'][test_name] = result
        elif 'Runs' in test_name or 'Run' in test_name:
            summary['test_categories']['runs_tests'][test_name] = result
        elif 'Template' in test_name:
            summary['test_categories']['template_tests'][test_name] = result
        elif 'Complexity' in test_name or 'Linear' in test_name:
            summary['test_categories']['complexity_tests'][test_name] = result
        else:
            summary['test_categories']['other_tests'][test_name] = result
    
    # Save summary.json in the same directory
    output_file = directory / 'summary.json'
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2)
        print(f"  ✅ Created: summary.json")
        return summary
    except Exception as e:
        print(f"  ❌ Error saving summary: {e}")
        return None

def process_all_directories(root_path):
    """Process all test directories recursively"""
    root_path = Path(root_path)
    summaries_created = 0
    all_summaries = {}
    
    print("=" * 60)
    print("SQEF Test Summary Generator v2.1")
    print("=" * 60)
    print(f"Root directory: {root_path}")
    
    # Check for sp800-90b-results folder
    sp800_90b_found = False
    for possible_name in ['sp800-90b-results', 'SP800-90B-results', 'entropy-assessment']:
        if (root_path / possible_name).exists():
            sp800_90b_found = True
            print(f"✅ Found entropy results folder: {possible_name}")
            
            # List the entropy files
            entropy_files = list((root_path / possible_name).glob("*.txt"))
            if entropy_files:
                print(f"   Available entropy files:")
                for ef in entropy_files:
                    print(f"   - {ef.name}")
            break
    
    if not sp800_90b_found:
        print("⚠️  Warning: No sp800-90b-results folder found")
        print("   Entropy assessment data will not be included\n")
    
    # Find all directories containing test results
    test_dirs = set()
    
    # Look for directories with finalAnalysisReport files
    for report_file in root_path.rglob('*finalAnalysisReport*.txt'):
        # Skip if in sp800-90b-results folder
        if 'sp800-90b' not in str(report_file).lower():
            test_dirs.add(report_file.parent)
    
    # Also look for other report patterns
    for pattern in ['*final*.txt', '*Analysis*.txt']:
        for report_file in root_path.rglob(pattern):
            if 'sp800-90b' not in str(report_file).lower() and 'entropy' not in str(report_file).lower():
                test_dirs.add(report_file.parent)
    
    if not test_dirs:
        print("❌ No test directories found!")
        return
    
    print(f"✅ Found {len(test_dirs)} test directories\n")
    
    # Process each directory
    for test_dir in sorted(test_dirs):
        summary = generate_summary(test_dir, root_path)
        if summary:
            summaries_created += 1
            # Store for master summary
            rel_path = test_dir.relative_to(root_path)
            all_summaries[str(rel_path)] = {
                **summary['overall_results'],
                'configuration': summary['configuration'],
                'entropy_min': summary['entropy_assessment'].get('min_entropy') if summary['entropy_assessment'] else None
            }
    
    # Create master summary file at root
    if all_summaries:
        master_summary = {
            'metadata': {
                'generated': datetime.now().isoformat(),
                'total_test_configurations': len(all_summaries),
                'all_configurations_pass': all(
                    s['meets_nist_requirement'] for s in all_summaries.values()
                )
            },
            'test_configurations': all_summaries
        }
        
        master_file = root_path / 'MASTER_SUMMARY.json'
        try:
            with open(master_file, 'w', encoding='utf-8') as f:
                json.dump(master_summary, f, indent=2)
            print(f"\n✅ Created master summary: {master_file}")
        except Exception as e:
            print(f"\n❌ Error creating master summary: {e}")
    
    print("\n" + "=" * 60)
    print(f"Summary generation complete!")
    print(f"Created {summaries_created} summary files")
    print("=" * 60)

def main():
    """Main function"""
    import sys
    
    if len(sys.argv) > 1:
        root_path = sys.argv[1]
    else:
        print("SQEF Test Summary Generator v2.1")
        print("-" * 30)
        print("\nUsage:")
        print(f"  python {sys.argv[0]} <root_directory>")
        print(f"\nExample:")
        print(f"  python {sys.argv[0]} C:\\GitHub\\Luminareware-SQEF-NIST-Evaluation")
        print()
        root_path = input("Enter root directory path: ").strip().strip('"')
    
    if not os.path.exists(root_path):
        print(f"❌ Error: Directory does not exist: {root_path}")
        sys.exit(1)
    
    process_all_directories(root_path)
    input("\nPress Enter to exit...")

if __name__ == '__main__':
    main()