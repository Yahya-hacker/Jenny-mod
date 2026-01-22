#!/usr/bin/env python3
"""
Package the Bedrock addon into a .mcaddon file
Creates proper BP and RP zip structure for Minecraft Bedrock
"""
import zipfile
import os
from pathlib import Path

def create_mcaddon():
    """Create .mcaddon package from BP and RP directories"""
    base_dir = Path('/home/runner/work/Jenny-mod/Jenny-mod')
    output_file = base_dir / 'Jenny_Mod_Bedrock_v1.0.0.mcaddon'
    
    # Temporary zip files
    bp_zip = base_dir / 'BP.zip'
    rp_zip = base_dir / 'RP.zip'
    
    print("Creating Behavior Pack zip...")
    with zipfile.ZipFile(bp_zip, 'w', zipfile.ZIP_DEFLATED) as zf:
        bp_dir = base_dir / 'BP'
        for root, dirs, files in os.walk(bp_dir):
            for file in files:
                file_path = Path(root) / file
                arcname = file_path.relative_to(bp_dir.parent)
                zf.write(file_path, arcname)
                print(f"  Added: {arcname}")
    
    print("\nCreating Resource Pack zip...")
    with zipfile.ZipFile(rp_zip, 'w', zipfile.ZIP_DEFLATED) as zf:
        rp_dir = base_dir / 'RP'
        for root, dirs, files in os.walk(rp_dir):
            for file in files:
                file_path = Path(root) / file
                arcname = file_path.relative_to(rp_dir.parent)
                zf.write(file_path, arcname)
                print(f"  Added: {arcname}")
    
    print("\nCreating .mcaddon package...")
    with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_STORED) as mcaddon:
        mcaddon.write(bp_zip, 'BP.zip')
        mcaddon.write(rp_zip, 'RP.zip')
    
    # Clean up temporary files
    bp_zip.unlink()
    rp_zip.unlink()
    
    file_size = output_file.stat().st_size / (1024 * 1024)
    print(f"\n✓ Created: {output_file.name}")
    print(f"  Size: {file_size:.2f} MB")
    print("\nInstallation:")
    print("  1. Copy .mcaddon file to your device")
    print("  2. Open with Minecraft Bedrock Edition")
    print("  3. Enable both packs in world settings")
    print("  4. Enable Experimental Features (Beta APIs, Molang)")

if __name__ == '__main__':
    create_mcaddon()
