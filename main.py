from pathlib import Path
from typing import Annotated

import cv2
import numpy as np
import typer
from pydantic import NonNegativeInt, PositiveInt

app = typer.Typer()


class Converter:
    def __init__(self, video_path: Path) -> None:
        if not video_path.exists():
            msg = f"Video not found: {video_path}"
            raise FileNotFoundError(msg)
        self.video_path = video_path

    def generate_timeslice(
        self,
        frame_start: NonNegativeInt | None,
        frame_end: PositiveInt | None,
        scan_line_pct: NonNegativeInt,
    ) -> None:
        typer.echo(f"Generating timeslice of: {self.video_path}")
        # Open the video file
        cap = cv2.VideoCapture(self.video_path)
        output_path = self.video_path.with_suffix(".png")
        # Get video properties
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))  # noqa: F841
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = int(cap.get(cv2.CAP_PROP_FPS))  # noqa: F841
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        # Create an empty image to store the timeslice
        timeslice = []
        row_num = 0
        for frame_number in range(frame_count):
            if frame_start is not None and frame_number < frame_start:
                continue
            if frame_end is not None and frame_number > frame_end:
                break
            ret, frame = cap.read()
            if not ret:
                break
            # Process the frame
            typer.echo(f"Processing frame {frame_number}")
            scan_line_px = int(height * scan_line_pct / 100)
            scan_line = frame[scan_line_px, :, :]
            timeslice.append(scan_line)
            row_num += 1

        # Convert the list of rows to a numpy array
        timeslice = np.array(timeslice)
        # print the 20 colors that are used most in the timeslice
        colors, counts = np.unique(timeslice.reshape(-1, 3), axis=0, return_counts=True)
        sorted_colors = colors[np.argsort(-counts)]
        typer.echo(f"Most common colors in the timeslice: {sorted_colors[:20]}")
        # Save the timeslice image
        cv2.imwrite(output_path, timeslice)

        typer.echo(f"Timeslice image saved to {output_path}")


@app.command()
def start(
    *,
    video_path: Annotated[
        Path,
        typer.Option("--path", help="Video path"),
    ],
    frame_start: Annotated[
        int | None,
        typer.Option("--frame-start", help="Start frame number"),
    ] = None,
    frame_end: Annotated[
        int | None,
        typer.Option("--frame-end", help="End frame number"),
    ] = None,
    debug: Annotated[bool, typer.Option("--debug", help="Enable debug mode")] = True,
) -> None:
    typer.echo(f"Starting conversion with video path: {video_path}")
    converter = Converter(video_path)
    if debug:
        typer.echo("Debug mode is enabled")
    converter.generate_timeslice(
        frame_start=frame_start, frame_end=frame_end, scan_line_pct=0
    )


if __name__ == "__main__":
    app()
