#!/usr/bin/env python3
"""
SMPL Fitting Visualization and Analysis Tools

This script provides utilities for visualizing SMPL fitting results,
comparing original and fitted meshes, and analyzing fitting quality.
"""

import numpy as np
import trimesh
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import argparse
import os
from smplx import SMPL


def load_smpl_from_params(param_file, smpl_model_path, gender='MALE'):
    """
    Load SMPL mesh from saved parameters.
    
    Args:
        param_file (str): Path to .npz parameter file
        smpl_model_path (str): Path to SMPL models directory
        gender (str): SMPL model gender
        
    Returns:
        trimesh.Trimesh: Generated SMPL mesh
    """
    import torch
    
    device = torch.device("cpu")
    
    # Load SMPL model
    smpl = SMPL(
        model_path=smpl_model_path,
        gender=gender,
        create_global_orient=True,
        create_body_pose=True,
        create_betas=True
    ).to(device)
    
    # Load parameters
    params = np.load(param_file)
    
    # Convert to tensors
    betas = torch.tensor(params['betas'], dtype=torch.float32, device=device)
    global_orient = torch.tensor(params['global_orient'], dtype=torch.float32, device=device)
    body_pose = torch.tensor(params['body_pose'], dtype=torch.float32, device=device)
    transl = torch.tensor(params['transl'], dtype=torch.float32, device=device)
    
    # Generate mesh
    with torch.no_grad():
        output = smpl(
            betas=betas,
            global_orient=global_orient,
            body_pose=body_pose,
            transl=transl
        )
        
        mesh = trimesh.Trimesh(
            vertices=output.vertices[0].cpu().numpy(),
            faces=smpl.faces
        )
    
    return mesh


def compute_mesh_distances(mesh1, mesh2, num_samples=10000):
    """
    Compute distances between two meshes.
    
    Args:
        mesh1, mesh2: trimesh.Trimesh objects
        num_samples: Number of points to sample for distance computation
        
    Returns:
        dict: Distance statistics
    """
    from scipy.spatial.distance import cdist
    
    # Sample points from meshes
    points1 = mesh1.sample(num_samples)
    points2 = mesh2.sample(num_samples)
    
    # Compute distances
    distances_1_to_2 = cdist(points1, points2).min(axis=1)
    distances_2_to_1 = cdist(points2, points1).min(axis=1)
    
    # Combine distances (symmetric)
    all_distances = np.concatenate([distances_1_to_2, distances_2_to_1])
    
    stats = {
        'mean': np.mean(all_distances),
        'median': np.median(all_distances),
        'std': np.std(all_distances),
        'max': np.max(all_distances),
        'min': np.min(all_distances),
        'percentile_95': np.percentile(all_distances, 95),
        'distances_1_to_2': distances_1_to_2,
        'distances_2_to_1': distances_2_to_1
    }
    
    return stats


def visualize_mesh_comparison(original_mesh, fitted_mesh, title="Mesh Comparison"):
    """
    Create a side-by-side visualization of original and fitted meshes.
    
    Args:
        original_mesh: trimesh.Trimesh of original scan
        fitted_mesh: trimesh.Trimesh of fitted SMPL model
        title: Plot title
    """
    fig = plt.figure(figsize=(15, 6))
    
    # Original mesh
    ax1 = fig.add_subplot(121, projection='3d')
    vertices = original_mesh.vertices
    ax1.scatter(vertices[:, 0], vertices[:, 1], vertices[:, 2], 
               c=vertices[:, 2], cmap='viridis', s=0.1, alpha=0.6)
    ax1.set_title('Original Scan')
    ax1.set_xlabel('X')
    ax1.set_ylabel('Y')
    ax1.set_zlabel('Z')
    
    # Fitted mesh
    ax2 = fig.add_subplot(122, projection='3d')
    vertices = fitted_mesh.vertices
    ax2.scatter(vertices[:, 0], vertices[:, 1], vertices[:, 2], 
               c=vertices[:, 2], cmap='viridis', s=0.1, alpha=0.6)
    ax2.set_title('Fitted SMPL')
    ax2.set_xlabel('X')
    ax2.set_ylabel('Y')
    ax2.set_zlabel('Z')
    
    plt.suptitle(title)
    plt.tight_layout()
    return fig


