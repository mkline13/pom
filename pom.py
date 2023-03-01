#! python3
import time
from time import sleep, monotonic
from subprocess import Popen
from os.path import join, dirname
from sys import argv, exit


class Beeper:
    def __init__(self, audio_file_abs_path):
        self._audio_file_abs_path = audio_file_abs_path
        self._proc = None

    def play(self):
        if self._proc is None:
            self._proc = Popen(["afplay", self._audio_file_abs_path])

    def stop(self):
        if self._proc:
            self._proc.terminate()
            self._proc = None


class Session:
    def __init__(self, work_interval, rest_interval):
        self._work_interval = work_interval
        self._rest_interval = rest_interval
        self._current_interval = 1

    def interval_count(self):
        # returns the number of completed work intervals
        return self._current_interval // 2

    def increment_interval_count(self):
        self._current_interval += 1

    def current_interval_type(self):
        # rest = 1, work = 0
        return self._current_interval % 2

    @property
    def work_interval(self):
        return self._work_interval
    
    @property
    def rest_interval(self):
        return self._rest_interval


def do_interval(minutes):
    interval_start_time_sec = time.monotonic()
    elapsed_min = 0.0
    minutes = float(minutes)

    while elapsed_min < minutes:
        percentage = round(elapsed_min / minutes * 100)
        print(f"\t[{str(percentage).rjust(3)}%]\t{round(elapsed_min, 2)} of {round(minutes, 2)} minutes")
        sleep(30)
        elapsed_min = (monotonic() - interval_start_time_sec) / 60


def main(session):
    audio_file_path = join(dirname(argv[0]), "alarm.wav")
    beeper = Beeper(audio_file_path)

    while True:
        if session.current_interval_type() == 1:
            _ = input(f"Start work interval for {session.work_interval}m? [press enter] ")
            interval_duration = session.work_interval
        else:
            _ = input(f"Start rest interval for {session.rest_interval}m?  [press enter] ")
            interval_duration = session.rest_interval

        # count the current interval

        # start next interval
        do_interval(interval_duration)
        session.increment_interval_count()

        # on interval finish
        print("\tInterval complete!")
        beeper.play()
        _ = input("continue [press enter] ")
        beeper.stop()


def usage():
    print(f"usage: `pom <work_interval_minutes> <rest_interval_minutes>`")


if __name__ == '__main__':
    print("=== Pomodoro Timer [ctrl-C to quit] ===")

    if len(argv) != 3:
        print("Error: wrong number of arguments.")
        usage()
        exit(1)

    try:
        work, rest = int(argv[1]), int(argv[2])
        print(f"\tWorking: {work} minute(s)")
        print(f"\tResting: {rest} minute(s)")
        s = Session(work, rest)

        # start main program loop, handle ctrl-C
        try:
            main(s)
        except KeyboardInterrupt:
            print(f"\nPomodoro session complete. ({s.interval_count()} work interval(s) completed)")
            exit(0)

    except ValueError:
        print("Error: invalid arguments.")
        usage()
        exit(1)
