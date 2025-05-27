"""
This module tests functions in calc.py
"""

import os

import parse

from calc import MainaMap, PatternType, get_pattern_type


def calc_4k_raw_stats_sum(m: MainaMap) -> float:
    """
    Returns the sum of the number of patterns for the test purpose.
    """
    pattern_stats = {pattern: 0.0 for pattern in PatternType}

    prev_notes = list(m.data.values())[0]

    prev_prev_notes = list(m.data.values())[1]
    line_count = len(m.data)

    for _, notes in list(m.data.items())[2:]:
        pattern_type = get_pattern_type(prev_prev_notes, prev_notes, notes)
        pattern_stats[pattern_type] += 1

        prev_prev_notes = prev_notes

        prev_notes = notes

    # This is gonnna be inaccurate but it's better than nothing
    _, notes = list(m.data.items())[-1]
    pattern_type = get_pattern_type(prev_notes, notes, [3])  # Dummy note
    pattern_stats[pattern_type] += 1

    for pattern in pattern_stats:
        pattern_stats[pattern] /= line_count

    return sum(pattern_stats.values())


def test_calc_4k_raw_stats_sum():
    """
    A test to check if the raw stats sums are equal for all 4k maps.
    """

    all_file_names: list[str] = [
        f"./test_files/{file}"
        for file in os.listdir("./test_files")
        if file.endswith(".osu")
    ]

    ss: list[float] = []
    file_names_4k: list[str] = []

    for file_name in all_file_names:
        m = parse.parse_map(file_name)

        if m.key_count != 4:
            continue

        file_names_4k.append(file_name)
        ss.append(calc_4k_raw_stats_sum(m))

    tolerance = 0.02

    for i, s1 in enumerate(ss):
        for j in range(i, len(ss)):
            s2 = ss[j]

            assert abs(s1 - s2) < tolerance, (
                f"Raw stats sums do not match: {s1} != {s2}"
                f" for files {file_names_4k[i]} and {file_names_4k[j]}"
            )


if __name__ == "__main__":
    test_calc_4k_raw_stats_sum()
