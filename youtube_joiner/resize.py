from pathlib import Path

import click
import moviepy.video.fx.resize as resize
from moviepy import VideoFileClip


@click.command()
@click.argument("video_path", type=click.Path(exists=True, path_type=Path))
@click.argument("resolution", type=str)
def resize_video(video_path, resolution):
    """Resize VIDEO_PATH to the given RESOLUTION (widthxheight)."""

    # Parse resolution argument (e.g., "720x1280" → width=720, height=1280)
    try:
        width, height = map(int, resolution.lower().split("x"))
    except ValueError:
        click.echo(
            "Error: Resolution must be in format WIDTHxHEIGHT (e.g., 720x1280).",
            err=True,
        )
        return

    # Load video
    clip = VideoFileClip(str(video_path))

    # Resize video using MoviePy's resize effect
    resized_clip = resize.resize(clip, newsize=(width, height))

    # Generate output filename
    output_path = video_path.with_name(
        f"{video_path.stem}_{width}x{height}{video_path.suffix}"
    )

    # Save resized video
    resized_clip.write_videofile(str(output_path), codec="libx264", audio_codec="aac")

    click.echo(f"Resized video saved as {output_path}")


if __name__ == "__main__":
    resize_video()
