# Use the CUDA 11.8.0 devel image with Ubuntu 20.04
FROM nvidia/cuda:11.8.0-cudnn8-devel-ubuntu20.04

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive

# Install required packages, including wget and unzip for downloading and extracting files
RUN apt-get update && apt-get install -y \
    python3-pip \
    python3-dev \
    cmake \
    ffmpeg \
    wget \
    unzip \
    git \
    ninja-build \
    && rm -rf /var/lib/apt/lists/*

# Clone the project repository
RUN git clone https://github.com/vinthony/video-retalking.git /video-retalking

# Set the working directory
WORKDIR /video-retalking

# Install Python dependencies
RUN pip3 install -r requirements.txt

# Apply the fix for basicsr
RUN sed -i 's/from torchvision.transforms.functional_tensor import rgb_to_grayscale/from torchvision.transforms.functional import rgb_to_grayscale/' \
    $(python3 -c "import site; print(site.getsitepackages()[0])")/basicsr/data/degradations.py

# Download pre-trained models
RUN mkdir ./checkpoints && \
    wget https://github.com/vinthony/video-retalking/releases/download/v0.0.1/30_net_gen.pth -O ./checkpoints/30_net_gen.pth && \
    wget https://github.com/vinthony/video-retalking/releases/download/v0.0.1/BFM.zip -O ./checkpoints/BFM.zip && \
    wget https://github.com/vinthony/video-retalking/releases/download/v0.0.1/DNet.pt -O ./checkpoints/DNet.pt && \
    wget https://github.com/vinthony/video-retalking/releases/download/v0.0.1/ENet.pth -O ./checkpoints/ENet.pth && \
    wget https://github.com/vinthony/video-retalking/releases/download/v0.0.1/expression.mat -O ./checkpoints/expression.mat && \
    wget https://github.com/vinthony/video-retalking/releases/download/v0.0.1/face3d_pretrain_epoch_20.pth -O ./checkpoints/face3d_pretrain_epoch_20.pth && \
    wget https://github.com/vinthony/video-retalking/releases/download/v0.0.1/GFPGANv1.3.pth -O ./checkpoints/GFPGANv1.3.pth && \
    wget https://github.com/vinthony/video-retalking/releases/download/v0.0.1/GPEN-BFR-512.pth -O ./checkpoints/GPEN-BFR-512.pth && \
    wget https://github.com/vinthony/video-retalking/releases/download/v0.0.1/LNet.pth -O ./checkpoints/LNet.pth && \
    wget https://github.com/vinthony/video-retalking/releases/download/v0.0.1/ParseNet-latest.pth -O ./checkpoints/ParseNet-latest.pth && \
    wget https://github.com/vinthony/video-retalking/releases/download/v0.0.1/RetinaFace-R50.pth -O ./checkpoints/RetinaFace-R50.pth && \
    wget https://github.com/vinthony/video-retalking/releases/download/v0.0.1/shape_predictor_68_face_landmarks.dat -O ./checkpoints/shape_predictor_68_face_landmarks.dat && \
    unzip -d ./checkpoints/BFM ./checkpoints/BFM.zip

# Expose the directory where results will be saved
VOLUME ["/video-retalking/results"]

# Command to run inference (replace with actual paths and options as necessary)
CMD ["python3", "inference.py", "--face", "examples/face/1.mp4", "--audio", "examples/audio/1.wav", "--outfile", "results/output.mp4"]
