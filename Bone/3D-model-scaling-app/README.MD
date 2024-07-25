# 3D Model Scaling Script

This Python script allows you to scale a 3D model to real-life dimensions using distinctive anatomical reference points. It takes 3D coordinates from anatomical landmarks obtained in 3D Slicer, as well as real-life distances measured in millimeters using a digital caliper. The script calculates the average scaling factor and provides the result for scaling the entire 3D model.

## Prerequisites

Before using the script, ensure you have the following:

- Python 3.x installed on your system.
- Required libraries: `tkinter`, `numpy`, and `pyperclip`.

## Usage

1. **Run the Script**: Open a terminal or command prompt and navigate to the directory containing the `3D-model-scaling.py` script. Run the script using the command:

   ```bash
   python 3D-model-scaling.py
   ```

2. **GUI Interface**: A graphical user interface (GUI) window will open.

3. **Adding Sets of Points and Distances**:
   - Click the "Add Set" button to add a new set of points and distances.
   - Enter the 3D coordinates for the anatomical reference points in the format: `x1, y1, z1, x2, y2, z2`.
   - Enter the real-life distance between these points in millimeters in the corresponding entry.

4. **Calculating Scaling Factor**:
   - Once you have added all the required point sets, click the "Calculate Scaling Factor" button.
   - The average scaling factor will be displayed on the GUI.

5. **Copying Scaling Factor**:
   - Click the "Copy to Clipboard" button to copy the average scaling factor to your clipboard.
   - You can then use this scaling factor to adjust the dimensions of your 3D model.

## Example

Here's an example of how to use the script:

1. Click the "Add Set" button.
2. Enter the coordinates and real-life distance for the left and right transverse processes.
3. Click the "Add Set" button again.
4. Enter the coordinates and real-life distance for a distinctive point anterior on the corpus.
5. Click the "Add Set" button once more.
6. Enter the coordinates and real-life distance for the most posterior point on the spinal process.
7. Click the "Calculate Scaling Factor" button.
8. The average scaling factor will be displayed.
9. Click the "Copy to Clipboard" button to copy the scaling factor to your clipboard.
10. Use the scaling factor to adjust the dimensions of your 3D model, for example in Meshlab.

## Note

- Make sure to enter valid (x, y, z) coordinates and real-life distances in millimeters (with two decimal points).
- The script calculates the average scaling factor based on the entered point sets.

## Disclaimer

This script is provided for educational purposes and may require further validation for specific use cases. Always double-check your results and ensure accuracy when scaling 3D models for critical applications.