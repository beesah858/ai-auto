"""
File & System Management Engine
Handles file operations, batch renaming, organization, and system tasks
"""

import os
import shutil
import hashlib
from datetime import datetime
from pathlib import Path


class FileManagerEngine:
    def __init__(self, log_callback=None):
        self.log_callback = log_callback or (lambda msg: None)
        
        # File type categories for organization
        self.file_categories = {
            'Images': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.ico', '.webp', '.tiff'],
            'Videos': ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm', '.m4v'],
            'Audio': ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.wma', '.m4a'],
            'Documents': ['.pdf', '.doc', '.docx', '.txt', '.rtf', '.odt', '.xls', '.xlsx', '.ppt', '.pptx'],
            'Archives': ['.zip', '.rar', '.7z', '.tar', '.gz', '.bz2'],
            'Code': ['.py', '.js', '.html', '.css', '.java', '.cpp', '.c', '.h', '.cs', '.php', '.rb', '.go', '.rs'],
            'Executables': ['.exe', '.msi', '.app', '.dmg', '.deb', '.rpm'],
        }
    
    def log(self, message):
        """Log a message with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_callback(f"[{timestamp}] {message}")
    
    def get_directory_contents(self, path):
        """Get contents of a directory with file info"""
        try:
            path = Path(path)
            if not path.exists():
                self.log(f"Path does not exist: {path}")
                return []
            
            items = []
            for item in path.iterdir():
                try:
                    stat = item.stat()
                    item_type = "folder" if item.is_dir() else "file"
                    size = stat.st_size if item.is_file() else 0
                    modified = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M")
                    
                    # Get file extension/type
                    if item.is_file():
                        ext = item.suffix.lower()
                        file_type = ext[1:].upper() if ext else "File"
                    else:
                        file_type = "Folder"
                    
                    items.append({
                        'name': item.name,
                        'path': str(item),
                        'type': item_type,
                        'size': size,
                        'modified': modified,
                        'file_type': file_type,
                        'is_dir': item.is_dir()
                    })
                except (PermissionError, OSError) as e:
                    self.log(f"Error accessing {item}: {e}")
            
            # Sort: folders first, then files alphabetically
            items.sort(key=lambda x: (not x['is_dir'], x['name'].lower()))
            return items
        except Exception as e:
            self.log(f"Error reading directory: {e}")
            return []
    
    def batch_rename(self, files, mode, value="", dry_run=True):
        """
        Batch rename files with various modes
        files: list of file paths
        mode: one of 'prefix', 'suffix', 'find_replace', 'sequence', 'lowercase', 'uppercase', 'strip', 'date_prefix'
        value: the value to use for renaming (depends on mode)
        dry_run: if True, only preview changes
        """
        try:
            changes = []
            
            for i, filepath in enumerate(files):
                path = Path(filepath)
                if not path.exists() or path.is_dir():
                    continue
                
                stem = path.stem
                suffix = path.suffix
                parent = path.parent
                
                new_name = stem
                
                if mode == 'prefix':
                    new_name = f"{value}{stem}"
                
                elif mode == 'suffix':
                    new_name = f"{stem}{value}"
                
                elif mode == 'find_replace':
                    if ':' in value:
                        find, replace = value.split(':', 1)
                        new_name = stem.replace(find, replace)
                
                elif mode == 'sequence':
                    seq_value = value if value else "{:03d}".format(i + 1)
                    new_name = f"{stem}_{seq_value}"
                
                elif mode == 'lowercase':
                    new_name = stem.lower()
                
                elif mode == 'uppercase':
                    new_name = stem.upper()
                
                elif mode == 'strip':
                    # Remove special characters
                    new_name = ''.join(c for c in stem if c.isalnum() or c in ' -_')
                
                elif mode == 'date_prefix':
                    modified = datetime.fromtimestamp(path.stat().st_mtime)
                    date_str = modified.strftime("%Y%m%d")
                    new_name = f"{date_str}_{stem}"
                
                new_path = parent / f"{new_name}{suffix}"
                
                # Handle duplicate names
                counter = 1
                while new_path.exists() and new_path != path:
                    new_path = parent / f"{new_name}_{counter}{suffix}"
                    counter += 1
                
                changes.append({
                    'old': str(path),
                    'new': str(new_path),
                    'old_name': path.name,
                    'new_name': new_path.name
                })
            
            if dry_run:
                self.log(f"DRY RUN: {len(changes)} files would be renamed")
                for change in changes:
                    self.log(f"  {change['old_name']} → {change['new_name']}")
                return {'success': True, 'changes': changes, 'applied': False}
            
            # Apply changes
            applied = 0
            for change in changes:
                try:
                    os.rename(change['old'], change['new'])
                    applied += 1
                except Exception as e:
                    self.log(f"Error renaming {change['old']}: {e}")
            
            self.log(f"Renamed {applied} files")
            return {'success': True, 'changes': changes, 'applied': True, 'count': applied}
        
        except Exception as e:
            self.log(f"Batch rename error: {e}")
            return {'success': False, 'error': str(e)}
    
    def organize_by_type(self, source_path, dry_run=True):
        """Organize files into folders by type"""
        try:
            source = Path(source_path)
            moved = []
            
            for item in source.iterdir():
                if item.is_dir():
                    continue
                
                # Find category
                category = 'Other'
                ext = item.suffix.lower()
                for cat, extensions in self.file_categories.items():
                    if ext in extensions:
                        category = cat
                        break
                
                # Create category folder
                target_folder = source / category
                if not dry_run and not target_folder.exists():
                    target_folder.mkdir(exist_ok=True)
                
                # Move file
                target = target_folder / item.name
                
                # Handle duplicates
                counter = 1
                while target.exists():
                    target = target_folder / f"{item.stem}_{counter}{item.suffix}"
                    counter += 1
                
                if not dry_run:
                    shutil.move(str(item), str(target))
                
                moved.append({
                    'from': str(item),
                    'to': str(target),
                    'category': category
                })
            
            action = "Would move" if dry_run else "Moved"
            self.log(f"{action} {len(moved)} files into categorized folders")
            return {'success': True, 'moved': moved, 'dry_run': dry_run}
        
        except Exception as e:
            self.log(f"Organize by type error: {e}")
            return {'success': False, 'error': str(e)}
    
    def organize_by_date(self, source_path, dry_run=True):
        """Organize files into folders by modification date (YYYY-MM)"""
        try:
            source = Path(source_path)
            moved = []
            
            for item in source.iterdir():
                if item.is_dir():
                    continue
                
                # Get modification date
                modified = datetime.fromtimestamp(item.stat().st_mtime)
                date_folder = modified.strftime("%Y-%m")
                
                # Create date folder
                target_folder = source / date_folder
                if not dry_run and not target_folder.exists():
                    target_folder.mkdir(exist_ok=True)
                
                # Move file
                target = target_folder / item.name
                
                # Handle duplicates
                counter = 1
                while target.exists():
                    target = target_folder / f"{item.stem}_{counter}{item.suffix}"
                    counter += 1
                
                if not dry_run:
                    shutil.move(str(item), str(target))
                
                moved.append({
                    'from': str(item),
                    'to': str(target),
                    'date': date_folder
                })
            
            action = "Would move" if dry_run else "Moved"
            self.log(f"{action} {len(moved)} files into date-based folders")
            return {'success': True, 'moved': moved, 'dry_run': dry_run}
        
        except Exception as e:
            self.log(f"Organize by date error: {e}")
            return {'success': False, 'error': str(e)}
    
    def find_duplicates(self, path, by='name_size'):
        """Find duplicate files by name+size or by hash"""
        try:
            source = Path(path)
            duplicates = []
            
            if by == 'name_size':
                # Group by name and size
                file_groups = {}
                for item in source.rglob('*'):
                    if item.is_file():
                        try:
                            key = f"{item.name}_{item.stat().st_size}"
                            if key not in file_groups:
                                file_groups[key] = []
                            file_groups[key].append(str(item))
                        except (PermissionError, OSError):
                            pass
                
                # Find groups with more than one file
                for key, files in file_groups.items():
                    if len(files) > 1:
                        duplicates.append(files)
            
            elif by == 'hash':
                # Group by file hash (slower but more accurate)
                file_hashes = {}
                for item in source.rglob('*'):
                    if item.is_file():
                        try:
                            file_hash = self._get_file_hash(item)
                            if file_hash not in file_hashes:
                                file_hashes[file_hash] = []
                            file_hashes[file_hash].append(str(item))
                        except (PermissionError, OSError):
                            pass
                
                for hash_val, files in file_hashes.items():
                    if len(files) > 1:
                        duplicates.append(files)
            
            self.log(f"Found {len(duplicates)} groups of duplicate files")
            return {'success': True, 'duplicates': duplicates}
        
        except Exception as e:
            self.log(f"Find duplicates error: {e}")
            return {'success': False, 'error': str(e)}
    
    def _get_file_hash(self, filepath, chunk_size=8192):
        """Calculate MD5 hash of a file"""
        hash_md5 = hashlib.md5()
        with open(filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(chunk_size), b''):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
    def create_video_project(self, base_path, project_name):
        """Create a video project folder structure"""
        try:
            project_path = Path(base_path) / project_name
            folders = [
                '01_Raw_Footage',
                '02_Audio',
                '03_Images_Graphics',
                '04_Music_SFX',
                '05_Text_Templates',
                '06_Export'
            ]
            
            project_path.mkdir(parents=True, exist_ok=True)
            
            for folder in folders:
                (project_path / folder).mkdir(exist_ok=True)
            
            self.log(f"Created video project: {project_path}")
            return {'success': True, 'path': str(project_path), 'folders': folders}
        
        except Exception as e:
            self.log(f"Create project error: {e}")
            return {'success': False, 'error': str(e)}
    
    def clean_empty_folders(self, path):
        """Remove all empty folders recursively"""
        try:
            source = Path(path)
            removed = []
            
            # Walk bottom-up to remove empty folders
            for root, dirs, files in os.walk(str(source), topdown=False):
                for dir_name in dirs:
                    dir_path = Path(root) / dir_name
                    try:
                        if not any(dir_path.iterdir()):
                            dir_path.rmdir()
                            removed.append(str(dir_path))
                    except (PermissionError, OSError):
                        pass
            
            self.log(f"Removed {len(removed)} empty folders")
            return {'success': True, 'removed': removed}
        
        except Exception as e:
            self.log(f"Clean empty folders error: {e}")
            return {'success': False, 'error': str(e)}
    
    def copy_files(self, files, destination):
        """Copy files to destination"""
        try:
            dest = Path(destination)
            dest.mkdir(parents=True, exist_ok=True)
            
            copied = []
            for filepath in files:
                src = Path(filepath)
                if src.is_file():
                    target = dest / src.name
                    # Handle duplicates
                    counter = 1
                    while target.exists():
                        target = dest / f"{src.stem}_{counter}{src.suffix}"
                        counter += 1
                    shutil.copy2(str(src), str(target))
                    copied.append(str(filepath))
            
            self.log(f"Copied {len(copied)} files to {destination}")
            return {'success': True, 'copied': copied}
        
        except Exception as e:
            self.log(f"Copy files error: {e}")
            return {'success': False, 'error': str(e)}
    
    def move_files(self, files, destination):
        """Move files to destination"""
        try:
            dest = Path(destination)
            dest.mkdir(parents=True, exist_ok=True)
            
            moved = []
            for filepath in files:
                src = Path(filepath)
                if src.is_file():
                    target = dest / src.name
                    # Handle duplicates
                    counter = 1
                    while target.exists():
                        target = dest / f"{src.stem}_{counter}{src.suffix}"
                        counter += 1
                    shutil.move(str(src), str(target))
                    moved.append(str(filepath))
            
            self.log(f"Moved {len(moved)} files to {destination}")
            return {'success': True, 'moved': moved}
        
        except Exception as e:
            self.log(f"Move files error: {e}")
            return {'success': False, 'error': str(e)}
    
    def delete_files(self, files):
        """Delete files"""
        try:
            deleted = []
            for filepath in files:
                path = Path(filepath)
                if path.is_file():
                    path.unlink()
                    deleted.append(str(filepath))
                elif path.is_dir():
                    shutil.rmtree(str(path))
                    deleted.append(str(filepath))
            
            self.log(f"Deleted {len(deleted)} items")
            return {'success': True, 'deleted': deleted}
        
        except Exception as e:
            self.log(f"Delete files error: {e}")
            return {'success': False, 'error': str(e)}
    
    def find_by_extension(self, path, extensions):
        """Find all files with specified extensions"""
        try:
            source = Path(path)
            ext_list = [ext.lower().strip() for ext in extensions.replace(',', ' ').split()]
            found = []
            
            for item in source.rglob('*'):
                if item.is_file():
                    ext = item.suffix.lower().lstrip('.')
                    if ext in ext_list:
                        found.append(str(item))
            
            self.log(f"Found {len(found)} files with extensions: {', '.join(ext_list)}")
            return {'success': True, 'files': found}
        
        except Exception as e:
            self.log(f"Find by extension error: {e}")
            return {'success': False, 'error': str(e)}
