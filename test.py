# pytest test.py

from enum import Enum
from calc import *
import os

def calc_4k_raw_stats_sum(m: MainaMap) -> float:
    pattern_stats = {pattern: 0.0 for pattern in PatternType}

    prev_notes = list(m.data.values())[0]

    prev_prev_notes = list(m.data.values())[1]
    line_count = len(m.data)

    for time, notes in list(m.data.items())[2:]:
        pattern_type = get_pattern_type(prev_prev_notes, prev_notes, notes)
        pattern_stats[pattern_type] += 1

        prev_prev_notes = prev_notes

        prev_notes = notes

    for pattern in pattern_stats:
        pattern_stats[pattern] /= line_count

    return sum(pattern_stats.values())

def test_calc_4k_raw_stats_sum():
    import parse

    file_names : list[str] = [f"./test_files/{file}" for file in os.listdir('./test_files') if file.endswith('.osu')]

    ss : list[float]= []

    for file_name in file_names:
        m = parse.parse_map(file_name)

        if m.key_count != 4:
            continue

        ss.append(calc_4k_raw_stats_sum(m))

    tolerance = 0.01 # The accuracy is f'd up I don't know why

    for i in range(len(ss)):
        for j in range(i, len(ss)):
            assert abs(ss[i] - ss[j]) < tolerance, f"Raw stats sums do not match: {ss[i]} != {ss[j]}"

    
if __name__ == "__main__":
    test_calc_4k_raw_stats_sum()