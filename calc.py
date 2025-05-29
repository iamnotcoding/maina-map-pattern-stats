"""
This module contains classes and functions to calculate pattern statistics
"""
# pylint: disable=too-many-return-statements, too-many-branches

import json
from enum import Enum
import math

from parse import MainaMap, parse_map


class ChordType(Enum):
    """
    Types of chords
    """

    SINGLE = 1
    JUMP = 2  # ##xx
    BROKEN_JUMP = 3  # #x#x
    HAND = 4  # x###
    BROKEN_HAND = 5  # #x##
    QUAD = 6
    MORE_THAN_QUAD = 7  # For higher key modes than 4k


class PatternType(Enum):
    """
    Types of patterns
    """

    SINGLE_STREAM = 0
    JUMP_STREAM = 1
    HAND_STREAM = 2
    SPEED_JACK = 3
    LIGHT_CHORD_JACK = 4
    DENSE_CHORD_JACK = 5
    JUMP_TRILL = 6  # two hand single trill also falls into this category
    SPLIT_TRILL = 7  # one hand single trill also falls into this category
    OVERALL = 8
    # TODO : patterns for higher key modes than 4k


def is_consecutive(li: list[int]) -> bool:
    """
    Returns True if the elements in the list are consecutive, False otherwise.
    """
    sotred_li = sorted(li)
    return all(n - i == sotred_li[0] for i, n in enumerate(sotred_li))


def get_chord_type(note_indexes: list[int]) -> ChordType:
    """
    Returns the type of chord based on the note_indexes in it.
    """
    # TODO : add support for more than quad chords

    if len(note_indexes) == 1:
        return ChordType.SINGLE

    if len(note_indexes) == 2:
        # Since very dense single streams may contain two note_indexes
        if is_consecutive(note_indexes):
            return ChordType.JUMP

        return ChordType.BROKEN_JUMP

    if len(note_indexes) == 3:
        if is_consecutive(note_indexes):
            return ChordType.HAND

        return ChordType.BROKEN_HAND
    if len(note_indexes) == 4:
        return ChordType.QUAD

    return ChordType.MORE_THAN_QUAD


def is_chord_overrlap(note_indexes1: list[int], note_indexes2: list[int]) -> bool:
    """
    Returns True if at least one of note from note_indexes1, note_indexes2 overlaps, False otherwise.
    """
    for note1 in note_indexes1:
        if note1 in note_indexes2:
            return True

    return False


