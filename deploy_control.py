#!/usr/bin/env python3
"""
Deployment Control System for Railway.app
Manages which version gets deployed to production
"""

import os
import shutil
import subprocess
import json
from datetime import datetime

class DeploymentController:
    def __init__(self):
        self.root_dir = os.getcwd()
        self.backup_dir = os.path.join(self.root_dir, "deployment_versions")
        self.current_version = "stable"
        
    def create_version(self, version_name, description=""):
        """Create a new version snapshot"""
        if not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir)
            
        version_path = os.path.join(self.backup_dir, version_name)
        if os.path.exists(version_path):
            print(f"⚠️  Version {version_name} already exists!")
            return False
            
        os.makedirs(version_path)
        
        # Copy current production files
        files_to_backup = [
            'app.py', 'dashboard.html', 'requirements.txt', 
            'runtime.txt', 'Procfile', 'railway.json', '.env.example',
            'README.md', '.gitignore'
        ]
        
        for file in files_to_backup:
            if os.path.exists(file):
                shutil.copy2(file, version_path)
                
        # Create version info
        version_info = {
            "created": datetime.now().isoformat(),
            "description": description,
            "files": files_to_backup,
            "git_commit": self.get_current_commit()
        }
        
        with open(os.path.join(version_path, "version_info.json"), "w") as f:
            json.dump(version_info, f, indent=2)
            
        print(f"✅ Version '{version_name}' created successfully!")
        return True
    
    def get_current_commit(self):
        """Get current git commit hash"""
        try:
            result = subprocess.run(['git', 'rev-parse', 'HEAD'], 
                                 capture_output=True, text=True, check=True)
            return result.stdout.strip()[:8]
        except:
            return "unknown"
        
    def list_versions(self):
        """List all available versions"""
        if not os.path.exists(self.backup_dir):
            print("📁 No versions created yet")
            return []
            
        versions = []
        for item in os.listdir(self.backup_dir):
            version_path = os.path.join(self.backup_dir, item)
            if os.path.isdir(version_path):
                info_file = os.path.join(version_path, "version_info.json")
                if os.path.exists(info_file):
                    with open(info_file, 'r') as f:
                        info = json.load(f)
                        versions.append({
                            "name": item,
                            "created": info.get("created", "Unknown"),
                            "description": info.get("description", "No description"),
                            "git_commit": info.get("git_commit", "unknown")
                        })
                        
        # Sort by creation date
        versions.sort(key=lambda x: x["created"], reverse=True)
        return versions
        
    def deploy_version(self, version_name):
        """Deploy a specific version to Railway"""
        version_path = os.path.join(self.backup_dir, version_name)
        if not os.path.exists(version_path):
            print(f"❌ Version '{version_name}' not found!")
            return False
            
        # Backup current production
        backup_name = f"backup_before_{version_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.create_version(backup_name, f"Auto backup before deploying {version_name}")
        
        # Copy version files to root
        for item in os.listdir(version_path):
            if item != "version_info.json":
                src = os.path.join(version_path, item)
                dst = os.path.join(self.root_dir, item)
                if os.path.isfile(src):
                    shutil.copy2(src, dst)
                    print(f"📁 Restored: {item}")
                    
        print(f"📦 Version '{version_name}' deployed to production!")
        
        # Ask for git commit
        commit_msg = f"Deploy version: {version_name}"
        choice = input(f"💾 Commit and push to Railway? (y/n): ")
        if choice.lower() == 'y':
            self.git_deploy(commit_msg)
            
        return True
        
    def git_deploy(self, commit_msg):
        """Commit and push to Railway"""
        try:
            subprocess.run(["git", "add", "."], check=True)
            subprocess.run(["git", "commit", "-m", commit_msg], check=True)
            subprocess.run(["git", "push", "origin", "main"], check=True)
            print("🚀 Successfully deployed to Railway!")
        except subprocess.CalledProcessError as e:
            print(f"❌ Git deployment failed: {e}")
    
    def show_current_status(self):
        """Show current production status"""
        print("\n📊 Current Production Status")
        print("=" * 40)
        
        # Show current files
        files = ['app.py', 'dashboard.html', 'requirements.txt', 'runtime.txt', 'Procfile', 'railway.json']
        for file in files:
            if os.path.exists(file):
                stat = os.stat(file)
                mod_time = datetime.fromtimestamp(stat.st_mtime)
                print(f"  ✅ {file:<15} (modified: {mod_time.strftime('%Y-%m-%d %H:%M')})")
            else:
                print(f"  ❌ {file:<15} (missing)")
        
        # Show git status
        try:
            result = subprocess.run(['git', 'status', '--porcelain'], 
                                 capture_output=True, text=True, check=True)
            if result.stdout.strip():
                print(f"\n⚠️  Uncommitted changes detected!")
                print(result.stdout)
            else:
                print(f"\n✅ Git working tree clean")
                
            # Show last commit
            result = subprocess.run(['git', 'log', '--oneline', '-1'], 
                                 capture_output=True, text=True, check=True)
            print(f"📝 Last commit: {result.stdout.strip()}")
        except:
            print("\n❌ Git status unavailable")

