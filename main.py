"""
This moudule gets a file name from the command line,
and prints the pattern stats of a osu maina map in a JSON format.
"""

import sys

import calc

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python main.py <path_to_osu_file>")
        sys.exit(1)

    print(calc.from_file(sys.argv[1]))