# Parameters' names are stupid, I know
def get_pattern_type(
    note_indexes1: list[int], note_indexes2: list[int], note_indexes3: list[int]
) -> PatternType:
    """
    Parm : a LIST of note objects
    Returns the pattern type
    """

    # TODO : add support for key modes higher than 4k

    higher_chord = (
        note_indexes1 if len(note_indexes1) > len(note_indexes2) else note_indexes2
    )
    lower_chord = (
        note_indexes1 if len(note_indexes1) <= len(note_indexes2) else note_indexes2
    )

    if get_chord_type(higher_chord) == ChordType.SINGLE:
        if is_chord_overrlap(higher_chord, lower_chord):
            return PatternType.SPEED_JACK

        if note_indexes1 == note_indexes3 and get_chord_type(note_indexes3) == ChordType.SINGLE:
            if note_indexes2[0] == 1 or note_indexes2[0] == 2:
                return PatternType.JUMP_TRILL

            return PatternType.SPLIT_TRILL

        return PatternType.SINGLE_STREAM

    if get_chord_type(higher_chord) == ChordType.JUMP:
        if is_chord_overrlap(higher_chord, lower_chord):
            if get_chord_type(lower_chord) == ChordType.SINGLE:
                return PatternType.SPEED_JACK

            return PatternType.LIGHT_CHORD_JACK

        #if get_chord_type(lower_chord) == ChordType.JUMP and note_indexes1 == note_indexes3:
        if note_indexes1 == note_indexes3:
            return PatternType.JUMP_TRILL

        return PatternType.JUMP_STREAM

    if get_chord_type(higher_chord) == ChordType.BROKEN_JUMP:
        if is_chord_overrlap(higher_chord, lower_chord):
            if get_chord_type(lower_chord) == ChordType.SINGLE:
                return PatternType.SPEED_JACK

            return PatternType.LIGHT_CHORD_JACK

        if higher_chord == note_indexes1:
            if get_chord_type(
                note_indexes3
            ) == ChordType.SINGLE and not is_chord_overrlap(note_indexes3, lower_chord):
                return PatternType.SINGLE_STREAM

        if higher_chord == note_indexes2:
            if get_chord_type(
                note_indexes3
            ) == ChordType.SINGLE and not is_chord_overrlap(
                note_indexes3, higher_chord
            ):
                return PatternType.SINGLE_STREAM

        if note_indexes1 == note_indexes3:
            return PatternType.SPLIT_TRILL

        return PatternType.JUMP_STREAM

    if (
        get_chord_type(higher_chord) == ChordType.HAND
        or get_chord_type(higher_chord) == ChordType.BROKEN_HAND
    ):
        if is_chord_overrlap(higher_chord, lower_chord):
            if get_chord_type(lower_chord) != ChordType.SINGLE:
                return PatternType.DENSE_CHORD_JACK

            return PatternType.SPEED_JACK

        # I know this has to be written the same as hand for consistency,
        # but this just doesn't work
        # if note_indexes1 == note_indexes3:
        # return PatternType.SPLIT_TRILL

        return PatternType.HAND_STREAM

    if get_chord_type(higher_chord) == ChordType.QUAD:
        if get_chord_type(lower_chord) == ChordType.JUMP and (
            sorted(lower_chord) == [0, 1] or sorted(lower_chord) == [2, 3]
        ):
            return PatternType.SPEED_JACK

        return PatternType.DENSE_CHORD_JACK

    raise ValueError(
        "Pattern type not supported for more than quad chords.\n"
        "This function is designed for 4k maps only."
    )


def get_point_from_hold_note_time_diff(time_diff: float) -> float:
    """
    A value which will be added to the pattern stat
    """

    # THIS IS JUST STUPID
    return (1000 / time_diff) ** 1.369999

    # return 1000 / time_diff * 10
    # return 1.1 / (1 + math.exp(-10 * (time_diff / lowest_time_diff - 0.88)))


def get_hold_note_lowest_time_diff(hold_notes: dict[float, list[int]]) -> float:
    """
    Get the time lowest time difference
    """
    times = list(hold_notes.keys())

    result = times[1] - times[0]

    for i in range(2, len(times)):
        result = min(result, times[i] - times[i - 1])

    return result


def get_closest_release_time(
    hold_time: float, hold_note_index: int, release_notes: dict[float, list[int]]
) -> float | None:
    for release_time, note_objs in release_notes.items():
        if release_time > hold_time and hold_note_index in note_objs:
            return release_time

    return None


# TODO : add support for higher key modes than 4k in a separate function
def calc_4k_hold_note_pattern_stats(
    hold_notes_dict: dict[int, list[int]],
) -> dict[PatternType, float]:
    """
    Calculates pattern stats for a 4k map.
    """
    pattern_stats = {pattern: 0.0 for pattern in PatternType}
    pattern_weights: dict[PatternType, float] = {
        PatternType.SINGLE_STREAM: 0.91, #x
        PatternType.JUMP_STREAM: 1.7, #x
        # lower then split trill since it may not be a trill.
        PatternType.HAND_STREAM: 4.3, #x
        PatternType.SPEED_JACK: 2.5, #x
        PatternType.LIGHT_CHORD_JACK: 2.9, #x
        PatternType.DENSE_CHORD_JACK: 5.298, #x
        PatternType.JUMP_TRILL: 2.81,  # x
        PatternType.SPLIT_TRILL: 5.692, #x
    }

    prev_notes = list(hold_notes_dict.values())[0]
    prev_time = list(hold_notes_dict.keys())[0]

    prev_prev_notes = list(hold_notes_dict.values())[1]

    line_count = len(hold_notes_dict)

    for time, notes in list(hold_notes_dict.items())[2:]:
        pattern_type = get_pattern_type(prev_prev_notes, prev_notes, notes)
        pattern_stats[pattern_type] += get_point_from_hold_note_time_diff(
            time - prev_time
        )

        prev_prev_notes = prev_notes

        prev_notes = notes
        prev_time = time

    # This is gonnna be inaccurate but it's better than nothing
    time, notes = list(hold_notes_dict.items())[-1]
    prev_time = list(hold_notes_dict.keys())[-2]

    pattern_type = get_pattern_type(prev_notes, notes, [3])  # Dummy note
    pattern_stats[pattern_type] += get_point_from_hold_note_time_diff(time - prev_time)

    for pattern in pattern_stats:
        if pattern == PatternType.OVERALL:
            continue

        pattern_stats[pattern] *= pattern_weights[pattern]
        pattern_stats[pattern] /= line_count

    pattern_stats[PatternType.OVERALL] = sum(pattern_stats.values())

    return pattern_stats


