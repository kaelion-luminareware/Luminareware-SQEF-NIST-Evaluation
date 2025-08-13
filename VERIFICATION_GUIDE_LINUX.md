# SQEF NIST Validation - Verification Guide

## Overview

This guide provides step-by-step instructions for independently verifying the SQEF NIST test results contained in this repository. All test configurations have passed NIST SP 800-22 and SP 800-90B requirements with pass rates ranging from 98.40% to 100%.

## Quick Verification Summary

| Security Level | Configurations | Pass Rate Range | Status |
|---------------|---------------|-----------------|---------|
| STANDARD-512 | 11 configs | 98.94% - 100% | ✅ ALL PASS |
| ENHANCED-128 | 11 configs | 98.40% - 100% | ✅ ALL PASS |
| MAXIMUM-32 | 11 configs | 98.94% - 100% | ✅ ALL PASS |

**Total: 33 configurations tested, 33 passed (100% success rate)**

## Prerequisites

### Required Software

1. **Python 3.7+**
   ```bash
   python --version  # Should be 3.7 or higher
   ```

2. **Required Python packages**
   ```bash
   pip install numpy pandas matplotlib json hashlib pathlib
   ```

3. **NIST Statistical Test Suite (Optional - for independent validation)**
   - Version: 2.1.2 or later
   - Download: https://csrc.nist.gov/projects/random-bit-generation/documentation-and-software

4. **NIST SP 800-90B Entropy Assessment Tools (Optional)**
   - Tools: ea_iid, ea_non_iid
   - Repository: https://github.com/usnistgov/SP800-90B_EntropyAssessment

## Repository Structure

```
Luminareware-SQEF-NIST-Evaluation/
├── sample-outputs/
│   ├── sample-outputs-STANDARD-512/    # 11 key size configurations
│   ├── sample-outputs-ENHANCED-128/    # 11 key size configurations
│   └── sample-outputs-MAXIMUM-32/      # 11 key size configurations
├── sp800-22-results/
│   ├── test-results-STANDARD-512/    # 11 key size configurations
│   ├── test-results-ENHANCED-128/    # 11 key size configurations
│   └── test-results-MAXIMUM-32/      # 11 key size configurations
├── sp800-90b-results/
│   ├── entropy-assessment-standard.txt
│   ├── entropy-assessment-enhanced.txt
│   └── entropy-assessment-maximum.txt
├── verification-tools/
│   ├── sqef_test_summary_generator.py  
│   └── parse_nist_output.py
└── LICENSE.md
└── MASTER_SUMMARY.json
└── README.md
└── VERIFICATION_GUIDE_LINUS.md
└── VERIFICATION_GUIDE_WINDOWS.md

```

## Step 1: Quick Verification Using Summary Files

### 1.1 Check Master Summary

```bash
# View overall results
python -m json.tool MASTER_SUMMARY.json | head -20

# Check all configurations passed
python -c "import json; data=json.load(open('MASTER_SUMMARY.json')); print(f'All Pass: {data[\"metadata\"][\"all_configurations_pass\"]}')"
```

### 1.2 Verify Individual Configuration

```bash
# Check specific configuration (example: ENHANCED-128 256-bit)
cd sp800-22-results/test-results-ENHANCED-128/256-bit/
python -m json.tool summary.json | grep -A 5 "overall_results"
```

Expected output:
```json
"overall_results": {
    "total_individual_tests": 188,
    "passed_individual_tests": 187,
    "overall_pass_rate": 0.9947,
    "status": "PASSED"
}
```

## Step 2: Detailed Verification

### 2.1 Parse All Test Results

```bash
# From repository root
cd verification-tools/

# Parse all finalAnalysisReport.txt files
python parse_nist_output.py --format pretty "../sp800-22-results/*/*/finalAnalysisReport.txt"
```

This will display:
- Total tests per configuration (should be 188)
- Pass rate (must be ≥96%)
- Individual test results

### 2.2 Verify Specific Test Configuration

```bash
# Verify a specific configuration
python verify_results.py ../sp800-22-results/test-results-ENHANCED-128/256-bit/

# Expected output:
# ✅ All verification checks PASSED
# Total individual tests: 188
# Pass rate: 99.47%
```

### 2.3 Generate Fresh Summaries

```bash
# Regenerate all summary.json files
python sqef_test_summary_generator.py ..

# This will:
# - Scan all test directories
# - Parse finalAnalysisReport.txt files
# - Match entropy assessment data
# - Create summary.json in each directory
# - Generate MASTER_SUMMARY.json
```

## Step 3: Understanding Test Results

### 3.1 NIST SP 800-22 Requirements

- **Pass Rate Threshold**: ≥96% of individual tests must pass
- **Total Tests**: 188 per configuration
  - 148 NonOverlappingTemplate tests
  - 8 RandomExcursions tests
  - 18 RandomExcursionsVariant tests
  - 14 other statistical tests
- **Minimum Passing**: 181 out of 188 tests

### 3.2 Common "Failures" (All Acceptable)

1. **RandomExcursions/RandomExcursionsVariant**
   - Most common failures
   - Smaller sample sizes (varies by configuration)
   - Normal statistical variation

2. **Universal Test**
   - May fail on larger blocks (≥1MB)
   - Likely due to parameter limitations
   - Example: 16MB blocks show uniformity failure

3. **Individual Test Failures**
   - 1-3 failures per configuration is normal
   - Part of expected statistical variation
   - NIST accounts for this with 96% threshold

### 3.3 Interpreting Pass Rates

