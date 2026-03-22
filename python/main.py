"""
main.py
-------
Entry point for the DICOM Image Viewer & Metadata Explorer.

Usage
-----
    python main.py                          # uses default ./data folder
    python main.py --data path/to/dicoms   # custom folder
    python main.py --no-display            # export metadata only (headless)
    python main.py --overview              # show summary slice grid instead
"""

import argparse
import os
import sys

# ── Add python/ directory to path when run from project root ──────────────────
sys.path.insert(0, os.path.dirname(__file__))

from loader   import load_dicom_volume
from metadata import export_metadata
from display  import display_slices, display_summary_grid


def parse_args():
    parser = argparse.ArgumentParser(
        description="DICOM Image Viewer & Metadata Explorer"
    )
    parser.add_argument(
        "--data",
        default=os.path.join(os.path.dirname(__file__), "..", "data"),
        help="Path to folder containing .dcm files (default: ../data)",
    )
    parser.add_argument(
        "--output",
        default=os.path.join(os.path.dirname(__file__), "..", "output", "metadata.csv"),
        help="Output CSV path (default: ../output/metadata.csv)",
    )
    parser.add_argument(
        "--no-display",
        action="store_true",
        help="Skip the viewer window (useful for headless / CI environments)",
    )
    parser.add_argument(
        "--overview",
        action="store_true",
        help="Show axial overview grid instead of interactive slider viewer",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    data_folder = os.path.abspath(args.data)
    output_path = os.path.abspath(args.output)

    print("=" * 55)
    print("  DICOM Image Viewer & Metadata Explorer")
    print("=" * 55)
    print(f"  Data   : {data_folder}")
    print(f"  Output : {output_path}")
    print("=" * 55)

    # ── Step 1: Load ─────────────────────────────────────────────────────────
    volume, dicom_files = load_dicom_volume(data_folder)

    # ── Step 2: Export metadata ───────────────────────────────────────────────
    export_metadata(dicom_files, output_path=output_path)

    # ── Step 3: Display ───────────────────────────────────────────────────────
    if not args.no_display:
        patient = str(getattr(dicom_files[0], "PatientName", "Unknown"))
        modality = str(getattr(dicom_files[0], "Modality", ""))
        title = f"{modality} — {patient}  [{volume.shape[0]} slices]"

        if args.overview:
            display_summary_grid(volume)
        else:
            display_slices(volume, title=title)

    print("\n[main] Done.")


if __name__ == "__main__":
    main()
