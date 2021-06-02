"""
===============================================================================
                                GPL v3 License                                
===============================================================================

Copyright (c) 2020 - 2021,
  - Tremeschin < https://tremeschin.gitlab.io > 

===============================================================================

Purpose: Quick "fluid" FFmpeg class implementation for rendering MMV videos

===============================================================================

This program is free software: you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later
version.

This program is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
You should have received a copy of the GNU General Public License along with
this program. If not, see <http://www.gnu.org/licenses/>.

===============================================================================
"""
import subprocess
import logging

PIPE = subprocess.PIPE


class BetterFFmpegWrapper:
    def __init__(self, ffmpeg_bin):
        self.ffmpeg_bin = ffmpeg_bin
        self.inputs = []
        self.before_inputs = []
        self.video_filters = []
        self.x264_params = []
        self.before_output = []

    # Return None if item doesn't exist
    def __getattr__(self, _): return None

    # "Global"
    def hwaccel_auto(self): self.before_inputs += ["-hwaccel", "auto"]; return self
    def crf(self, crf): self._crf = ["-crf", f"{crf}"]; return self
    def vf(self, what): self.video_filters.append(what); return self
    def hide_banner(self): self.before_inputs += ["-hide_banner"]; return self
    def loglevel(self, what): self.before_inputs += ["-loglevel", what]; return self
    def override(self): self.before_output += ["-y"]; return self
    def nostats(self): self.before_output += ["-nostats"]; return self
    def shortest(self): self.before_output += ["-shortest"]; return self
    def threads(self, n): self.before_output += ["-threads", str(n)]; return self
    def duration(self, t):
        if ":" in str(t): self.before_output += ["-t", f"{t}"]  # User sent XX:YY:ZZ
        else: self.before_output += ["-t", f"{t}"]  # Convert to that
        return self

    # Input stuff
    def input(self, path):
        if path: self.inputs += ["-i", path]
        return self
    def input_pipe(self): self.inputs += ["-f", "rawvideo", "-i", "-"]; return self
    def input_framerate(self, n): self.before_inputs += ["-r", f"{n}"]; return self
    def input_resolution(self, width, height): self.before_inputs += ["-s", f"{width}x{height}"]; return self
    def input_pixel_format(self, f): self.before_inputs += ["-pix_fmt", f]; return self

    # Output
    def output(self, path): self._output = path; return self
    def output_stdout(self): self._output = "-"; return self
    def output_framerate(self, n): self.before_output += ["-r", f"{n}"]; return self
    def output_resolution(self, width, height): self.before_output += ["-s", f"{width}x{height}"]; return self
    def output_pixel_format(self, f): self.before_output += ["-pix_fmt", f]; return self
    def output_format(self, f): self.before_output += ["-f", f]; return self

    # Audio
    def audio_codec(self, what): self.acodec = ["-acodec", what]; return self
    def audio_channels(self, n): self.ac = ["-ac", f"{n}"]; return self
    def audio_samplerate(self, n): self.ar = ["-ar", f"{n}"]; return self

    # Encoder codecs
    def encoder_libx264(self): self.encoder = ["-c:v", "libx264"]; return self
    def encoder_libx265(self): self.encoder = ["-c:v", "libx265"]; return self
    def encoder_h264_nvenc(self): self.encoder = ["-c:v", "h264_nvenc"]; return self
    def encoder_h265_nvenc(self): self.encoder = ["-c:v", "h265_nvenc"]; return self
    def encoder_manual(self, encoder): self.encoder = ["-c:v", encoder]; return self

    # Tune
    def tune_animation(self): self.tune = ["-tune", "animation"]; return self
    def tune_film(self): self.tune = ["-tune", "film"]; return self
    def tune_grain(self): self.tune = ["-tune", "grain"]; return self
    def tune_stillimage(self): self.tune = ["-tune", "stillimage"]; return self
    def tune_fastdecode(self): self.tune = ["-tune", "fastdecode"]; return self
    def tune_manual(self, tune): self.tune = ["-tune", tune]; return self

    # Profiles
    def profile_main(self): self.profile = ["-profile:v", "main"]; return self
    def profile_baseline(self): self.profile = ["-profile:v", "baseline"]; return self

    # Preset to encode
    def preset_ultrafast(self): self.preset = ["-preset", "ultrafast"]; return self
    def preset_superfast(self): self.preset = ["-preset", "superfast"]; return self
    def preset_veryfast(self): self.preset = ["-preset", "veryfast"]; return self
    def preset_faster(self): self.preset = ["-preset", "faster"]; return self
    def preset_fast(self): self.preset = ["-preset", "fast"]; return self
    def preset_medium(self): self.preset = ["-preset", "medium"]; return self
    def preset_slow(self): self.preset = ["-preset", "slow"]; return self
    def preset_slower(self): self.preset = ["-preset", "slower"]; return self
    def preset_veryslow(self): self.preset = ["-preset", "veryslow"]; return self
    def preset_placebo(self): self.preset = ["-preset", "placebo"]; return self
    def preset_manual(self, p): self.preset = ["-preset", p]; return self

    # Add a advanced x264 parameter
    def x264_param(self, new):
        if isinstance(new, list):
            for item in new: self.x264_param(item)
        else: self.x264_params.append(new)
        return self

    # Build the command, returns list of arguments to be called
    def _build_command(self):
        for banned in ["265", "nvenc"]: # NVENC doens't accept tune
            if any([banned in item for item in self.encoder]): self.tune = []
        cmd = [self.ffmpeg_bin]
        cmd += self.before_inputs
        cmd += self.inputs
        cmd += self.ac or []
        cmd += self.ar or []
        cmd += self.acodec or []
        cmd += self.tune or []
        cmd += self.encoder or []
        cmd += self.preset or []
        cmd += self._crf or []
        cmd += self.profile or []
        if self.x264_params: cmd += ["-x264-params", ":".join(self.x264_params)]
        if self.video_filters: cmd += ["-vf", ",".join(self.video_filters)]
        cmd += self.before_output
        cmd += [self._output]
        return cmd

    def run(self):
        cmd = self._build_command()
        logging.info(f"[BetterFFmpegWrapper.run] Run command is: [" + '" "'.join(cmd) + "]")
        self.subprocess = subprocess.Popen(cmd, stdin = PIPE, stdout = PIPE)
        self.stdin = self.subprocess.stdin
        self.stdout = self.subprocess.stdout
        self.stderr = self.subprocess.stderr

