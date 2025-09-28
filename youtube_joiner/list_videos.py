from pathlib import Path

import click


@click.command()
@click.argument(
    "directory", type=click.Path(exists=True, file_okay=False, path_type=Path)
)
def list_videos(directory):
    """List all videos in DIRECTORY and save them in a text file named after the directory."""

    # Define video extensions to look for
    video_extensions = {".mp4", ".mov", ".avi", ".mkv", ".flv", ".wmv", ".webm"}

    # Find all video files in the directory
    video_files = sorted(
        [
            file
            for file in directory.iterdir()
            if file.suffix.lower() in video_extensions
        ]
    )

    if not video_files:
        click.echo(f"No video files found in {directory}.", err=True)
        return

    # Create output text file with the same name as the directory
    output_file = directory.with_suffix(".txt")

    # Write video filenames to the text file
    output_file.write_text(
        "\n".join(file.name for file in video_files), encoding="utf-8"
    )

    click.echo(f"Saved list of {len(video_files)} videos to {output_file}")


if __name__ == "__main__":
    list_videos()