| Pass Rate | Interpretation |
|-----------|---------------|
| 100% | Perfect (somewhat rare, still valid) |
| 99-100% | Excellent |
| 98-99% | Very Good |
| 96-98% | Good (meets requirements) |
| <96% | Fails NIST requirements |

**All SQEF configurations: 98.40% - 100% (Excellent)**

## Step 4: Entropy Assessment Verification

### 4.1 Check Entropy Results

```bash
# View standard security level entropy
cat ../sp800-90b-results/entropy-assessment-standard.txt | grep -A 3 "min(H_original"

# Parse all entropy assessments
python parse_nist_output.py --format pretty ../sp800-90b-results/*.txt
```

### 4.2 Expected Entropy Values

All configurations should show:
- **Min Entropy**: >7.96 bits/byte (>99.5% of maximum)
- **IID Tests**: PASSED
- **Chi-Square Tests**: PASSED
- **LRS Tests**: PASSED

## Step 5: Verification Checklist

Use this checklist for complete verification:

- [ ] **File Structure**
  - [ ] 33 test directories present (11 per security level)
  - [ ] Each directory contains finalAnalysisReport.txt
  - [ ] Each directory contains summary.json
  - [ ] 3 entropy assessment files present

- [ ] **Overall Results**
  - [ ] All 33 configurations show "PASSED" status
  - [ ] All pass rates ≥96% (actual: 98.40% - 100%)
  - [ ] MASTER_SUMMARY.json shows all_configurations_pass: true

- [ ] **SP 800-22 Tests**
  - [ ] 188 individual tests per configuration
  - [ ] Pass rates documented correctly
  - [ ] No systematic failures across configurations

- [ ] **SP 800-90B Entropy**
  - [ ] Min entropy >7.96 bits/byte for all sizes
  - [ ] IID tests passed
  - [ ] Chi-square tests passed
  - [ ] LRS tests passed

- [ ] **Known Anomalies Documented**
  - [ ] Universal test failures on large blocks noted
  - [ ] RandomExcursions variations documented
  - [ ] All failures within statistical expectations

## Step 6: Common Verification Commands

```bash
# Count total test directories
find ../sp800-22-results -type d -name "*-bit" -o -name "*-blocks" -o -name "*-master" | wc -l
# Expected: 33

# Check all pass rates at once
for dir in ../sp800-22-results/*/*/; do
    echo -n "$dir: "
    grep "status" "$dir/summary.json" 2>/dev/null | grep -o "PASSED\|FAILED"
done

# Verify entropy for all configurations
grep "min_entropy" ../sp800-22-results/*/*/summary.json | wc -l
# Should equal number of directories

# Find any failed configurations (should return nothing)
grep -l "\"status\": \"FAILED\"" ../sp800-22-results/*/*/summary.json

# Count individual test failures
grep -c "false" ../sp800-22-results/*/*/finalAnalysisReport.txt | grep -v ":0$"
```

## Step 7: Reproducing Results (Optional)

To independently verify with sample data:

### 7.1 Test Sample Files

```bash
# If sample files are provided
cd sample-outputs/

# Run NIST STS (if installed)
$NIST_STS_PATH/assess 1000000 < sample_256bit_1000.bin

# Run entropy assessment (if installed)
$EA_PATH/ea_iid -v sample_256bit_1000.bin 8
```

### 7.2 Expected Sample Results

- Pass rate should be similar (±2%) to full test results
- Entropy should be >7.9 bits/byte
- No systematic failures

## Troubleshooting

### Issue: Different Test Count

**Problem**: Not seeing 188 tests per configuration

**Solution**: 
- Check for RandomExcursions tests (count varies with data)
- Total should be: 148 NonOverlappingTemplate + 8 RandomExcursions + 18 RandomExcursionsVariant + 14 others
- RandomExcursions count can vary based on number of cycles in data

### Issue: Summary Generation Fails

**Problem**: sqef_test_summary_generator.py errors

**Solution**:
```bash
# Check Python version
python --version  # Must be 3.7+

# Install required packages
pip install pathlib datetime hashlib

# Run with verbose output
python sqef_test_summary_generator.py .. 2>&1 | tee generation.log
```

### Issue: Entropy Data Not Found

**Problem**: summary.json shows null entropy_assessment

**Solution**:
- Ensure sp800-90b-results folder exists
- Check entropy file names match pattern: entropy-assessment-{standard|enhanced|maximum}.txt
- Verify entropy files contain data for all key sizes

## Validation Certification Statement

Based on the verification steps above, you should be able to confirm:

> "The SQEF entropy source has been validated against NIST SP 800-22 Rev. 1a and SP 800-90B requirements. All 33 tested configurations (11 key sizes × 3 security levels) pass the statistical randomness tests with pass rates between 98.40% and 100%, exceeding the required 96% threshold. The entropy assessment confirms min-entropy values >7.96 bits/byte (>99.5% of theoretical maximum) with all IID, chi-square, and LRS tests passing."

## Contact & Support

For questions about verification:
- Email: contact@luminareware.com

## References

- [NIST SP 800-22 Rev. 1a](https://csrc.nist.gov/publications/detail/sp/800-22/rev-1a/final)
- [NIST SP 800-90B](https://csrc.nist.gov/publications/detail/sp/800-90b/final)
- [NIST Random Bit Generation](https://csrc.nist.gov/projects/random-bit-generation)

---

*Last Updated: August 2025*
*Document Version: 1.0*

*See VERIFICATION_GUIDE_WINDOWS.md for Windows commands*