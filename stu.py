from enum import Enum


class Student:
    def __init__(self, filename=None):
        self.filename = filename
        temp = filename.split('_')
        self.name = temp[0]
        self.nid = temp[-1]
        self.status = Status.waiting


class Status(Enum):
    # Error:
    can_not_compile = -1
    can_not_run = -2
    compile_fail = -3
    run_fail = -4
    other = -99

    # Info
    waiting = 0
    compile_success = 1
    run_success = 2
    run_current = 3
    run_not_current = 4
