import os
import sys
from difflib import SequenceMatcher

# Change this to 0.80 (for 80%) or 0.90 (for 90%) depending on your preference
SIMILARITY_THRESHOLD = 0.85  

# Predefined common media extensions
MUSIC_EXTENSIONS = ('.mp3', '.wav', '.flac', '.m4a', '.aac', '.ogg')
VIDEO_EXTENSIONS = ('.mp4', '.mkv', '.avi', '.mov', '.flv', '.wmv')
IMAGE_EXTENSIONS = ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp')

# ANSI Color Codes
GREEN = "\033[92m"
RED = "\033[91m"
BLUE = "\033[94m"
CYAN = "\033[96m"
YELLOW = "\033[93m"
RESET = "\033[0m"

def show_ascii_intro():
    """Displays the colorized creator splash screen at startup."""
    intro_art = f"""
{CYAN}=======================================================
{GREEN}  _____   _   _____ __  __    _    _   _ 
 |  ___| / \ |_   _|  \/  |  / \  | \ | |
 | |_   / _ \  | | | |\/| | / _ \ |  \| |
 |  _| / ___ \ | | | |  | |/ ___ \| |\  |
 |_|  /_/   \_\|_| |_|  |_/_/   \_\_| \_|
{CYAN}                                               
         🚀 {GREEN}FUZZY DUPLICATE MANAGER{CYAN} 🚀
         ✨ Created by: {YELLOW}PROTANX{CYAN} ✨
======================================================={RESET}
    """
    print(intro_art)

def get_file_type_filter():
    """Prompts the user to select the specific media category or file type they want to scan."""
    print("=== File Type Filter Menu ===")
    print("1. Scan ALL file types")
    print("2. Scan MUSIC files only (.mp3, .wav, .flac, etc.)")
    print("3. Scan VIDEO files only (.mp4, .mkv, .avi, etc.)")
    print("4. Scan IMAGE files only (.jpg, .png, .webp, etc.)")
    print("5. Scan a CUSTOM file extension (e.g., .pdf, .docx)")
    
    while True:
        choice = input("\nEnter your choice (1-5): ").strip()
        if choice == '1':
            return None  # No filter
        elif choice == '2':
            return MUSIC_EXTENSIONS
        elif choice == '3':
            return VIDEO_EXTENSIONS
        elif choice == '4':
            return IMAGE_EXTENSIONS
        elif choice == '5':
            ext = input("Enter the extension to look for (including the dot, e.g., .pdf): ").strip().lower()
            if not ext.startswith('.'):
                ext = '.' + ext
            return (ext,)
        else:
            print(f"{RED}Invalid choice.{RESET} Please enter a number between 1 and 5.")

def get_all_files(target_dir, allowed_extensions=None):
    """Scans the specified directory and subdirectories for files matching the filter."""
    all_files = []
    for root, _, files in os.walk(target_dir):
        for file in files:
            # Skip hidden system files (like .DS_Store on Mac)
            if file.startswith('.'):
                continue
            
            # Apply file extension filter if one is active
            if allowed_extensions and not file.lower().endswith(allowed_extensions):
                continue
                
            full_path = os.path.join(root, file)
            all_files.append((file, full_path))
    return all_files

def calculate_similarity(str1, str2):
    """Returns the similarity ratio between two strings (0.0 to 1.0)."""
    return SequenceMatcher(None, str1.lower(), str2.lower()).ratio()

def find_fuzzy_duplicates(files_list):
    """Groups files together if their names match by at least the threshold."""
    duplicates_groups = []
    visited = set()

    for i, (file1, path1) in enumerate(files_list):
        if path1 in visited:
            continue
            
        group = [(file1, path1)]
        
        for j in range(i + 1, len(files_list)):
            file2, path2 = files_list[j]
            if path2 in visited:
                continue
                
            if calculate_similarity(file1, file2) >= SIMILARITY_THRESHOLD:
                group.append((file2, path2))
                
        if len(group) > 1:
            for _, path in group:
                visited.add(path)
            duplicates_groups.append(group)
            
    return duplicates_groups

