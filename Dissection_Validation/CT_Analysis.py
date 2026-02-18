"""
CT Photogrammetry Validation Analysis
======================================
Analyzes vertex quality data from PLY meshes representing distance to reference CT mesh.
Creates ridgeline (joy) plots to visualize the distribution of distances across different methods.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from typing import Dict, List, Tuple
import re


def read_ply_vertex_quality(ply_path: str) -> np.ndarray:
    """
    Read vertex quality values from a PLY file.
    
    Args:
        ply_path: Path to the PLY file
        
    Returns:
        numpy array of quality values
    """
    qualities = []
    in_data_section = False
    vertex_count = 0
    current_vertex = 0
    
    with open(ply_path, 'r') as f:
        for line in f:
            line = line.strip()
            
            # Parse header to get vertex count
            if line.startswith('element vertex'):
                vertex_count = int(line.split()[2])
            
            # Detect end of header
            if line == 'end_header':
                in_data_section = True
                continue
            
            # Read vertex data
            if in_data_section and current_vertex < vertex_count:
                values = line.split()
                if len(values) >= 8:  # x, y, z, r, g, b, a, quality
                    quality = float(values[7])
                    qualities.append(quality)
                    current_vertex += 1
    
    return np.array(qualities)


def parse_filename(filename: str) -> Dict[str, str]:
    """
    Parse information from PLY filename.
    
    Expected format: {Device}_Set_CT_{Method}_vs_CT.ply
    Example: CP_Set_CT_OC_vs_CT.ply
    
    Returns:
        Dictionary with 'device' and 'method' keys
    """
    # Remove .ply extension
    name = filename.replace('.ply', '')
    
    # Split by underscore
    parts = name.split('_')
    
    if len(parts) >= 5:
        device = parts[0]  # CP, DL, or Iphone
        method = parts[3]  # OC or RC
        return {
            'device': device,
            'method': method,
            'label': f"{device} - {method}"
        }
    else:
        return {
            'device': 'Unknown',
            'method': 'Unknown',
            'label': filename
        }


def normalize_quality_data(quality_values: np.ndarray) -> np.ndarray:
    """
    Normalize quality values by converting to density (probability distribution).
    This accounts for different vertex counts across meshes.
    
    Args:
        quality_values: Array of quality values
        
    Returns:
        Normalized quality values (as-is, normalization happens in histogram)
    """
    # Return as-is; normalization will be handled by histogram density parameter
    return quality_values


def remove_outliers(data: np.ndarray, method: str = 'iqr', 
                   iqr_multiplier: float = 1.5) -> Tuple[np.ndarray, int]:
    """
    Remove outliers from data.
    
    Args:
        data: Array of values
        method: Method to use ('iqr' or 'percentile')
        iqr_multiplier: Multiplier for IQR method (default 1.5)
        
    Returns:
        Tuple of (filtered_data, num_outliers_removed)
    """
    if method == 'iqr':
        # IQR method
        q1, q3 = np.percentile(data, [25, 75])
        iqr = q3 - q1
        lower_bound = q1 - iqr_multiplier * iqr
        upper_bound = q3 + iqr_multiplier * iqr
    elif method == 'percentile':
        # Percentile method - remove top and bottom 1%
        lower_bound, upper_bound = np.percentile(data, [1, 99])
    else:
        raise ValueError(f"Unknown method: {method}")
    
    mask = (data >= lower_bound) & (data <= upper_bound)
    filtered_data = data[mask]
    num_outliers = len(data) - len(filtered_data)
    
    return filtered_data, num_outliers


def load_all_meshes(data_folder: str, remove_outliers_flag: bool = True,
                   outlier_method: str = 'iqr') -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Load vertex quality data from all PLY files in the folder.
    
    Args:
        data_folder: Path to folder containing PLY files
        remove_outliers_flag: Whether to remove outliers
        outlier_method: Method for outlier removal ('iqr' or 'percentile')
        
    Returns:
        Tuple of (filtered_df, original_df)
    """
    data_path = Path(data_folder)
    ply_files = sorted(data_path.glob('*.ply'))
    
    all_data = []
    all_data_original = []
    
    for ply_file in ply_files:
        print(f"Loading {ply_file.name}...")
        
        # Read quality values
        qualities = read_ply_vertex_quality(str(ply_file))
        
        # Parse filename
        info = parse_filename(ply_file.name)
        
        # Store original data
        mesh_df_original = pd.DataFrame({
            'quality': qualities,
            'device': info['device'],
            'method': info['method'],
            'label': info['label']
        })
        all_data_original.append(mesh_df_original)
        
        # Apply outlier removal if requested
        if remove_outliers_flag:
            qualities_filtered, num_outliers = remove_outliers(qualities, method=outlier_method)
            print(f"  Original: {len(qualities):,} vertices, "
                  f"mean: {np.mean(qualities):.3f} mm, "
                  f"median: {np.median(qualities):.3f} mm")
            print(f"  Removed {num_outliers:,} outliers ({num_outliers/len(qualities)*100:.2f}%)")
            print(f"  Filtered: {len(qualities_filtered):,} vertices, "
                  f"mean: {np.mean(qualities_filtered):.3f} mm, "
                  f"median: {np.median(qualities_filtered):.3f} mm")
            qualities_to_use = qualities_filtered
        else:
            print(f"  Loaded {len(qualities):,} vertices, "
                  f"mean distance: {np.mean(qualities):.3f} mm, "
                  f"median: {np.median(qualities):.3f} mm")
            qualities_to_use = qualities
        
        # Create dataframe for this mesh
        mesh_df = pd.DataFrame({
            'quality': qualities_to_use,
            'device': info['device'],
            'method': info['method'],
            'label': info['label']
        })
        
        all_data.append(mesh_df)
    
    # Combine all data
    df = pd.concat(all_data, ignore_index=True)
    df_original = pd.concat(all_data_original, ignore_index=True)
    return df, df_original


