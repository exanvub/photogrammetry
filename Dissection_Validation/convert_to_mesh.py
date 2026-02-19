#!/usr/bin/env python3
"""
Medical Images to Mesh
Converts NRRD files or DICOM series into mesh formats (PLY, OBJ, STL)
"""

import nrrd
import numpy as np
from skimage import measure
import trimesh
import argparse
import os
import glob

try:
    import pydicom
    HAS_PYDICOM = True
except ImportError:
    HAS_PYDICOM = False


def read_dicom_series(dicom_path):
    """
    Read a DICOM series from a directory and return the 3D volume with spacing.

    Parameters:
    -----------
    dicom_path : str
        Path to directory containing DICOM files, or path to a single DICOM file.

    Returns:
    --------
    data : np.ndarray
        3D numpy array of the volume (in Hounsfield units if CT).
    spacing : np.ndarray
        Voxel spacing [z, y, x] in mm.
    """
    if not HAS_PYDICOM:
        raise ImportError(
            "pydicom is required to read DICOM files. Install it with: pip install pydicom"
        )

    # If a single file is given, use its parent directory
    if os.path.isfile(dicom_path):
        dicom_path = os.path.dirname(dicom_path)

    # Collect all DICOM files in the directory
    dicom_files = []
    for fname in sorted(os.listdir(dicom_path)):
        fpath = os.path.join(dicom_path, fname)
        if os.path.isfile(fpath):
            try:
                ds = pydicom.dcmread(fpath, stop_before_pixels=True, force=True)
                if hasattr(ds, 'pixel_array') or 'PixelData' in ds:
                    dicom_files.append(fpath)
            except Exception:
                # Also accept files with common DICOM extensions that fail the quick check
                if fname.lower().endswith(('.dcm', '.ima', '.dicom')):
                    dicom_files.append(fpath)

    if not dicom_files:
        # Fallback: try all files
        dicom_files = sorted([
            os.path.join(dicom_path, f) for f in os.listdir(dicom_path)
            if os.path.isfile(os.path.join(dicom_path, f))
        ])

    if not dicom_files:
        raise FileNotFoundError(f"No DICOM files found in: {dicom_path}")

    print(f"Found {len(dicom_files)} DICOM files in: {dicom_path}")

    # Read all slices
    slices = []
    for fpath in dicom_files:
        try:
            ds = pydicom.dcmread(fpath)
            if hasattr(ds, 'pixel_array'):
                slices.append(ds)
        except Exception:
            continue

    if not slices:
        raise ValueError(f"No readable DICOM slices found in: {dicom_path}")

    # Sort slices by ImagePositionPatient (z-coordinate) or InstanceNumber
    try:
        slices.sort(key=lambda s: float(s.ImagePositionPatient[2]))
    except (AttributeError, TypeError):
        try:
            slices.sort(key=lambda s: int(s.InstanceNumber))
        except (AttributeError, TypeError):
            pass  # keep original order

    print(f"Loaded {len(slices)} DICOM slices")

    # Build 3D volume
    first = slices[0]
    rows = int(first.Rows)
    cols = int(first.Columns)
    data = np.zeros((len(slices), rows, cols), dtype=np.float64)

    for i, s in enumerate(slices):
        img = s.pixel_array.astype(np.float64)
        # Apply rescale slope / intercept to get Hounsfield units
        slope = float(getattr(s, 'RescaleSlope', 1))
        intercept = float(getattr(s, 'RescaleIntercept', 0))
        data[i] = img * slope + intercept

    # Determine spacing
    pixel_spacing = getattr(first, 'PixelSpacing', [1.0, 1.0])
    # Slice thickness / spacing between slices
    if len(slices) > 1:
        try:
            z_spacing = abs(
                float(slices[1].ImagePositionPatient[2])
                - float(slices[0].ImagePositionPatient[2])
            )
        except (AttributeError, TypeError):
            z_spacing = float(getattr(first, 'SliceThickness', 1.0))
    else:
        z_spacing = float(getattr(first, 'SliceThickness', 1.0))

    spacing = np.array([z_spacing, float(pixel_spacing[0]), float(pixel_spacing[1])])

    return data, spacing


def read_nrrd_file(nrrd_file):
    """
    Read an NRRD file and return the 3D volume with spacing.

    Parameters:
    -----------
    nrrd_file : str
        Path to input NRRD file.

    Returns:
    --------
    data : np.ndarray
        3D numpy array of the volume.
    spacing : np.ndarray
        Voxel spacing.
    """
    data, header = nrrd.read(nrrd_file)

    # Get spacing information from header if available
    space_dirs = header.get('space directions', None)
    if space_dirs is not None:
        spacing = np.array([space_dirs[i][i] for i in range(len(space_dirs))])
    else:
        spacing = np.ones(3)

    return data, spacing


def detect_input_type(input_path):
    """
    Detect whether the input is a DICOM directory/file or an NRRD file.

    Returns:
    --------
    str : 'nrrd' or 'dicom'
    """
    if os.path.isfile(input_path):
        ext = os.path.splitext(input_path)[1].lower()
        if ext in ('.nrrd', '.nhdr'):
            return 'nrrd'
        if ext in ('.dcm', '.ima', '.dicom'):
            return 'dicom'
        # Try reading header to detect format
        try:
            nrrd.read_header(input_path)
            return 'nrrd'
        except Exception:
            pass
        try:
            if HAS_PYDICOM:
                pydicom.dcmread(input_path, stop_before_pixels=True, force=True)
                return 'dicom'
        except Exception:
            pass
        raise ValueError(f"Cannot determine file type for: {input_path}")
    elif os.path.isdir(input_path):
        return 'dicom'
    else:
        raise FileNotFoundError(f"Input path does not exist: {input_path}")


