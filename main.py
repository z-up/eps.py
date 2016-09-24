#!/usr/bin/env python3

from eps import EinsteinPuzzleSolver
from pcoperator import PCOperator


if __name__ == '__main__':
    solver = EinsteinPuzzleSolver()
    operator = PCOperator()

    operator.launch_app()

    number_of_games = 10
    for i in range(number_of_games):
        operator.start_new_game()
        task = operator.dump_task()
        # for l in task: print(l)
        solver.load_task(task)
        solver.solve()
        if solver.is_solved():
            operator.apply_solution(solver.dump_solution(), i == number_of_games - 1)
        else:
            print("Could not solve the puzzle")
            break


    # task = operator.dump_task()
    # # for l in task: print(l)
    # solver.load_task(task)
    # solver.solve()
    # if solver.is_solved():
    #     operator.apply_solution(solver.dump_solution())
    # else:
    #     print("Could not solve the puzzle")


