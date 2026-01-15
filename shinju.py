#!/usr/bin/env python3
"""
Shinju - A Python 3 remake of the classic 'tree' command with search functionality.

Features:
- Display directory tree structure with classic tree formatting
- Search for keywords/regex patterns in file contents
- Highlight files containing matches with match count
"""

import argparse
import os
import re
import sys
from pathlib import Path

# ANSI color codes
class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    YELLOW = "\033[33m"
    GREEN = "\033[32m"
    BLUE = "\033[34m"
    DIM = "\033[2m"
    RED = "\033[31m"

BANNER = f"""
{Colors.CYAN}    ▄▄▄ ▐▌   ▄ ▄▄▄▄     ▗▖█  ▐▌
{Colors.CYAN}   ▀▄▄  ▐▌   ▄ █   █    ▗▖▀▄▄▞▘
{Colors.CYAN}   ▄▄▄▀ ▐▛▀▚▖█ █   █ ▄  ▐▌     
{Colors.CYAN}        ▐▌ ▐▌█       ▀▄▄▞▘{Colors.RESET}

{Colors.BOLD}   神樹(GodTree) + Search Tool{Colors.RESET}
"""

# Tree branch characters
BRANCH = "├── "
LAST_BRANCH = "└── "
PIPE = "│   "
SPACE = "    "

# File extensions to exclude from content search
EXCLUDE_EXTENSIONS = {
    "gz", "zip", "tar", "rar", "7z", "bz2", "xz",
    "deb", "img", "iso", "vmdk", "dll", "ovf", "ova"
}


def is_binary_file(filepath: Path) -> bool:
    """Check if a file is binary by reading a small chunk."""
    try:
        with open(filepath, "rb") as f:
            chunk = f.read(1024)
            return b"\x00" in chunk
    except (IOError, OSError):
        return True


def search_file(filepath: Path, pattern: str, is_regex: bool, ignore_case: bool) -> tuple[int, str]:
    """
    Search for matches in a file.
    Supports comma-separated keywords (when not regex mode).
    Returns a tuple of (match_count, first_match_snippet).
    """
    # Skip excluded extensions
    ext = filepath.suffix.lstrip(".").lower()
    if ext in EXCLUDE_EXTENSIONS:
        return 0, ""
    
    if is_binary_file(filepath):
        return 0, ""
    
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
        
        flags = re.IGNORECASE if ignore_case else 0
        
        # Handle comma-separated keywords (only in non-regex mode)
        if is_regex:
            patterns = [pattern]
        else:
            patterns = [p.strip() for p in pattern.split(",") if p.strip()]
        
        compiled_patterns = []
        for p in patterns:
            compiled_patterns.append(re.compile(p if is_regex else re.escape(p), flags))
        
        match_count = 0
        first_snippet = ""
        
        for line in lines:
            for compiled_pattern in compiled_patterns:
                matches = compiled_pattern.findall(line)
                if matches:
                    match_count += len(matches)
                    if not first_snippet:
                        # Get the first match and its line context
                        first_match = matches[0]
                        line_stripped = line.strip()
                        # Truncate long lines
                        if len(line_stripped) > 50:
                            line_stripped = line_stripped[:50] + "..."
                        first_snippet = f"['{first_match}' => '{line_stripped}']"
        
        return match_count, first_snippet
    except (IOError, OSError, re.error):
        return 0, ""


def format_entry(name: str, is_dir: bool, match_count: int = 0, snippet: str = "", name_matched: bool = False, search_active: bool = False) -> str:
    """Format a directory entry with optional highlighting."""
    if name_matched and match_count > 0:
        # Both name match AND content match - show name in green + snippet only (no match count)
        suffix = "/" if is_dir else ""
        formatted = (
            f"{Colors.GREEN}{Colors.BOLD}{name}{suffix}{Colors.RESET} "
            f"{Colors.CYAN}{snippet}{Colors.RESET}"
        )
    elif name_matched:
        # File name match only - show [match] indicator
        suffix = "/" if is_dir else ""
        formatted = f"{Colors.GREEN}{Colors.BOLD}{name}{suffix}{Colors.RESET} {Colors.YELLOW}[match]{Colors.RESET}"
    elif is_dir:
        formatted = f"{Colors.BLUE}{Colors.BOLD}{name}/{Colors.RESET}"
    elif match_count > 0:
        # Content match only
        match_text = "match" if match_count == 1 else "matches"
        formatted = (
            f"{Colors.MAGENTA}{Colors.BOLD}{name}{Colors.RESET} "
            f"{Colors.YELLOW}[{match_count} {match_text}]{Colors.RESET} "
            f"{Colors.CYAN}{snippet}{Colors.RESET}"
        )
    elif search_active:
        formatted = f"{Colors.DIM}{name}{Colors.RESET}"
    else:
        formatted = name
    
    return formatted


