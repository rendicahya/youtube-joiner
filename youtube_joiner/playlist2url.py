from pathlib import Path

import click
from pytubefix import Playlist


@click.command()
@click.argument("playlist_url")
def extract_urls(playlist_url):
    """Extracts all video URLs from a YouTube playlist and saves them to a .txt file."""

    playlist = Playlist(playlist_url)
    playlist_name = "".join(
        c if c.isalnum() or c in " _-" else "_" for c in playlist.title
    )
    downloads_dir = Path("downloads")
    filename = downloads_dir / f"{playlist_name}.txt"

    downloads_dir.mkdir(exist_ok=True, parents=True)

    with open(filename, "w") as file:
        for url in playlist.video_urls:
            file.write(url + "\n")

    print(f"Extracted {len(playlist.video_urls)} video URLs and saved to {filename}")


if __name__ == "__main__":
    extract_urls()
