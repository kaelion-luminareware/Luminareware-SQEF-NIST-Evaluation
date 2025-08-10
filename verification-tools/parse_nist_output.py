#!/usr/bin/env python3
"""
NIST Output Parser
Parses NIST SP 800-22 and SP 800-90B output files into structured formats
"""

import os
import sys
import re
import json
import csv
import argparse
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime

class NISTOutputParser:
    """Parse NIST test output files"""
    
    def __init__(self):
        self.sp800_22_results = {}
        self.sp800_90b_results = {}
        
    def parse_sp800_22_report(self, filepath: Path) -> Dict[str, Any]:
        """Parse NIST SP 800-22 finalAnalysisReport.txt"""
        results = {
            'file': str(filepath),
            'timestamp': datetime.now().isoformat(),
            'tests': {},
            'summary': {}
        }
        
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except Exception as e:
            print(f"Error reading {filepath}: {e}")
            return results
            
        # Parse header information
        lines = content.split('\n')
        
        # Find test results section
        in_results = False
        test_count = 0
        passed_count = 0
        
        for line in lines:
            # Skip empty lines and separators
            if not line.strip() or line.startswith('-'):
                continue
                
            # Look for test result lines (contain pass/total ratio)
            if '/' in line and not line.startswith('RESULTS'):
                parts = line.split()
                if len(parts) >= 3:
                    # Extract test name (last column)
                    test_name = parts[-1]
                    
                    # Find the proportion (e.g., "96/100")
                    for i, part in enumerate(parts):
                        if '/' in part:
                            try:
                                passed, total = map(int, part.split('/'))
                                
                                # Find p-value (usually before proportion)
                                p_value = None
                                if i > 0:
                                    try:
                                        p_value = float(parts[i-1])
                                    except:
                                        pass
                                
                                # Check for uniformity warning (*)
                                has_warning = '*' in line
                                
                                # Calculate pass rate
                                pass_rate = passed / total
                                
                                # Store result
                                results['tests'][test_name] = {
                                    'passed': passed,
                                    'total': total,
                                    'pass_rate': pass_rate,
                                    'percentage': f"{pass_rate*100:.2f}%",
                                    'p_value': p_value,
                                    'uniformity_warning': has_warning,
                                    'meets_requirement': pass_rate >= 0.96 and not has_warning
                                }
                                
                                test_count += 1
                                if pass_rate >= 0.96:
                                    passed_count += 1
                                    
                                break
                            except:
                                continue
        
        # Calculate summary statistics
        if test_count > 0:
            overall_pass_rate = passed_count / test_count
            results['summary'] = {
                'total_tests': test_count,
                'passed_tests': passed_count,
                'failed_tests': test_count - passed_count,
                'overall_pass_rate': overall_pass_rate,
                'percentage': f"{overall_pass_rate*100:.2f}%",
                'meets_nist_requirement': overall_pass_rate >= 0.96
            }
            
        return results
    
    def parse_sp800_90b_output(self, filepath: Path) -> Dict[str, Any]:
        """Parse NIST SP 800-90B entropy assessment output"""
        results = {
            'file': str(filepath),
            'timestamp': datetime.now().isoformat(),
            'assessments': []
        }
        
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except Exception as e:
            print(f"Error reading {filepath}: {e}")
            return results
            
        # Split into sections by filename
        sections = re.split(r'^(.*\.bin\s+\d+)$', content, flags=re.MULTILINE)
        
        for i in range(1, len(sections), 2):
            if i + 1 < len(sections):
                header = sections[i].strip()
                section_content = sections[i + 1]
                
                # Parse filename and bits per symbol
                match = re.match(r'(.+\.bin)\s+(\d+)', header)
                if not match:
                    continue
                    
                filename = match.group(1)
                bits_per_symbol = int(match.group(2))
                
                assessment = {
                    'filename': filename,
                    'bits_per_symbol': bits_per_symbol,
                    'results': {}
                }
                
                # Extract entropy values
                h_orig = re.search(r'H_original:\s*(\d+\.?\d*)', section_content)
                if h_orig:
                    assessment['results']['h_original'] = float(h_orig.group(1))
                    
                h_bit = re.search(r'H_bitstring:\s*(\d+\.?\d*)', section_content)
                if h_bit:
                    assessment['results']['h_bitstring'] = float(h_bit.group(1))
                    
                min_h = re.search(r'min\([^)]+\):\s*(\d+\.?\d*)', section_content)
                if min_h:
                    assessment['results']['min_entropy'] = float(min_h.group(1))
                    assessment['results']['min_entropy_per_byte'] = float(min_h.group(1))
                    assessment['results']['entropy_percentage'] = \
                        (float(min_h.group(1)) / 8.0) * 100
                    
                # Check test results
                tests = {
                    'chi_square': 'chi square tests',
                    'iid_permutation': 'IID permutation tests',
                    'lrs': 'length of longest repeated substring test'
                }
                
                for test_name, pattern in tests.items():
                    if f'Passed {pattern}' in section_content:
                        assessment['results'][f'{test_name}_test'] = 'PASSED'
                    elif f'Failed {pattern}' in section_content:
                        assessment['results'][f'{test_name}_test'] = 'FAILED'
                        
                # Determine overall status
                test_results = [v for k, v in assessment['results'].items() 
                              if k.endswith('_test')]
                if all(r == 'PASSED' for r in test_results):
                    assessment['results']['overall_status'] = 'PASSED'
                elif any(r == 'FAILED' for r in test_results):
                    assessment['results']['overall_status'] = 'FAILED'
                else:
                    assessment['results']['overall_status'] = 'UNKNOWN'
                    
                results['assessments'].append(assessment)
                
        return results
    
    def parse_individual_test(self, filepath: Path) -> Dict[str, Any]:
        """Parse individual NIST test output file (e.g., frequency.txt)"""
        result = {
            'file': str(filepath),
            'test_name': filepath.stem,
            'data': []
        }
        
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
        except Exception as e:
            print(f"Error reading {filepath}: {e}")
            return result
            
        # Parse based on test type
        test_name = filepath.stem.lower()
        
        if 'frequency' in test_name:
            result['data'] = self._parse_frequency_test(lines)
        elif 'runs' in test_name:
            result['data'] = self._parse_runs_test(lines)
        elif 'template' in test_name:
            result['data'] = self._parse_template_test(lines)
        else:
            result['data'] = self._parse_generic_test(lines)
            
        return result
    
    def _parse_frequency_test(self, lines: List[str]) -> List[Dict]:
        """Parse frequency test output"""
        data = []
        for line in lines:
            if line.strip() and not line.startswith('#'):
                parts = line.split()
                if len(parts) >= 3:
                    try:
                        data.append({
                            'sample': int(parts[0]),
                            'p_value': float(parts[1]),
                            'result': parts[2] if len(parts) > 2 else 'UNKNOWN'
                        })
                    except:
                        continue
        return data
    
    def _parse_runs_test(self, lines: List[str]) -> List[Dict]:
        """Parse runs test output"""
        return self._parse_frequency_test(lines)  # Similar format
    
    def _parse_template_test(self, lines: List[str]) -> List[Dict]:
        """Parse template test output"""
        data = []
        for line in lines:
            if line.strip() and not line.startswith('#'):
                # Template tests may have multiple p-values per line
                parts = line.split()
                if len(parts) >= 2:
                    try:
                        sample_data = {'sample': int(parts[0]), 'p_values': []}
                        for i in range(1, len(parts)):
                            try:
                                sample_data['p_values'].append(float(parts[i]))
                            except:
                                break
                        if sample_data['p_values']:
                            data.append(sample_data)
                    except:
                        continue
        return data
    
    def _parse_generic_test(self, lines: List[str]) -> List[Dict]:
        """Generic parser for test output"""
        data = []
        for line in lines:
            if line.strip() and not line.startswith('#'):
                # Try to extract numeric values
                numbers = re.findall(r'\d+\.?\d*', line)
                if numbers:
                    data.append({'values': [float(n) for n in numbers]})
        return data
    
    def export_to_csv(self, data: Dict, output_file: Path):
        """Export parsed data to CSV format"""
        if 'tests' in data:  # SP 800-22 format
            with open(output_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['Test Name', 'Passed', 'Total', 'Pass Rate', 
                               'P-Value', 'Meets Requirement'])
                
                for test_name, result in data['tests'].items():
                    writer.writerow([
                        test_name,
                        result['passed'],
                        result['total'],
                        result['pass_rate'],
                        result.get('p_value', 'N/A'),
                        'YES' if result['meets_requirement'] else 'NO'
                    ])
                    
        elif 'assessments' in data:  # SP 800-90B format
            with open(output_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['Filename', 'Min Entropy', 'Chi-Square', 
                               'IID Test', 'LRS Test', 'Overall Status'])
                
                for assessment in data['assessments']:
                    results = assessment['results']
                    writer.writerow([
                        assessment['filename'],
                        results.get('min_entropy', 'N/A'),
                        results.get('chi_square_test', 'N/A'),
                        results.get('iid_permutation_test', 'N/A'),
                        results.get('lrs_test', 'N/A'),
                        results.get('overall_status', 'N/A')
                    ])