def create_ridgeline_plot(df: pd.DataFrame, output_path: str = None, 
                          xlim: Tuple[float, float] = None):
    """
    Create an overlapping ridgeline (joy) plot of vertex quality distributions.
    
    Args:
        df: DataFrame with quality data
        output_path: Optional path to save the figure
        xlim: Optional tuple (min, max) for x-axis limits
    """
    from scipy import stats
    
    # Get unique labels in a consistent order
    labels = sorted(df['label'].unique())
    n_labels = len(labels)
    
    # Create figure with single axis
    fig, ax = plt.subplots(figsize=(14, 8))
    
    # Color palette - using a colorblind-friendly palette
    colors = sns.color_palette("colorblind", n_labels)
    
    # Determine x-axis range if not specified
    if xlim is None:
        all_data = df['quality'].values
        q01, q99 = np.percentile(all_data, [1, 99])
        xlim = (q01, q99)
    
    x_range = np.linspace(xlim[0], xlim[1], 1000)
    
    # Calculate vertical spacing with overlap
    max_density = 0
    kdes = []
    
    # Pre-compute KDEs to find max density for scaling
    # Also store full dataset statistics
    full_stats = {}
    for label in labels:
        full_data = df[df['label'] == label]['quality'].values
        
        # Store statistics from full dataset
        full_stats[label] = {
            'mean': np.mean(full_data),
            'median': np.median(full_data),
            'std': np.std(full_data)
        }
        
        # Filter data to xlim range for KDE
        data = full_data[(full_data >= xlim[0]) & (full_data <= xlim[1])]
        if len(data) > 10:
            kde = stats.gaussian_kde(data, bw_method=0.15)
            density = kde(x_range)
            kdes.append(density)
            max_density = max(max_density, np.max(density))
        else:
            kdes.append(np.zeros_like(x_range))
    
    # Vertical spacing (adjust for overlap)
    vertical_spacing = max_density * 0.6  # Reduced for more overlap
    
    # Plot each distribution in reverse order so bottom ones are drawn last (on top)
    for idx, (label, color, density) in enumerate(reversed(list(zip(labels, colors, kdes)))):
        # Calculate y_offset based on original position
        y_offset = (n_labels - 1 - idx) * vertical_spacing
        
        # Plot KDE with fill
        ax.fill_between(x_range, y_offset, y_offset + density, 
                       alpha=1.0, color=color, linewidth=0)
        ax.plot(x_range, y_offset + density, color=color, linewidth=2)
        
        # Add a baseline
        ax.plot(x_range, np.full_like(x_range, y_offset), 
               color='black', linewidth=0.5, alpha=0.3)
        
        # Add label text
        ax.text(xlim[0] + (xlim[1] - xlim[0]) * 0.02, y_offset + max_density * 0.35, 
               label, fontsize=11, fontweight='bold', va='bottom')
        
        # Add statistics text from full dataset
        mean_val = full_stats[label]['mean']
        median_val = full_stats[label]['median']
        std_val = full_stats[label]['std']
        stats_text = f'μ={mean_val:.3f}, σ={std_val:.3f}, med={median_val:.3f}'
        ax.text(xlim[1] - (xlim[1] - xlim[0]) * 0.02, y_offset + max_density * 0.35,
               stats_text, fontsize=9, va='bottom', ha='right',
               bbox=dict(boxstyle='round,pad=0.4', facecolor='white', 
                        edgecolor=color, alpha=0.9, linewidth=1.5))
        
        # Add mean marker
        if xlim[0] <= mean_val <= xlim[1]:
            ax.plot([mean_val], [y_offset], 'o', color='black', 
                   markersize=6, zorder=10)
            ax.axvline(mean_val, ymin=(y_offset)/(n_labels*vertical_spacing*1.15), 
                      ymax=(y_offset + max_density*0.8)/(n_labels*vertical_spacing*1.15),
                      color='black', linestyle='--', linewidth=1, alpha=0.3)
    
    # Styling - add extra space at top to prevent cropping
    ax.set_xlim(xlim)
    ax.set_ylim(-vertical_spacing * 0.1, (n_labels * vertical_spacing) + max_density * 0.5)
    ax.set_xlabel('Distance to CT Reference (mm)', fontsize=13, fontweight='bold')


    ax.set_yticks([])
    ax.spines['left'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.grid(axis='x', alpha=0.3, linestyle='--')
    ax.axvline(0, color='red', linestyle='-', linewidth=1.5, alpha=0.5, label='Reference (0 mm)')
    
    # Title
    title = f'Vertex Quality Distribution - Ridgeline Plot\n({xlim[0]:.2f} to {xlim[1]:.2f} mm)'
    ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
    
    # Add legend for the zero line
    ax.legend(loc='upper right', framealpha=0.9)
    
    plt.tight_layout()
    
    if output_path:
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"Saved ridgeline plot to {output_path}")
    
    plt.show()
    plt.close()


