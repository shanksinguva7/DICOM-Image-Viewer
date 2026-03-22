"""
display.py
----------
Displays DICOM image data using matplotlib.

- 3D volumes (CT, MRI — large Z): shows interactive axial / sagittal / coronal
  orthogonal views with independent sliders.
- 2D datasets (X-ray, CR, DX — small Z < 20): shows three neighbouring frames
  side-by-side with a single frame-select slider, since cross-sections through
  only a handful of slices would be invisible.
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider

# Datasets with fewer Z-slices than this threshold are treated as 2D collections
_2D_THRESHOLD = 20


def _normalize(arr: np.ndarray) -> np.ndarray:
    """Normalize a 2D slice to [0, 1] for display."""
    lo, hi = arr.min(), arr.max()
    if hi == lo:
        return np.zeros_like(arr, dtype=np.float32)
    return (arr - lo) / (hi - lo)


# ── 3D volume viewer (CT / MRI) ───────────────────────────────────────────────

def _display_3d(volume: np.ndarray, title: str):
    """Orthogonal slice viewer for true 3D volumes."""
    Z, H, W = volume.shape
    z0, y0, x0 = Z // 2, H // 2, W // 2

    fig, axes = plt.subplots(1, 3, figsize=(16, 5))
    fig.suptitle(title, fontsize=14, fontweight="bold", color="white")
    fig.patch.set_facecolor("#1a1a2e")

    ax_ax, ax_sag, ax_cor = axes

    img_ax  = ax_ax.imshow(_normalize(volume[z0, :, :]),  cmap="gray", origin="upper")
    img_sag = ax_sag.imshow(_normalize(volume[:, :, x0]), cmap="gray", origin="upper")
    img_cor = ax_cor.imshow(_normalize(volume[:, y0, :]), cmap="gray", origin="upper")

    for ax, lbl in zip(axes, ["Axial (Z)", "Sagittal (X)", "Coronal (Y)"]):
        ax.set_title(lbl, color="white", fontsize=11)
        ax.axis("off")
        ax.set_facecolor("black")

    fig.subplots_adjust(bottom=0.20, top=0.88)
    slider_color = "#e94560"

    ax_sl_z = fig.add_axes([0.10, 0.10, 0.22, 0.03], facecolor="#16213e")
    ax_sl_x = fig.add_axes([0.40, 0.10, 0.22, 0.03], facecolor="#16213e")
    ax_sl_y = fig.add_axes([0.70, 0.10, 0.22, 0.03], facecolor="#16213e")

    sl_z = Slider(ax_sl_z, "Z", 0, Z - 1, valinit=z0, valstep=1, color=slider_color)
    sl_x = Slider(ax_sl_x, "X", 0, W - 1, valinit=x0, valstep=1, color=slider_color)
    sl_y = Slider(ax_sl_y, "Y", 0, H - 1, valinit=y0, valstep=1, color=slider_color)

    for sl in (sl_z, sl_x, sl_y):
        sl.label.set_color("white")
        sl.valtext.set_color("white")

    def update(_):
        img_ax.set_data(_normalize(volume[int(sl_z.val), :, :]))
        img_sag.set_data(_normalize(volume[:, :, int(sl_x.val)]))
        img_cor.set_data(_normalize(volume[:, int(sl_y.val), :]))
        fig.canvas.draw_idle()

    sl_z.on_changed(update)
    sl_x.on_changed(update)
    sl_y.on_changed(update)

    plt.show()


# ── 2D image set viewer (X-ray / CR / DX) ────────────────────────────────────

def _display_2d(volume: np.ndarray, title: str):
    """
    Frame gallery viewer for 2D datasets.
    Shows the selected frame (centre panel) plus the previous and next frames.
    A single slider lets the user scroll through all images.
    """
    Z = volume.shape[0]
    mid = Z // 2

    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    fig.suptitle(title, fontsize=14, fontweight="bold", color="white")
    fig.patch.set_facecolor("#1a1a2e")

    def _frame(idx):
        """Clamp idx to valid range."""
        return int(np.clip(idx, 0, Z - 1))

    # Labels
    labels = ["Previous Frame", "Current Frame", "Next Frame"]
    imgs = []
    for ax, lbl in zip(axes, labels):
        ax.set_facecolor("black")
        ax.axis("off")
        ax.set_title(lbl, color="white", fontsize=11)

    imgs.append(axes[0].imshow(_normalize(volume[_frame(mid - 1)]), cmap="gray"))
    imgs.append(axes[1].imshow(_normalize(volume[_frame(mid)]),     cmap="gray"))
    imgs.append(axes[2].imshow(_normalize(volume[_frame(mid + 1)]), cmap="gray"))

    # Highlight border on centre panel
    for spine in axes[1].spines.values():
        spine.set_edgecolor("#e94560")
        spine.set_linewidth(2)
        spine.set_visible(True)

    fig.subplots_adjust(bottom=0.18, top=0.88)

    ax_sl = fig.add_axes([0.25, 0.07, 0.50, 0.04], facecolor="#16213e")
    sl = Slider(ax_sl, "Frame", 0, Z - 1, valinit=mid, valstep=1, color="#e94560")
    sl.label.set_color("white")
    sl.valtext.set_color("white")

    # Frame counter text
    frame_text = fig.text(
        0.5, 0.02, f"Frame {mid + 1} / {Z}",
        ha="center", color="#aaaaaa", fontsize=10
    )

    def update(_):
        z = int(sl.val)
        imgs[0].set_data(_normalize(volume[_frame(z - 1)]))
        imgs[1].set_data(_normalize(volume[_frame(z)]))
        imgs[2].set_data(_normalize(volume[_frame(z + 1)]))
        frame_text.set_text(f"Frame {z + 1} / {Z}")
        fig.canvas.draw_idle()

    sl.on_changed(update)
    plt.show()


# ── Public API ────────────────────────────────────────────────────────────────

def display_slices(volume: np.ndarray, title: str = "DICOM Volume"):
    """
    Auto-select the right viewer based on volume depth:
      - Z >= 20  →  3D orthogonal viewer (Axial / Sagittal / Coronal)
      - Z <  20  →  2D frame gallery viewer (Prev / Current / Next)
    """
    Z = volume.shape[0]
    if Z >= _2D_THRESHOLD:
        _display_3d(volume, title)
    else:
        mode_note = f"2D X-ray dataset ({Z} images)"
        print(f"[display] {mode_note} — switching to frame gallery view.")
        _display_2d(volume, f"{title}  |  {mode_note}")


def display_summary_grid(volume: np.ndarray, n: int = 6):
    """
    Display a quick grid of n evenly-spaced frames — useful as a fast
    sanity-check overview of the entire volume or image collection.
    """
    Z = volume.shape[0]
    n = min(n, Z)
    indices = np.linspace(0, Z - 1, n, dtype=int)

    fig, axes = plt.subplots(1, n, figsize=(4 * n, 4))
    fig.suptitle("Image Overview", fontsize=13, fontweight="bold", color="white")
    fig.patch.set_facecolor("#1a1a2e")

    if n == 1:
        axes = [axes]

    for ax, idx in zip(axes, indices):
        ax.imshow(_normalize(volume[idx]), cmap="gray")
        ax.set_title(f"#{idx}", color="white", fontsize=9)
        ax.axis("off")

    plt.tight_layout()
    plt.show()
