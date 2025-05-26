class MainaMap:
    """notes should be sotred by time"""

    def __init__(self, key_count: int, data: dict[float, list[int]], note_count: int):
        self.key_count = key_count
        self.data = data
        self.note_count = note_count


def get_key_count(path: str) -> int:
    file = open(path, "r", encoding="utf-8")

    lines = file.readlines()

    for line in lines:
        if line.startswith("CircleSize"):
            return int(line.split(":")[1].strip())

    file.close()

    raise ValueError("Key count not found in the map file.")


def parse_map(path: str) -> MainaMap:
    """
    Long notes are treated as regular notes
    """

    tolerance = 0.1
    data: dict[float, list[int]] = {}
    key_count = get_key_count(path)

    file = open(path, "r", encoding="utf-8")

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

        if time not in data:
            data[time] = []

        data[time].append(index)

    note_count = len(lines[object_start_line:])

    return MainaMap(key_count, dict(sorted(data.items())), note_count)


if __name__ == "__main__":
    map = parse_map("example.osu")
    print(f"Key Count: {map.key_count}")
    print(f"data: {map.data}")
    print(f"Note Count: {map.note_count}")
