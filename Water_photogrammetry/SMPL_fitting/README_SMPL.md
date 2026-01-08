# SMPL Model Fitting for Photogrammetry Meshes

This collection of Python scripts provides tools for fitting SMPL (Skinned Multi-Person Linear) models to photogrammetry meshes of human subjects. The toolkit includes multiple approaches ranging from simple to advanced, with visualization and analysis capabilities.

## Overview

The SMPL model is a statistical model of human body shape and pose. These scripts allow you to:

1. **Fit SMPL models** to photogrammetry scans of humans
2. **Batch process** multiple meshes
3. **Analyze fitting quality** with distance metrics and visualizations
4. **Extract shape and pose parameters** for further analysis

## Files Description

### Core Scripts

- **`smpl_mesh_fitter.py`** - Advanced SMPL fitting with full optimization pipeline
- **`simple_smpl_fit.py`** - Basic SMPL fitting for quick testing
- **`batch_smpl_fit.py`** - Batch processing for multiple meshes
- **`analyze_smpl_results.py`** - Visualization and analysis tools
- **`SPML.py`** - Original simple fitting script (legacy)

### Requirements

- **`requirements.txt`** - Python package dependencies
- **`README_SMPL.md`** - This documentation file

## Installation

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Install SMPL-X library:**
   ```bash
   pip install smplx[all]
   ```

