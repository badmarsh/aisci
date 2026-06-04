#!/usr/bin/env python3
"""Extract a ZIP file attachment and prepare it for deployment.

This script helps the agent find and extract a ZIP file uploaded by the user.
It handles the common case where a ZIP contains a top-level directory
(e.g., github-username-repo-branch/) by flattening it.

Usage:
    python extract_zip.py <zip_path> [--output-dir /tmp/app]
    python extract_zip.py --auto          # Finds the most recent ZIP in uploads
"""

import argparse
import os
import sys
import zipfile
import glob
import time


def find_latest_zip(search_dirs):
    """Find the most recently modified .zip file in the given directories."""
    best = None
    best_time = 0
    for d in search_dirs:
        if not os.path.isdir(d):
            continue
        for path in glob.glob(os.path.join(d, "**", "*.zip"), recursive=True):
            try:
                mtime = os.path.getmtime(path)
                if mtime > best_time:
                    best_time = mtime
                    best = path
            except OSError:
                continue
    return best


def extract_zip(zip_path, output_dir):
    """Extract a ZIP, flattening a top-level directory if present."""
    os.makedirs(output_dir, exist_ok=True)

    with zipfile.ZipFile(zip_path, "r") as zf:
        # Check if all files are inside a single top-level directory
        top_dirs = set()
        for name in zf.namelist():
            parts = name.split("/")
            if len(parts) > 1 and parts[0]:
                top_dirs.add(parts[0])

        if len(top_dirs) == 1:
            # Extract and flatten
            extract_dir = os.path.join(output_dir, "_extract")
            os.makedirs(extract_dir, exist_ok=True)
            zf.extractall(extract_dir)
            sub = os.path.join(extract_dir, list(top_dirs)[0])
            if os.path.isdir(sub):
                for item in os.listdir(sub):
                    src = os.path.join(sub, item)
                    dst = os.path.join(output_dir, item)
                    if os.path.exists(dst):
                        if os.path.isdir(dst):
                            os.rmdir(dst) if not os.listdir(dst) else None
                        else:
                            os.remove(dst)
                    os.rename(src, dst)
                os.rmdir(sub)
            os.rmdir(extract_dir)
            print(f"Extracted and flattened: {zip_path} -> {output_dir}")
        else:
            # Simple extract
            zf.extractall(output_dir)
            print(f"Extracted: {zip_path} -> {output_dir}")

    # List the contents for the agent
    items = os.listdir(output_dir)
    print(f"Contents ({len(items)} items): {', '.join(sorted(items)[:20])}")
    if len(items) > 20:
        print(f"  ... and {len(items) - 20} more")


def main():
    parser = argparse.ArgumentParser(description="Extract a ZIP file for deployment")
    parser.add_argument("zip_path", nargs="?", help="Path to the ZIP file")
    parser.add_argument("--output-dir", default="/tmp/app", help="Output directory (default: /tmp/app)")
    parser.add_argument("--auto", action="store_true", help="Automatically find the most recent ZIP in uploads")
    parser.add_argument("--list", action="store_true", help="List available ZIP files and exit")
    args = parser.parse_args()

    if args.list or (args.auto and not args.zip_path):
        search_dirs = [
            "/mnt/user-data/uploads",
            "/mnt/user-data",
            "/tmp",
        ]
        zips = []
        for d in search_dirs:
            if os.path.isdir(d):
                for path in glob.glob(os.path.join(d, "**", "*.zip"), recursive=True):
                    try:
                        mtime = os.path.getmtime(path)
                        size = os.path.getsize(path)
                        zips.append((mtime, path, size))
                    except OSError:
                        continue

        zips.sort(reverse=True)

        if args.list:
            if not zips:
                print("No ZIP files found.")
                sys.exit(0)
            print("Available ZIP files (newest first):")
            for mtime, path, size in zips[:20]:
                age = time.time() - mtime
                if age < 60:
                    age_str = f"{age:.0f}s ago"
                elif age < 3600:
                    age_str = f"{age/60:.0f}m ago"
                else:
                    age_str = f"{age/3600:.1f}h ago"
                print(f"  {path}  ({size/1024:.1f} KB, {age_str})")
            sys.exit(0)

        if not zips:
            print("ERROR: No ZIP files found. Upload a .zip file first.", file=sys.stderr)
            sys.exit(1)

        args.zip_path = zips[0][1]
        print(f"Auto-selected: {args.zip_path}")

    if not args.zip_path:
        parser.error("Provide a ZIP path or use --auto to find the most recent one")

    if not os.path.exists(args.zip_path):
        print(f"ERROR: File not found: {args.zip_path}", file=sys.stderr)
        # Suggest alternatives
        search_dirs = ["/mnt/user-data/uploads", "/mnt/user-data", "/tmp"]
        for d in search_dirs:
            if os.path.isdir(d):
                matches = glob.glob(os.path.join(d, "**", "*.zip"), recursive=True)
                if matches:
                    print(f"Found ZIPs in {d}:", file=sys.stderr)
                    for m in matches[:5]:
                        print(f"  {m}", file=sys.stderr)
        sys.exit(1)

    extract_zip(args.zip_path, args.output_dir)


if __name__ == "__main__":
    main()