def create_summary_statistics(df: pd.DataFrame, output_path: str = None):
    """
    Create a summary statistics table.
    
    Args:
        df: DataFrame with quality data
        output_path: Optional path to save CSV
    """
    summary = df.groupby(['device', 'method', 'label'])['quality'].agg([
        ('count', 'count'),
        ('mean', 'mean'),
        ('std', 'std'),
        ('median', 'median'),
        ('q25', lambda x: np.percentile(x, 25)),
        ('q75', lambda x: np.percentile(x, 75)),
        ('min', 'min'),
        ('max', 'max')
    ]).reset_index()
    
    print("\n" + "="*80)
    print("SUMMARY STATISTICS")
    print("="*80)
    print(summary.to_string(index=False))
    print("="*80)
    
    if output_path:
        summary.to_csv(output_path, index=False)
        print(f"\nSaved summary statistics to {output_path}")
    
    return summary


def create_violin_plot(df: pd.DataFrame, output_path: str = None, 
                       xlim: Tuple[float, float] = None):
    """
    Create a violin plot comparing distributions.
    
    Args:
        df: DataFrame with quality data
        output_path: Optional path to save the figure
        xlim: Optional tuple (min, max) for y-axis limits
    """
    # Filter data if needed
    plot_df = df.copy()
    if xlim is not None:
        plot_df = plot_df[(plot_df['quality'] >= xlim[0]) & (plot_df['quality'] <= xlim[1])]
    
    # Create figure
    fig, ax = plt.subplots(figsize=(12, 7))
    
    # Create violin plot
    parts = ax.violinplot([plot_df[plot_df['label'] == label]['quality'].values 
                           for label in sorted(plot_df['label'].unique())],
                          positions=range(len(plot_df['label'].unique())),
                          widths=0.7,
                          showmeans=True,
                          showmedians=True,
                          showextrema=True)
    
    # Color the violins
    colors = sns.color_palette("colorblind", len(plot_df['label'].unique()))
    for patch, color in zip(parts['bodies'], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)
    
    # Styling
    ax.set_xticks(range(len(plot_df['label'].unique())))
    ax.set_xticklabels(sorted(plot_df['label'].unique()), rotation=45, ha='right')
    ax.set_xlabel('Method', fontsize=12, fontweight='bold')
    ax.set_ylabel('Distance to CT Reference (mm)', fontsize=12, fontweight='bold')
    
    title = 'Vertex Quality Distribution - Violin Plot'
    if xlim is not None:
        title += f'\n({xlim[0]:.2f} to {xlim[1]:.2f} mm)'
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    ax.axhline(0, color='red', linestyle='-', linewidth=1.5, alpha=0.5)
    
    if xlim is not None:
        ax.set_ylim(xlim)
    
    plt.tight_layout()
    
    if output_path:
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"Saved violin plot to {output_path}")
    
    plt.show()
    plt.close()


