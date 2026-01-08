import json
import numpy as np

# Load the Meshroom / COLMAP cameras.sfm JSON
with open('/Volumes/Research/Photogrammetry/Water/cameras.sfm') as f:
    data = json.load(f)

# Build lookup dictionaries
pose_map = {p['poseId']: p['pose']['transform'] for p in data['poses']}
intr_map = {i['intrinsicId']: i for i in data['intrinsics']}

# List to store all views
camera_list = []

for v in data['views']:
    pose_id = v['poseId']
    intr_id = v['intrinsicId']

    # --- Pose (extrinsics) ---
    tr = pose_map[pose_id]
    R = np.array(tr['rotation'], dtype=float).reshape(3, 3)
    C = np.array(tr['center'], dtype=float)
    t = -R @ C
    extrinsic = np.eye(4)
    extrinsic[:3, :3] = R
    extrinsic[:3, 3] = t

    # --- Intrinsics ---
    intr = intr_map[intr_id]
    # handle possible keys
    if 'pxFocalLength' in intr:
        fx = fy = float(intr['pxFocalLength'])
    elif 'focalLength' in intr:
        fx = fy = float(intr['focalLength'])
    else:
        raise KeyError(f"No focal length found for intrinsic {intr_id}")

    cx, cy = map(float, intr['principalPoint'])
    K = np.array([[fx, 0, cx],
                  [0, fy, cy],
                  [0, 0, 1]])

    # Add this view to the list
    camera_list.append({
        "view": v['path'],
        "K": K.tolist(),
        "extrinsic": extrinsic.tolist()
    })

# Write all views to a single JSON file
with open('camera_parameters.json', 'w') as f:
    json.dump(camera_list, f, indent=2)

print(f"Saved {len(camera_list)} camera parameters to camera_parameters.json")


