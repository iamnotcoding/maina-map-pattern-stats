"""
This module tests functions in calc.py
"""

# pylint: disable=line-too-long

import json
import os

import parse

from calc import (
    MainaMap,
    PatternType,
    get_pattern_type,
    calc_4k_hold_note_pattern_stats,
    butify_pattern_stats,
)


def calc_4k_raw_stats_sum(m: MainaMap) -> float:
    """
    Returns the sum of the number of patterns for the test purpose.
    """
    pattern_stats = {pattern: 0.0 for pattern in PatternType}

    hold_notes_dict_cpy = m.hold_notes_dict.copy()
    hold_notes_dict_cpy.update(m.release_notes_dict)

    all_notes : dict[int,list[int]] = hold_notes_dict_cpy
    all_notes = dict(sorted(all_notes.items()))

    print(all_notes)
    prev_notes = list(all_notes.values())[0]

    prev_prev_notes = list(all_notes.values())[1]
    line_count = len(all_notes)

    for _, notes in list(all_notes.items())[2:]:
        pattern_type = get_pattern_type(prev_prev_notes, prev_notes, notes)
        pattern_stats[pattern_type] += 1

        prev_prev_notes = prev_notes

        prev_notes = notes

    # This is gonnna be inaccurate but it's better than nothing
    _, notes = list(all_notes.items())[-1]
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


def test_reform_dan():
    """
    A test to check if the dans' difficulty is appropirately calculated
    """

    all_file_names: list[str] = []

    all_file_names.append(
        "test_files/reform/Various Artists - Dan ~ REFORM ~ 1st Pack v2 (DDMythical) [~ 1st ~ (Marathon)].osu"
    )
    all_file_names.append(
        "test_files/reform/Various Artists - Dan ~ REFORM ~ 1st Pack v2 (DDMythical) [~ 2nd ~ (Marathon)].osu"
    )
    all_file_names.append(
        "test_files/reform/Various Artists - Dan ~ REFORM ~ 1st Pack v2 (DDMythical) [~ 3rd ~ (Marathon)].osu"
    )
    for i in range(4, 7):
        all_file_names.append(
            f"test_files/reform/Various Artists - Dan ~ REFORM ~ 1st Pack v2 (DDMythical) [~ {i}th ~ (Marathon)].osu"
        )

    for i in range(7, 11):
        all_file_names.append(
            f"test_files/reform/Various Artists - Dan ~ REFORM ~ 2nd Pack (DDMythical) [~ {i}th ~ (Marathon)].osu"
        )

    for c in ["ALPHA", "BETA", "GAMMA", "DELTA", "EPSILON"]:
        all_file_names.append(
            f"test_files/reform/Various Artists - Dan ~ REFORM ~ 2nd Pack (DDMythical) [~ EXTRA-{c} ~ (Marathon)].osu"
        )

    overall_ss: list[float] = []
    detailed_ss: list[dict[PatternType, float]] = []
    file_names_4k: list[str] = []

    for file_name in all_file_names:
        m = parse.parse_map(file_name)

        if m.key_count != 4:
            raise ValueError("The map is not 4k what?")

        file_names_4k.append(file_name)
        detailed_ss.append(calc_4k_hold_note_pattern_stats(m.hold_notes_dict))
        overall_ss.append(detailed_ss[-1][PatternType.OVERALL])

    for i in range(len(all_file_names) - 1):
        assert overall_ss[i] < overall_ss[i + 1], (
            f"{overall_ss[i]} ({file_names_4k[i]}) is NOT lower then {overall_ss[i + 1]} ({file_names_4k[i + 1]})\n\
        {json.dumps(butify_pattern_stats(detailed_ss[i]), indent=4)}\n\
        {json.dumps(butify_pattern_stats(detailed_ss[i + 1]), indent=4)}"
        )