3. **Download SMPL models:**
   - Register at [SMPL website](https://smpl.is.tue.mpg.de/)
   - Download SMPL models and place them in the `smpl_models/` directory

## Usage Examples

### Basic Fitting (Simple Script)

```bash
python simple_smpl_fit.py
```

This will fit the SMPL model to the default mesh (`Aldo.obj`) using predefined settings.

### Advanced Fitting (Command Line)

```bash
python smpl_mesh_fitter.py input_mesh.obj \
    --gender MALE \
    --iterations 500 \
    --lr 0.01 \
    --output fitted_mesh.obj \
    --save_params
```

**Parameters:**
- `input_mesh.obj` - Input photogrammetry mesh
- `--gender` - SMPL model gender (MALE/FEMALE/NEUTRAL)
- `--iterations` - Number of optimization iterations
- `--lr` - Learning rate for optimization
- `--output` - Output path for fitted mesh
- `--save_params` - Save SMPL parameters to .npz file

### Batch Processing

```bash
python batch_smpl_fit.py input_meshes/ output_results/ \
    --gender MALE \
    --pattern "*.obj" \
    --iterations 500
```

**Parameters:**
- `input_meshes/` - Directory containing input mesh files
- `output_results/` - Directory for output files
- `--pattern` - File pattern to match (e.g., "*.obj", "*.ply")

### Analysis and Visualization

```bash
python analyze_smpl_results.py original_mesh.obj fitted_mesh.obj \
    --params fitted_params.npz \
    --output_dir analysis_plots/
```

This generates:
- Side-by-side mesh comparisons
- Distance distribution histograms
- SMPL parameter visualizations

## Script Details

### `smpl_mesh_fitter.py`

**Features:**
- Advanced optimization with learning rate scheduling
- Mesh preprocessing (outlier removal, downsampling)
- Comprehensive loss function with regularization
- Parameter saving/loading capabilities

**Key Parameters:**
- `lambda_shape`: Shape parameter regularization (default: 1e-4)
- `lambda_pose`: Pose parameter regularization (default: 1e-5)
- `lambda_transl`: Translation regularization (default: 1e-3)

### `batch_smpl_fit.py`

**Features:**
- Parallel processing capability
- Progress tracking and error handling
- Comprehensive result summaries
- Resume capability (skips already processed files)

**Output:**
- Fitted meshes (.obj files)
- SMPL parameters (.npz files)
- Processing summary (JSON file)

### `analyze_smpl_results.py`

**Features:**
- Mesh distance computation using sampling
- Statistical analysis (mean, median, percentiles)
- 3D visualizations
- Parameter interpretation plots

## SMPL Parameters

The SMPL model uses three main parameter types:

1. **Shape Parameters (betas)**: 10 coefficients controlling body shape
2. **Pose Parameters (body_pose)**: 69 coefficients for joint rotations
3. **Global Parameters**: 
   - `global_orient`: Overall body orientation (3 coefficients)
   - `transl`: Global translation (3 coefficients)

## Optimization Strategy

The fitting process uses the following loss function:

```
Total Loss = Chamfer Distance + λ₁ * Shape Regularization + λ₂ * Pose Regularization + λ₃ * Translation Regularization
```

Where:
- **Chamfer Distance**: Measures geometric similarity between meshes
- **Regularization terms**: Prevent overfitting and maintain realistic poses

## Tips for Better Results

### 1. Mesh Preprocessing
- Ensure input mesh is properly aligned
- Remove background/noise vertices
- Consider mesh resolution (10k-50k vertices work well)

### 2. Parameter Tuning
- Increase iterations for better convergence (500-1000)
- Adjust learning rate based on convergence speed
- Tune regularization weights for your specific use case

### 3. Gender Selection
- Use appropriate gender model for best results
- NEUTRAL model works well for children or ambiguous cases

### 4. Quality Assessment
- Check distance statistics (mean < 0.01 is typically good)
- Visualize results to identify problem areas
- Use parameter analysis to check for extreme values

## Common Issues and Solutions

### 1. Poor Convergence
- **Increase iterations**: Try 1000+ for complex poses
- **Adjust learning rate**: Lower LR (0.001) for stability
- **Check input mesh quality**: Remove noise and outliers

### 2. Unrealistic Poses
- **Increase pose regularization**: Higher `lambda_pose` values
- **Initialize with better pose**: Start from T-pose or similar

### 3. Scale Issues
- **Check mesh units**: Ensure consistent scaling
- **Adjust translation bounds**: Allow larger translation range

### 4. Memory Issues
- **Reduce mesh resolution**: Downsample input mesh
- **Use CPU**: Add `--device cpu` flag
- **Batch size**: Process fewer meshes simultaneously

## Output Files

### Fitted Mesh (.obj)
Standard OBJ file containing the fitted SMPL mesh with:
- Vertex positions in 3D space
- Face connectivity from SMPL topology

### Parameters (.npz)
NumPy archive containing:
- `betas`: Shape parameters [1, 10]
- `global_orient`: Global rotation [1, 3]
- `body_pose`: Joint rotations [1, 69]
- `transl`: Translation [1, 3]

### Analysis Plots
- **Mesh comparison**: Side-by-side visualization
- **Distance histograms**: Error distribution analysis
- **Parameter plots**: SMPL coefficient visualization

## Performance Benchmarks

Typical processing times on different hardware:

| Hardware | Mesh Size | Iterations | Time |
|----------|-----------|------------|------|
| RTX 3080 | 10k verts | 500 | ~30s |
| GTX 1060 | 10k verts | 500 | ~60s |
| CPU (8 cores) | 10k verts | 500 | ~180s |

## Research Applications

This toolkit is suitable for:

- **Anthropometric analysis**: Body shape measurements
- **Pose estimation**: Human posture analysis
- **Animation**: Character rigging and motion capture
- **Medical research**: Body shape studies
- **Fashion/clothing**: Fit analysis and sizing

## License and Attribution

Please cite the SMPL paper if you use this toolkit in research:

```
@article{SMPL:2015,
  title = {SMPL: A Skinned Multi-Person Linear Model},
  author = {Loper, Matthew and Mahmood, Naureen and Romero, Javier and Pons-Moll, Gerard and Black, Michael J.},
  journal = {ACM Transactions on Graphics (Proc. SIGGRAPH Asia)},
  year = {2015}
}
```

## Support

For issues and questions:
1. Check this documentation
2. Review error messages and logs
3. Try adjusting parameters
4. Create issue with minimal example

## Future Improvements

Potential enhancements:
- Multi-person fitting
- Temporal consistency for video sequences
- Integration with other body models (SMPL-X, STAR)
- Real-time fitting capabilities