def delete_duplicates_interactive(duplicate_groups):
    """Prompts the user to handle duplicate groups one by one with color coding."""
    print("\n--- Duplicate Deletion Menu ---")
    
    for group_idx, group in enumerate(duplicate_groups, start=1):
        print(f"\n[Group {group_idx}] High-similarity files found:")
        
        for idx, (filename, path) in enumerate(group, start=1):
            folder_name = os.path.basename(os.path.dirname(path))
            folder_prefix = f"{BLUE}[{folder_name}]{RESET} "

            if idx == 1:
                status = f"{GREEN}[ORIGINAL]{RESET}"
                color = GREEN
            else:
                status = f"{RED}[DUPLICATE]{RESET}"
                color = RED
                
            print(f"  [{idx}] {status} {folder_prefix}Name: {color}{filename}{RESET}")
            print(f"      Path: {path}")
            
        print(f"  [{len(group) + 1}] Skip this group (Keep all)")

        while True:
            try:
                choice = int(input(f"Which one do you want to KEEP? (1-{len(group) + 1}): "))
                if 1 <= choice <= len(group):
                    keep_path = group[choice - 1][1]
                    for _, path in group:
                        if path != keep_path:
                            os.remove(path)
                            print(f"{RED}Deleted:{RESET} {path}")
                    break
                elif choice == len(group) + 1:
                    print("Skipped group.")
                    break
                else:
                    print("Invalid choice. Try again.")
            except ValueError:
                print("Please enter a valid number.")

def main():
    # Show the colorized ASCII splash intro right away
    show_ascii_intro()

    # Check if a custom path was entered after the script name
    if len(sys.argv) > 1:
        target_directory = sys.argv[1]
        if not os.path.isdir(target_directory):
            print(f"{RED}Error:{RESET} '{target_directory}' is not a valid folder path.")
            return
    else:
        target_directory = os.getcwd()

    # Step 0: Choose specific media type filtering upfront
    allowed_extensions = get_file_type_filter()

    print(f"\nScanning target path: {target_directory}")
    print(f"Matching Threshold: {int(SIMILARITY_THRESHOLD * 100)}%\n")
    
    all_files = get_all_files(target_directory, allowed_extensions)

    if not all_files:
        print("No matching files found in this directory.")
        return

    # 1. Print all file names with serial numbers and blue folder brackets
    print(f"--- Found {len(all_files)} Matching Files ---")
    for index, (filename, path) in enumerate(all_files, start=1):
        folder_name = os.path.basename(os.path.dirname(path))
        print(f"{index}. {BLUE}[{folder_name}]{RESET} {filename}")

    # 2. Find and print strict fuzzy duplicates
    print("\nAnalyzing filtered file names for high similarities...")
    duplicate_groups = find_fuzzy_duplicates(all_files)
    
    print(f"\n--- Found {len(duplicate_groups)} Groups of Highly Similar Files ---")
    for idx, group in enumerate(duplicate_groups, start=1):
        paths_set = {path for _, path in group}
        
        colored_names = []
        for f_idx, (f, p) in enumerate(group):
            f_folder = os.path.basename(os.path.dirname(p))
            f_prefix = f"{BLUE}[{f_folder}]{RESET}"
            if f_idx == 0:
                colored_names.append(f"{f_prefix} {GREEN}'{f}' (Orig){RESET}")
            else:
                colored_names.append(f"{f_prefix} {RED}'{f}' (Dup){RESET}")
                
        filenames_str = ", ".join(colored_names)
        print(f"Group {idx} ({filenames_str}) \n-> Paths Set: {paths_set}\n")

    # 3. Option to delete
    if duplicate_groups:
        proceed = input("Would you like to manage and delete duplicates? (yes/no): ").strip().lower()
        if proceed in ['yes', 'y']:
            delete_duplicates_interactive(duplicate_groups)
        else:
            print("No files deleted.")
    else:
        print(f"\n{GREEN}Clean directory! No duplicate patterns matched at this threshold for selected file types.{RESET}")

if __name__ == "__main__":
    main()
