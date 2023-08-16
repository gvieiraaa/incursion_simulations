import itertools
import random
import pandas as pd
from enum import IntEnum
from dataclasses import dataclass


class Name(IntEnum):
    locus = 0
    nexus = 1
    doryani = 2


class Side(IntEnum):
    left = 0
    right = 1


@dataclass
class Rules:
    mechanic: int
    incursions_per_map: int
    skip_after_locus: bool
    skip_after_doryani: bool
    skip_after_nexus: bool
    skip_last_if_0: bool
    switch_if_lvl0: bool

    def __repr__(self):
        return (
            f"Rules(m={mechanic}, "
            f"inc_per_map={self.incursions_per_map}, "
            f"skip_after[l={self.skip_after_locus!s:^5}, "
            f"d={self.skip_after_doryani!s:^5}, "
            f"n={self.skip_after_nexus!s:^5}], "
            f"skip last if lvl0={self.skip_last_if_0!s:^5}, "
            f"switch_if_lvl0={self.switch_if_lvl0}!s:^5)"
    )


class Room:
    __slots__ = ("number", "left", "right", "level")

    def __init__(self, *, number: int, left: int, right: int, level: int) -> None:
        self.number = number
        self.left = left
        self.right = right
        self.level = level

    def is_complete(self) -> bool:
        return self.level == 3

    def compare(self, side: Side, name: Name) -> bool:
        if side == Side.right:
            return self.right == name
        else:
            return self.left == name

    def is_nexus3(self) -> bool:
        return self.left == Name.nexus and self.level == 3

    def evolve_replace(self, side: Side, new: int = -1):
        if side == Side.left:
            self.left, self.right = self.right, new
            self.level = min(3, self.level + 1)
        else:
            self.level = min(3, self.level + random.randint(1, 2))

    def add_lvl(self):
        self.level = min(3, self.level + 1)


class Temple:
    __slots__ = (
        "rules",
        "locus_was_seen",
        "deck",
        "exclusion_list",
        "rooms",
        "connections",
        "next_room",
        "map",
    )

    def __init__(self, rules: Rules) -> None:
        self.rules = rules
        self.locus_was_seen = False
        self.deck = set(range(25))
        self.exclusion_list: set[int] = set()
        self.rooms: list[Room] = list()
        self.connections = {
            0: [1, 2, 3],
            1: [0, 3, 4],
            2: [0, 3, 5, 6],
            3: [0, 1, 2, 4, 6, 7],
            4: [1, 3, 7, 8],
            5: [2, 6, 9],
            6: [2, 3, 5, 7, 9],
            7: [3, 4, 6, 8, 10],
            8: [4, 7, 10],
            9: [5, 6],
            10: [7, 8],
        }

    def get_valid_room(self) -> int:
        valids = {
            room.number for room in self.rooms if not room.is_complete()
        } - self.exclusion_list
        return random.choice(tuple(valids))

    def populate(self) -> None:
        for number in range(11):
            left = random.choice(tuple(self.deck))
            self.deck.remove(left)
            right = random.choice(tuple(self.deck))
            level = random.randint(0, 1)
            self.deck.remove(right)
            self.rooms.append(
                Room(
                    number=number,
                    left=left,
                    right=right,
                    level=level,
                )
            )
            if left == Name.locus and level == 1:
                self.locus_was_seen = True

    def get_result(self) -> tuple[bool, bool, int]:
        locus, doryani = False, False
        for room in self.rooms:
            if room.level != 3:
                continue
            if room.left == Name.locus:
                locus = True
            if room.left == Name.doryani:
                doryani = True
        return locus, doryani, self.map

    def kill(self, side: Side, current_room: Room):
        if side == Side.left:
            new = random.choice(list(self.deck))
            self.deck.remove(new)
            self.deck.add(current_room.right)
            current_room.evolve_replace(Side.left, new)
        else:
            current_room.evolve_replace(Side.right)

    def run(self) -> None:
        # populate rooms
        self.populate()
        self.map = 1
        current_incursion = 0
        force_next_map = False
        next_room = random.randint(0, 10)
        for _ in range(12):
            if force_next_map and current_incursion != self.rules.incursions_per_map:
                current_incursion = 0
                self.map += 1
                self.exclusion_list.clear()
                self.exclusion_list.add(current_room)  # type: ignore

            if current_incursion == self.rules.incursions_per_map:
                self.map += 1
                current_incursion = 0
                self.exclusion_list.clear()
                if self.rules.mechanic == 1:
                    self.exclusion_list.add(current_room)  # type: ignore

            try:  # This exists because of a 1 in 48,828,125 chance situation ¯\_(ツ)_/¯
                next_room = self.get_valid_room()
            except:
                break

            current_room = self.rooms[next_room]
            current_incursion += 1
            force_next_map = False

            if current_room.compare(Side.left, Name.locus):
                self.locus_was_seen = True
                self.kill(Side.right, current_room)
                if self.rules.skip_after_locus and current_room.level < 3:
                    force_next_map = True

            elif current_room.compare(Side.right, Name.locus):
                self.locus_was_seen = True
                self.kill(Side.left, current_room)
                if self.rules.skip_after_locus and current_room.level < 3:
                    force_next_map = True

            elif (
                current_room.compare(Side.left, Name.nexus)
                and self.locus_was_seen
                and any(
                    self.rooms[room_number].compare(Side.left, Name.locus)
                    for room_number in self.connections[current_room.number]
                )
            ):
                self.kill(Side.right, current_room)
                if self.rules.skip_after_nexus and current_room.level < 3:
                    force_next_map = True

            elif (
                current_room.compare(Side.right, Name.nexus)
                and self.locus_was_seen
                and any(
                    self.rooms[room_number].compare(Side.left, Name.locus)
                    for room_number in self.connections[current_room.number]
                )
            ):
                self.kill(Side.left, current_room)
                if self.rules.skip_after_nexus and current_room.level < 3:
                    force_next_map = True

            elif current_room.compare(Side.left, Name.doryani):
                self.kill(Side.right, current_room)
                if self.rules.skip_after_doryani and current_room.level < 3:
                    force_next_map = True

            elif current_room.compare(Side.right, Name.doryani):
                self.kill(Side.left, current_room)
                if self.rules.skip_after_doryani and current_room.level < 3:
                    force_next_map = True

            elif (
                self.rules.skip_last_if_0
                and current_incursion == self.rules.incursions_per_map
            ):
                force_next_map = True

            elif self.locus_was_seen:
                self.kill(Side.right, current_room)

            else:
                if self.rules.switch_if_lvl0 and current_room.level == 0:
                    self.kill(Side.left, current_room)
                else:
                    self.kill(Side.right, current_room)

            self.exclusion_list.add(current_room.number)

        # add from nexus
        for room in self.rooms:
            if room.is_nexus3():
                for i in self.connections[room.number]:
                    self.rooms[i].add_lvl()
                return


