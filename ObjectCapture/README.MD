# Apple's Object Capture API Command Line App Tutorial

This guide explains how to install and use Apple's Object Capture API as a command line app for creating photogrammetric models. The Object Capture API enables the creation of high-quality 3D models from a sequence of 2D images. These models can be saved in the USDZ format, which is optimized for use in augmented reality (AR) applications.

## Prerequisites

Before you begin, ensure you have the following:

1. macOS Monterey 12.0 beta or later.
2. Xcode 13 or later installed.
3. A compatible Apple device, preferably an M1 Pro / M1 or later (these are much faster than Intel-based Macs).
4. A camera or smartphone to capture images of the object you want to model. Set the aperture high enough to ensure the entire image is sharp.
5. A model with minimal reflective surfaces (consider using cross-polarization filters).
6. Place your model on a dark, neutral background without textures for optimal results.

## Installation Steps

1. **Download and Extract the Xcode Project:**
   
   Download the Xcode project from the following link: [Apple's Object Capture Photogrammetry Example](https://developer.apple.com/documentation/realitykit/creating_a_photogrammetry_command-line_app). Unzip the downloaded file.

2. **Open the Xcode Project:**

   - Launch Xcode.
   - Open the `HelloPhotogrammetry.xcodeproj` file you extracted earlier.
   - If you encounter any errors on launch, try the following:
     - Go to the "Product" menu in the top menu bar.
     - Select "Clean build folder..."
   
3. **Configure Project Settings:**

   - In the project navigator, select the target `HelloPhotogrammetry`.
   - In the "General" tab, choose your desired "Deployment Target."
   - In the "Signing & Capabilities" tab, select the "Signing Certificate: Sign to Run Locally."

4. **Build and Export the Executable:**

   - In the menu bar, navigate to "Product" and choose "Archive."
   - In the popup window, click on "Distribute Content."
   - Select "Built Products" and click "Next."
   - Choose the directory where you want the executable to be exported.
   - Click "Export."

5. **Run the Photogrammetry App:**

   - Navigate to the folder where you exported the executable.
   - Open a terminal window in that directory.
   - To run the app, either:
     - Double-click the executable file, or
     - Drag and drop the executable into the terminal window.
   
## Using the App

To create a 3D model using the Object Capture API command line app, follow these steps:

1. Open a terminal window.

2. Use the following command format:

   ```bash
   ./HelloPhotogrammetry <input-folder> <output-filename> [--detail <detail>] [--sample-ordering <sample-ordering>] [--feature-sensitivity <feature-sensitivity>]
   ```

   - `<input-folder>`: The local input file folder containing images of the object.
   - `<output-filename>`: Full path to the desired USDZ output file.
   - `--detail <detail>`: Set the detail level of the output model (preview, reduced, medium, full, raw). Default: none.
   - `--sample-ordering <sample-ordering>`: Set sample ordering (unordered, sequential) to potentially speed up computation. Default: unordered.
   - `--feature-sensitivity <feature-sensitivity>`: Set feature sensitivity (normal, high) based on object characteristics. Default: normal.

3. Example usage:

   ```bash
   ./HelloPhotogrammetry /Users/username/Desktop/Images /Users/username/Desktop/OutputModel -d raw
   ```

4. Press Enter to execute the command.

5. Wait for the process to complete. The process might take some time and could appear frozen. You can check the Activity Monitor to see the photogrammetry app's resource usage.

6. The app doesn't provide a completion message. When you see a new prompt line, the process has likely finished. You can find the generated model in the output folder you specified.

## Conclusion

You've successfully installed and used the Apple Object Capture API command line app to create high-quality 3D models from a sequence of images. These models can be used in various AR applications to enhance user experiences. Experiment with different settings and capture techniques to achieve the best results for your specific use case.

## Note

If the Commandline app is to complicated to use, you can also try a free app from the Apple App store called: PhotoCatch.
This app uses the same API in a more userfriendly GUI and looks easy to instal and use.  
Disclaimer: The PhotoCatch app is not developed by us and all credits and responsibilities for this app go to 'eos innovations llc'