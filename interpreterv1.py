from intbase import *
from bparser import *
from class_def import *
from object_def import *
from items import *

# TODO change to using InterpreterBase Constants


class Interpreter(InterpreterBase):
    def __init__(self, console_output=True, inp=None, trace_output=False):
        super().__init__(console_output, inp)
        self.classes = dict()
        self.objects = dict()

    def run(self, program):
        # Parse program with given BParser
        result, parsed_program = BParser.parse(program)
        print(parsed_program)

        # Error case
        if result == False:
            return

        self.__parse_all_classes(parsed_program)

        # Instantiate main
        main_obj = self.create_object("main")

        # Run main method
        main_obj.call_method("main", [], "me", self)

    def __parse_all_classes(self, parsed_program):
        # Create class structure of program
        for class_def in parsed_program:
            # Check for duplicate class name
            class_name = class_def[1]
            if class_name in self.classes:
                super().error(ErrorType.TYPE_ERROR, "Duplicate class name: {}".format(
                    class_name))

            # Create class definition
            self.classes[class_name] = ClassDefinition(class_name)

            # Parse class items
            for item in class_def:
                if item[0] == "field":
                    self.classes[class_name].add_field(item, super().error)
                elif item[0] == "method":
                    self.classes[class_name].add_method(item, super().error)

    def create_object(self, class_name):
        if class_name not in self.classes:
            super().error(ErrorType.TYPE_ERROR, "")

        obj_class = self.classes[class_name]
        object = obj_class.instantiate_object()
        self.objects[object.obj_name] = object
        return object