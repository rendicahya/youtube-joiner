import re
from pathlib import Path

import click
from moviepy import VideoFileClip, concatenate_videoclips


def same_resolution(videos):
    resolutions = [video.size for video in videos]

    if len(resolutions) < 2 or all(res == resolutions[0] for res in resolutions[1:]):
        return True

    click.echo("Resolution mismatch. All resolutions:")

    for i, resolution in enumerate(resolutions):
        click.echo(f"Video {i+1}: {resolution[0]}x{resolution[1]}")

    return False


@click.command()
@click.argument("list_file", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--resolution",
    "-r",
    type=str,
    help="Target resolution in WIDTHxHEIGHT format (e.g., 1280x720).",
)
def merge_videos(list_file, resolution):
    output_dir = list_file.with_suffix("")
    video_paths = []

    for line in list_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue

        file_path = output_dir / line

        if file_path.exists() and file_path.is_file():
            video_paths.append(file_path)
        else:
            video_id_match = re.search(r"(?:v=|shorts/)([a-zA-Z0-9_-]+)", line)
            if video_id_match:
                video_id = video_id_match.group(1)
                video_path = output_dir / f"{video_id}.mp4"
                if video_path.exists():
                    video_paths.append(video_path)
                else:
                    click.echo(f"Skipping {line}: Video not found.", err=True)
            else:
                click.echo(
                    f"Skipping {line}: Not a valid file or YouTube URL.", err=True
                )

    if not video_paths:
        click.echo("No valid videos. Exiting.", err=True)
        return

    video_clips = [VideoFileClip(str(video)) for video in video_paths]

    if not resolution and not same_resolution(video_clips):
        click.echo("Resolutions mismatch. Exiting.", err=True)
        return

    final_clip = concatenate_videoclips(video_clips, method="compose")
    final_output = output_dir / f"{output_dir.name}.mp4"
    minutes, seconds = divmod(int(final_clip.duration), 60)
    time_format = f"{minutes:02}:{seconds:02}"

    click.echo(f"Video length: {time_format}.")

    if resolution:
        width, height = map(int, resolution.lower().split("x"))
        final_clip = final_clip.resized((width, height))

        click.echo(f"Resizing final video to {width}x{height}")

    if click.confirm("Do you want to continue?", default=True):
        final_clip.write_videofile(
            str(final_output),
            codec="libx264",
            audio_codec="aac",
            threads=16,
        )
        click.echo(f"Merge complete! Saved as {final_output}")
    else:
        click.echo("Merge cancelled.")


if __name__ == "__main__":
    merge_videos()
