import tkinter as tk
from tkinter import messagebox
import numpy as np


def calculate_distance(p1, p2):
    return np.sqrt(sum((p1[i] - p2[i]) ** 2 for i in range(3)))


def calculate_scaling_factor(model_distances, real_life_distances):
    scaling_factors = [real_dist / model_dist for model_dist, real_dist in zip(model_distances, real_life_distances)]
    average_scaling_factor = np.mean(scaling_factors)
    return average_scaling_factor


def calculate_and_show_scaling_factor():
    model_points = []
    real_life_distances = []

    # Get the user input from the Entry widgets
    for i in range(len(model_entries)):
        try:
            x1, y1, z1, x2, y2, z2 = model_entries[i].get().split(',')
            model_points.append([(float(x1), float(y1), float(z1)), (float(x2), float(y2), float(z2))])

            real_life_distances.append(float(real_entries[i].get()))
        except ValueError:
            # Handle invalid input (not enough coordinates)
            messagebox.showerror("Input Error",
                                 "Please enter two sets of (x, y, z) coordinates for each model points set.")
            return

    # Calculate model distances
    model_distances = [calculate_distance(p1, p2) for p1, p2 in model_points]

    # Calculate average scaling factor
    scaling_factor = calculate_scaling_factor(model_distances, real_life_distances)

    # Update the scaling factor label
    scaling_factor_label.config(text=f"Average Scaling Factor: {scaling_factor:.4f}")


# Create the main window
root = tk.Tk()
root.title("3D Model Scaling")

# Lists to store Entry widgets for model points and real-life distances
model_entries = []
real_entries = []


# Function to add new set of model points and real-life distance entries
def add_entry_fields():
    model_label = tk.Label(root, text="Model Points: x1, y1, z1, x2, y2, z2:")
    model_label.grid(row=len(model_entries) + 1, column=0)

    model_entry = tk.Entry(root)
    model_entry.grid(row=len(model_entries) + 1, column=1)
    model_entries.append(model_entry)

    real_label = tk.Label(root, text="Real-Life Distance: mm:")
    real_label.grid(row=len(real_entries) + 1, column=2)

    real_entry = tk.Entry(root)
    real_entry.grid(row=len(real_entries) + 1, column=3)
    real_entries.append(real_entry)


# Button to add more model points and real-life distance entries
add_button = tk.Button(root, text="Add Set", command=add_entry_fields)
add_button.grid(row=0, column=0, columnspan=2)

# Button to calculate the scaling factor
calculate_button = tk.Button(root, text="Calculate Scaling Factor", command=calculate_and_show_scaling_factor)
calculate_button.grid(row=0, column=2, columnspan=2)

# Add initial entry fields
add_entry_fields()

# Label to display the scaling factor
scaling_factor_label = tk.Label(root, text="Average Scaling Factor: ")
scaling_factor_label.grid(row=len(model_entries) + 2, column=0, columnspan=4)

# Start the Tkinter event loop
root.mainloop()
