import torch, trimesh, numpy as np
from smplx import SMPL

def chamfer_distance(x, y):
    """
    Simple chamfer distance implementation to replace pytorch3d dependency
    x: [B, N, 3] predicted points
    y: [B, M, 3] target points
    """
    # Compute pairwise distances
    x_expanded = x.unsqueeze(2)  # [B, N, 1, 3]
    y_expanded = y.unsqueeze(1)  # [B, 1, M, 3]
    
    # Squared euclidean distance
    dists = torch.sum((x_expanded - y_expanded) ** 2, dim=-1)  # [B, N, M]
    
    # Chamfer distance: min distance from x to y + min distance from y to x
    chamfer_x_to_y = torch.min(dists, dim=2)[0].mean(dim=1)  # [B]
    chamfer_y_to_x = torch.min(dists, dim=1)[0].mean(dim=1)  # [B]
    
    chamfer_dist = (chamfer_x_to_y + chamfer_y_to_x) / 2
    
    return chamfer_dist.mean(), None  # Return mean and None to match pytorch3d interface

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# --- Load torso scan ---
scan = trimesh.load("/Users/nicolas/Github/nvanvlasselaer/photogrammetry/Water_photogrammetry/Aldo.obj")
scan_pts = torch.tensor(scan.vertices, dtype=torch.float32, device=device).unsqueeze(0)

# --- Load SMPL male ---
smpl = SMPL(model_path="/Users/nicolas/Github/nvanvlasselaer/photogrammetry/Water_photogrammetry/smpl_models",
            gender="MALE",
            create_global_orient=True,
            create_body_pose=True,
            create_betas=True).to(device)

# --- Use full mesh ---
# No need for torso-specific vertex filtering - we'll use all vertices

# --- Parameters to optimise ---
betas = torch.zeros((1,10), device=device, requires_grad=True)
global_orient = torch.zeros((1,3), device=device, requires_grad=True)
body_pose = torch.zeros((1,69), device=device, requires_grad=True)
transl = torch.zeros((1,3), device=device, requires_grad=True)
optim = torch.optim.Adam([betas, global_orient, body_pose, transl], lr=0.01)

for it in range(400):
    optim.zero_grad()
    out = smpl(betas=betas, global_orient=global_orient,
               body_pose=body_pose, transl=transl)
    # Use all vertices for full mesh fitting
    full_verts = out.vertices
    loss, _ = chamfer_distance(full_verts, scan_pts)
    loss += 1e-4*(betas**2).sum() + 1e-5*(body_pose**2).sum()
    loss.backward()
    optim.step()
    if it % 50 == 0:
        print(f"Iter {it}, loss {loss.item():.6f}")

# --- Save result ---
full_mesh_fitted = trimesh.Trimesh(vertices=out.vertices[0].detach().cpu().numpy(),
                                   faces=smpl.faces)
full_mesh_fitted.export("smpl_full_mesh_fit.obj")
print("Saved smpl_full_mesh_fit.obj")