def run_temples(runs: int, mechanic: int):
    bools = (True, False)
    values = [(3, 4), *[bools] * 5]
    data = list()
    for (
        incursions_per_map,
        skip_after_locus,
        skip_after_doryani,
        skip_after_nexus,
        skip_last_if_0,
        switch_if_lvl0,
    ) in itertools.product(*values):
        (
            total_locus,
            total_doryani,
            total_both,
            total_any,
            only_locus,
            only_doryani,
            maps,
        ) = (0, 0, 0, 0, 0, 0, 0)
        rules = Rules(
            mechanic=mechanic,
            incursions_per_map=incursions_per_map,
            skip_after_locus=skip_after_locus,
            skip_after_doryani=skip_after_doryani,
            skip_after_nexus=skip_after_nexus,
            skip_last_if_0=skip_last_if_0,
            switch_if_lvl0=switch_if_lvl0,
        )
        for _ in range(runs):
            temple = Temple(rules)
            temple.run()
            l, d, m = temple.get_result()
            total_locus += l
            total_doryani += d
            if l and d:
                total_both += 1
            if l or d:
                total_any += 1
            if l and not d:
                only_locus += 1
            if not l and d:
                only_doryani += 1
            maps += m

        rules_summary = [
            mechanic,
            incursions_per_map,
            skip_after_locus,
            skip_after_doryani,
            skip_after_nexus,
            skip_last_if_0,
            switch_if_lvl0,
        ]
        results = [
            total_locus,
            total_doryani,
            total_both,
            only_locus,
            only_doryani,
            total_any,
            maps,
        ]
        data.append(rules_summary + results)
        show(rules_summary, results, runs) # type: ignore
    return data


def show(rules: dict, results: dict, runs: int):
    print(
        f"{rules}\n"
        f"Locus:{100*results[0]/runs:05.02f}% / "
        f"Doryani: {100*results[1]/runs:05.02f}% / "
        f"Both: {100*results[2]/runs:05.02f}% / "
        f"Only Locus: {100*results[3]/runs:05.02f}% / "
        f"Only Doryani: {100*results[4]/runs:05.02f}% / "
        f"Any: {100*results[5]/runs:05.02f}% / "
        f"Avg maps: {results[6]/runs:.2f}"
    )

def save(data: dict, mechanic: int):
    columns = [
        [
            "mechanic",
            "incursions_per_map",
            "skip_after_locus",
            "skip_after_doryani",
            "skip_after_nexus",
            "skip_last_if_0",
            "switch_if_lvl0",
            "total_locus",
            "total_doryani",
            "total_both",
            "only_locus",
            "only_doryani",
            "total_any",
            "maps",
        ]
    ]
    df = pd.DataFrame(data, columns=columns)
    df.to_csv(f"alva_simulation_mechanic_{mechanic}.csv", index=False)

if __name__ == "__main__":
    TOTAL_RUNS = 1_000_000
    # Mechanic 1 = decides next room on demand, excluding current map - means the last incursion and first next incursion can be the same room
    # Mechanic 2 = decides next room when you finish an incursion - means the last incursion and first next incursion can't be the same room
    for mechanic in (1, 2):
        print(f"{mechanic=}")
        data = run_temples(TOTAL_RUNS, mechanic)
        save(data, mechanic) # type: ignore
