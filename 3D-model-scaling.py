import tkinter as tk
import numpy as np
import pyperclip  # Import pyperclip library for clipboard operations


def calculate_distance(p1, p2):
    return np.sqrt(sum((p1[i] - p2[i]) ** 2 for i in range(3)))


def calculate_scaling_factor(model_distances, real_life_distances):
    scaling_factors = [real_dist / model_dist for model_dist, real_dist in zip(model_distances, real_life_distances)]
    average_scaling_factor = np.mean(scaling_factors)
    return average_scaling_factor


def calculate_and_show_scaling_factor():
    model_points = []
    real_life_distances = []
    error_message = ""

    # Get the user input from the Entry widgets
    for i in range(len(model_entries)):
        try:
            x1, y1, z1, x2, y2, z2 = model_entries[i].get().split(',')
            model_points.append([(float(x1), float(y1), float(z1)), (float(x2), float(y2), float(z2))])

            real_life_distances.append(float(real_entries[i].get()))
        except ValueError:
            # Handle invalid input (not enough coordinates)
            error_message = "Please enter two sets of (x, y, z) coordinates for each model points set."
            break

    if not error_message:
        # Calculate model distances
        model_distances = [calculate_distance(p1, p2) for p1, p2 in model_points]

        if len(model_distances) == 0:
            error_message = "Please enter at least one set of model points."
        else:
            # Calculate average scaling factor
            scaling_factor = calculate_scaling_factor(model_distances, real_life_distances)

            # Update the scaling factor label
            scaling_factor_label.config(text=f"Average Scaling Factor: {scaling_factor:.4f}")

            # Clear the error message
            clear_error_message()
            return

    # Display error message if there was an issue with the input
    error_label.config(text=error_message)


def add_entry_fields():
    wrapper_frame = tk.Frame(root)
    wrapper_frame.grid(row=len(model_entries) + 1, column=0, columnspan=11)
    wrapper_entries.append(wrapper_frame)

    model_label = tk.Label(wrapper_frame, text="Model Points: x1, y1, z1, x2, y2, z2:")
    model_label.grid(row=0, column=0)

    model_entry = tk.Entry(wrapper_frame, width=50)
    model_entry.grid(row=0, column=1, columnspan=8)
    model_entries.append(model_entry)

    real_label = tk.Label(wrapper_frame, text="Real-Life Distance: mm:")
    real_label.grid(row=0, column=9)

    real_entry = tk.Entry(wrapper_frame)
    real_entry.grid(row=0, column=10)
    real_entries.append(real_entry)


def remove_last_set():
    if len(model_entries) > 0:
        model_entries[-1].destroy()
        model_entries.pop()

    if len(real_entries) > 0:
        real_entries[-1].destroy()
        real_entries.pop()

    if len(wrapper_entries) > 0:
        wrapper_entries[-1].destroy()
        wrapper_entries.pop()


def copy_to_clipboard():
    scaling_factor = scaling_factor_label.cget("text")
    scaling_factor = scaling_factor.split(": ")[1]
    pyperclip.copy(scaling_factor)
    success_label.config(text="Average Scaling Factor copied to clipboard!")


def clear_error_message():
    error_label.config(text="")


root = tk.Tk()
root.title("3D Model Scaling")
root.geometry("1200x300")  # Set window size (width x height)

model_entries = []
real_entries = []
wrapper_entries = []

add_button = tk.Button(root, text="Add Set", command=add_entry_fields)
add_button.grid(row=0, column=0, columnspan=2)

remove_button = tk.Button(root, text="Remove Set", command=remove_last_set)
remove_button.grid(row=0, column=1, columnspan=2)

calculate_button = tk.Button(root, text="Calculate Scaling Factor", command=calculate_and_show_scaling_factor)
calculate_button.grid(row=len(model_entries) + 5, column=0, columnspan=11)  # Adjust position here

add_entry_fields()

scaling_factor_label = tk.Label(root, text="Average Scaling Factor: ")
scaling_factor_label.grid(row=len(model_entries) + 6, column=0, columnspan=11)  # Adjust column span here

error_label = tk.Label(root, text="", fg="red")
error_label.grid(row=len(model_entries) + 3, column=0, columnspan=11)  # Adjust column span here

copy_button = tk.Button(root, text="Copy to Clipboard", command=copy_to_clipboard)
copy_button.grid(row=len(model_entries) + 7, column=0, columnspan=11)  # Adjust position here

success_label = tk.Label(root, text="", fg="green")
success_label.grid(row=len(model_entries) + 8, column=0, columnspan=11)  # Adjust column span here

root.mainloop()
