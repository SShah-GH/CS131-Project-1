from intbase import *
from object_def import *
from items import *


class ClassDefinition:
    # ClassDefinition constructor
    def __init__(self, class_name):
        self.class_name = class_name
        self.fields = dict()
        self.methods = dict()

    def add_field(self, field, error_handler):
        # Check for duplicate field name
        field_name = field[1]
        if field_name in self.fields:
            error_handler(ErrorType.NAME_ERROR, "Duplicate field name: {}".format(
                field_name))

        self.fields[field_name] = Field(field_name, field[2])

    def add_method(self, method, error_handler):
        # Check for duplicate method name
        method_name = method[1]
        if method_name in self.methods:
            error_handler(ErrorType.NAME_ERROR, "Duplicate field name: {}".format(
                method_name))

        self.methods[method_name] = Method(method_name, method[2], method[3])

    def __str__(self):
        return "Class Name: {}\n Fields: {}\n Methods: {}".format(self.class_name, self.fields, self.methods)

    def instantiate_object(self):
        obj = ObjectDefinition()

        # Create field copy (since objects can change values)
        for field_name, field in self.fields.items():
            obj.add_field(field.field_name, field.value)

        # Use class method
        for method_name, method in self.methods.items():
            obj.add_method(method)

        return obj
