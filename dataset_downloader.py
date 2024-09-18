import os
import zipfile
import subprocess
import tarfile

#reference https://gist.github.com/KarthikMAM/d8ebde4db84a72b083df0e14242edb1a

# Create directories
os.makedirs("gridcorpus/raw/audio", exist_ok=True)
os.makedirs("gridcorpus/raw/video", exist_ok=True)
os.makedirs("gridcorpus/audio", exist_ok=True)
os.makedirs("gridcorpus/video", exist_ok=True)

# Define range of speakers 1 to 34
start_speaker = int(input("Enter the starting speaker number: "))
end_speaker = int(input("Enter the ending speaker number: "))
extract_files = input("Do you want to extract files after downloading? (y/n): ")

for i in range(start_speaker, end_speaker + 1):
    print(f"\n\n------------------------- Downloading {i}th speaker -------------------------\n\n")

    # Download audio and video files
    subprocess.run(["curl", f"https://spandh.dcs.shef.ac.uk/gridcorpus/s{i}/audio/s{i}.tar", "-o", f"gridcorpus/raw/audio/s{i}.tar"])
    subprocess.run(["curl", f"https://spandh.dcs.shef.ac.uk/gridcorpus/s{i}/video/s{i}.mpg_vcd.zip", "-o", f"gridcorpus/raw/video/s{i}.zip"])

    # Extract files if requested
    if extract_files.lower() == "y":
        with zipfile.ZipFile(f"gridcorpus/raw/video/s{i}.zip", 'r') as zip_ref:
            zip_ref.extractall(f"gridcorpus/video/s{i}")
        with tarfile.open(f"gridcorpus/raw/audio/s{i}.tar", 'r') as tar_ref:
            tar_ref.extractall(f"gridcorpus/audio/s{i}")

print("Download completed.")