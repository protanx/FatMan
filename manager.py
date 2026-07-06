import os
import sys
from difflib import SequenceMatcher

# Change this to 0.80 (for 80%) or 0.90 (for 90%) depending on your preference
SIMILARITY_THRESHOLD = 0.85  

# ANSI Color Codes
GREEN = "\033[92m"
RED = "\033[91m"
BLUE = "\033[94m"
RESET = "\033[0m"

def get_all_files(target_dir):
    """Scans the specified directory and subdirectories for ALL files."""
    all_files = []
    for root, _, files in os.walk(target_dir):
        for file in files:
            # Skip hidden files (like .DS_Store on Mac)
            if file.startswith('.'):
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
            # Extract only the name of the folder containing this file
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
    # Check if a custom path was entered after the file name
    if len(sys.argv) > 1:
        target_directory = sys.argv[1]
        # Validate if the provided path actually exists
        if not os.path.isdir(target_directory):
            print(f"{RED}Error:{RESET} '{target_directory}' is not a valid folder path.")
            return
    else:
        # Fallback to current working directory if no argument is passed
        target_directory = os.getcwd()

    print(f"Scanning target path: {target_directory}")
    print(f"Matching Threshold: {int(SIMILARITY_THRESHOLD * 100)}%\n")
    
    all_files = get_all_files(target_directory)

    if not all_files:
        print("No files found in this directory.")
        return

    # 1. Print all file names with serial numbers and blue folder brackets
    print(f"--- Found {len(all_files)} Total Files ---")
    for index, (filename, path) in enumerate(all_files, start=1):
        folder_name = os.path.basename(os.path.dirname(path))
        print(f"{index}. {BLUE}[{folder_name}]{RESET} {filename}")

    # 2. Find and print strict fuzzy duplicates
    print("\nAnalyzing all file names for high similarities...")
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
        print(f"\n{GREEN}Clean directory! No duplicate patterns matched at this threshold.{RESET}")

if __name__ == "__main__":
    main()
