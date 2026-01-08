#!/usr/bin/env python3
"""
Enhanced SMPL Model Fitting to Photogrammetry Mesh

This script fits a SMPL (Skinned Multi-Person Linear) model to a photogrammetry mesh
of a human subject. It includes advanced optimization strategies, preprocessing options,
and robust fitting capabilities.

Requirements:
    - torch
    - trimesh
    - numpy
    - smplx
    - scipy
    - argparse
"""

import torch
import trimesh
import numpy as np
import argparse
import os
from pathlib import Path
from smplx import SMPL
from scipy.spatial.distance import cdist
from scipy.optimize import minimize
import time

class SMPLMeshFitter:
    def __init__(self, smpl_model_path, gender='MALE', device='auto'):
        """
        Initialize the SMPL mesh fitter.
        
        Args:
            smpl_model_path (str): Path to SMPL models directory
            gender (str): Gender of the model ('MALE', 'FEMALE', 'NEUTRAL')
            device (str): Device to use ('auto', 'cuda', 'cpu')
        """
        if device == 'auto':
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        else:
            self.device = torch.device(device)
        
        print(f"Using device: {self.device}")
        
        # Load SMPL model
        self.smpl = SMPL(
            model_path=smpl_model_path,
            gender=gender,
            create_global_orient=True,
            create_body_pose=True,
            create_betas=True
        ).to(self.device)
        
        print(f"Loaded SMPL {gender} model")
        
    def chamfer_distance(self, x, y, reduction='mean'):
        """
        Compute chamfer distance between two point sets.
        
        Args:
            x: [B, N, 3] predicted points
            y: [B, M, 3] target points
            reduction: 'mean' or 'sum'
        
        Returns:
            chamfer distance
        """
        # Compute pairwise distances
        x_expanded = x.unsqueeze(2)  # [B, N, 1, 3]
        y_expanded = y.unsqueeze(1)  # [B, 1, M, 3]
        
        # Squared euclidean distance
        dists = torch.sum((x_expanded - y_expanded) ** 2, dim=-1)  # [B, N, M]
        
        # Chamfer distance: min distance from x to y + min distance from y to x
        chamfer_x_to_y = torch.min(dists, dim=2)[0]  # [B, N]
        chamfer_y_to_x = torch.min(dists, dim=1)[0]  # [B, M]
        
        if reduction == 'mean':
            chamfer_x_to_y = chamfer_x_to_y.mean(dim=1)  # [B]
            chamfer_y_to_x = chamfer_y_to_x.mean(dim=1)  # [B]
        else:
            chamfer_x_to_y = chamfer_x_to_y.sum(dim=1)  # [B]
            chamfer_y_to_x = chamfer_y_to_x.sum(dim=1)  # [B]
        
        chamfer_dist = (chamfer_x_to_y + chamfer_y_to_x) / 2
        
        return chamfer_dist.mean()
    
    def preprocess_mesh(self, mesh, target_vertices=None, remove_outliers=True):
        """
        Preprocess the input mesh.
        
        Args:
            mesh: Input trimesh object
            target_vertices: Target number of vertices for downsampling
            remove_outliers: Whether to remove outlier vertices
            
        Returns:
            Preprocessed mesh vertices as torch tensor
        """
        vertices = mesh.vertices.copy()
        
        # Remove outliers if requested
        if remove_outliers:
            # Remove vertices that are too far from the center
            center = np.mean(vertices, axis=0)
            distances = np.linalg.norm(vertices - center, axis=1)
            threshold = np.percentile(distances, 95)  # Keep 95% of vertices
            mask = distances <= threshold
            vertices = vertices[mask]
            print(f"Removed {np.sum(~mask)} outlier vertices")
        
        # Downsample if requested
        if target_vertices and len(vertices) > target_vertices:
            indices = np.random.choice(len(vertices), target_vertices, replace=False)
            vertices = vertices[indices]
            print(f"Downsampled to {target_vertices} vertices")
        
        # Normalize to unit scale (optional - comment out if you want to preserve scale)
        # vertices = vertices - np.mean(vertices, axis=0)
        # scale = np.max(np.linalg.norm(vertices, axis=1))
        # vertices = vertices / scale
        
        return torch.tensor(vertices, dtype=torch.float32, device=self.device).unsqueeze(0)
    
    def fit_mesh(self, target_mesh_path, output_path=None, 
                 num_iterations=500, learning_rate=0.01,
                 lambda_shape=1e-4, lambda_pose=1e-5, lambda_transl=1e-3,
                 use_face_loss=False, verbose=True):
        """
        Fit SMPL model to target mesh.
        
        Args:
            target_mesh_path (str): Path to target mesh file
            output_path (str): Path to save fitted mesh
            num_iterations (int): Number of optimization iterations
            learning_rate (float): Learning rate for optimization
            lambda_shape (float): Regularization weight for shape parameters
            lambda_pose (float): Regularization weight for pose parameters
            lambda_transl (float): Regularization weight for translation
            use_face_loss (bool): Whether to use face-specific loss (experimental)
            verbose (bool): Whether to print progress
            
        Returns:
            Fitted SMPL parameters dictionary
        """
        print(f"Loading target mesh: {target_mesh_path}")
        
        # Load and preprocess target mesh
        target_mesh = trimesh.load(target_mesh_path)
        target_vertices = self.preprocess_mesh(target_mesh, target_vertices=10000)
        
        print(f"Target mesh has {target_vertices.shape[1]} vertices")
        
        # Initialize SMPL parameters
        batch_size = 1
        betas = torch.zeros((batch_size, 10), device=self.device, requires_grad=True)
        global_orient = torch.zeros((batch_size, 3), device=self.device, requires_grad=True)
        body_pose = torch.zeros((batch_size, 69), device=self.device, requires_grad=True)
        transl = torch.zeros((batch_size, 3), device=self.device, requires_grad=True)
        
        # Setup optimizer
        optimizer = torch.optim.Adam([
            {'params': [betas], 'lr': learning_rate},
            {'params': [global_orient], 'lr': learning_rate * 0.1},
            {'params': [body_pose], 'lr': learning_rate * 0.1},
            {'params': [transl], 'lr': learning_rate}
        ])
        
        # Learning rate scheduler
        scheduler = torch.optim.lr_scheduler.StepLR(optimizer, step_size=100, gamma=0.8)
        
        best_loss = float('inf')
        best_params = None
        
        print("Starting optimization...")
        start_time = time.time()
        
        for iteration in range(num_iterations):
            optimizer.zero_grad()
            
            # Forward pass through SMPL
            smpl_output = self.smpl(
                betas=betas,
                global_orient=global_orient,
                body_pose=body_pose,
                transl=transl
            )
            
            # Get SMPL vertices
            smpl_vertices = smpl_output.vertices
            
            # Compute chamfer distance loss
            chamfer_loss = self.chamfer_distance(smpl_vertices, target_vertices)
            
            # Regularization losses
            shape_reg = lambda_shape * (betas ** 2).sum()
            pose_reg = lambda_pose * (body_pose ** 2).sum()
            transl_reg = lambda_transl * (transl ** 2).sum()
            
            # Total loss
            total_loss = chamfer_loss + shape_reg + pose_reg + transl_reg
            
            # Backward pass
            total_loss.backward()
            optimizer.step()
            scheduler.step()
            
            # Track best parameters
            if total_loss.item() < best_loss:
                best_loss = total_loss.item()
                best_params = {
                    'betas': betas.clone().detach(),
                    'global_orient': global_orient.clone().detach(),
                    'body_pose': body_pose.clone().detach(),
                    'transl': transl.clone().detach()
                }
            
            # Print progress
            if verbose and (iteration % 50 == 0 or iteration == num_iterations - 1):
                elapsed_time = time.time() - start_time
                print(f"Iter {iteration:4d} | "
                      f"Total: {total_loss.item():.6f} | "
                      f"Chamfer: {chamfer_loss.item():.6f} | "
                      f"Shape: {shape_reg.item():.6f} | "
                      f"Pose: {pose_reg.item():.6f} | "
                      f"Time: {elapsed_time:.1f}s")
        
        print(f"Optimization completed in {time.time() - start_time:.1f} seconds")
        
        # Generate final mesh with best parameters
        with torch.no_grad():
            final_output = self.smpl(
                betas=best_params['betas'],
                global_orient=best_params['global_orient'],
                body_pose=best_params['body_pose'],
                transl=best_params['transl']
            )
            
            fitted_mesh = trimesh.Trimesh(
                vertices=final_output.vertices[0].cpu().numpy(),
                faces=self.smpl.faces
            )
        
        # Save fitted mesh
        if output_path is None:
            output_path = target_mesh_path.replace('.obj', '_smpl_fitted.obj')
            output_path = output_path.replace('.ply', '_smpl_fitted.obj')
        
        fitted_mesh.export(output_path)
        print(f"Saved fitted mesh to: {output_path}")
        
        # Return parameters for further use
        return {
            'betas': best_params['betas'].cpu().numpy(),
            'global_orient': best_params['global_orient'].cpu().numpy(),
            'body_pose': best_params['body_pose'].cpu().numpy(),
            'transl': best_params['transl'].cpu().numpy(),
            'fitted_mesh': fitted_mesh,
            'final_loss': best_loss
        }
    
    def save_parameters(self, params, filepath):
        """Save SMPL parameters to file."""
        np.savez(filepath, **{k: v for k, v in params.items() if k != 'fitted_mesh'})
        print(f"Saved parameters to: {filepath}")
    
    def load_parameters(self, filepath):
        """Load SMPL parameters from file."""
        return dict(np.load(filepath))


