from enum import Enum
from parse import MainaMap
import itertools
import math


class ChordType(Enum):
    SINGLE = 1
    JUMP = 2  # ##xx
    BROKEN_JUMP = 3  # #x#x
    HAND = 4  # x###
    BROKEN_HAND = 5  # #x##
    QUAD = 6
    MORE_THAN_QUAD = 7  # For higher key modes than 4k


class PatternType(Enum):
    SINGLE_STREAM = 0
    JUMP_STREAM = 1
    HAND_STREAM = 2
    JACK = 3
    TRILL = 4  # Single note trill is not supported yet


def is_consecutive(l: list[int]) -> bool:
    return all(n - i == l[0] for i, n in enumerate(l))


def get_chord_type(notes: list[int]) -> ChordType:
    if len(notes) == 1:
        return ChordType.SINGLE
    elif len(notes) == 2:
        # Since very dense single streams may contain two notes
        if is_consecutive(notes):
            return ChordType.JUMP
        else:
            return ChordType.BROKEN_JUMP
    elif len(notes) == 3:
        sorted_notes = sorted(notes)

        if is_consecutive(sorted_notes):
            return ChordType.HAND
        else:
            return ChordType.BROKEN_HAND
    elif len(notes) == 4:
        return ChordType.QUAD
    else:
        return ChordType.MORE_THAN_QUAD


def is_chord_overrlap(notes1: list[int], notes2: list[int]) -> bool:
    for note1 in notes1:
        if note1 in notes2:
            return True

    return False


def get_pattern_type(
    notes1: list[int], notes2: list[int], notes3: list[int]
) -> PatternType:
    higher_chord = notes1 if len(notes1) > len(notes2) else notes2
    lower_chord = notes1 if len(notes1) <= len(notes2) else notes2

    if get_chord_type(higher_chord) == ChordType.SINGLE:
        if is_chord_overrlap(higher_chord, lower_chord):
            return PatternType.JACK
        else:
            return PatternType.SINGLE_STREAM
    elif get_chord_type(higher_chord) == ChordType.JUMP:
        if is_chord_overrlap(higher_chord, lower_chord):
            return PatternType.JACK
        else:
            if get_chord_type(lower_chord) == ChordType.JUMP:
                return PatternType.TRILL
            else:
                return PatternType.JUMP_STREAM
    elif get_chord_type(higher_chord) == ChordType.BROKEN_JUMP:
        if is_chord_overrlap(higher_chord, lower_chord):
            return PatternType.JACK
        else:
            if higher_chord == notes1:
                if get_chord_type(notes3) == ChordType.SINGLE and not is_chord_overrlap(
                    notes3, lower_chord
                ):
                    return PatternType.SINGLE_STREAM
            elif higher_chord == notes2:
                if get_chord_type(notes3) == ChordType.SINGLE and not is_chord_overrlap(
                    notes3, higher_chord
                ):
                    return PatternType.SINGLE_STREAM

            return PatternType.JUMP_STREAM
    elif (
        get_chord_type(higher_chord) == ChordType.HAND
        or get_chord_type(higher_chord) == ChordType.BROKEN_HAND
    ):
        if is_chord_overrlap(higher_chord, lower_chord):
            return PatternType.JACK
        else:
            return PatternType.HAND_STREAM
    elif get_chord_type(higher_chord) == ChordType.QUAD:
        return PatternType.JACK
    else:
        raise ValueError(
            "Pattern type not supported for more than quad chords.\n"
            "This function is designed for 4k maps only."
        )


def calc_4k_pattern_stats(m: MainaMap) -> dict[PatternType, float]:
    pattern_stats = {pattern: 0.0 for pattern in PatternType}
    pattern_weights = {
        PatternType.SINGLE_STREAM: 1.0,
        PatternType.JUMP_STREAM: 1.1,
        PatternType.HAND_STREAM: 1.2,
        PatternType.JACK: 1.0,
        PatternType.TRILL: 1.0,
    }
    multiplier = 100000

    prev_notes = list(m.data.values())[0]
    prev_time = list(m.data.keys())[0]

    prev_prev_notes = list(m.data.values())[1]

    for time, notes in list(m.data.items())[2:]:
        pattern_type = get_pattern_type(prev_prev_notes, prev_notes, notes)
        pattern_stats[pattern_type] += 1 / ((time - prev_time) ** 2)

        prev_prev_notes = prev_notes

        prev_notes = notes
        prev_time = time

    for pattern in pattern_stats:
        pattern_stats[pattern] *= pattern_weights[pattern]
        pattern_stats[pattern] /= m.note_count
        pattern_stats[pattern] *= multiplier

    return pattern_stats


if __name__ == "__main__":
    import parse

    print(get_chord_type([0, 2, 3]))
    m = parse.parse_map("example.osu")
    print(f"pattern stats: {calc_4k_pattern_stats(m)}")
