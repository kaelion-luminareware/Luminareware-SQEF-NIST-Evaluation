# Luminareware-SQEF-NIST-Evaluation

## Simulated Quantum Entropy Fusion (SQEF™) - NIST Evaluation Repository

**Technology:** SQEF™ (Patent Pending, Trademark Filed)  
**Developer:** Luminareware LLC  
**Patent Status:** USPTO Applications 19/198,077 and 19/267,394 (Pending)  
**Contact:** contact@luminareware.com

## Overview

This repository contains comprehensive test results and validation data for Luminareware's SQEF (Simulated Quantum Entropy Fusion) cryptographic random number generation technology, submitted for NIST evaluation. SQEF achieves quantum-grade randomness through pure software implementation without requiring quantum hardware, specialized chips, or network connectivity.

## Key Performance Metrics

* **Min-Entropy:** 7.96-7.99 bits/byte across all configurations (NIST SP 800-90B validated)
* **NIST SP 800-22:** All 33 configurations pass (6,204 tests, 98.40%-100% pass rates per configuration)
* **NIST SP 800-90B:** 100% IID compliance (all 33 configurations validated)
* **Throughput:** 273 MB/s baseline, up to 9,943 keys/ms for 256-bit keys
* **Security Levels:** Three validated levels (Standard 1:512, Enhanced 1:128, Maximum 1:32)
* **Hardware Required:** None (pure software implementation)

## Test Configuration Summary

### Comprehensive Testing Coverage
- **11 Key Sizes:** 256-bit through 512MB
- **3 Security Levels:** Standard, Enhanced, Maximum
- **33 Total Configurations:** All validated and passed
- **6,204 Individual Tests:** Across all configurations

### Security Level Definitions
- **STANDARD (1:512):** Each 1MB seed expands to maximum 512MB
- **ENHANCED (1:128):** Each 1MB seed expands to maximum 128MB  
- **MAXIMUM (1:32):** Each 1MB seed expands to maximum 32MB

All modes maintain >2^123 operation security margins against SHA3-256 attacks.

## Repository Structure

| Directory | Description | Notes |
|---|---|---|
| `/sp800-22-results/` | Complete NIST SP 800-22 test outputs | All 33 configurations |
| `/sp800-90b-results/` | NIST SP 800-90B entropy assessments | IID validation results |
| `/documentation/` | Technical specifications & methodologies | Includes EXECUTIVE_SUMMARY |
| `/sample-outputs/` | Sample keys for verification | Binary samples for analysis |
| `/verification-tools/` | Scripts to verify results | Python validation tools |
| `MASTER_SUMMARY.json` | Consolidated test results | Machine-readable summary |
| `EXECUTIVE_SUMMARY.md` | Executive overview for NIST/DARPA | Complete technical summary |

## Large Test Files (256MB & 512MB)

Due to GitHub's 100MB file size limitation, the following large test files are available separately:

### Files Available on Request

**STANDARD Security (1:512):**
- `sqef_master_512mb_STANDARD_for_slicing.bin` (512MB)
- `sqef_sliced_256MB_1keys_from_STANDARD_master.bin` (256MB)
- `sqef_sliced_512MB_1keys_from_STANDARD_master.bin` (512MB)

**ENHANCED Security (1:128):**
- `sqef_master_512mb_ENHANCED_for_slicing.bin` (512MB)
- `sqef_sliced_256MB_1keys_from_ENHANCED_master.bin` (256MB)
- `sqef_sliced_512MB_1keys_from_ENHANCED_master.bin` (512MB)

**MAXIMUM Security (1:32):**
- `sqef_master_512mb_MAXIMUM_for_slicing.bin` (512MB)
- `sqef_sliced_256MB_1keys_from_MAXIMUM_master.bin` (256MB)
- `sqef_sliced_512MB_1keys_from_MAXIMUM_master.bin` (512MB)

### Accessing Large Files

1. **GitHub Releases:** Check the [Releases](https://github.com/kaelion-luminareware/Luminareware-SQEF-NIST-Evaluation/releases) section for complete dataset
2. **Direct Request:** Contact contact@luminareware.com for secure transfer link
3. **NIST Evaluators:** We can provide physical media (USB/SSD) or direct server access

SHA-256 checksums for all large files are provided in `/checksums/large_files_checksums.txt`

## Test Results Summary

### NIST SP 800-22 Statistical Test Suite
- **Total Configurations Tested:** 33
- **Individual Tests Performed:** 6,204 (188 tests × 33 configurations)
- **Overall Pass Requirement:** ≥96% per configuration (NIST threshold)
- **Actual Performance:** 98.40% to 100% pass rate per configuration
- **Result:** ALL CONFIGURATIONS PASS

### NIST SP 800-90B Entropy Assessment
- **IID Validation:** 100% pass rate (33/33 configurations)
- **Min-Entropy Range:** 7.963836 to 7.994706 bits/byte
- **NIST Threshold:** ≥7.976 bits/byte for full entropy
- **Result:** ALL CONFIGURATIONS EXCEED THRESHOLD

## Key Advantages

- **No Hardware Dependencies:** Runs on any standard processor
- **Air-Gap Compatible:** No network connectivity required
- **Quantum-Resistant:** Designed for post-quantum cryptography
- **Platform Agnostic:** Deployable from embedded systems to HPC
- **Deterministic Validation:** Reproducible testing and verification

## Validation and Verification

All test results can be independently verified using:
1. NIST Statistical Test Suite (SP 800-22)
2. NIST Entropy Assessment Tool (SP 800-90B)
3. Included Python verification scripts in `/verification-tools/`

## Documentation

- **Executive Summary:** See `EXECUTIVE_SUMMARY.md` for complete technical overview
- **Test Methodology:** Detailed in `/documentation/test_methodology.md`
- **Security Analysis:** Available in `/documentation/security_analysis.md`

## Citation

If referencing this work, please cite: Luminareware LLC. (2025). SQEF: Simulated Quantum Entropy Fusion.
USPTO Patent Applications 19/198,077 and 19/267,394 (Pending).
GitHub: https://github.com/kaelion-luminareware/Luminareware-SQEF-NIST-Evaluation

## Legal Notice

SQEF™ is a trademark of Luminareware LLC (registration pending). Implementation details are proprietary and patent pending. This repository contains test results and validation data only. For licensing inquiries, contact: contact@luminareware.com

## Contact

**Organization:** Luminareware LLC  
**Technical Contact:** William Diacont (Doug)  
**Email:** contact@luminareware.com  
**Repository:** https://github.com/kaelion-luminareware/Luminareware-SQEF-NIST-Evaluation

---

*This repository represents our initial presentation of SQEF technology to the cryptographic community for NIST evaluation. We welcome feedback and look forward to contributing to the advancement of cryptographic entropy generation.*

