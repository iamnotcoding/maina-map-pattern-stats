"""
This module parses an .osu file (osu maina) and store its data in a structured format.
"""

# pylint: disable=too-few-public-methods, line-too-long

class Note:
    '''
    Can contain either a regluar or long note
    '''
    def __init__(self, index: int, hold_time: int, release_time: int | None = None) ->None:
        self.index = index
        self.hold_time = hold_time
        self.release_time = release_time

    def is_LN(self) -> bool:
        if self.release_time is None:
            return False

        return True


class MainaMap:
    """notes should be sotred by time"""

    def __init__(
        self,
        key_count: int,
        notes: list[Note]
    ) -> None:
        self.key_count = key_count
        self.notes = notes


def get_key_count(path: str) -> int:
    """
    Returns the maina key count from an osu! map file.
    """
    with open(path, "r", encoding="utf-8") as file:
        lines = file.readlines()

        for line in lines:
            if line.startswith("CircleSize"):
                return int(line.split(":")[1].strip())

        raise ValueError("Key count not found in the map file.")


def parse_map(path: str) -> MainaMap:
    """
    Long notes are treated as regular notes
    """

    tolerance = 0.1
    hold_notes: dict[float, list[int]] = {}
    release_notes: dict[float, list[int]] = {}

    key_count = get_key_count(path)

    with open(path, "r", encoding="utf-8") as file:
        lines = file.readlines()

        object_start_line = 0

        for line in lines:
            object_start_line += 1

            if line.strip() == "[HitObjects]":
                break

        for line in lines[object_start_line:]:
            tokens = line.split(",")
            index = int(int(tokens[0]) * key_count / 512 + tolerance)
            time = int(tokens[2])

            if int(tokens[3]) == 1:
                if time not in hold_notes:
                    hold_notes[time] = []

                hold_notes[time].append(index)
            else:  # if 128
                if time not in release_notes:
                    release_notes[time] = []

                release_notes[time].append(index)

    return MainaMap(key_count, hold_notes, release_notes)


if __name__ == "__main__":
    ex_m = parse_map(
        "test_files/LN/Various Artists - 4K LN Dan Courses v2 - Level 1 - (_underjoy) [1st Dan (Marathon)].osu"
    )
    print(f"Key Count: {ex_m.key_count}")
    print(f"hold_notes: {ex_m.hold_notes}")
    print(f"release_notes: {ex_m.realse_notes}")
