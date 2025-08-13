# SQEF NIST Validation - Verification Guide (Windows)

## Overview

This guide provides step-by-step instructions for independently verifying the SQEF NIST test results on **Windows systems**. All test configurations have passed NIST SP 800-22 and SP 800-90B requirements with pass rates ranging from 98.40% to 100%.

*For Linux/Unix systems, see `VERIFICATION_GUIDE_LINUX.md`*

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
   ```cmd
   python --version
   REM Should show Python 3.7 or higher
   ```

2. **Required Python packages**
   ```cmd
   pip install numpy pandas matplotlib
   ```

3. **Windows PowerShell** (Pre-installed on Windows 7+)
   ```cmd
   powershell -Version
   ```

4. **NIST Statistical Test Suite (Optional - for independent validation)**
   - Version: 2.1.2 or later
   - Download: https://csrc.nist.gov/projects/random-bit-generation/documentation-and-software

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
└── VERIFICATION_GUIDE_LINUX.md
└── VERIFICATION_GUIDE_WINDOWS.md
```

## Step 1: Quick Verification Using Summary Files

### 1.1 Check Master Summary (Command Prompt)

```cmd
REM View formatted JSON
python -m json.tool MASTER_SUMMARY.json

REM Check if all configurations passed
python -c "import json; data=json.load(open('MASTER_SUMMARY.json')); print(f'All Pass: {data[\"metadata\"][\"all_configurations_pass\"]}')"
```

### 1.2 Check Master Summary (PowerShell)

```powershell
# View master summary
$master = Get-Content MASTER_SUMMARY.json | ConvertFrom-Json
$master.metadata

# Check all passed
Write-Host "All configurations passed: $($master.metadata.all_configurations_pass)"
```

### 1.3 Verify Individual Configuration

```cmd
REM Navigate to specific configuration
cd sp800-22-results\test-results-ENHANCED-128\256-bit\

REM View summary
python -m json.tool summary.json

REM Check pass status
findstr "status" summary.json
```

Expected output:
```
"status": "PASSED"
```

## Step 2: Detailed Verification

### 2.1 Parse All Test Results

```cmd
REM Navigate to verification tools
cd verification-tools

REM Parse all finalAnalysisReport.txt files (use quotes for wildcards)
python parse_nist_output.py --format pretty "..\sp800-22-results\*\*\finalAnalysisReport.txt"

REM Save results to file
python parse_nist_output.py --format pretty "..\sp800-22-results\*\*\finalAnalysisReport.txt" > all_results.txt
```

### 2.2 Verify Specific Test Configuration

```cmd
REM From verification-tools directory
python verify_results.py ..\sp800-22-results\test-results-ENHANCED-128\256-bit\

REM Expected output:
REM ✅ All verification checks PASSED
REM Total individual tests: 188
REM Pass rate: 99.47%
```

### 2.3 Generate Fresh Summaries

```cmd
REM From repository root
cd C:\GitHub\Luminareware-SQEF-NIST-Evaluation

REM Run summary generator
python verification-tools\sqef_test_summary_generator.py .

REM Or from verification-tools directory
cd verification-tools
python sqef_test_summary_generator.py ..
```

## Step 3: Windows Batch Script for Quick Verification

Create `verify_windows.bat`:

```batch
@echo off
title SQEF NIST Validation Verification
color 0A
cls

echo ============================================
echo    SQEF NIST Validation Quick Verification
echo ============================================
echo.

echo [1] Checking MASTER_SUMMARY.json...
python -c "import json; d=json.load(open('MASTER_SUMMARY.json')); print(f'  Total Configurations: {d[\"metadata\"][\"total_test_configurations\"]}'); print(f'  All Configurations Pass: {d[\"metadata\"][\"all_configurations_pass\"]}')"
echo.

echo [2] Counting test directories...
dir /b /s /ad sp800-22-results 2>nul | find /c "-bit" > temp.txt
set /p bitcount=<temp.txt
dir /b /s /ad sp800-22-results 2>nul | find /c "-blocks" > temp.txt
set /p blockcount=<temp.txt
dir /b /s /ad sp800-22-results 2>nul | find /c "-master" > temp.txt
set /p mastercount=<temp.txt
del temp.txt
set /a total=%bitcount%+%blockcount%+%mastercount%
echo   Found %total% test directories (Expected: 33)
echo.

echo [3] Checking for FAILED configurations...
findstr /s /m "\"status\": \"FAILED\"" sp800-22-results\*\*\summary.json 2>nul
if %errorlevel%==1 (
    echo   SUCCESS: No failed configurations found!
) else (
    echo   WARNING: Found failed configurations!
)
echo.