def volume_to_mesh(input_path, output_file, threshold=None, step_size=1, format='ply', mode='surface'):
    """
    Convert a medical image (NRRD file or DICOM series) to a mesh format.
    
    Parameters:
    -----------
    input_path : str
        Path to input NRRD file or directory containing DICOM files
    output_file : str
        Path to output mesh file
    threshold : float, optional
        Iso-surface threshold value. If None, uses mean of non-zero values (or auto-detected based on mode)
    step_size : int
        Step size for marching cubes (higher = faster but lower quality)
    format : str
        Output format: 'ply', 'obj', or 'stl'
    mode : str
        Extraction mode: 'surface' for outer surface, 'threshold' for iso-surface at specific value
    """
    
    # Detect input type and read volume
    input_type = detect_input_type(input_path)
    print(f"Detected input type: {input_type.upper()}")

    if input_type == 'nrrd':
        print(f"Reading NRRD file: {input_path}")
        data, spacing = read_nrrd_file(input_path)
    else:
        print(f"Reading DICOM series: {input_path}")
        data, spacing = read_dicom_series(input_path)

    print(f"Data shape: {data.shape}")
    print(f"Data type: {data.dtype}")
    print(f"Data range: [{data.min()}, {data.max()}]")
    print(f"Voxel spacing: {spacing}")
    
    # Determine threshold if not provided
    if threshold is None:
        if mode == 'surface':
            # For outer surface, use a threshold that captures air/tissue boundary
            # This should be between air (-1000) and tissue (0 to 100)
            threshold = -400
            print(f"Mode: outer surface - using threshold: {threshold}")
        else:
            # Use mean of non-zero values as threshold
            non_zero = data[data > 0]
            if len(non_zero) > 0:
                threshold = non_zero.mean()
            else:
                threshold = (data.max() - data.min()) / 2
            print(f"Auto-detected threshold: {threshold}")
    else:
        print(f"Using threshold: {threshold}")
    
    # Generate mesh using marching cubes
    print("Generating mesh with marching cubes algorithm...")
    try:
        verts, faces, normals, values = measure.marching_cubes(
            data, 
            level=threshold,
            step_size=step_size,
            spacing=tuple(spacing)
        )
        
        print(f"Generated mesh: {len(verts)} vertices, {len(faces)} faces")
        
        # Create trimesh object with process=True to clean up degenerate/duplicate geometry
        mesh = trimesh.Trimesh(vertices=verts, faces=faces, vertex_normals=normals, process=True)
        
        print(f"Cleaned mesh: {len(mesh.vertices)} vertices, {len(mesh.faces)} faces")
        
        # Export mesh
        print(f"Exporting to {output_file}...")
        mesh.export(output_file)
        
        print(f"Successfully converted {input_path} to {output_file}")
        print(f"\nYou can now import this file into Blender:")
        print(f"  File > Import > {format.upper()} > {os.path.basename(output_file)}")
        
        return mesh
        
    except Exception as e:
        print(f"Error during mesh generation: {e}")
        raise


# Keep backward-compatible alias
nrrd_to_mesh = volume_to_mesh


def main():
    parser = argparse.ArgumentParser(
        description='Convert medical images (NRRD or DICOM) to mesh formats for Blender',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Convert NRRD file with auto-detected threshold
  python nrrd_to_mesh.py "3 HERSENEN C2.nrrd" output.ply
  
  # Convert a DICOM series directory
  python nrrd_to_mesh.py /path/to/dicom_folder/ output.ply
  
  # Specify threshold value
  python nrrd_to_mesh.py input.nrrd output.stl --threshold 500
  
  # Lower quality for faster processing
  python nrrd_to_mesh.py input.nrrd output.obj --step-size 2
  
  # Export as STL format
  python nrrd_to_mesh.py input.nrrd output.stl --format stl
        """
    )
    
    parser.add_argument('input', help='Input NRRD file path or DICOM directory')
    parser.add_argument('output', help='Output mesh file path')
    parser.add_argument('--threshold', '-t', type=float, default=None,
                        help='Iso-surface threshold value (auto-detected if not specified)')
    parser.add_argument('--step-size', '-s', type=int, default=1,
                        help='Marching cubes step size (default: 1, higher = faster but lower quality)')
    parser.add_argument('--format', '-f', choices=['ply', 'obj', 'stl'], default='ply',
                        help='Output format (default: ply)')
    parser.add_argument('--mode', '-m', choices=['surface', 'threshold'], default='surface',
                        help='Extraction mode: "surface" for outer surface, "threshold" for iso-surface (default: surface)')
    
    args = parser.parse_args()
    
    # Check input path exists
    if not os.path.exists(args.input):
        print(f"Error: Input path '{args.input}' not found")
        return 1
    
    # Ensure output has correct extension
    output_ext = os.path.splitext(args.output)[1].lower()
    if output_ext not in ['.ply', '.obj', '.stl']:
        args.output = f"{args.output}.{args.format}"
    
    try:
        volume_to_mesh(
            args.input,
            args.output,
            threshold=args.threshold,
            step_size=args.step_size,
            format=args.format,
            mode=args.mode
        )
        return 0
    except Exception as e:
        print(f"Conversion failed: {e}")
        return 1


if __name__ == '__main__':
    exit(main())
