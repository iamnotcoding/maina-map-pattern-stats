"""
This moudule gets a file name from the command line,
and prints the pattern stats of a osu maina map in a JSON format.
"""

import json
import sys

import parse
import calc


def print_pattern_stats(file_path: str) -> None:
    """
    Prints the pattern stats of a osu maina map in a JSON format.
    """
    map_data = parse.parse_map(file_path)
    pattern_stats = calc.calc_4k_pattern_stats(map_data)
    butified_stats = calc.butify_pattern_stats(pattern_stats)

    print(json.dumps(butified_stats, indent=4, ensure_ascii=False))


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python main.py <path_to_osu_file>")
        sys.exit(1)

    print_pattern_stats(sys.argv[1])
