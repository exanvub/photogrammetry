import matplotlib.pyplot as plt
import numpy as np
import matplotlib.colors as mcolors

def read_data_file(file_path):
    try:
        with open(file_path, 'r') as file:
            data_lines = file.readlines()
        return data_lines
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        return None

def extract_quality(data_lines):
    quality = []
    for line in data_lines:
        columns = line.strip().split()
        if columns:
            try:
                quality_value = float(columns[-1])
                quality.append(quality_value)
            except ValueError:
                print(f"Warning: Invalid quality value in line '{line}'")
    return quality

def create_normalized_3d_histogram(quality_data, ax, title='', y_offset=0):
    counts, edges = np.histogram(quality_data, bins=50, range=[-1.5, 1.5], density=True)
    colors = ["blue", "white", "red"]
    cmap = mcolors.LinearSegmentedColormap.from_list("CustomMap", colors, N=256)
    norm_factor = abs(edges).max()

    for count, edge in zip(counts, edges[:-1]):
        norm_val = (edge + norm_factor) / (2 * norm_factor)
        color = cmap(norm_val)
        x = edge
        dx = edges[1] - edges[0]
        z = 0
        dz = count
        y = y_offset
        dy = dx / 4
        ax.bar3d(x, y, z, dx, dy, dz, color=color, 
                 shade=True, 
                 zsort='max', 
                 #edgecolor='black', 
                 #linewidth=0.2
                 )

    ax.set_xlabel('Quality')
    #ax.set_ylabel('Normalized Frequency')
    #ax.set_zlabel('Data Sets')
    ax.set_title(f'Normalized 3D Histogram of Quality ({title})')

    # Adjust x-axis ticks
    ax.set_xticks(np.arange(-2, 2.1, 0.5))
    ax.set_xlim(-1.5, 1.5)

    # Set gridlines for better visibility
    ax.grid(True)

