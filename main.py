from pathlib import Path
from typing import Annotated

import typer

from piano_midi.color_picker import ColorPicker
from piano_midi.key_picker import KeyPicker
from piano_midi.key_press_detector import KeyPressDetector
from piano_midi.key_sequence_writer import KeySequenceWriter
from piano_midi.models import KeyColors, KeySegments
from piano_midi.time_slicer import TimeSlicer
from piano_midi.video_capture import VideoCapture

app = typer.Typer(
    name="midi tools",
    add_completion=False,
)


@app.command()
def key_picker(
    *,
    video_path: Annotated[
        Path,
        typer.Option(
            "--video-path", help="Video path that is used for creating the mask"
        ),
    ],
    key_segments_path: Annotated[
        Path,
        typer.Option("--key-segments-path", help="Path to store the keysegments to"),
    ],
) -> None:
    typer.echo(f"Starting key picker with image path: {video_path}")
    video_capture = VideoCapture(video_path)
    with video_capture as cap:
        frame = cap.get_frame(frame_number=0)
    key_picker = KeyPicker(frame=frame, key_segments_path=key_segments_path)
    key_picker.run()


@app.command()
def color_picker(
    *,
    video_path: Annotated[
        Path,
        typer.Option(
            "--video-path", help="Video path that is used for creating the mask"
        ),
    ],
    colors_path: Annotated[
        Path,
        typer.Option("--colors-path", help="Path to store the colors to"),
    ],
    frame_start: Annotated[
        int,
        typer.Option("--frame-start", help="Frame start for the timeslice"),
    ] = 0,
    frame_end: Annotated[
        int | None,
        typer.Option("--frame-end", help="Frame end for the timeslice"),
    ] = None,
    scan_line_pct: Annotated[
        int,
        typer.Option("--scan-line-pct", help="Percentage of the scan line"),
    ] = 0,
) -> None:
    typer.echo(f"Starting color picker with image path: {video_path}")
    video_capture = VideoCapture(video_path)
    time_slicer = TimeSlicer(video_capture)
    time_slice = time_slicer.generate(
        frame_start=frame_start, frame_end=frame_end, scan_line_pct=scan_line_pct
    )
    color_picker = ColorPicker(time_slice=time_slice, colors_path=colors_path)
    color_picker.run()


@app.command()
def video_to_midi(
    *,
    video_path: Annotated[
        Path,
        typer.Option(
            "--video-path", help="Video path that is used for creating the mask"
        ),
    ],
    key_segments_path: Annotated[
        Path,
        typer.Option("--key-segments-path", help="Path to store the keysegments to"),
    ],
    colors_path: Annotated[
        Path,
        typer.Option("--colors-path", help="Path to store the colors to"),
    ],
    midi_path: Annotated[
        Path,
        typer.Option("--midi-path", help="Path to store the midi file to"),
    ],
    frame_start: Annotated[
        int,
        typer.Option("--frame-start", help="Frame start for the timeslice"),
    ] = 0,
    frame_end: Annotated[
        int | None,
        typer.Option("--frame-end", help="Frame end for the timeslice"),
    ] = None,
) -> None:
    typer.echo(f"Starting video to midi with image path: {video_path}")
    video_capture = VideoCapture(video_path)
    key_segments = KeySegments.from_yaml(key_segments_path)
    key_colors = KeyColors.from_yaml(colors_path)
    key_sequence_writer = KeySequenceWriter(midi_file_path=midi_path)
    key_press_detector = KeyPressDetector(
        video_capture=video_capture, key_segments=key_segments, key_colors=key_colors
    )
    key_press_detector.run(key_sequence_writer=key_sequence_writer, frame_start=frame_start, frame_end=frame_end)


if __name__ == "__main__":
    app()
