from pathlib import Path

import click
from moviepy import VideoFileClip


@click.command()
@click.argument("directory", type=click.Path(exists=True, path_type=Path))
def print_resolutions(directory):
    """Print the resolution of all video files in the specified directory, regardless of format."""

    valid_extensions = {".mp4", ".mov", ".avi", ".mkv", ".flv", ".wmv", ".webm"}
    video_files = [file for file in directory.iterdir() if file.suffix.lower() in valid_extensions]

    if not video_files:
        click.echo("No video files found in the directory.")
        return

    click.echo(f"Found {len(video_files)} video(s) in {directory}.")

    for video_path in video_files:
        try:
            clip = VideoFileClip(str(video_path))
            resolution = clip.size
            click.echo(f"{video_path.name}: {resolution[0]}x{resolution[1]}")
        except Exception as e:
            click.echo(f"Could not read {video_path.name}: {e}", err=True)

if __name__ == "__main__":
    print_resolutions()
