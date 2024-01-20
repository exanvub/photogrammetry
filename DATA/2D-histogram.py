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

def create_normalized_2d_histogram(quality_data, ax, title='', ylabel=True, xlabel=True):
    counts, edges = np.histogram(quality_data, bins=50, range=[-1.5, 1.5], density=True)
    colors = ["blue", "white", "red"]
    cmap = mcolors.LinearSegmentedColormap.from_list("CustomMap", colors, N=256)
    norm_factor = abs(edges).max()

    for count, edge in zip(counts, edges[:-1]):
        norm_val = (edge + norm_factor) / (2 * norm_factor)
        color = cmap(norm_val)
        x = edge
        width = edges[1] - edges[0]
        ax.bar(x, count, width=width, color=color, edgecolor='black', linewidth=0.5, alpha=0.8)

    ax.set_ylim(0, 1.8)

    if ylabel:
        ax.set_ylabel('Normalized Frequency')
    if xlabel:
        ax.set_xlabel('Distance from reference mesh (mm)')
    # ax.set_title(f'Normalized 2D Histogram of Quality ({title})')
    ax.set_title(f'{title}')
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
        fig, axs = plt.subplots(2, 2, figsize=(10, 5))

        if combined_data:
            create_normalized_2d_histogram(combined_data, axs[1, 1], title='OC - filter', ylabel=False, xlabel=True)

        if combined_data2:
            create_normalized_2d_histogram(combined_data2, axs[0, 1], title='OC - No filter', ylabel=False, xlabel=False)

        if combined_data3:
            create_normalized_2d_histogram(combined_data3, axs[1, 0], title='Colmap - filter', ylabel=True)

        if combined_data4:
            create_normalized_2d_histogram(combined_data4, axs[0, 0], title='Colmap - No filter', ylabel=True, xlabel=False)


        plt.show()
