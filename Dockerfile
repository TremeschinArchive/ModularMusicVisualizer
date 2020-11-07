# Python 3.8 and Ubuntu 20.04
FROM ubuntu:20.04
FROM python:3.8

# Make /home/ubuntu and copy mmv folder to it
RUN mkdir /home/ubuntu
RUN cd /home/ubuntu && git clone https://github.com/Tremeschin/modular-music-visualizer

# Upgrade system
RUN apt update && apt upgrade -y

# Install apt deps
RUN apt install ffmpeg fluidsynth libglfw3 libglfw3-dev build-essential -y

# Install Python dependencies
RUN pip install -r /home/ubuntu/modular-music-visualizer/mmv/mmv/requirements.txt

# Run mmv
CMD ["python", "/home/ubuntu/modular-music-visualizer/mmv/example_basic.py"]