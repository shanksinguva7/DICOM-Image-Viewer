"""
loader.py
---------
Loads a folder of DICOM (.dcm) files, sorts them by slice position,
and assembles a 3D NumPy volume of shape (Z, H, W).

Handles datasets where slices have different image dimensions by
resizing every slice to the most common (H, W) shape found in the folder.
"""

import os
from collections import Counter

import numpy as np
import pydicom


def _resize_slice(arr: np.ndarray, target_h: int, target_w: int) -> np.ndarray:
    """
    Resize a 2D array to (target_h, target_w) using simple zoom.
    Uses scipy if available, otherwise falls back to nearest-neighbour via numpy.
    """
    if arr.shape == (target_h, target_w):
        return arr
    try:
        from scipy.ndimage import zoom
        zy = target_h / arr.shape[0]
        zx = target_w / arr.shape[1]
        return zoom(arr, (zy, zx), order=1).astype(np.float32)
    except ImportError:
        # Nearest-neighbour fallback (no scipy needed)
        y_idx = (np.arange(target_h) * arr.shape[0] / target_h).astype(int)
        x_idx = (np.arange(target_w) * arr.shape[1] / target_w).astype(int)
        return arr[np.ix_(y_idx, x_idx)]


def load_dicom_volume(folder_path: str):
    """
    Load all DICOM slices from *folder_path* and return:
      - volume      : np.ndarray of shape (Z, H, W)  [float32]
      - dicom_files : list[pydicom.Dataset] sorted by physical Z position
    """
    if not os.path.isdir(folder_path):
        raise FileNotFoundError(f"DICOM folder not found: {folder_path}")

    dcm_paths = [
        os.path.join(folder_path, f)
        for f in os.listdir(folder_path)
        if f.lower().endswith(".dcm")
    ]

    if not dcm_paths:
        raise ValueError(f"No .dcm files found in: {folder_path}")

    # Read all datasets
    datasets = [pydicom.dcmread(p) for p in dcm_paths]

    # Sort by ImagePositionPatient Z (fallback: InstanceNumber, then filename)
    def _sort_key(ds):
        try:
            return float(ds.ImagePositionPatient[2])
        except Exception:
            try:
                return float(ds.InstanceNumber)
            except Exception:
                return 0.0

    datasets.sort(key=_sort_key)

    # Decode pixel arrays and apply rescale
    raw_slices = []
    for ds in datasets:
        arr = ds.pixel_array.astype(np.float32)
        slope    = float(getattr(ds, "RescaleSlope",     1))
        intercept = float(getattr(ds, "RescaleIntercept", 0))
        arr = arr * slope + intercept
        raw_slices.append(arr)

    # If all slices share the same shape, stack directly
    shapes = [s.shape for s in raw_slices]
    if len(set(shapes)) == 1:
        volume = np.stack(raw_slices, axis=0)
    else:
        # Pick the most common (H, W) as the target resolution
        target_h, target_w = Counter(shapes).most_common(1)[0][0]
        print(
            f"[loader] Mixed image sizes detected — resizing all slices to "
            f"({target_h}, {target_w})."
        )
        resized = [_resize_slice(s, target_h, target_w) for s in raw_slices]
        volume = np.stack(resized, axis=0)

    print(f"[loader] Loaded {len(datasets)} slices → volume shape: {volume.shape}")
    return volume, datasets
