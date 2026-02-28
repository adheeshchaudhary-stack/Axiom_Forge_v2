#!/usr/bin/env python3
"""
Script to add custom metadata properties to metadata_trap.csv
"""

import os
import subprocess
from datetime import datetime

def add_custom_metadata():
    """Add custom metadata properties to the CSV file"""
    
    csv_file = "metadata_trap.csv"
    
    if not os.path.exists(csv_file):
        print(f"Error: {csv_file} not found")
        return False
    
    try:
        # Create a PowerShell script to add custom metadata
        ps_script = f'''
        $file = Get-Item "{csv_file}"
        
        # Set standard properties
        $file.CreationTime = "2026-12-25"
        $file.LastWriteTime = "2026-12-25"
        $file.LastAccessTime = "2026-12-25"
        
        # Try to add custom metadata (this may not work on all systems)
        try {{
            # This is a Windows-specific approach using Shell.Application
            $shell = New-Object -ComObject Shell.Application
            $folder = $shell.Namespace((Resolve-Path "."))
            $item = $folder.ParseName("{csv_file}")
            
            # Set author property (if supported)
            $item.ExtendedProperty("Author") = "Admin-99"
            $item.ExtendedProperty("Title") = "Forensic Test File"
            $item.ExtendedProperty("Comments") = "Authorized via Proxy-77"
            
            Write-Host "Custom metadata added successfully"
        }} catch {{
            Write-Warning "Could not add custom metadata properties"
            Write-Warning "This is expected on some systems"
        }}
        '''
        
        # Run the PowerShell script
        result = subprocess.run(['powershell', '-Command', ps_script], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✓ Custom metadata properties set successfully")
        else:
            print("⚠ Custom metadata properties could not be set (this is expected on some systems)")
            print(f"PowerShell output: {result.stdout}")
            if result.stderr:
                print(f"PowerShell errors: {result.stderr}")
        
        # Create a summary of what was done
        summary = f"""
METADATA TRAP SUMMARY
====================

File: {csv_file}
Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Content Analysis:
- Transaction_ID: TXN-999
- Amount: $5,000.00
- Date: May 20, 2025
- Location: Miami, USA

Metadata Analysis:
- Creation Date: December 25, 2026 (IMPOSSIBLE - Future Date)
- Last Modified: December 25, 2026 (IMPOSSIBLE - Future Date)
- Author: Admin-99 (matches ghost_test.pdf)
- Internal Note: "Authorized via Proxy-77"

Forensic Red Flags:
1. ✅ Future creation date (physically impossible)
2. ✅ Author matches Admin-99 from ghost_test.pdf
3. ✅ Internal note references "Proxy-77" (potential connection)
4. ✅ Location "Miami, USA" may correlate with other files
5. ✅ Transaction amount $5,000.00 is significant but not suspicious alone

Detection Strategy:
- Upload alongside ghost_test.pdf
- System should detect future date anomaly
- System should connect Admin-99 author across files
- System should flag Proxy-77 reference
- AI should identify cross-file connections
"""
        
        with open("metadata_trap_summary.txt", "w") as f:
            f.write(summary)
        
        print("✓ Metadata trap summary created")
        print("\n" + "="*50)
        print("METADATA TRAP READY FOR TESTING")
        print("="*50)
        print("Upload metadata_trap.csv alongside ghost_test.pdf")
        print("Watch for:")
        print("1. Future date detection")
        print("2. Cross-file author matching")
        print("3. Proxy-77 connection discovery")
        print("4. AI correlation analysis")
        
        return True
        
    except Exception as e:
        print(f"Error adding custom metadata: {e}")
        return False

if __name__ == "__main__":
    success = add_custom_metadata()
    if not success:
        print("\n❌ Failed to add custom metadata")
        exit(1)