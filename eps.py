#!/usr/bin/env python3

from itertools import groupby
from re import sub
import sys

from cardcodes import CARD_UNICODES as CU, CARD_ASCII_CODES as CA


class EinsteinPuzzleSolver:
    def __init__(self):
        self.reset_data_structures()

    
    def reset_data_structures(self):
        self.cards = {r + c: {1, 2, 3, 4, 5, 6} for r in "ABCDEF" for c in "123456"}
        self.rows = [[self.cards[r + c] for c in "123456"] for r in "ABCDEF"]
        self.same_col_clues = []
        self.left_right_clues = []
        self.pair_clues = []
        self.triple_clues = []


    def solve(self):
        cycles = 0
        while (not self.is_solved()) and cycles < 1000:
            self.make_obvious_exclusions()
            self.apply_same_col_clues()
            self.apply_left_right_clues()
            self.apply_pair_clues()
            self.apply_triple_clues()
            cycles += 1


    def is_solved(self):
        for card in self.cards.values():
            if len(card) != 1:
                return False
        return True


    def make_obvious_exclusions(self):
        for row in self.rows:
            for size in range(1, 4):
                sets_of_same_size = [card for card in row if len(card) == size]
                equals = groupby(sorted([list(s) for s in sets_of_same_size]))
                for key, group in equals:
                    if len(list(group)) == size:
                        positions_to_exclude = set(key)
                        for card in row:
                            if card != positions_to_exclude:
                                card.difference_update(positions_to_exclude)
            # if some position occurs only once in a row
            pos_occurances = {p: [] for p in range(1, 7)}
            for c in row:
                for p in c:
                    pos_occurances[p].append(c)
            for p, cs in pos_occurances.items():
                if len(cs) == 1:
                    cs[0].intersection_update({p})


    def apply_same_col_clues(self):
        for c1, c2 in self.same_col_clues:
            c1.intersection_update(c2)
            c2.intersection_update(c1)


    def apply_left_right_clues(self):
        for l, r in self.left_right_clues:
            l.difference_update(set(range(max(r), 7)))
            r.difference_update(set(range(1, min(l) + 1)))


    def apply_pair_clues(self):
        for c1, c2 in self.pair_clues:
            c1.intersection_update({x - 1 for x in c2} | {x + 1 for x in c2})
            c2.intersection_update({x - 1 for x in c1} | {x + 1 for x in c1})


    def apply_triple_clues(self):
        for c1, c2, c3 in self.triple_clues:
            c1.intersection_update(
                ({x - 1 for x in c2} | {x + 1 for x in c2}) &
                ({x - 2 for x in c3} | {x + 2 for x in c3})
            )
            c2.intersection_update(
                ({x - 1 for x in c1} | {x + 1 for x in c1}) &
                ({x - 1 for x in c3} | {x + 1 for x in c3})
            )
            c3.intersection_update(
                ({x - 2 for x in c1} | {x + 2 for x in c1}) &
                ({x - 1 for x in c2} | {x + 1 for x in c2})
            )
            positions_to_exclude = set()
            for p in c2:
                if ((p + 1 not in c1) and (p + 1 not in c3)) or ((p - 1 not in c1) and (p - 1 not in c3)):
                    positions_to_exclude.add(p)
            c2.difference_update(positions_to_exclude)


    def parse_clue_line(self, line):
        x = line.find(":") + 1
        desc = line[0: x].strip()
        clues = line[x:].strip()
        if len(clues) == 0:
            clues = []
        else:
            clues = [c.split(",") for c in sub("r| |\(|\)", "", clues).split(";")]
        return (desc, clues)


    def load_task(self, lines):
        self.reset_data_structures()
        if lines[0] !=  "[task]" or lines[11] != "[/task]":
            raise Exception("Invalid input data")
        # set card positions for opened cards
        for line in lines[1:7]:
            line = list(line.replace(" ", ""))
            c = 0
            for u in line:
                if u == '|':
                    c += 1
                    continue
                self.cards[CA[u]].intersection_update({c})
        # add clues
        clue_lists = {
            "Same column clues:": self.same_col_clues,
            "Left-right clues:": self.left_right_clues,
            "Pair clues:": self.pair_clues,
            "Triple clues:": self.triple_clues
        }
        for line in lines[7:11]:
            desc, clues = self.parse_clue_line(line)
            clue_list = clue_lists.get(desc)
            if clue_list == None:
                raise Exception("Invalid input data")
            for clue in clues:
                clue_list.append(tuple([self.cards[CA[u]] for u in clue]))


    def dump_solution(self):
        if not self.is_solved():
            return ["[solution]", "Not solved", "[/solution]"]
        lines = ["[solution]"]
        row = []
        for code, pos in sorted(self.cards.items()):
            row.append((list(pos)[0], CU[code]))
            if code[1] == '6':
                row.sort()
                lines.append("| " + " | ".join([v for k, v in row]) + " |")
                row = []
        lines.append("[/solution]")
        return lines


if __name__ == '__main__':
    lines = sys.stdin.readlines()
    task_dump = []
    for line in lines:
        line = line.strip()
        if len(line) > 0:
            task_dump.append(line)
        if len(task_dump) == 12:
            solver = EinsteinPuzzleSolver()
            solver.load_task(task_dump)
            solver.solve()
            for l in solver.dump_solution():
                print(l)
            task_dump = []