def main():
    """Main analysis pipeline."""
    # Configuration
    script_dir = Path(__file__).parent
    data_folder = script_dir / "DATA" / "CT_VQ" / "vs_CT"
    output_folder = data_folder / "analysis_results"
    output_folder.mkdir(parents=True, exist_ok=True)
    
    # Load all mesh data with outlier removal
    print("Loading PLY meshes and removing outliers...")
    print("Using IQR method (Q1 - 1.5*IQR to Q3 + 1.5*IQR)\n")
    # df, df_original = load_all_meshes(data_folder, remove_outliers_flag=True, 
    #                                   outlier_method='iqr')
    print("using percentile method (1st to 99th percentile)\n")
    df, df_original = load_all_meshes(data_folder, remove_outliers_flag=True, 
                                      outlier_method='percentile')
    print(f"\nTotal vertices after filtering: {len(df):,}")
    print(f"Original total vertices: {len(df_original):,}")
    print(f"Total outliers removed: {len(df_original) - len(df):,} "
          f"({(len(df_original) - len(df))/len(df_original)*100:.2f}%)")
    print(f"Number of meshes: {df['label'].nunique()}")
    
    # Create summary statistics
    summary = create_summary_statistics(
        df, 
        output_path=output_folder / "summary_statistics.csv"
    )
    
    # Create ridgeline plots with different zoom levels
    print("\nCreating ridgeline plot (focused on main distribution -1 to +1 mm)...")
    create_ridgeline_plot(
        df, 
        output_path=output_folder / "ridgeline_plot_focused.png",
        xlim=(-1.0, 1.0)
    )
    
    print("\nCreating ridgeline plot (extended range -2 to +2 mm)...")
    create_ridgeline_plot(
        df, 
        output_path=output_folder / "ridgeline_plot_extended.png",
        xlim=(-2.0, 2.0)
    )
    
    print("\nCreating ridgeline plot (full range auto-scaled)...")
    create_ridgeline_plot(
        df, 
        output_path=output_folder / "ridgeline_plot_full.png",
        xlim=None  # Auto-scale to 1st-99th percentile
    )
    
    # Create violin plots
    print("\nCreating violin plot (focused -1 to +1 mm)...")
    create_violin_plot(
        df,
        output_path=output_folder / "violin_plot_focused.png",
        xlim=(-1.0, 1.0)
    )
    
    print("\nCreating violin plot (extended -2 to +2 mm)...")
    create_violin_plot(
        df,
        output_path=output_folder / "violin_plot_extended.png",
        xlim=(-2.0, 2.0)
    )
    
    print("\n" + "="*80)
    print("Analysis complete! Results saved to:", output_folder)
    print("="*80)


if __name__ == "__main__":
    main()
