# Blender Add-ons for Photogrammetry & Anatomical Research

A collection of Blender add-ons designed for working with photogrammetry models in anatomical research and education.

| Add-on | File | Sidebar Tab | Description |
|---|---|---|---|
| **Landmark Registration** | `blender_landmarks.py` | Landmark Registration | Place, track, rename, and export anatomical landmarks |
| **3D Model Scaling** | `blender_scaling.py` | Model Scaling | Scale photogrammetry models to real-world dimensions |

---

# Landmark Registration

Place, track, rename, and export anatomical landmarks on 3D meshes. Inspired by the fiducial/landmark workflow in [3D Slicer](https://www.slicer.org/), adapted for the Blender environment.

## Features

- **Place landmarks** directly on mesh surfaces via raycasting (snaps to nearest vertex).
- **Landmark list** — a scrollable UIList that tracks every landmark across all objects in the scene.
- **Inline renaming** — click a landmark name in the list to rename it, or use the dedicated Rename dialog.
- **Delete individual landmarks** from the list and the underlying object data.
- **Jump to landmark** — centers the 3D viewport on any selected landmark.
- **Bulk delete** — remove all landmarks from selected objects or from the entire scene.
- **Export to CSV** — export landmark names and world-space coordinates for all objects.
- **Create landmark spheres** — generate small Ico spheres at landmark positions, organized into per-object collections.
- **Live 3D labels** — landmark names are drawn in the viewport at their vertex positions.

---

## Installation

1. Download `blender_landmarks.py`.
2. Open Blender → **Edit → Preferences → Add-ons → Install…**
3. Navigate to the downloaded file and click **Install Add-on**.
4. Enable the add-on by ticking the checkbox next to **"Landmark Registration"** in the add-on list.

The panel will appear in **View3D → Sidebar (N-panel) → Landmark Registration**.

---

## Usage

### Placing Landmarks

1. **Select** one or more mesh objects in the viewport.
2. Open the **Landmark Registration** panel in the sidebar.
3. Click **Place Landmarks**.
4. **Left-click** on the surface of a selected object to place a landmark. Each landmark is automatically numbered.
5. Press **Enter** to confirm all placed landmarks, or **Esc** to cancel and discard them.

> **Tip:** If you click on an area where two selected objects overlap, the landmark is placed on the surface closest to the camera.

### Managing Landmarks

| Action | How |
|---|---|
| **View all landmarks** | The **Landmark List** shows every landmark, its name, and the object it belongs to. |
| **Rename (inline)** | Click the landmark name directly in the list and type a new name. |
| **Rename (dialog)** | Select a landmark in the list and click the **Rename** button (Aa icon) on the right side. |
| **Delete one landmark** | Select it in the list and click the **Remove** button (− icon). |
| **Jump to landmark** | Select it and click the **Jump to** button (magnifier icon) to center the viewport on it. |
| **Refresh list** | Click the refresh icon (↻) next to the "Landmark List" header if the list gets out of sync. |

### Landmark Details

When a landmark is selected in the list, a details box below shows:

- The **object** the landmark belongs to.
- The **vertex index** on that object.
- The **world-space coordinates** (X, Y, Z).

### Bulk Operations

| Button | Description |
|---|---|
| **Delete Selected Object Landmarks** | Removes all landmarks from the currently selected object(s). |
| **Delete ALL Landmarks** | Removes every landmark from every object in the scene. |

### Export

Click **Export All Landmarks** to save a `.csv` file with the columns:

```
Object_Name, Landmark, X, Y, Z
```

Coordinates are in **world space**.

### Create Landmark Spheres

Click **Create Landmark Spheres** to generate small red Ico spheres at each landmark location. Spheres are organized into Blender collections named `Landmarks_<ObjectName>`.

---

## Keyboard Shortcuts (during Place Landmarks mode)

| Key | Action |
|---|---|
| **Left-click** | Place a landmark on the surface under the cursor |
| **Enter / Numpad Enter** | Confirm and keep all placed landmarks |
| **Esc** | Cancel and remove all landmarks placed in this session |
| **Middle-mouse / Scroll** | Navigate the viewport (passed through) |

---

# 3D Model Scaling

Scale photogrammetry models to real-world dimensions using point-pair measurements directly in Blender. Replaces the external tkinter-based scaling workflow by bringing everything into the 3D viewport.

## Features

- **Point-pair measurement** — click two points on the model surface to define a distance, then enter the corresponding real-world measurement.
- **Multiple measurements** — add as many measurement pairs as needed; the average scaling factor is computed automatically.
- **Standard deviation** — see how consistent your measurements are across pairs.
- **Re-pick points** — use the eyedropper to re-pick points for any existing measurement without deleting it.
- **Viewport overlay** — toggle an overlay showing point labels and model distances in the 3D view.
- **Two apply modes** — apply scaling and freeze the transform, or apply while keeping the scale editable.
- **Real-time recalculation** — the scaling factor updates automatically when real-world distances are changed.

## Installation

1. Download `blender_scaling.py`.
2. Open Blender → **Edit → Preferences → Add-ons → Install…**
3. Navigate to the downloaded file and click **Install Add-on**.
4. Enable the add-on by ticking the checkbox next to **"3D Model Scaling"** in the add-on list.

The panel will appear in **View3D → Sidebar (N-panel) → Model Scaling**.

## Usage

### Adding Measurements

1. **Select** the photogrammetry mesh in the viewport.
2. Open the **Model Scaling** panel in the sidebar.
3. Click **Add Measurement Pair**.
4. **Left-click** on the surface to place **Point A**.
5. **Left-click** again to place **Point B** — the model distance is calculated automatically.
6. In the detail box below the list, enter the **Real-World Distance (mm)** for that pair.
7. Repeat for additional measurement pairs.

> **Tip:** More measurement pairs produce a more robust and reliable average scaling factor.

### Managing Measurements

| Action | How |
|---|---|
| **View measurements** | The scrollable list shows all measurement pairs with their status. |
| **Edit label** | Click the label in the list or use the detail box below to rename. |
| **Re-pick points** | Select a measurement and click the eyedropper icon to re-pick both points. |
| **Remove measurement** | Select it and click the − button. |
| **Clear all** | Click **Clear All Measurements** to start over. |

### Measurement Details

When a measurement is selected in the list, a detail box shows:

- **Label** — editable name for the measurement.
- **Point A / Point B** — object name and vertex index for each point.
- **Model Distance** — Euclidean distance in Blender units.
- **Real-World Distance (mm)** — enter the corresponding real-world distance here.

### Scaling Results

The results box displays:

- **Valid pairs** — how many pairs have both a model distance and a real-world distance.
- **Scaling Factor** — the average ratio of real-world to model distances.
- **Std Dev** — standard deviation across all scaling factors (shown when ≥ 2 pairs).

### Applying the Scale

| Button | Description |
|---|---|
| **Apply Scaling & Freeze Transform** | Multiplies the object scale by the factor and applies the transform (`Ctrl+A` scale). |
| **Apply Scaling (Keep Transform)** | Multiplies the object scale but does not apply it, so you can revert or adjust later. |

### Keyboard Shortcuts (during Add Measurement / Re-pick mode)

| Key | Action |
|---|---|
| **Left-click** | Place a point on the surface under the cursor |
| **Esc** | Cancel the current measurement / re-pick |
| **Middle-mouse / Scroll** | Navigate the viewport (passed through) |

---

# General Information

## Requirements

| Requirement | Version |
|---|---|
| Blender | **4.0** or newer |
| Python packages | `numpy` (bundled with Blender) |

No external dependencies beyond what ships with Blender.

---

## How to Cite

If you use these add-ons in academic work, **you must cite the following publication**:

> Van Vlasselaer N, Keelson B, Scafoglieri A, Cattrysse E. Exploring reliable photogrammetry techniques for 3D modeling in anatomical research and education. *Anat Sci Educ*. 2024; **17**: 674–682. [https://doi.org/10.1002/ase.2391](https://doi.org/10.1002/ase.2391)

### BibTeX

```bibtex
@article{VanVlasselaer2024,
  author  = {Van Vlasselaer, N. and Keelson, B. and Scafoglieri, A. and Cattrysse, E.},
  title   = {Exploring reliable photogrammetry techniques for {3D} modeling in anatomical research and education},
  journal = {Anatomical Sciences Education},
  year    = {2024},
  volume  = {17},
  pages   = {674--682},
  doi     = {10.1002/ase.2391}
}
```

---

## License

Both **Landmark Registration** and **3D Model Scaling** are released under a **Creative Commons Attribution-NonCommercial 4.0 International (CC BY-NC 4.0)** license.

### You are free to

- **Share** — copy and redistribute the add-on in any medium or format.
- **Adapt** — remix, transform, and build upon the add-on.

### Under the following terms

- **Attribution** — You must give appropriate credit (see [How to Cite](#how-to-cite)), provide a link to the license, and indicate if changes were made.
- **NonCommercial** — You may **not** use the add-on for commercial purposes.

### Full license text

[https://creativecommons.org/licenses/by-nc/4.0/legalcode](https://creativecommons.org/licenses/by-nc/4.0/legalcode)

```
Copyright (c) 2024 Van Vlasselaer N.

This software is provided free of charge for non-commercial use only.
Commercial use of this software, in whole or in part, is strictly prohibited
without prior written permission from the author.

When using this software in academic publications, the following citation
is required:

  Van Vlasselaer N, Keelson B, Scafoglieri A, Cattrysse E. Exploring
  reliable photogrammetry techniques for 3D modeling in anatomical research
  and education. Anat Sci Educ. 2024; 17: 674–682.
  https://doi.org/10.1002/ase.2391

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
```

---

## Author

**N. Van Vlasselaer**

For questions, issues, or contributions, please contact the author.