echo [4] Verifying entropy assessments exist...
if exist sp800-90b-results\entropy-assessment-standard.txt (
    echo   [OK] entropy-assessment-standard.txt found
) else (
    echo   [!!] entropy-assessment-standard.txt missing
)
if exist sp800-90b-results\entropy-assessment-enhanced.txt (
    echo   [OK] entropy-assessment-enhanced.txt found
) else (
    echo   [!!] entropy-assessment-enhanced.txt missing
)
if exist sp800-90b-results\entropy-assessment-maximum.txt (
    echo   [OK] entropy-assessment-maximum.txt found
) else (
    echo   [!!] entropy-assessment-maximum.txt missing
)
echo.

echo ============================================
echo    Verification Complete
echo ============================================
pause
```

## Step 4: PowerShell Script for Detailed Verification

Create `verify_windows.ps1`:

```powershell
# SQEF NIST Validation Verification Script for Windows
Write-Host "`nSQEF NIST Validation Verification" -ForegroundColor Green
Write-Host ("=" * 50) -ForegroundColor Green

# Check if running from correct directory
if (-not (Test-Path "MASTER_SUMMARY.json")) {
    Write-Host "ERROR: MASTER_SUMMARY.json not found. Run from repository root." -ForegroundColor Red
    exit
}

# Load and check master summary
Write-Host "`n[1] Master Summary Analysis:" -ForegroundColor Yellow
$master = Get-Content "MASTER_SUMMARY.json" | ConvertFrom-Json
Write-Host "    Total Configurations: $($master.metadata.total_test_configurations)"
Write-Host "    All Configurations Pass: $($master.metadata.all_configurations_pass)"

if ($master.metadata.all_configurations_pass -eq $true) {
    Write-Host "    ✓ MASTER VALIDATION PASSED" -ForegroundColor Green
} else {
    Write-Host "    ✗ MASTER VALIDATION FAILED" -ForegroundColor Red
}

# Count and verify test directories
Write-Host "`n[2] Test Directory Verification:" -ForegroundColor Yellow
$dirs = Get-ChildItem -Path "sp800-22-results" -Recurse -Directory | 
        Where-Object {$_.Name -match "bit|blocks|master"}
Write-Host "    Directories Found: $($dirs.Count)"
Write-Host "    Expected: 33"

if ($dirs.Count -eq 33) {
    Write-Host "    ✓ Directory count correct" -ForegroundColor Green
} else {
    Write-Host "    ✗ Directory count mismatch" -ForegroundColor Red
}

# Check each configuration
Write-Host "`n[3] Individual Configuration Status:" -ForegroundColor Yellow
$passCount = 0
$failCount = 0
$configs = @{}

foreach ($dir in $dirs) {
    $summaryPath = Join-Path $dir.FullName "summary.json"
    if (Test-Path $summaryPath) {
        $summary = Get-Content $summaryPath | ConvertFrom-Json
        $status = $summary.overall_results.status
        $passRate = $summary.overall_results.pass_percentage
        $secLevel = $dir.Parent.Name
        
        if ($status -eq "PASSED") {
            $passCount++
            Write-Host "    ✓ " -NoNewline -ForegroundColor Green
        } else {
            $failCount++
            Write-Host "    ✗ " -NoNewline -ForegroundColor Red
        }
        
        $configName = "$secLevel/$($dir.Name)"
        Write-Host "$configName : $passRate"
        
        # Track by security level
        if (-not $configs.ContainsKey($secLevel)) {
            $configs[$secLevel] = @()
        }
        $configs[$secLevel] += [PSCustomObject]@{
            KeySize = $dir.Name
            PassRate = $passRate
            Status = $status
        }
    }
}

# Summary by security level
Write-Host "`n[4] Summary by Security Level:" -ForegroundColor Yellow
foreach ($level in $configs.Keys | Sort-Object) {
    $levelConfigs = $configs[$level]
    $levelPassed = ($levelConfigs | Where-Object {$_.Status -eq "PASSED"}).Count
    Write-Host "    $level : $levelPassed/$($levelConfigs.Count) configurations passed"
}

# Entropy assessment check
Write-Host "`n[5] Entropy Assessment Files:" -ForegroundColor Yellow
$entropyFiles = @(
    "sp800-90b-results\entropy-assessment-standard.txt",
    "sp800-90b-results\entropy-assessment-enhanced.txt",
    "sp800-90b-results\entropy-assessment-maximum.txt"
)

foreach ($file in $entropyFiles) {
    if (Test-Path $file) {
        $size = (Get-Item $file).Length
        Write-Host "    ✓ $(Split-Path $file -Leaf) ($size bytes)" -ForegroundColor Green
    } else {
        Write-Host "    ✗ $(Split-Path $file -Leaf) NOT FOUND" -ForegroundColor Red
    }
}

# Final summary
Write-Host "`n" ("=" * 50) -ForegroundColor Green
Write-Host "VERIFICATION SUMMARY" -ForegroundColor Green
Write-Host ("=" * 50) -ForegroundColor Green
Write-Host "Total Configurations: $($dirs.Count)"
Write-Host "Passed: $passCount" -ForegroundColor Green
Write-Host "Failed: $failCount" -ForegroundColor $(if ($failCount -eq 0) {"Green"} else {"Red"})

