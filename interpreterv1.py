from intbase import *
from bparser import *


class Interpreter(InterpreterBase):
    def __init__(self, console_output=True, inp=None, trace_output=False):
        super().__init__(console_output, inp)

    def run(self, program):
        # Parse program with given BParser
        result, parsed_program = BParser.parse(program)

        # Error case
        if result == False:
            return
