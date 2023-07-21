import re
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

# Read the data from histo.txt
with open("DATA/histo2.txt", "r") as file:
    data = file.read()

# Extract the intervals and counts using regular expressions
pattern = r"\[(.+?)\) : (\d+)"
matches = re.findall(pattern, data)

intervals = []
counts = []

for match in matches:
    interval_str, count = match
    interval = tuple(map(float, interval_str.split("..")))
    intervals.append(interval)
    counts.append(int(count))

# Create a list of labels for the histogram bars
labels = [f"{interval[0]:.6f} to {interval[1]:.6f}" for interval in intervals]

# Calculate the maximum absolute interval value
max_abs_interval = max(max(abs(interval[0]), abs(interval[1])) for interval in intervals)

# Define a custom colormap from blue to white to red
colors = ["blue", "white", "red"]
cmap = mcolors.LinearSegmentedColormap.from_list("CustomMap", colors, N=256)

# Create the histogram plot
plt.figure(figsize=(12, 6))
bars = plt.bar(labels, counts, width=1, linewidth=0.5)  # Set the width and linewidth for the bars

for bar, interval in zip(bars, intervals):
    # Map the interval value to the range [0, 1] based on max_abs_interval
    norm_val = (interval[1] + max_abs_interval) / (2 * max_abs_interval)
    color = cmap(norm_val)
    bar.set_color(color)
    bar.set_edgecolor('black')  # Set the edge color to black for each bar

plt.xlabel("Intervals")
plt.ylabel("Counts")
plt.title("Histogram")
plt.xticks(rotation=90)
plt.tight_layout()

# Show the plot
plt.show()
