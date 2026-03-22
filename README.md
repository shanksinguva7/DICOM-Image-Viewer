# DICOM Image Viewer & Metadata Explorer

A modular Python tool (+ parallel MATLAB script) that loads a folder of DICOM (`.dcm`) files as a 3D volume, displays **axial / sagittal / coronal** slice views with interactive sliders, and exports key metadata to a CSV file.

---

## Project Structure

```
dicom_viewer/
├── python/
│   ├── loader.py       ← Load .dcm folder → 3D NumPy volume
│   ├── display.py      ← Render slice views (interactive sliders)
│   ├── metadata.py     ← Extract DICOM tags → CSV
│   └── main.py         ← Entry point (wires everything together)
├── matlab/
│   └── dicom_viewer.m  ← Equivalent MATLAB script
├── data/               ← Place your .dcm files here
├── output/
│   └── metadata.csv    ← Generated automatically on run
└── requirements.txt
```

---

## Quick Start (Python)

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Add your DICOM data
Place all `.dcm` files from one series into the `data/` folder.

> **Free datasets:**
> - [The Cancer Imaging Archive (TCIA)](https://www.cancerimagingarchive.net/)
> - [OsiriX DICOM Library](https://www.osirix-viewer.com/resources/dicom-image-library/)

### 3. Run the viewer
```bash
# From the project root:
python python/main.py

# Custom data folder:
python python/main.py --data path/to/dicoms

# Headless (export CSV only, no GUI):
python python/main.py --no-display

# Quick axial overview grid:
python python/main.py --overview
```

---

## How the Modules Connect

```
main.py
  ├── loader.py   → load_dicom_volume(folder)  → (volume, dicom_files)
  ├── metadata.py → export_metadata(dicom_files, output_path) → metadata.csv
  └── display.py  → display_slices(volume)     → matplotlib window
```

---

## MATLAB Usage

Open `matlab/dicom_viewer.m` in MATLAB, update `DATA_FOLDER` if needed, then run:
```matlab
>> dicom_viewer
```

The script uses `dicomread` / `dicominfo` and writes the same `output/metadata.csv`.

---

## Exported Metadata Fields

| Field | Description |
|---|---|
| `PatientName` | Patient identifier |
| `PatientID` | Unique patient ID |
| `Modality` | CT, MR, PET, etc. |
| `StudyDate` | Date of study |
| `SliceThickness` | Distance between slices (mm) |
| `PixelSpacing` | In-plane pixel size (mm) |
| `Rows` / `Columns` | Image dimensions |
| `Manufacturer` | Scanner manufacturer |
| + more… | See `metadata.py → METADATA_TAGS` |

---

## Requirements

| Package | Purpose |
|---|---|
| `pydicom` | Read `.dcm` files |
| `numpy` | 3D array manipulation |
| `matplotlib` | Slice display + sliders |
| `pandas` | Metadata CSV export |