def plot_distance_histogram(distance_stats, title="Distance Distribution"):
    """
    Plot histogram of distances between meshes.
    
    Args:
        distance_stats: Output from compute_mesh_distances
        title: Plot title
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    
    # Distance histogram
    all_distances = np.concatenate([
        distance_stats['distances_1_to_2'], 
        distance_stats['distances_2_to_1']
    ])
    
    ax1.hist(all_distances, bins=50, alpha=0.7, density=True)
    ax1.axvline(distance_stats['mean'], color='red', linestyle='--', 
                label=f"Mean: {distance_stats['mean']:.4f}")
    ax1.axvline(distance_stats['median'], color='orange', linestyle='--', 
                label=f"Median: {distance_stats['median']:.4f}")
    ax1.set_xlabel('Distance')
    ax1.set_ylabel('Density')
    ax1.set_title('Distance Distribution')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Cumulative distribution
    sorted_distances = np.sort(all_distances)
    cumulative = np.arange(1, len(sorted_distances) + 1) / len(sorted_distances)
    
    ax2.plot(sorted_distances, cumulative)
    ax2.axvline(distance_stats['percentile_95'], color='red', linestyle='--',
                label=f"95th percentile: {distance_stats['percentile_95']:.4f}")
    ax2.set_xlabel('Distance')
    ax2.set_ylabel('Cumulative Probability')
    ax2.set_title('Cumulative Distance Distribution')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    plt.suptitle(title)
    plt.tight_layout()
    return fig


def analyze_smpl_parameters(param_file):
    """
    Analyze and visualize SMPL parameters.
    
    Args:
        param_file: Path to .npz parameter file
    """
    params = np.load(param_file)
    
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    
    # Shape parameters (betas)
    axes[0, 0].bar(range(len(params['betas'].flatten())), params['betas'].flatten())
    axes[0, 0].set_title('Shape Parameters (Betas)')
    axes[0, 0].set_xlabel('Parameter Index')
    axes[0, 0].set_ylabel('Value')
    axes[0, 0].grid(True, alpha=0.3)
    
    # Global orientation
    axes[0, 1].bar(['X', 'Y', 'Z'], params['global_orient'].flatten())
    axes[0, 1].set_title('Global Orientation')
    axes[0, 1].set_ylabel('Rotation (radians)')
    axes[0, 1].grid(True, alpha=0.3)
    
    # Body pose (first 21 joints, 3 params each)
    body_pose_reshaped = params['body_pose'].reshape(-1, 3)[:21]  # First 21 joints
    axes[1, 0].imshow(body_pose_reshaped.T, aspect='auto', cmap='RdBu')
    axes[1, 0].set_title('Body Pose (First 21 Joints)')
    axes[1, 0].set_xlabel('Joint Index')
    axes[1, 0].set_ylabel('Rotation Axis (X, Y, Z)')
    
    # Translation
    axes[1, 1].bar(['X', 'Y', 'Z'], params['transl'].flatten())
    axes[1, 1].set_title('Translation')
    axes[1, 1].set_ylabel('Distance')
    axes[1, 1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    return fig


def generate_report(original_mesh_path, fitted_mesh_path, param_file=None, 
                   smpl_model_path=None, gender='MALE', output_dir=None):
    """
    Generate a comprehensive analysis report.
    
    Args:
        original_mesh_path: Path to original mesh
        fitted_mesh_path: Path to fitted SMPL mesh
        param_file: Path to SMPL parameters (optional)
        smpl_model_path: Path to SMPL models (required if param_file provided)
        gender: SMPL model gender
        output_dir: Directory to save report plots
    """
    print("Generating analysis report...")
    
    # Load meshes
    original_mesh = trimesh.load(original_mesh_path)
    fitted_mesh = trimesh.load(fitted_mesh_path)
    
    print(f"Original mesh: {len(original_mesh.vertices)} vertices, {len(original_mesh.faces)} faces")
    print(f"Fitted mesh: {len(fitted_mesh.vertices)} vertices, {len(fitted_mesh.faces)} faces")
    
    # Compute distances
    print("Computing mesh distances...")
    distance_stats = compute_mesh_distances(original_mesh, fitted_mesh)
    
    print(f"Distance statistics:")
    print(f"  Mean: {distance_stats['mean']:.4f}")
    print(f"  Median: {distance_stats['median']:.4f}")
    print(f"  Std: {distance_stats['std']:.4f}")
    print(f"  Max: {distance_stats['max']:.4f}")
    print(f"  95th percentile: {distance_stats['percentile_95']:.4f}")
    
    # Create visualizations
    base_name = os.path.splitext(os.path.basename(original_mesh_path))[0]
    
    # Mesh comparison
    fig1 = visualize_mesh_comparison(original_mesh, fitted_mesh, 
                                   f"Mesh Comparison: {base_name}")
    
    # Distance histogram
    fig2 = plot_distance_histogram(distance_stats, 
                                 f"Distance Analysis: {base_name}")
    
    figures = [fig1, fig2]
    
    # Parameter analysis if available
    if param_file and os.path.exists(param_file):
        print("Analyzing SMPL parameters...")
        fig3 = analyze_smpl_parameters(param_file)
        figures.append(fig3)
    
    # Save figures if output directory specified
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        
        fig1.savefig(os.path.join(output_dir, f"{base_name}_mesh_comparison.png"), 
                    dpi=150, bbox_inches='tight')
        fig2.savefig(os.path.join(output_dir, f"{base_name}_distance_analysis.png"), 
                    dpi=150, bbox_inches='tight')
        
        if len(figures) > 2:
            figures[2].savefig(os.path.join(output_dir, f"{base_name}_parameters.png"), 
                              dpi=150, bbox_inches='tight')
        
        print(f"Saved analysis plots to: {output_dir}")
    
    plt.show()
    
    return distance_stats


def main():
    parser = argparse.ArgumentParser(description='Analyze SMPL fitting results')
    parser.add_argument('original_mesh', type=str, help='Path to original mesh file')
    parser.add_argument('fitted_mesh', type=str, help='Path to fitted SMPL mesh file')
    parser.add_argument('--params', type=str, help='Path to SMPL parameters file (.npz)')
    parser.add_argument('--smpl_path', type=str,
                       default='/Users/nicolas/Github/nvanvlasselaer/photogrammetry/Water_photogrammetry/smpl_models',
                       help='Path to SMPL models directory')
    parser.add_argument('--gender', type=str, choices=['MALE', 'FEMALE', 'NEUTRAL'],
                       default='MALE', help='SMPL model gender')
    parser.add_argument('--output_dir', type=str, help='Directory to save analysis plots')
    
    args = parser.parse_args()
    
    # Validate input files
    if not os.path.exists(args.original_mesh):
        print(f"Error: Original mesh file '{args.original_mesh}' does not exist")
        return
    
    if not os.path.exists(args.fitted_mesh):
        print(f"Error: Fitted mesh file '{args.fitted_mesh}' does not exist")
        return
    
    # Generate report
    generate_report(
        original_mesh_path=args.original_mesh,
        fitted_mesh_path=args.fitted_mesh,
        param_file=args.params,
        smpl_model_path=args.smpl_path,
        gender=args.gender,
        output_dir=args.output_dir
    )


if __name__ == "__main__":
    main()
