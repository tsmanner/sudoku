import curses
import curse
import threading
import subprocess as sp
import sys
import time


class Job(threading.Thread):
    def __init__(self, job_command, board, complete_function, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.proc = None
        self.job_command = job_command
        self.board = board
        self.complete_function = complete_function


    def run(self):
        self.proc = sp.run(" ".join(self.job_command), stdout=sp.PIPE, stderr=sp.STDOUT, shell=True)
        self.complete_function(self.board)


def board_quit(board):
    board.quit()


def board_message(board, message):
    board.default_message = message
    board.message(message)


def main(screen, job_command, complete_function):
    board = curse.CursesBoard(screen, autostart=False)
    print(board)
    job = Job(job_command, board, complete_function)
    job.start()
    board.mainloop()
    return job


if __name__ == "__main__":
    args = sys.argv[1:]
    comp_func = board_quit
    while True:
        if args[0] == "--wait":
            comp_func = lambda b: board_message(b, "Your Job Has Completed!")
            args.pop(0)
        else:
            break
    job = curses.wrapper(main, args, comp_func)
    while job.is_alive():
        time.sleep(1)
    print(job.proc.stdout.decode(), end="")