if __name__ == "__main__":
    file_paths_OC_filter = [
        "/Volumes/SAMSUNG_1T/Photogrammetry/Spine/Calculations/42/txt/42_C3-OC-filter-quality.txt",
        "/Volumes/SAMSUNG_1T/Photogrammetry/Spine/Calculations/25/txt/25_C3-OC-filter-quality.txt",
        "/Volumes/SAMSUNG_1T/Photogrammetry/Spine/Calculations/104/txt/102_C3_OC-filter-quality.txt",
        "/Volumes/SAMSUNG_1T/Photogrammetry/Spine/Calculations/62/txt/62_C3_OC-filter-quality.txt",
        "/Volumes/SAMSUNG_1T/Photogrammetry/Spine/Calculations/7/txt/7_C3-OC-filter-quality.txt",
        "/Volumes/SAMSUNG_1T/Photogrammetry/Spine/Calculations/35/txt/35_C3-OC-filter-quality.txt",

        # Add more file paths for the first dataset as needed
    ]

    file_paths_OC_NOfilter = [
        "/Volumes/SAMSUNG_1T/Photogrammetry/Spine/Calculations/42/txt/42_C3-OC-NOfilter-quality.txt",
        "/Volumes/SAMSUNG_1T/Photogrammetry/Spine/Calculations/25/txt/25_C3-OC-NOfilter-quality.txt",
        "/Volumes/SAMSUNG_1T/Photogrammetry/Spine/Calculations/104/txt/102_C3_OC-no-filter-quality.txt",
        "/Volumes/SAMSUNG_1T/Photogrammetry/Spine/Calculations/62/txt/62_C3_OC-no-filter-quality.txt",
        "/Volumes/SAMSUNG_1T/Photogrammetry/Spine/Calculations/7/txt/7_C3-OC-nofilter-quality.txt",
        "/Volumes/SAMSUNG_1T/Photogrammetry/Spine/Calculations/35/txt/35_C3-OC-NOfilter-quality.txt"
        # Add more file paths for the second dataset as needed
    ]

    file_paths_colmap_filter = [
        "/Volumes/SAMSUNG_1T/Photogrammetry/Spine/Calculations/42/txt/42_C3-colmap-filter-quality.txt",
        "/Volumes/SAMSUNG_1T/Photogrammetry/Spine/Calculations/25/txt/25_C3-colmap-filter-quality.txt",
        "/Volumes/SAMSUNG_1T/Photogrammetry/Spine/Calculations/104/txt/102_C3_colmap-filter-quality.txt",
        "/Volumes/SAMSUNG_1T/Photogrammetry/Spine/Calculations/62/txt/62_C3_colmap-filter-quality.txt",
        "/Volumes/SAMSUNG_1T/Photogrammetry/Spine/Calculations/7/txt/7_C3-colmap-filter-quality.txt",
        "/Volumes/SAMSUNG_1T/Photogrammetry/Spine/Calculations/35/txt/35_C3-colmap-filter-quality.txt"
        # Add more file paths for the second dataset as needed
    ]

    file_paths_colmap_NOfilter = [
        "/Volumes/SAMSUNG_1T/Photogrammetry/Spine/Calculations/42/txt/42_C3-colmap-NOfilter-quality.txt",
        "/Volumes/SAMSUNG_1T/Photogrammetry/Spine/Calculations/25/txt/25_C3-colmap-NOfilter-quality.txt",
        "/Volumes/SAMSUNG_1T/Photogrammetry/Spine/Calculations/104/txt/102_C3_colmap-no-filter-quality.txt",
        "/Volumes/SAMSUNG_1T/Photogrammetry/Spine/Calculations/62/txt/62_C3_colmap-no-filter-quality.txt",
        "/Volumes/SAMSUNG_1T/Photogrammetry/Spine/Calculations/7/txt/7_C3-colmap-Nofilter-quality.txt",
        "/Volumes/SAMSUNG_1T/Photogrammetry/Spine/Calculations/35/txt/35_C3-colmap-NOfilter-quality.txt"
        # Add more file paths for the second dataset as needed
    ]

    combined_data = []
    combined_data2 = []
    combined_data3 = [] 
    combined_data4 = []

    for file_path in file_paths_OC_filter:
        data_lines = read_data_file(file_path)
        if data_lines:
            quality = extract_quality(data_lines)
            combined_data.extend(quality)

    for file_path2 in file_paths_OC_NOfilter:
        data_lines2 = read_data_file(file_path2)
        if data_lines2:
            quality2 = extract_quality(data_lines2)
            combined_data2.extend(quality2)

    for file_path3 in file_paths_colmap_filter:
        data_lines3 = read_data_file(file_path3)
        if data_lines3:
            quality3 = extract_quality(data_lines3)
            combined_data3.extend(quality3)

    for file_path4 in file_paths_colmap_NOfilter:
        data_lines4 = read_data_file(file_path4)
        if data_lines4:
            quality4 = extract_quality(data_lines4)
            combined_data4.extend(quality4)

    if combined_data or combined_data2 or combined_data3 or combined_data4:
        fig = plt.figure(figsize=(10, 6))
        ax = fig.add_subplot(111, projection='3d')

        y_offset_set1 = 0.0
        y_offset_set2 = y_offset_set1 + 0.1
        y_offset_set3 = y_offset_set2 + 0.1
        y_offset_set4 = y_offset_set3 + 0.1

        if combined_data:
            create_normalized_3d_histogram(combined_data, ax, title='Combined Data (Set 1)', y_offset=y_offset_set1)

        if combined_data2:
            create_normalized_3d_histogram(combined_data2, ax, title='Combined Data (Set 2)', y_offset=y_offset_set2)

        if combined_data3:
            create_normalized_3d_histogram(combined_data3, ax, title='Combined Data (Set 3)', y_offset=y_offset_set3)

        if combined_data4:
            create_normalized_3d_histogram(combined_data4, ax, title='Combined Data', y_offset=y_offset_set4)

        # Adjust y-axis limits to start from 0
        ax.set_ylim(0, y_offset_set4 + 0.05)

        ax.set_yticks([y_offset_set1, y_offset_set2, y_offset_set3, y_offset_set4])
        ax.set_yticklabels(['OC-filter', 'OC-NoFilter', 'Colmap-filter', 'Colmap-NoFilter'])

        plt.show()