def test_joker_dan():
    """
    A test to check if the dans' difficulty is appropirately calculated
    """

    all_file_names: list[str] = []

    for c in ["I", "II", "III", "IV", "V", "VI", "VII", "PHI", "CHI", "PSI"]:
        all_file_names.append(
            f"test_files/jocker/Various Artists - Chordjack Joker Dan ([Crz]Rachel&Ice V) [Joker - {c}].osu"
        )

    all_file_names.append(
        "test_files/jocker/Various Artists - Chordjack Joker Dan ([Crz]Rachel&Jhown) [Joker - OMEGA].osu"
    )

    overall_ss: list[float] = []
    detailed_ss: list[dict[PatternType, float]] = []
    file_names_4k: list[str] = []

    for file_name in all_file_names:
        m = parse.parse_map(file_name)

        if m.key_count != 4:
            raise ValueError("The map is not 4k what?")

        file_names_4k.append(file_name)
        detailed_ss.append(calc_4k_hold_note_pattern_stats(m.hold_notes_dict))
        overall_ss.append(detailed_ss[-1][PatternType.OVERALL])

    for i in range(len(all_file_names) - 1):
        assert overall_ss[i] < overall_ss[i + 1], (
            f"{overall_ss[i]} ({file_names_4k[i]}) is NOT lower then {overall_ss[i + 1]} ({file_names_4k[i + 1]})\n\
        {json.dumps(butify_pattern_stats(detailed_ss[i]), indent=4)}\n\
        {json.dumps(butify_pattern_stats(detailed_ss[i + 1]), indent=4)}"
        )

def test_malody_regular_dan():
    """
    A test to check if the dans' difficulty is appropirately calculated
    """

    all_file_names: list[str] = []

    for i in range(0, 5):
        all_file_names.append(
            f"test_files/malody/Various Artists - Malody 4K Regular Dans v3 (Part.1) (Muses) [Regular-{i}].osu"
        )

    for i in range(5, 11):
        all_file_names.append(
            f"test_files/malody/Various Artists - Malody 4K Regular Dans v3 (Part.2) (Muses) [Regular-{i}].osu"
        )

    overall_ss: list[float] = []
    detailed_ss: list[dict[PatternType, float]] = []
    file_names_4k: list[str] = []

    for file_name in all_file_names:
        m = parse.parse_map(file_name)

        if m.key_count != 4:
            raise ValueError("The map is not 4k what?")

        file_names_4k.append(file_name)
        detailed_ss.append(calc_4k_hold_note_pattern_stats(m.hold_notes_dict))
        overall_ss.append(detailed_ss[-1][PatternType.OVERALL])

    for i in range(len(all_file_names) - 1):
        assert overall_ss[i] < overall_ss[i + 1], (
            f"{overall_ss[i]} ({file_names_4k[i]}) is NOT lower then {overall_ss[i + 1]} ({file_names_4k[i + 1]})\n\
        {json.dumps(butify_pattern_stats(detailed_ss[i]), indent=4)}\n\
        {json.dumps(butify_pattern_stats(detailed_ss[i + 1]), indent=4)}"
        )


def test_malody_extra_dan():
    """
    A test to check if the dans' difficulty is appropirately calculated
    """

    all_file_names: list[str] = []

    for i in range(1, 6):
        all_file_names.append(
            f"test_files/malody/Various Artists - Malody 4K Extra Dan v3 (Pack 1) ([GS]hina) [Extra-{i} v3].osu"
        )

    for i in range(6, 10):
        all_file_names.append(
            f"test_files/malody/Various Artists - Malody 4K Extra Dan v3 (Pack 2) ([GS]hina) [Extra-{i} v3].osu"
        )

    all_file_names.append(
        "test_files/malody/Various Artists - Malody 4K Extra Dan v3 (Pack 2) ([GS]hina) [Ex-Final v3].osu"
    )

    overall_ss: list[float] = []
    detailed_ss: list[dict[PatternType, float]] = []
    file_names_4k: list[str] = []

    for file_name in all_file_names:
        m = parse.parse_map(file_name)

        if m.key_count != 4:
            raise ValueError("The map is not 4k what?")

        file_names_4k.append(file_name)
        detailed_ss.append(calc_4k_hold_note_pattern_stats(m.hold_notes_dict))
        overall_ss.append(detailed_ss[-1][PatternType.OVERALL])

    for i in range(len(all_file_names) - 1):
        assert overall_ss[i] < overall_ss[i + 1], (
            f"{overall_ss[i]} ({file_names_4k[i]}) is NOT lower then {overall_ss[i + 1]} ({file_names_4k[i + 1]})\n\
        {json.dumps(butify_pattern_stats(detailed_ss[i]), indent=4)}\n\
        {json.dumps(butify_pattern_stats(detailed_ss[i + 1]), indent=4)}"
        )