def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description='Parse NIST test output files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Output formats:
  --json    Export to JSON format (default)
  --csv     Export to CSV format
  --pretty  Pretty print to console

Examples:
  %(prog)s finalAnalysisReport.txt
  %(prog)s --csv entropy-assessment-standard.txt
  %(prog)s --pretty sp800-22-results/*/finalAnalysisReport.txt
        """
    )
    
    parser.add_argument('files', nargs='+', help='NIST output files to parse')
    parser.add_argument('--output', '-o', help='Output file (default: stdout)')
    parser.add_argument('--format', choices=['json', 'csv', 'pretty'], 
                       default='json', help='Output format')
    parser.add_argument('--merge', action='store_true', 
                       help='Merge multiple files into single output')
    
    args = parser.parse_args()
    
    nist_parser = NISTOutputParser()
    all_results = []
    
    for file_pattern in args.files:
        # Handle wildcards
        files = Path('.').glob(file_pattern) if '*' in file_pattern else [Path(file_pattern)]
        
        for filepath in files:
            if not filepath.exists():
                print(f"Warning: File not found: {filepath}", file=sys.stderr)
                continue
                
            print(f"Processing: {filepath}")
            
            # Determine file type and parse accordingly
            if 'finalAnalysisReport' in filepath.name:
                result = nist_parser.parse_sp800_22_report(filepath)
            elif 'entropy' in filepath.name.lower() or '90b' in str(filepath):
                result = nist_parser.parse_sp800_90b_output(filepath)
            else:
                result = nist_parser.parse_individual_test(filepath)
                
            all_results.append(result)
    
    # Output results
    if args.merge:
        output_data = {'merged_results': all_results}
    else:
        output_data = all_results[0] if len(all_results) == 1 else all_results
        
    if args.format == 'json':
        json_str = json.dumps(output_data, indent=2)
        if args.output:
            with open(args.output, 'w') as f:
                f.write(json_str)
            print(f"✅ Results saved to: {args.output}")
        else:
            print(json_str)
            
    elif args.format == 'csv':
        if args.output:
            output_path = Path(args.output)
        else:
            output_path = Path('output.csv')
            
        if isinstance(output_data, list):
            for i, data in enumerate(output_data):
                csv_file = output_path.parent / f"{output_path.stem}_{i}{output_path.suffix}"
                nist_parser.export_to_csv(data, csv_file)
                print(f"✅ CSV saved to: {csv_file}")
        else:
            nist_parser.export_to_csv(output_data, output_path)
            print(f"✅ CSV saved to: {output_path}")
            
    elif args.format == 'pretty':
        # Pretty print to console
        for result in (output_data if isinstance(output_data, list) else [output_data]):
            print("\n" + "="*60)
            print(f"File: {result.get('file', 'Unknown')}")
            print("="*60)
            
            if 'summary' in result:
                summary = result['summary']
                print(f"\nSummary:")
                print(f"  Total Tests: {summary.get('total_tests', 0)}")
                print(f"  Passed: {summary.get('passed_tests', 0)}")
                print(f"  Failed: {summary.get('failed_tests', 0)}")
                print(f"  Pass Rate: {summary.get('percentage', 'N/A')}")
                print(f"  Meets NIST: {'✅ YES' if summary.get('meets_nist_requirement') else '❌ NO'}")
                
            if 'tests' in result:
                print(f"\nIndividual Tests:")
                for test_name, test_result in result['tests'].items():
                    status = '✅' if test_result['meets_requirement'] else '❌'
                    print(f"  {status} {test_name}: {test_result['percentage']} "
                          f"({test_result['passed']}/{test_result['total']})")
                          
            if 'assessments' in result:
                print(f"\nEntropy Assessments:")
                for assessment in result['assessments']:
                    print(f"\n  File: {assessment['filename']}")
                    results = assessment['results']
                    if 'min_entropy' in results:
                        print(f"    Min Entropy: {results['min_entropy']:.6f} bits/byte")
                    if 'overall_status' in results:
                        status = '✅' if results['overall_status'] == 'PASSED' else '❌'
                        print(f"    Status: {status} {results['overall_status']}")

if __name__ == '__main__':
    main()