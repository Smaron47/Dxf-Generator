# Dxf-Generator
DXF Triangle Generator is a desktop application for fabricators and CNC operators to generate precise DXF outlines of a custom triangular chimney layout. Users specify length (L) and width (W), visualize the nested geometry, and export a clean outline DXF for CNC cutting or CAD import.
# DXF Triangle Generator Documentation

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Key Features](#key-features)
3. [Technology Stack & Dependencies](#technology-stack--dependencies)
4. [Installation & Setup](#installation--setup)
5. [File Structure](#file-structure)
6. [User Interface](#user-interface)
7. [Core Components & Workflow](#core-components--workflow)

   * 7.1 `compute_updated_drawing`
   * 7.2 Outline Extraction
   * 7.3 DXF Saving
   * 7.4 Matplotlib Preview
8. [Class & Function Descriptions](#class--function-descriptions)
9. [Usage Guide](#usage-guide)
10. [Customization & Extensibility](#customization--extensibility)
11. [Troubleshooting & FAQs](#troubleshooting--faqs)
12. [SEO Keywords](#seo-keywords)

---

## 1. Project Overview

**DXF Triangle Generator** is a desktop application for fabricators and CNC operators to generate precise DXF outlines of a custom triangular chimney layout. Users specify length (L) and width (W), visualize the nested geometry, and export a clean outline DXF for CNC cutting or CAD import.

## 2. Key Features

* **Parametric Geometry**: Automatically computes core dimensions, offsets, and rectangle cutouts based on input L and W.
* **Outline Optimization**: Extracts only the outermost outline and essential edges using Shapely (if available), otherwise deduplicates segments.
* **DXF Export**: Saves the computed outline to a DXF file via `ezdxf`.
* **Interactive Preview**: Matplotlib-based rendering in a Tkinter GUI for instant visual feedback.
* **User-Friendly GUI**: Simple form to input dimensions, generate layout, and save DXF.

## 3. Technology Stack & Dependencies

* **Python 3.7+**
* **Tkinter** (standard)
* **ezdxf** for DXF creation
* **matplotlib** for preview plotting
* **Shapely** (optional, for true outline extraction)

Install via pip:

```bash
pip install ezdxf matplotlib shapely
```

## 4. Installation & Setup

1. Clone or download the repository.
2. Ensure Python 3.7+ is installed.
3. Install dependencies:

   ```bash
   pip install ezdxf matplotlib shapely
   ```
4. Run the application:

   ```bash
   python dxf_generator.py
   ```

## 5. File Structure

```
DXFGenerator/
├── dxf_generator.py       # Main application
└── requirements.txt       # Dependency list
```

## 6. User Interface

* Two input fields:

  * **Width (W)**
  * **Height (L)**
* Buttons:

  * **Generate**: Compute and render layout.
  * **Save as DXF**: Export the outline to a .dxf file.
* **Text Box**: Shows calculated dimension values and formulas.
* **Canvas**: Matplotlib figure displaying the outline.

## 7. Core Components & Workflow

### 7.1 `compute_updated_drawing(L, W)`

* Computes derived dimensions A…I and geometric groups:

  * **group1**: Primary outline segments.
  * **group2**: Base small rectangles segments.
  * **Rotated copies** for mirroring.
* Returns a dict containing sheet size, segments, rectangles, and a summary text.

### 7.2 Outline Extraction

* **`uniq_segments`**: Deduplicates shared edges.
* **`get_outline_segments`**: Uses Shapely’s `polygonize` for true outer boundary, else falls back to dedupe.

### 7.3 DXF Saving

* **`save_dxf(data, filename)`**:

  * Creates a new DXF using `ezdxf`.
  * Draws sheet border and cleaned outline segments.
  * Saves to user‑provided path.

### 7.4 Matplotlib Preview

* **`plot_drawing(data, canvas)`**:

  * Plots sheet border and outline on a Matplotlib figure.
  * Inverts the Y axis to match CAD coordinate orientation.
  * Embeds figure in Tkinter via `FigureCanvasTkAgg`.

## 8. Class & Function Descriptions

### `class DXFApp(tk.Tk)`

* Inherits `Tk` to build the main window.
* **UI Elements**: Input fields, buttons, text log, and preview canvas.
* **`on_generate()`**: Reads inputs, calls `compute_updated_drawing`, updates text box, and calls `plot_drawing`.
* **`on_save()`**: Prompts for filename and calls `save_dxf`.

Other helper functions:

* `compute_updated_drawing`, `uniq_segments`, `get_outline_segments`, `save_dxf`, `plot_drawing`.

## 9. Usage Guide

1. Launch the app.
2. Enter numeric **Width** and **Height**.
3. Click **Generate** to compute and preview the outline.
4. Review the calculated parameters in the text panel.
5. Click **Save as DXF** and choose a location to export.
6. Import the DXF into your CNC/CAD software.

## 10. Customization & Extensibility

* **Profiles without Shapely**: Remove Shapely import to work in minimal installs.
* **Different Sheet Size**: Modify `sheet_W`, `sheet_L` constants.
* **Additional Cutouts**: Extend `group2` or `rects2` definitions.
* **Alternate Export**: Integrate SVG or DXF versioning options.

## 11. Troubleshooting & FAQs

* **Blank Preview**: Ensure inputs are numeric; invalid parse shows an error.
* **Shapely Missing**: App still runs but uses simple deduplication.
* **DXF Errors**: Confirm `ezdxf` is installed and file path is writable.

## 12. SEO Keywords

```
DXF generator CNC
parametric DXF Python
chimney layout DXF
ezdxf tutorial
tkinter CAD tool
matplotlib DXF preview
Shapely outline extraction
triangle DXF Python
geometry CNC software
CAD automation script
DXF generator CNC
parametric DXF Python
chimney layout DXF
ezdxf tutorial
tkinter CAD tool
matplotlib DXF preview
Shapely outline extraction
triangle DXF Python
geometry CNC software
CAD automation script
```
