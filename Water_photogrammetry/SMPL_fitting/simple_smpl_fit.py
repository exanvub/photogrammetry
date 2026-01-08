#!/usr/bin/env python3
"""
Simple SMPL Fitting Example

A basic example of fitting a SMPL model to a photogrammetry mesh.
This script provides a simplified interface for quick fitting.
"""

import torch
import trimesh
import numpy as np
from smplx import SMPL
import os

def simple_smpl_fit(mesh_path, smpl_model_path, output_path=None, gender='MALE', iterations=300):
    """
    Simple function to fit SMPL model to a mesh.
    
    Args:
        mesh_path (str): Path to the input mesh file
        smpl_model_path (str): Path to SMPL models directory
        output_path (str): Output path for fitted mesh (optional)
        gender (str): SMPL model gender ('MALE', 'FEMALE', 'NEUTRAL')
        iterations (int): Number of optimization iterations
    
    Returns:
        dict: Fitted parameters and mesh
    """
    
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")
    
    # Load target mesh
    print(f"Loading mesh: {mesh_path}")
    mesh = trimesh.load(mesh_path)
    target_vertices = torch.tensor(mesh.vertices, dtype=torch.float32, device=device).unsqueeze(0)
    
    # Load SMPL model
    print(f"Loading SMPL {gender} model...")
    smpl = SMPL(
        model_path=smpl_model_path,
        gender=gender,
        create_global_orient=True,
        create_body_pose=True,
        create_betas=True
    ).to(device)
    
    # Initialize parameters
    betas = torch.zeros((1, 10), device=device, requires_grad=True)
    global_orient = torch.zeros((1, 3), device=device, requires_grad=True)
    body_pose = torch.zeros((1, 69), device=device, requires_grad=True)
    transl = torch.zeros((1, 3), device=device, requires_grad=True)
    
    # Setup optimizer
    optimizer = torch.optim.Adam([betas, global_orient, body_pose, transl], lr=0.01)
    
    print("Starting optimization...")
    
    for i in range(iterations):
        optimizer.zero_grad()
        
        # Forward pass
        output = smpl(
            betas=betas,
            global_orient=global_orient,
            body_pose=body_pose,
            transl=transl
        )
        
        # Simple chamfer distance loss
        smpl_verts = output.vertices
        
        # Compute distances (simplified version)
        # For each SMPL vertex, find closest target vertex
        smpl_expanded = smpl_verts.unsqueeze(2)  # [1, N_smpl, 1, 3]
        target_expanded = target_vertices.unsqueeze(1)  # [1, 1, N_target, 3]
        dists = torch.sum((smpl_expanded - target_expanded) ** 2, dim=-1)  # [1, N_smpl, N_target]
        
        # Chamfer distance components
        smpl_to_target = torch.min(dists, dim=2)[0].mean()  # Mean min distance from SMPL to target
        target_to_smpl = torch.min(dists, dim=1)[0].mean()  # Mean min distance from target to SMPL
        
        chamfer_loss = (smpl_to_target + target_to_smpl) / 2
        
        # Regularization
        reg_loss = 1e-4 * (betas ** 2).sum() + 1e-5 * (body_pose ** 2).sum()
        
        total_loss = chamfer_loss + reg_loss
        
        # Backward pass
        total_loss.backward()
        optimizer.step()
        
        if i % 50 == 0:
            print(f"Iteration {i:3d}: Loss = {total_loss.item():.6f}, Chamfer = {chamfer_loss.item():.6f}")
    
    # Create fitted mesh
    with torch.no_grad():
        final_output = smpl(
            betas=betas,
            global_orient=global_orient,
            body_pose=body_pose,
            transl=transl
        )
        
        fitted_mesh = trimesh.Trimesh(
            vertices=final_output.vertices[0].cpu().numpy(),
            faces=smpl.faces
        )
    
    # Save result
    if output_path is None:
        base_name = os.path.splitext(mesh_path)[0]
        output_path = f"{base_name}_smpl_fitted.obj"
    
    fitted_mesh.export(output_path)
    print(f"Saved fitted mesh to: {output_path}")
    
    return {
        'betas': betas.detach().cpu().numpy(),
        'global_orient': global_orient.detach().cpu().numpy(),
        'body_pose': body_pose.detach().cpu().numpy(),
        'transl': transl.detach().cpu().numpy(),
        'fitted_mesh': fitted_mesh,
        'loss': total_loss.item()
    }


def example_usage():
    """Example of how to use the simple fitting function."""
    
    # Paths (adjust these to your setup)
    mesh_path = "/Users/nicolas/Github/nvanvlasselaer/photogrammetry/Water_photogrammetry/Aldo.obj"
    smpl_model_path = "/Users/nicolas/Github/nvanvlasselaer/photogrammetry/Water_photogrammetry/smpl_models"
    
    # Check if files exist
    if not os.path.exists(mesh_path):
        print(f"Error: Mesh file {mesh_path} not found!")
        return
    
    if not os.path.exists(smpl_model_path):
        print(f"Error: SMPL model path {smpl_model_path} not found!")
        return
    
    # Fit SMPL model
    results = simple_smpl_fit(
        mesh_path=mesh_path,
        smpl_model_path=smpl_model_path,
        gender='MALE',
        iterations=300
    )
    
    print("Fitting completed!")
    print(f"Final loss: {results['loss']:.6f}")
    print(f"Shape parameters (betas): {results['betas'].flatten()[:5]}...")  # Show first 5 betas
    

if __name__ == "__main__":
    example_usage()
