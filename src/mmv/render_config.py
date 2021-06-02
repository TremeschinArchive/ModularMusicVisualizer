"""
===============================================================================
                                GPL v3 License                                
===============================================================================

Copyright (c) 2020 - 2021,
  - Tremeschin < https://tremeschin.gitlab.io > 

===============================================================================

Purpose: Render 

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
from wonderwords import RandomSentence
from dotmap import DotMap
from tqdm import tqdm
import datetime



def setup(ctx):
	expect = DotMap(_dynamic = False)
	ctx.interface.externals.check_download_externals(target_externals = ["ffmpeg"])
	random_sentence = RandomSentence()

	# # FFmpeg

	expect.audio = ctx.get("input_audio", None)
	expect.width = ctx.config["render"]["width"]
	expect.height = ctx.config["render"]["height"]
	expect.ssaa = ctx.config["render"]["ssaa"]
	expect.final_ssaa = ctx.config["render"]["final_ssaa"]
	expect.crf = ctx.config["render"]["ffmpeg"]["crf"]
	expect.encoder = ctx.config["render"]["ffmpeg"]["vcodec"]
	expect.tune = ctx.config["render"]["ffmpeg"]["tune"]
	expect.preset = ctx.config["render"]["ffmpeg"]["preset"]
	expect.motionblur = ctx.config["render"]["ffmpeg"]["motionblur"]
	expect.fps = ctx.config["render"]["fps"]
	expect.final = ctx.config["render"]["final"]

	expect.output = ctx.config["render"]["output_video"]
	if expect.output == "auto":
		s = random_sentence.bare_bone_with_adjective().capitalize()
		s = ' '.join([word.capitalize() for word in s.split(' ')]).replace(".", "")
		t = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
		expect.output = f"{t} | {s}.mkv"

	# Set output to render directory
	if ctx.config["render"]["output_to_render_directory"]:
		expect.output = ctx.interface.renders_dir / expect.output

	if expect.audio is None:
		expect.duration = ctx.config["render"]["no_audio_duration"]
		expect.total_steps = ctx.config["render"]["fps"] * expect.duration
	else:
		raise NotImplementedError()

	# Change resolution
	ctx.context.width = expect.width
	ctx.context.height = expect.height

	expect.ffmpeg = ctx.interface.get_ffmpeg_wrapper()
	if not expect.audio: expect.ffmpeg.duration(expect.duration)

	# Base FFmpeg
	expect.ffmpeg \
		.hwaccel_auto() \
		.loglevel("info") \
		.nostats() \
		.override() \
		.shortest() \
		.input_pipe() \
		.input_framerate(expect.fps) \
		.input_resolution(expect.width * ctx.context.ssaa, expect.height * ctx.context.ssaa) \
		.input_pixel_format("rgb24") \
		.input(expect.audio) \
		.encoder_manual(expect.encoder) \
		.tune_manual(expect.tune) \
		.crf(expect.crf) \
		.profile_main() \
		.preset_manual(expect.preset) \
		.vf("vflip") \
		.vf("format=yuv420p") \
		.output_framerate(expect.fps) \
		.output(str(expect.output)) \
		.output_resolution(expect.width, expect.height) \

	# Juicy x264 flags for final export
	if expect.final:
		ctx.context.ssaa = expect.final_ssaa
		expect.ffmpeg \
		.x264_param("opencl=true") \
		.x264_param("bframes=16") \
		.x264_param("b_pyramid=normal") \
		.x264_param("partitions=all") \
		.x264_param("aq-mode=2") \
		.x264_param("aq-strength=0.8") \
		.x264_param("rc-lookahead=250:ref=16") \
		.x264_param("me=esa:merange=24") \
		.x264_param("subq=7") \
		.x264_param("frameref=3") \
		.x264_param("cabac=1") \
		.vf("noise=8a:4a")
		# .x264_param("qcomp=0.8") \
		# .x264_param("limit-sao:psy-rd=1:aq-mode=3") \
	else:
		ctx.context.ssaa = expect.ssaa

	# Optional
	if expect.motionblur: expect.ffmpeg.vf("tmix")

	# Run FFmpeg
	expect.ffmpeg.run()

	# Create progress bar
	expect.progress_bar = tqdm(
		total = expect.total_steps,
		# unit_scale = True,
		unit = " frames",
		dynamic_ncols = True,
		colour = '#38bed6',
		position = 0,
		smoothing = 0.3
	)

	# Set description
	expect.progress_bar.set_description((
		f"Rendering [SSAA={ctx.context.ssaa}]"
		f"({int(ctx.context.width * ctx.context.ssaa)}x"
		f"{int(ctx.context.height * ctx.context.ssaa)})"
		f"->({ctx.context.width}x{ctx.context.height})"
		f"[{expect.duration:.2f}s] MMV video"
	))

	return expect