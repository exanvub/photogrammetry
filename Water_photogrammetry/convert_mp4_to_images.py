import subprocess
import os

def extract_frames_ffmpeg(video_path, output_folder, image_format="png"):
    """
    Extracts all frames from a video using FFmpeg at the highest quality possible.

    Parameters:
        video_path (str): Path to the input video file (e.g., "input.mp4")
        output_folder (str): Directory where frames will be saved
        image_format (str): Output format ("png" = lossless, "tiff" = lossless, "jpg" = lossy)
    """
    # Make sure output folder exists
    os.makedirs(output_folder, exist_ok=True)

    # Build ffmpeg command
    output_pattern = os.path.join(output_folder, f"frame_%06d.{image_format}")
    if image_format.lower() in ["jpg", "jpeg"]:
        # -q:v 1 = highest quality for JPEG
        cmd = ["ffmpeg", "-i", video_path, "-vsync", "0", "-q:v", "1", output_pattern]
    else:
        # PNG or TIFF (lossless)
        # only capture every 10th frame to reduce number of images
        cmd = ["ffmpeg", "-i", video_path, "-vsync", "0", "-vf", "select=not(mod(n\,10))", output_pattern]

    # Run the command
    try:
        subprocess.run(cmd, check=True)
        print(f"Frames extracted successfully to '{output_folder}'")
    except subprocess.CalledProcessError as e:
        print("Error running ffmpeg:", e)


if __name__ == "__main__":
    video_path = "/Volumes/Research/Photogrammetry/Water/Session_2/DJI_20250912181507_0025_D.MP4"
    
    output_folder = "/Volumes/Research/Photogrammetry/Water/Session_2/DJI_20250912181507_0025_D_Frames" # Output folder
    extract_frames_ffmpeg(video_path, output_folder, image_format="png")