def main():
    parser = argparse.ArgumentParser(description='Fit SMPL model to photogrammetry mesh')
    parser.add_argument('input_mesh', type=str, help='Path to input mesh file (.obj or .ply)')
    parser.add_argument('--smpl_path', type=str, 
                       default='/Users/nicolas/Github/nvanvlasselaer/photogrammetry/Water_photogrammetry/SMPL_fitting/smpl_models',
                       help='Path to SMPL models directory')
    parser.add_argument('--gender', type=str, choices=['MALE', 'FEMALE', 'NEUTRAL'], 
                       default='MALE', help='SMPL model gender')
    parser.add_argument('--output', type=str, help='Output path for fitted mesh')
    parser.add_argument('--iterations', type=int, default=500, help='Number of optimization iterations')
    parser.add_argument('--lr', type=float, default=0.01, help='Learning rate')
    parser.add_argument('--lambda_shape', type=float, default=1e-4, help='Shape regularization weight')
    parser.add_argument('--lambda_pose', type=float, default=1e-5, help='Pose regularization weight')
    parser.add_argument('--device', type=str, choices=['auto', 'cuda', 'cpu'], 
                       default='auto', help='Device to use for computation')
    parser.add_argument('--save_params', action='store_true', help='Save SMPL parameters to file')
    
    args = parser.parse_args()
    
    # Validate input file
    if not os.path.exists(args.input_mesh):
        print(f"Error: Input mesh file '{args.input_mesh}' does not exist")
        return
    
    # Initialize fitter
    fitter = SMPLMeshFitter(
        smpl_model_path=args.smpl_path,
        gender=args.gender,
        device=args.device
    )
    
    # Fit mesh
    results = fitter.fit_mesh(
        target_mesh_path=args.input_mesh,
        output_path=args.output,
        num_iterations=args.iterations,
        learning_rate=args.lr,
        lambda_shape=args.lambda_shape,
        lambda_pose=args.lambda_pose
    )
    
    # Save parameters if requested
    if args.save_params:
        param_path = args.input_mesh.replace('.obj', '_smpl_params.npz')
        param_path = param_path.replace('.ply', '_smpl_params.npz')
        fitter.save_parameters(results, param_path)
    
    print("SMPL fitting completed successfully!")
    print(f"Final loss: {results['final_loss']:.6f}")


if __name__ == "__main__":
    main()