# Test
if __name__ == "__main__":
    f = BetterFFmpegWrapper("/usr/bin/ffmpeg")
    f \
    .loglevel("panic") \
    .hide_banner() \
    .input("audio.mp3") \
    .audio_codec("pcm_f32le") \
    .audio_channels(2) \
    .output_format("f32le") \
    .output_stdout() \
    .run()

    print("\n" + "-"*120 + "\n")

    f = BetterFFmpegWrapper("/usr/bin/ffmpeg")
    f \
    .hwaccel_auto() \
    .loglevel("panic") \
    .hide_banner() \
    .input_pipe() \
    .input_resolution(1920, 1080) \
    .input("audio.mp3") \
    .encoder_libx264() \
    .tune_film() \
    .crf(18) \
    .profile_main() \
    .preset_slow() \
    .vf("vflip") \
    .vf("tmix") \
    .vf("format=yuv420p") \
    .x264_param("opencl=true") \
    .x264_param("deblock=-3,-3") \
    .x264_param("bframes=16") \
    .x264_param("aq-mode=2") \
    .x264_param("aq-strength=0.8") \
    .x264_param("rc-lookahead=250:ref=16") \
    .x264_param("me=uhm:merange=24") \
    .x264_param("limit-sao:psy-rd=1:aq-mode=3") \
    .override() \
    .output("Final.mkv") \
    .shortest() \
    .output_resolution(1280, 720) \
    .output_framerate(60) \
    .run() \