def main():
    controller = DeploymentController()
    
    print("🎯 Railway Deployment Controller v1.0")
    print("=====================================")
    print("Single source control for Railway.app deployments")
    print("")
    
    while True:
        print("\n📋 Available Actions:")
        print("1. 📦 Create new version snapshot")
        print("2. 📋 List all versions")
        print("3. 🚀 Deploy version to Railway")
        print("4. 📊 Show current production status")
        print("5. 🧹 Clean up old versions")
        print("6. 👋 Exit")
        
        choice = input("\n🎯 Select option (1-6): ").strip()
        
        if choice == "1":
            print("\n📦 Create New Version")
            print("-" * 20)
            name = input("📝 Version name (e.g., 'v1.1', 'feature-alerts'): ").strip()
            if not name:
                print("❌ Version name cannot be empty")
                continue
            desc = input("📝 Description (optional): ").strip()
            controller.create_version(name, desc)
            
        elif choice == "2":
            print("\n📋 Available Versions")
            print("-" * 20)
            versions = controller.list_versions()
            if not versions:
                print("📁 No versions found. Create one first!")
            else:
                for i, v in enumerate(versions, 1):
                    created_date = v['created'][:10] if v['created'] != "Unknown" else "Unknown"
                    print(f"  {i:2}. {v['name']:<20} | {created_date} | {v['description']}")
                    if v['git_commit'] != "unknown":
                        print(f"      📝 Git: {v['git_commit']}")
                
        elif choice == "3":
            print("\n🚀 Deploy to Railway")
            print("-" * 20)
            versions = controller.list_versions()
            if not versions:
                print("❌ No versions available to deploy")
                continue
                
            print("📦 Available Versions:")
            for i, v in enumerate(versions, 1):
                created_date = v['created'][:10] if v['created'] != "Unknown" else "Unknown"
                print(f"  {i:2}. {v['name']:<20} | {created_date} | {v['description']}")
                
            try:
                selection = input("\n🎯 Select version number (or 'q' to cancel): ").strip()
                if selection.lower() == 'q':
                    continue
                    
                idx = int(selection) - 1
                if 0 <= idx < len(versions):
                    version = versions[idx]
                    print(f"\n⚠️  You are about to deploy: {version['name']}")
                    print(f"📝 Description: {version['description']}")
                    confirm = input("🚀 Proceed with deployment? (y/n): ").strip().lower()
                    if confirm == 'y':
                        controller.deploy_version(version['name'])
                    else:
                        print("❌ Deployment cancelled")
                else:
                    print("❌ Invalid selection")
            except ValueError:
                print("❌ Please enter a valid number")
                
        elif choice == "4":
            controller.show_current_status()
                
        elif choice == "5":
            print("\n🧹 Clean Up Versions")
            print("-" * 20)
            versions = controller.list_versions()
            backup_versions = [v for v in versions if v['name'].startswith('backup_before_')]
            
            if backup_versions:
                print(f"📁 Found {len(backup_versions)} auto-backup versions")
                if input("🗑️  Delete old auto-backups? (y/n): ").strip().lower() == 'y':
                    for v in backup_versions:
                        version_path = os.path.join(controller.backup_dir, v['name'])
                        shutil.rmtree(version_path)
                        print(f"🗑️  Deleted: {v['name']}")
                    print("✅ Cleanup completed!")
            else:
                print("✅ No auto-backups to clean")
                
        elif choice == "6":
            print("\n👋 Goodbye!")
            print("🎯 Your Railway deployment is under control!")
            break
            
        else:
            print("❌ Invalid choice. Please select 1-6.")

if __name__ == "__main__":
    main()