from __future__ import annotations

import argparse

from .analysis import write_processed
from .collectors import collect_all, save_collected_frames
from .visualization import build_all_figures


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Save you in history research pipeline")
    parser.add_argument("--online", action="store_true", help="Fetch pages online instead of using HTML snapshots")
    parser.add_argument("--collect", action="store_true", help="Run static parsers and save parsed files")
    args = parser.parse_args()

    if args.collect:
        frames = collect_all(offline=not args.online)
        save_collected_frames(frames)

    write_processed()
    build_all_figures()
    print("Pipeline completed: processed CSVs and figures are ready.")


if __name__ == "__main__":
    main()
