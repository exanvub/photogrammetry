# Photogrammetry using Colmap

This repository contains instructions for creating 3D models from photographs using Colmap, a powerful open-source software for photogrammetry. The process involves multiple steps, from feature extraction to dense reconstruction, and finally, the generation of a 3D point cloud that can be visualized in Meshlab.

## Getting Started

Follow these step-by-step instructions to set up the environment and create your 3D model:

### Prerequisites

- Colmap: Install Colmap on your system by following the instructions on the official Colmap website: [Colmap](https://colmap.github.io/). Make sure it is properly installed and accessible in your terminal or command prompt.

- Meshlab: Download and install Meshlab from the official website: [Meshlab](https://www.meshlab.net/). Meshlab will be used for visualizing the final 3D point cloud.

### Step 1: Setting up the project

1. Open the Colmap GUI

   ```bash
   colmap gui
   ```

2. Create new project

   - Click on "File" in the top menu and choose "New Project".
   - Select a folder for your new database and choose the folder containing your images.
   - Click "OK" to create the project and open it in the Colmap GUI.

### Step 2: Feature extraction and matching

1. In the Colmap GUI, go to the "Processing" tab.
2. Click on "Feature Extraction" to extract features from the images.
3. Next, click on "Feature Matching" to match features across images.

### Step 3: Reconstruction

1. In the Colmap GUI, go to the "Reconstruction" tab.
2. Click on "Start Reconstruction" to perform the structure from motion (SfM) reconstruction.

   - If the reconstruction is not satisfactory and some cameras are out of position, adjust the reconstruction options:
     - Go to "Reconstruction Options".
     - Increase the value of "min_num_matches" to enforce stricter matching constraints.
     - Rerun the reconstruction if necessary.

3. If the reconstruction is successful, proceed to the dense reconstruction.

### Step 4: Dense reconstruction

1. In the Colmap GUI, go to the "Dense Reconstruction" tab.
2. Choose a Workspace by creating a new folder named 'dense' inside your current working directory.
3. Perform the following steps in sequence:
   - Undistortion
   - Stereo
   - Fusion

4. Once the dense reconstruction is complete, you will have a dense point cloud file (`.ply`) inside the 'dense' folder.

### Step 5: Mesh reconstruction in Meshlab

1. Open Meshlab from your system and import your model.
2. Preclean: Use various tools avalable in Meshlab to remove unwanted vertices.
3. Go to the "Filters" menu and choose "Remeshing, Simplification, and Reconstruction".
4. In the sub-menu, select "Surface Reconstruction: Screened Poisson".
5. Adjust the reconstruction depth for higher detail by setting the value (default 8) to a higher range (usually 10-12 provides more detail).
6. Click "Apply" to start the mesh reconstruction process.

Congratulations! You now have a detailed 3D model that you can explore and visualize in Meshlab.

7. You can use other filters in Meshlab to postclean your model

## Acknowledgments

This project was made possible with the help of Colmap and Meshlab. Their respective websites contain valuable resources and documentation that contributed to the success of this photogrammetry workflow.

- Colmap: [https://colmap.github.io/](https://colmap.github.io/)
- Meshlab: [https://www.meshlab.net/](https://www.meshlab.net/)

Most of the time the default settings work fine, but feel free to experiment with different settings and improve your 3D models.

Happy photogrammetry and 3D modeling!