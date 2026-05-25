"""
Inspect MIMIC-CXR report file format to understand structure for preprocessing
"""

import os
from pathlib import Path

def inspect_report_file(report_path):
    """Inspect a single report file and show its structure"""
    print(f"\n{'='*80}")
    print(f"Report: {report_path}")
    print(f"{'='*80}\n")

    try:
        with open(report_path, 'r', encoding='utf-8') as f:
            content = f.read()

        print(f"File size: {len(content)} characters")
        print(f"Number of lines: {len(content.splitlines())}")
        print("\n" + "-"*80)
        print("Full content:")
        print("-"*80)
        print(content)
        print("-"*80)

        # Try to identify sections
        lines = content.splitlines()
        sections_found = []

        common_sections = [
            'FINDINGS', 'IMPRESSION', 'INDICATION', 'HISTORY',
            'TECHNIQUE', 'COMPARISON', 'EXAMINATION', 'CLINICAL',
            'REASON FOR EXAM', 'FINAL REPORT', 'ADDENDUM'
        ]

        print("\nIdentified sections:")
        for i, line in enumerate(lines, 1):
            line_upper = line.strip().upper()
            for section in common_sections:
                if section in line_upper and line_upper.startswith(section):
                    sections_found.append((i, section, line))
                    print(f"  Line {i}: {section}")

        if not sections_found:
            print("  No standard sections found - may be free-text format")

        return content, sections_found

    except Exception as e:
        print(f"ERROR reading file: {e}")
        return None, []


def find_sample_reports(base_path, num_samples=3):
    """Find a few sample report files"""
    base = Path(base_path)

    print(f"Searching for report files in: {base}")
    print("This may take a moment...\n")

    report_files = []

    # Search for .txt files
    for txt_file in base.rglob("*.txt"):
        report_files.append(txt_file)
        if len(report_files) >= num_samples:
            break

    return report_files


def main():
    # Try to find reports
    base_path = r"D:\datasets\mimic-cxr-reports\reports\files"

    print("MIMIC-CXR Report Format Inspector")
    print("="*80)

    if not os.path.exists(base_path):
        print(f"\nERROR: Base path not found: {base_path}")
        print("\nPlease provide the correct path to MIMIC-CXR reports.")
        input("Press Enter to exit...")
        return

    # Find sample reports
    print(f"\nSearching for sample reports in: {base_path}")
    sample_files = find_sample_reports(base_path, num_samples=3)

    if not sample_files:
        print("\nNo .txt report files found!")
        print("The directory structure may be different than expected.")
        input("Press Enter to exit...")
        return

    print(f"\nFound {len(sample_files)} sample report(s)")

    # Inspect each sample
    all_sections = set()
    for report_file in sample_files:
        content, sections = inspect_report_file(report_file)
        for _, section, _ in sections:
            all_sections.add(section)

    # Summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print(f"\nTotal samples inspected: {len(sample_files)}")
    print(f"Section types found: {', '.join(sorted(all_sections)) if all_sections else 'None'}")

    print("\n" + "="*80)
    print("NEXT STEPS")
    print("="*80)
    print("""
Based on the report format above, we can now create the preprocessing script.

MIMIC-CXR reports typically have sections like:
  - FINDINGS: Main body of the radiology report
  - IMPRESSION: Summary/conclusion
  - INDICATION: Why the exam was ordered
  - COMPARISON: Previous studies referenced

For CXRMate, we need to extract FINDINGS and IMPRESSION sections.
""")

    input("\nPress Enter to exit...")


if __name__ == "__main__":
    main()
