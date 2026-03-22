"""
metadata.py
-----------
Extracts key DICOM metadata tags from a list of pydicom Datasets
and exports the results to a CSV file using pandas.
"""

import os
import pandas as pd
import pydicom


# Tags to extract — add/remove as needed
METADATA_TAGS = [
    "PatientName",
    "PatientID",
    "PatientAge",
    "PatientSex",
    "Modality",
    "StudyDate",
    "StudyDescription",
    "SeriesDescription",
    "SliceThickness",
    "PixelSpacing",
    "Rows",
    "Columns",
    "BitsAllocated",
    "PhotometricInterpretation",
    "InstanceNumber",
    "ImagePositionPatient",
    "Manufacturer",
    "InstitutionName",
    "KVP",
]


def _safe_get(ds: pydicom.Dataset, tag: str) -> str:
    """Safely retrieve a DICOM tag value as a string."""
    try:
        val = getattr(ds, tag)
        # Convert sequences / lists to a readable string
        if hasattr(val, "__iter__") and not isinstance(val, str):
            return str(list(val))
        return str(val)
    except AttributeError:
        return "N/A"


def extract_metadata(dicom_files: list) -> pd.DataFrame:
    """
    Build a DataFrame with one row per DICOM slice and
    one column per metadata tag.
    """
    rows = []
    for ds in dicom_files:
        row = {"Filename": os.path.basename(str(ds.filename))}
        for tag in METADATA_TAGS:
            row[tag] = _safe_get(ds, tag)
        rows.append(row)

    df = pd.DataFrame(rows)
    print(f"[metadata] Extracted metadata for {len(df)} slices.")
    return df


def export_metadata(dicom_files: list, output_path: str = "output/metadata.csv") -> str:
    """
    Extract metadata and write it to *output_path* as a CSV file.
    Returns the absolute path of the written file.
    """
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    df = extract_metadata(dicom_files)
    df.to_csv(output_path, index=False)
    abs_path = os.path.abspath(output_path)
    print(f"[metadata] Metadata exported → {abs_path}")
    return abs_path
