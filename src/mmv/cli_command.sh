python cli.py \
    init --who skia \
    resolution --preset 1080p,60 \
    skia-fft \
        --batch-size 2048 \
    skia-globals \
        --audio-amplitude-multiplier 1.0 \
        --render-backend gpu \
        --max-images-on-pipe-buffer 20 \
    ensure-ffmpeg --force \
    ensure-mpv --force \
    ensure-musescore --force \
    encoding \
        --output-video out.mkv \
        --input-audio ./assets/free_assets/kawaii_bass.ogg \
        --preset slow \
        --crf 17 \
        --tune film