def walk_tree(
    directory: Path,
    prefix: str = "",
    show_hidden: bool = False,
    dirs_only: bool = False,
    max_depth: int = None,
    current_depth: int = 0,
    search_pattern: str = None,
    name_pattern: str = None,
    is_regex: bool = False,
    ignore_case: bool = False,
    match_only: bool = False,
) -> tuple[list[str], dict]:
    """
    Recursively walk the directory tree and build the output.
    Returns a tuple of (lines, stats).
    """
    lines = []
    stats = {"dirs": 0, "files": 0, "name_matches": 0, "content_matches": 0}
    
    if max_depth is not None and current_depth >= max_depth:
        return lines, stats
    
    try:
        entries = sorted(directory.iterdir(), key=lambda e: (not e.is_dir(), e.name.lower()))
    except PermissionError:
        lines.append(f"{prefix}{Colors.DIM}[permission denied]{Colors.RESET}")
        return lines, stats
    
    # Filter hidden files if needed
    if not show_hidden:
        entries = [e for e in entries if not e.name.startswith(".")]
    
    # Filter to directories only if needed
    if dirs_only:
        entries = [e for e in entries if e.is_dir()]
    
    for i, entry in enumerate(entries):
        is_last = i == len(entries) - 1
        branch = LAST_BRANCH if is_last else BRANCH
        next_prefix = prefix + (SPACE if is_last else PIPE)
        
        is_dir = entry.is_dir()
        match_count = 0
        snippet = ""
        name_matched = False
        
        if is_dir:
            stats["dirs"] += 1
        else:
            stats["files"] += 1
        
        # File name search
        if name_pattern:
            flags = re.IGNORECASE if ignore_case else 0
            compiled = re.compile(name_pattern if is_regex else re.escape(name_pattern), flags)
            if compiled.search(entry.name):
                name_matched = True
                stats["name_matches"] += 1
        
        # File content search (independent of name search)
        if search_pattern and not is_dir:
            match_count, snippet = search_file(entry, search_pattern, is_regex, ignore_case)
            if match_count > 0:
                stats["content_matches"] += 1
        
        formatted_name = format_entry(
            entry.name, 
            is_dir, 
            match_count,
            snippet,
            name_matched=name_matched,
            search_active=search_pattern is not None or name_pattern is not None
        )
        
        if is_dir:
            sub_lines, sub_stats = walk_tree(
                entry,
                next_prefix,
                show_hidden,
                dirs_only,
                max_depth,
                current_depth + 1,
                search_pattern,
                name_pattern,
                is_regex,
                ignore_case,
                match_only,
            )
            
            # In match_only mode, only show directory if it has matches inside or name matched
            has_matches = sub_stats["name_matches"] > 0 or sub_stats["content_matches"] > 0 or name_matched
            if not match_only or has_matches:
                lines.append(f"{prefix}{branch}{formatted_name}")
                lines.extend(sub_lines)
            
            stats["dirs"] += sub_stats["dirs"]
            stats["files"] += sub_stats["files"]
            stats["name_matches"] += sub_stats["name_matches"]
            stats["content_matches"] += sub_stats["content_matches"]
        else:
            # In match_only mode, only show file if it has a match
            has_match = name_matched or match_count > 0
            if not match_only or has_match:
                lines.append(f"{prefix}{branch}{formatted_name}")
    
    return lines, stats