def test_tr1ple_dan():
    """
    A test to check if the dans' difficulty is appropirately calculated
    """

    all_file_names: list[str] = []

    for c in ["ALPHA", "BETA", "GAMMA"]:
        all_file_names.append(
            f"test_files/tr1ple/Various Artists - TR1PLE DAN (wonder5193) [Stage ~ {c} ~].osu"
        )

    all_file_names.append(
        "test_files/tr1ple/Various Artists - TR1PLE DAN (wonder5193) [Last Stage ~ DELTA ~].osu"
    )

    overall_ss: list[float] = []
    detailed_ss: list[dict[PatternType, float]] = []
    file_names_4k: list[str] = []

    for file_name in all_file_names:
        m = parse.parse_map(file_name)

        if m.key_count != 4:
            raise ValueError("The map is not 4k what?")

        file_names_4k.append(file_name)
        detailed_ss.append(calc_4k_hold_note_pattern_stats(m.hold_notes_dict))
        overall_ss.append(detailed_ss[-1][PatternType.OVERALL])

    for i in range(len(all_file_names) - 1):
        assert overall_ss[i] < overall_ss[i + 1], (
            f"{overall_ss[i]} ({file_names_4k[i]}) is NOT lower then {overall_ss[i + 1]} ({file_names_4k[i + 1]})\n\
        {json.dumps(butify_pattern_stats(detailed_ss[i]), indent=4)}\n\
        {json.dumps(butify_pattern_stats(detailed_ss[i + 1]), indent=4)}"
        )


def test_shoegazor_dan():
    """
    A test to check if the dans' difficulty is appropirately calculated
    """

    all_file_names: list[str] = [
        r"test_files\shoegazor\Various Artists - 4k 1st dan v2 (Yuudachi-kun) [d-1].osu",
        r"test_files\shoegazor\Various Artists - 4k 2nd dan v2 (Yuudachi-kun) [d-2].osu",
        r"test_files\shoegazor\Various Artists - 4k 3rd dan v2 (Yuudachi-kun) [d-3].osu",
        r"test_files\shoegazor\Various Artists - 4K 4th Dan (Yuudachi-kun) [Dan4].osu",
        r"test_files\shoegazor\Various Artists - 4K 5th Dan (wjh0133) [dan5].osu",
        r"test_files\shoegazor\Various Artists - 4K 6th Dan (wjh0133) [dan6].osu",
        r"test_files\shoegazor\Various Artists - 4K 7th Dan v2 (wjh0133) [dan7].osu",
        r"test_files\shoegazor\Various Artists - 4K 8th Dan v2 (wjh0133) [dan8].osu",
        r"test_files\shoegazor\Various Artists - 4K 9th Dan v2 (wjh0133) [dan9].osu",
        r"test_files\shoegazor\Various Artists - 4K 10th Dan (pikachuuuuu-) [dan10].osu",
        r"test_files\shoegazor\Various Artists - 4K Luminal v2 (Pikapikapikapi) [Luminal].osu",
        r"test_files\shoegazor\Various Artists - 4K Tachyon v3 (chicken Little) [Tachyon].osu",
    ]

    overall_ss: list[float] = []
    detailed_ss: list[dict[PatternType, float]] = []
    file_names_4k: list[str] = []

    for file_name in all_file_names:
        m = parse.parse_map(file_name)

        if m.key_count != 4:
            raise ValueError("The map is not 4k what?")

        file_names_4k.append(file_name)
        detailed_ss.append(calc_4k_hold_note_pattern_stats(m.hold_notes_dict))
        overall_ss.append(detailed_ss[-1][PatternType.OVERALL])

    for i in range(len(all_file_names) - 1):
        assert overall_ss[i] < overall_ss[i + 1], (
            f"{overall_ss[i]} ({file_names_4k[i]}) is NOT lower then {overall_ss[i + 1]} ({file_names_4k[i + 1]})\n\
        {json.dumps(butify_pattern_stats(detailed_ss[i]), indent=4)}\n\
        {json.dumps(butify_pattern_stats(detailed_ss[i + 1]), indent=4)}"
        )


if __name__ == "__main__":
    test_calc_4k_raw_stats_sum()
    test_reform_dan()
    test_joker_dan()
    test_malody_regular_dan()
    test_malody_extra_dan()  # Fails at Extra2<->Extra3. Gave up.
    test_tr1ple_dan()
    test_shoegazor_dan()