if ($passCount -eq 33 -and $failCount -eq 0) {
    Write-Host "`n✓✓✓ ALL VALIDATIONS PASSED ✓✓✓" -ForegroundColor Green
} else {
    Write-Host "`n✗✗✗ VALIDATION ISSUES FOUND ✗✗✗" -ForegroundColor Red
}
```

Run with:
```cmd
powershell -ExecutionPolicy Bypass -File verify_windows.ps1
```

## Step 5: Common Windows Commands

### Count Test Directories

```cmd
REM Using dir command
dir /b /s /ad sp800-22-results | find /c "-bit"
dir /b /s /ad sp800-22-results | find /c "-blocks"
dir /b /s /ad sp800-22-results | find /c "-master"
```

### Find All PASSED Status

```cmd
REM Find all passed configurations
findstr /s "\"status\": \"PASSED\"" sp800-22-results\*\*\summary.json

REM Count passed configurations
findstr /s /m "\"status\": \"PASSED\"" sp800-22-results\*\*\summary.json | find /c "summary.json"
```

### Check Pass Rates

```cmd
REM Find all pass rates
findstr /s "pass_percentage" sp800-22-results\*\*\summary.json

REM Find configurations below 99%
findstr /s "\"pass_percentage\": \"98" sp800-22-results\*\*\summary.json
```

### Verify Entropy Results

```cmd
REM Check entropy values in summaries
findstr /s "min_entropy" sp800-22-results\*\*\summary.json

REM View entropy assessment files
type sp800-90b-results\entropy-assessment-standard.txt | more
```

## Step 6: Windows Python One-Liners

```cmd
REM Check all configurations passed
python -c "import json; d=json.load(open('MASTER_SUMMARY.json')); print('All Pass:', d['metadata']['all_configurations_pass'])"

REM Count configurations
python -c "import json; d=json.load(open('MASTER_SUMMARY.json')); print('Total:', d['metadata']['total_test_configurations'])"

REM List all pass rates
python -c "import json, glob; [print(f.split('\\')[-2:], json.load(open(f))['overall_results']['pass_percentage']) for f in glob.glob('sp800-22-results/*/*/summary.json')]"

REM Find lowest pass rate
python -c "import json, glob; rates = [float(json.load(open(f))['overall_results']['overall_pass_rate']) for f in glob.glob('sp800-22-results/*/*/summary.json')]; print(f'Lowest: {min(rates)*100:.2f}%')"
```

## Step 7: Verification Checklist (Windows)

Use Windows Explorer and these commands to verify:

- [ ] **File Structure**
  ```cmd
  dir /b sp800-22-results
  REM Should show: test-results-STANDARD-512, test-results-ENHANCED-128, test-results-MAXIMUM-32
  ```

- [ ] **Count Configurations**
  ```cmd
  dir /b /s /ad sp800-22-results | find /c "summary.json"
  REM Should show: 33
  ```

- [ ] **Check All Pass**
  ```cmd
  findstr /s /m "\"status\": \"FAILED\"" sp800-22-results\*\*\summary.json
  REM Should show nothing (no failures)
  ```

- [ ] **Verify Entropy Files**
  ```cmd
  dir sp800-90b-results\*.txt
  REM Should show 3 entropy assessment files
  ```

## Step 8: Troubleshooting (Windows)

### Issue: Python not recognized

```cmd
REM Check if Python is installed
where python

REM If not found, add Python to PATH or use full path
C:\Python39\python.exe --version
```

### Issue: Cannot run PowerShell scripts

```cmd
REM Run PowerShell with bypass
powershell -ExecutionPolicy Bypass -File verify_windows.ps1

REM Or change execution policy (admin required)
powershell Set-ExecutionPolicy RemoteSigned
```

### Issue: Wildcards not working

```cmd
REM Use quotes around wildcards
python parse_nist_output.py "..\sp800-22-results\*\*\*.txt"

REM Or use explicit paths
python parse_nist_output.py ..\sp800-22-results\test-results-ENHANCED-128\256-bit\finalAnalysisReport.txt
```

### Issue: Access denied errors

```cmd
REM Run as administrator
REM Right-click Command Prompt -> Run as Administrator

REM Or check file permissions
icacls sp800-22-results
```

## Quick Validation Script (save as validate.cmd)

```batch
@echo off
cls
echo Quick SQEF Validation Check
echo ===========================
python -c "import json; d=json.load(open('MASTER_SUMMARY.json')); print('Result:', 'PASS' if d['metadata']['all_configurations_pass'] else 'FAIL')"
pause
```

## Validation Certification Statement

Based on the Windows verification steps above, you should be able to confirm:

> "The SQEF entropy source has been validated against NIST SP 800-22 Rev. 1a and SP 800-90B requirements on Windows platform. All 33 tested configurations (11 key sizes × 3 security levels) pass the statistical randomness tests with pass rates between 98.40% and 100%, exceeding the required 96% threshold."

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

*See VERIFICATION_GUIDE_LINUX.md for Linux/Unix commands*