def print_tree(
    directory: Path,
    show_hidden: bool = False,
    dirs_only: bool = False,
    max_depth: int = None,
    search_pattern: str = None,
    name_pattern: str = None,
    is_regex: bool = False,
    ignore_case: bool = False,
    match_only: bool = False,
) -> None:
    """Print the directory tree."""
    # Print root directory
    print(f"{Colors.BLUE}{Colors.BOLD}{directory}{Colors.RESET}")
    
    lines, stats = walk_tree(
        directory,
        "",
        show_hidden,
        dirs_only,
        max_depth,
        0,
        search_pattern,
        name_pattern,
        is_regex,
        ignore_case,
        match_only,
    )
    
    for line in lines:
        print(line)
    
    # Print summary
    print()
    dir_text = "directory" if stats["dirs"] == 1 else "directories"
    file_text = "file" if stats["files"] == 1 else "files"
    
    summary = f"{stats['dirs']} {dir_text}, {stats['files']} {file_text}"
    
    if name_pattern:
        match_text = "name match" if stats["name_matches"] == 1 else "name matches"
        summary += f", {Colors.GREEN}{stats['name_matches']} {match_text}{Colors.RESET}"
    
    if search_pattern:
        match_text = "content match" if stats["content_matches"] == 1 else "content matches"
        summary += f", {Colors.MAGENTA}{stats['content_matches']} {match_text}{Colors.RESET}"
    
    print(summary)


def main():
    print(BANNER)
    
    parser = argparse.ArgumentParser(
        prog="shinju",
        description="A Python tree command with search functionality",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  shinju                      Show tree of current directory
  shinju /path/to/dir         Show tree of specified directory
  shinju -a                   Include hidden files
  shinju -d                   Show directories only
  shinju -L 2                 Limit depth to 2 levels
  shinju -s "import"          Search for 'import' in files
  shinju -s "def\\s+\\w+" -r   Search using regex pattern
  shinju -s "TODO" -i         Case-insensitive search
        """,
    )
    
    parser.add_argument(
        "directory",
        nargs="?",
        default=".",
        help="Directory to display (default: current directory)",
    )
    parser.add_argument(
        "-a", "--all",
        action="store_true",
        dest="show_hidden",
        help="Show hidden files and directories",
    )
    parser.add_argument(
        "-d", "--dirs-only",
        action="store_true",
        help="List directories only",
    )
    parser.add_argument(
        "-L", "--level",
        type=int,
        metavar="DEPTH",
        dest="max_depth",
        help="Limit the depth of the tree",
    )
    parser.add_argument(
        "-s", "--search",
        metavar="PATTERN",
        help="Search for pattern in file contents",
    )
    parser.add_argument(
        "-n", "--name",
        metavar="PATTERN",
        help="Search for pattern in file/directory names",
    )
    parser.add_argument(
        "-r", "--regex",
        action="store_true",
        help="Treat search pattern as regex",
    )
    parser.add_argument(
        "-i", "--ignore-case",
        action="store_true",
        help="Case-insensitive search",
    )
    parser.add_argument(
        "-m", "--matches-only",
        action="store_true",
        help="Show only matching files/directories",
    )
    
    args = parser.parse_args()
    
    directory = Path(args.directory).resolve()
    
    if not directory.exists():
        print(f"Error: '{args.directory}' does not exist", file=sys.stderr)
        sys.exit(1)
    
    if not directory.is_dir():
        print(f"Error: '{args.directory}' is not a directory", file=sys.stderr)
        sys.exit(1)
    
    # Validate regex pattern if provided
    search_to_validate = args.search or args.name
    if search_to_validate and args.regex:
        try:
            re.compile(search_to_validate)
        except re.error as e:
            print(f"Error: Invalid regex pattern: {e}", file=sys.stderr)
            sys.exit(1)
    
    print_tree(
        directory,
        show_hidden=args.show_hidden,
        dirs_only=args.dirs_only,
        max_depth=args.max_depth,
        search_pattern=args.search,
        name_pattern=args.name,
        is_regex=args.regex,
        ignore_case=args.ignore_case,
        match_only=args.matches_only,
    )


if __name__ == "__main__":
    main()
