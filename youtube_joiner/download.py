import os
import re
from pathlib import Path

import click
from moviepy import VideoFileClip
from pytubefix import YouTube


@click.command()
@click.argument("list_file", type=click.Path(exists=True, path_type=Path))
def download_videos(list_file):
    output_dir = list_file.with_suffix("")
    output_dir.mkdir(parents=True, exist_ok=True)

    report_file = output_dir / "download_report.txt"

    video_urls = [
        line.strip()
        for line in list_file.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]

    if not video_urls:
        click.echo(f"No URLs found in {list_file}. Exiting.", err=True)
        return

    for url in video_urls:
        video_id_match = re.search(r"(?:v=|shorts/)([a-zA-Z0-9_-]+)", url)
        if not video_id_match:
            click.echo(f"Could not extract video ID from {url}. Skipping.", err=True)
            continue

        video_id = video_id_match.group(1)
        video_file_path = output_dir / f"{video_id}_video.mp4"
        audio_file_path = output_dir / f"{video_id}_audio.mp4"
        combined_output = output_dir / f"{video_id}.mp4"

        if combined_output.exists():
            click.echo(
                f"Video {video_id} already downloaded and merged. Skipping.", err=True
            )
            continue

        try:
            yt = YouTube(url)

            video_stream = max(
                yt.streams.filter(adaptive=True, mime_type="video/mp4"),
                key=lambda s: int(s.resolution.replace("p", "")),
                default=None,
            )

            audio_stream = max(
                yt.streams.filter(only_audio=True, mime_type="audio/mp4"),
                key=lambda s: int(s.abr.replace("kbps", "")),
                default=None,
            )

            if not video_stream or not audio_stream:
                click.echo(
                    f"Skipping {video_id}: No suitable video or audio streams found.",
                    err=True,
                )
                continue

            click.echo(
                f"Downloading video: {video_stream.resolution} and audio: {audio_stream.abr}..."
            )

            video_stream.download(output_dir, filename=video_file_path.name)
            audio_stream.download(output_dir, filename=audio_file_path.name)

            click.echo(f"Downloaded video: {video_file_path}, audio: {audio_file_path}")

            video_clip = VideoFileClip(str(video_file_path))
            video_clip.write_videofile(
                str(combined_output),
                audio=str(audio_file_path),
                codec="libx264",
                audio_codec="aac",
                threads=8,
            )

            click.echo(f"Combined video saved as {combined_output}")
            os.remove(video_file_path)
            os.remove(audio_file_path)

            # Append video details to the report file
            with report_file.open("a", encoding="utf-8") as report:
                report.write(
                    f"Video ID: {video_id}\n"
                    f"Title: {yt.title}\n"
                    f"Resolution: {video_stream.resolution}\n"
                    f"Audio Bitrate: {audio_stream.abr}\n"
                    f"URL: {url}\n"
                    f"Saved As: {combined_output}\n"
                    f"{'-'*40}\n"
                )

        except Exception as e:
            click.echo(f"Failed to download {url}: {e}", err=True)


if __name__ == "__main__":
    download_videos()