def logistic(
    x: float, midpointOffset: float, multiplier: float, maxValue: float = 1
) -> float:
    return maxValue / (1 + math.exp(multiplier * (midpointOffset - x)))


# TODO : add support for higher key modes than 4k in a separate function
def calc_4k_release_note_pattern_stats(
    hold_notes: dict[float, list[int]], release_notes: dict[float, list[int]]
) -> dict[PatternType, float]:
    """
    Basically uses the same algorithm that osu!lazor does
    """
    pattern_stats = {pattern: 0.0 for pattern in PatternType}
    pattern_weights: dict[PatternType, float] = {
        PatternType.SINGLE_STREAM: 0.91,
        PatternType.JUMP_STREAM: 1.92,
        # lower then split trill since it may not be a trill.
        PatternType.HAND_STREAM: 4.2,
        PatternType.SPEED_JACK: 2.2,
        PatternType.LIGHT_CHORD_JACK: 2.8,
        PatternType.DENSE_CHORD_JACK: 5.3,
        PatternType.JUMP_TRILL: 2.7,
        PatternType.SPLIT_TRILL: 6,
    }

    prev_notes = list(release_notes.values())[0]
    prev_time = list(release_notes.keys())[0]

    prev_prev_notes = list(release_notes.values())[1]

    line_count = len(release_notes)

    for time, notes in list(release_notes.items())[2:]:
        pattern_type = get_pattern_type(prev_prev_notes, prev_notes, notes)
        pattern_stats[pattern_type] += get_point_from_hold_note_time_diff(
            time - prev_time
        )

        prev_prev_notes = prev_notes

        prev_notes = notes
        prev_time = time

    # This is gonnna be inaccurate but it's better than nothing
    time, notes = list(release_notes.items())[-1]
    prev_time = list(release_notes.keys())[-2]

    pattern_type = get_pattern_type(prev_notes, notes, [3])  # Dummy note
    pattern_stats[pattern_type] += get_point_from_hold_note_time_diff(time - prev_time)

    for pattern in pattern_stats:
        if pattern == PatternType.OVERALL:
            continue

        pattern_stats[pattern] *= pattern_weights[pattern]
        pattern_stats[pattern] /= line_count

    pattern_stats[PatternType.OVERALL] = sum(pattern_stats.values())

    return pattern_stats


def butify_pattern_stats(
    pattern_stats: dict[PatternType, float],
) -> dict[str, float]:
    """
    Replaces the enum itself with its name
    """
    result: dict[str, float] = {}

    for pattern, value in pattern_stats.items():
        result[pattern.name] = value

    return result


def from_file(file_path: str) -> dict[str, float]:
    """
    Reads a osu! map file and returns the pattern stats in a butified format.
    """
    m = parse_map(file_path)
    pattern_stats = calc_4k_hold_note_pattern_stats(m.hold_notes_dict)
    butified_stats = butify_pattern_stats(pattern_stats)
    return butified_stats


if __name__ == "__main__":
    print(json.dumps(from_file("test_files/delay.osu"), indent=4))
    print(get_chord_type([3, 4, 1]))
