#!/usr/bin/env python3
"""
Script to set metadata properties on the metadata_trap.csv file
"""

import os
import sys
from datetime import datetime
import subprocess

def set_file_metadata():
    """Set metadata properties on the CSV file"""
    
    # File path
    csv_file = "metadata_trap.csv"
    
    if not os.path.exists(csv_file):
        print(f"Error: {csv_file} not found")
        return False
    
    try:
        # Set file creation date to future date (2026-12-25)
        # Note: This is a Windows-specific operation
        future_date = "2026-12-25"
        print(f"Setting creation date to: {future_date}")
        
        # On Windows, we can use PowerShell to set file properties
        if os.name == 'nt':  # Windows
            # Set creation time using PowerShell
            ps_command = f'''
            $file = Get-Item "{csv_file}"
            $file.CreationTime = "2026-12-25"
            $file.LastWriteTime = "2026-12-25"
            $file.LastAccessTime = "2026-12-25"
            '''
            
            try:
                subprocess.run(['powershell', '-Command', ps_command], check=True)
                print("✓ File timestamps updated successfully")
            except subprocess.CalledProcessError as e:
                print(f"Warning: Could not set file timestamps: {e}")
        
        # Create a simple metadata file to document the trap
        metadata_doc = f"""
METADATA TRAP DOCUMENTATION
===========================

File: {csv_file}
Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Content:
- Transaction_ID: TXN-999
- Amount: 5000.00
- Date: 2025-05-20
- Location: Miami, USA

Metadata Trap Properties:
- Author: Admin-99
- Creation Date: 2026-12-25 (Future date - RED FLAG)
- Internal_Note: Authorized via Proxy-77

Purpose:
This file is designed to test the forensic system's ability to detect:
1. Future creation dates (impossible)
2. Hidden metadata fields
3. Connection between metadata and content
4. Cross-references with other files (like ghost_test.pdf)

Detection Points:
- File created in future (2026-12-25)
- Author field matches Admin-99 from ghost_test.pdf
- Internal_Note references Proxy-77 (potential connection)
- Location "Miami, USA" may correlate with other files
"""
        
        with open("metadata_trap_documentation.txt", "w") as f:
            f.write(metadata_doc)
        
        print("✓ Metadata trap documentation created")
        print("✓ metadata_trap.csv is ready for upload")
        print("\nFile Properties:")
        print(f"- Content: Normal-looking transaction")
        print(f"- Author: Admin-99 (matches ghost_test.pdf)")
        print(f"- Creation Date: 2026-12-25 (Future date - IMPOSSIBLE)")
        print(f"- Internal_Note: 'Authorized via Proxy-77'")
        
        return True
        
    except Exception as e:
        print(f"Error setting metadata: {e}")
        return False

if __name__ == "__main__":
    success = set_file_metadata()
    if success:
        print("\n✅ Metadata trap successfully created!")
        print("Upload metadata_trap.csv alongside ghost_test.pdf to test the system.")
    else:
        print("\n❌ Failed to create metadata trap")
        sys.exit(1)