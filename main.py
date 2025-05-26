import sys
import calc
import parse
import json


def butify_pattern_stats(
    pattern_stats: dict[calc.PatternType, float],
) -> dict[str, float]:
    result: dict[str, float] = {}

    for pattern, value in pattern_stats.items():
        result[pattern.name] = value

    return result


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python main.py <path_to_osu_file>")
        sys.exit(1)

    osu_file_path = sys.argv[1]
    map_data = parse.parse_map(osu_file_path)
    pattern_stats = calc.calc_4k_pattern_stats(map_data)
    butified_stats = butify_pattern_stats(pattern_stats)
    
    print(json.dumps(butified_stats, indent=4, ensure_ascii=False))
