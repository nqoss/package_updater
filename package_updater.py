#!/usr/bin/env python3

import subprocess
import re
import sys
import argparse
from typing import List, Dict, Tuple

class PackageUpdater:
    def __init__(self, dry_run=False, verbose=False):
        self.dry_run = dry_run
        self.verbose = verbose
        self.updatable_packages = []
        self.removable_packages = []
        
    def run_command(self, command: List[str]) -> Tuple[bool, str]:
        try:
            if self.verbose:
                print(f"Running: {' '.join(command)}")
                
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=False
            )
            
            if result.returncode != 0 and self.verbose:
                print(f"Command failed: {result.stderr}")
                
            return result.returncode == 0, result.stdout
        except Exception as e:
            if self.verbose:
                print(f"Error running command: {e}")
            return False, str(e)
    
    def check_apt_updates(self) -> bool:
        print("Checking for APT package updates...")
        
        success, _ = self.run_command(["sudo", "apt", "update"])
        if not success:
            print("Failed to update package lists")
            return False
        
        success, output = self.run_command(["apt", "list", "--upgradable"])
        if not success:
            print("Failed to check upgradable packages")
            return False
        
        packages = []
        for line in output.strip().split('\n'):
            if line and '/' in line and not line.startswith('Listing...'):
                match = re.match(r'^([^/]+)/(?:\S+)\s+(\S+)\s+(\S+).*$', line)
                if match:
                    package_name = match.group(1)
                    current_version = match.group(2)
                    new_version = match.group(3)
                    packages.append({
                        'name': package_name,
                        'current': current_version,
                        'available': new_version
                    })
        
        self.updatable_packages = packages
        
        if packages:
            print(f"Found {len(packages)} packages that can be updated:")
            for pkg in packages:
                print(f"   {pkg['name']}: {pkg['current']} → {pkg['available']}")
        else:
            print("All APT packages are up to date")
            
        return True
    
    def check_flatpak_updates(self) -> bool:
        print("Checking for Flatpak updates...")
        
        success, _ = self.run_command(["which", "flatpak"])
        if not success:
            print("Flatpak not installed, skipping")
            return True
        
        success, output = self.run_command(["flatpak", "remote-ls", "--updates"])
        if not success:
            print("Failed to check Flatpak updates")
            return False
        
        flatpak_updates = []
        for line in output.strip().split('\n'):
            if line:
                parts = line.split('\t')
                if len(parts) >= 3:
                    flatpak_updates.append({
                        'name': parts[0],
                        'arch': parts[1],
                        'branch': parts[2]
                    })
        
        if flatpak_updates:
            print(f"Found {len(flatpak_updates)} Flatpak packages that can be updated:")
            for pkg in flatpak_updates:
                print(f"   {pkg['name']} ({pkg['arch']})")
        else:
            print("All Flatpak packages are up to date")
            
        return True
    
    def check_autoremove(self) -> bool:
        print("Checking for orphaned packages...")
        
        success, output = self.run_command(["apt", "autoremove", "--dry-run"])
        if not success:
            print("Failed to check autoremove candidates")
            return False
        
        packages = []
        in_package_list = False
        
        for line in output.strip().split('\n'):
            if 'The following packages will be REMOVED:' in line:
                in_package_list = True
                continue
            elif in_package_list and line.strip() and not line.startswith(' ' * 3):
                break
            elif in_package_list and line.strip():
                package_name = line.strip().split()[0]
                if package_name and package_name not in packages:
                    packages.append(package_name)
        
        self.removable_packages = packages
        
        if packages:
            print(f"Found {len(packages)} packages that can be removed:")
            for pkg in packages:
                print(f"   {pkg}")
        else:
            print("No orphaned packages found")
            
        return True
    
    def update_apt_packages(self) -> bool:
        if not self.updatable_packages:
            print("No APT packages to update")
            return True
        
        print(f"Updating {len(self.updatable_packages)} APT packages...")
        
        if self.dry_run:
            print("Dry run - would run: sudo apt upgrade -y")
            return True
        
        success, output = self.run_command(["sudo", "apt", "upgrade", "-y"])
        if success:
            print("APT packages updated successfully")
            return True
        else:
            print("Failed to update APT packages")
            return False
    
    def update_flatpak_packages(self) -> bool:
        print("Updating Flatpak packages...")
        
        if self.dry_run:
            print("Dry run - would run: flatpak update -y")
            return True
        
        success, output = self.run_command(["flatpak", "update", "-y"])
        if success:
            print("Flatpak packages updated successfully")
            return True
        else:
            print("Failed to update Flatpak packages")
            return False
    
    def clean_orphaned_packages(self) -> bool:
        if not self.removable_packages:
            print("No packages to clean")
            return True
        
        print(f"Removing {len(self.removable_packages)} orphaned packages...")
        
        if self.dry_run:
            print("Dry run - would run: sudo apt autoremove -y")
            return True
        
        success, output = self.run_command(["sudo", "apt", "autoremove", "-y"])
        if success:
            print("Orphaned packages removed successfully")
            return True
        else:
            print("Failed to remove orphaned packages")
            return False
    
    def clean_cache(self) -> bool:
        print("Cleaning package cache...")
        
        if self.dry_run:
            print("Dry run - would run: sudo apt autoclean")
            return True
        
        success, output = self.run_command(["sudo", "apt", "autoclean"])
        if success:
            print("Package cache cleaned successfully")
            return True
        else:
            print("Failed to clean package cache")
            return False
    
    def full_update_and_clean(self) -> bool:
        print("Starting full system update and clean...")
        
        if not self.check_apt_updates():
            return False
        
        if not self.check_flatpak_updates():
            return False
        
        if not self.check_autoremove():
            return False
        
        print("="*50)
        
        success = True
        
        if self.updatable_packages:
            if not self.update_apt_packages():
                success = False
        
        if not self.update_flatpak_packages():
            pass
        
        if not self.clean_orphaned_packages():
            success = False
        
        if not self.clean_cache():
            success = False
        
        if success:
            print("Update and clean completed successfully!")
        else:
            print("Update completed with some errors")
        
        return success

def main():
    parser = argparse.ArgumentParser(description='Debian Package Updater and Cleaner')
    parser.add_argument('--dry-run', action='store_true')
    parser.add_argument('--verbose', action='store_true')
    parser.add_argument('--check-only', action='store_true')
    
    args = parser.parse_args()
    
    updater = PackageUpdater(dry_run=args.dry_run, verbose=args.verbose)
    
    if args.check_only:
        updater.check_apt_updates()
        updater.check_flatpak_updates()
        updater.check_autoremove()
    else:
        success = updater.full_update_and_clean()
        sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()