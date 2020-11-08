# Python 3.8 and Ubuntu 20.04
FROM ubuntu:20.04
FROM python:3.8

# Make /home/ubuntu and copy mmv folder to it
RUN mkdir /home/ubuntu

# Git clone or git pull from cache
RUN git clone https://github.com/Tremeschin/modular-music-visualizer /home/ubuntu/modular-music-visualizer
RUN cd /home/ubuntu/modular-music-visualizer && git pull

# Upgrade system
RUN apt update && apt upgrade -y

# Install apt deps
RUN apt install ffmpeg fluidsynth libglfw3 libglfw3-dev build-essential -y

# Install Python dependencies
RUN pip install -r /home/ubuntu/modular-music-visualizer/mmv/mmv/requirements.txt

# Run mmv
CMD ["python", "/home/ubuntu/modular-music-visualizer/mmv/example_basic.py", "render=cpu"]
