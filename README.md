# Browser History & Password Extraction Tool

## Overview

This is a Windows-based utility designed for authorized internal investigations and digital forensics purposes only. The tool extracts browser history and credentials from major web browsers installed on the target system.

## ⚠️ Legal Notice

**IMPORTANT**: This tool is intended exclusively for:
- Internal IT security investigations within your organization
- Authorized forensic analysis by trained personnel
- Compliance with company security policies

**Disclaimer**: The creator assumes no responsibility for unauthorized use or misuse of this application. Users are solely responsible for ensuring compliance with all applicable local, state, and federal laws, including computer fraud and unauthorized access statutes. Unauthorized access to computer systems is illegal. This tool should only be used with explicit written authorization from the system owner.

## Features

- **Browser History Extraction**: Retrieve browsing history from supported browsers
- **Credential Recovery**: Extract stored passwords and authentication data
- **Automated Compilation**: Build portable executable via batch script
- **Logging Support**: Comprehensive execution logs for audit trails

## Requirements

- Windows OS (7 and above)
- Python 3.7 or higher
- Administrator privileges
- Supported browsers: Chrome, Firefox, Edge, IE

## Installation

1. Clone or download this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### As Python Script
```bash
python main.py
```

### As Compiled Executable
```bash
build_exe.bat
```
Then run the generated executable from the output directory.

## Output

All extracted data is stored in the `output/` directory with timestamped files and execution logs.

## Support & Contribution

This tool is maintained for internal use only. External contributions or support requests are not accepted.