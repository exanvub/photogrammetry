# Photogrammetry-bone Repository

This repository serves as a supplementary resource for the research paper titled "Reliable and Efficient Photogrammetry in Anatomical Research and Education." It contains 3D models generated using the Colmap and ObjectCapture processes, along with the data used in the statistical analysis of the research paper. Additionally, there is a Python script called "3D-model-scaling" that facilitates scaling measurements for the 3D models.

## Table of Contents

- [Introduction](#introduction)
- [Colmap](#colmap)
- [ObjectCapture](#objectcapture)
- [Data](#data)
- [3D Model Scaling Script](#3d-model-scaling-app)

## Introduction

Photogrammetry plays a crucial role in anatomical research and education, enabling the creation of accurate 3D models from 2D images. This repository accompanies the research paper "Reliable and Efficient Photogrammetry in Anatomical Research and Education," providing resources related to the photogrammetry process.

## Colmap

The `Colmap` folder contains 3D models generated using the Colmap process. Colmap is a popular photogrammetry software that allows the reconstruction of 3D structures from image sequences. Refer to the "Colmap-models/README.MD" file for a step-by-step guide on how these models were created with Colmap.

## ObjectCapture

The `ObjectCapture` folder includes 3D models generated using the ObjectCapture process. ObjectCapture is photogrammetry API by Apple inc. for fast and easy creation of 3D models. To understand the process of generating these models using ObjectCapture, please consult the "ObjectCapture-models/README.MD" file.

## Data

The `DATA` folder contains all the datasets used in the statistical analysis presented in the research paper. The data provided here is essential for reproducing the results and verifying the findings of the study.

## 3D Model Scaling Script

The repository includes a Python script named "3D-model-scaling.py." This script provides a simple graphical user interface (GUI) to calculate scaling factors for 3D models. The scaling factor is crucial for accurately measuring distances in the real world based on measurements in the 3D model space.

The "3D-model-scaling" script employs the following libraries:

- `tkinter`: Python's standard GUI library for creating the interface.
- `numpy`: Used for numerical computations.
- `pyperclip`: Enables clipboard operations for easy copying of results.

The script enables users to input model points' coordinates and their corresponding real-life distances. The average scaling factor is then calculated and displayed on the GUI.


For any questions or issues related to this repository, please feel free to contact the authors of the research paper.
