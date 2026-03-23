# DICOM Image Viewer & Metadata Explorer

A modular Python tool (+ parallel MATLAB script) that loads a folder of DICOM (`.dcm`) files as a 3D volume, displays **axial / sagittal / coronal** slice views with interactive sliders, and exports key metadata to a CSV file.

On GitHub, everything is shown **from the repository root** (e.g. `python/`, `data/`). Your local folder name (`Desktop`, `OneDrive`, etc.) is **not** part of the repo—clone the project and work inside that folder only.

---

## Clone & project root

```bash
git clone https://github.com/shanksinguva7/DICOMViewer.git
cd DICOMViewer
```

All commands below assume your terminal’s **current directory is this repo root** (`DICOMViewer/`), not a parent path on your PC.

---

## Project Structure

```
DICOMViewer/
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

## Results
<img width="1902" height="706" alt="Screenshot 2026-03-21 165119" src="https://github.com/user-attachments/assets/a1a0b090-4cbc-469b-8c3d-07333f839070" />

<img width="1902" height="705" alt="Screenshot 2026-03-21 165152" src="https://github.com/user-attachments/assets/c5ea082b-3640-48b2-bf36-fa65a4d1f127" />
You can view all the images from the axial/saggital/cornal slice views and the slider can be used for easy viewing.

## Requirements

| Package | Purpose |
|---|---|
| `pydicom` | Read `.dcm` files |
| `numpy` | 3D array manipulation |
| `matplotlib` | Slice display + sliders |
| `pandas` | Metadata CSV export |
