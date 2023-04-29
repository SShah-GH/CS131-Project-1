from intbase import *
from items import *


class ObjectDefinition:
    # ObjectDefinition constructor
    def __init__(self, obj_name="main"):
        self.obj_name = obj_name
        self.obj_fields = dict()
        self.obj_methods = dict()

    def add_field(self, field_name, field_value):
        self.obj_fields[field_name] = Field(field_name, field_value)

    def add_method(self, method):
        self.obj_methods[method.method_name] = method

    # Process method call
    def call_method(self, method_name, parameters, error_handler):
        # TODO: check that method exists
        if method_name not in self.obj_methods:
            error_handler(ErrorType.NAME_ERROR, "")

        # TODO: check that correct parameters are used (number/type)

        # TODO: call __run_expression with the expression, parameter vals, error_handler

        print(self.obj_methods[method_name])

    def __str__(self):
        return "Object Name: {}\n Fields: {}\n Methods: {}".format(self.obj_name, self.obj_fields, self.obj_methods)


'''
  # Interpret the specified method using the provided parameters    
  def call_method(self, method_name, parameters):
    method = self.__find_method(method_name)
    statement = method.get_top_level_statement()
    result = self.__run_statement(statement)
    return result

  # runs/interprets the passed-in statement until completion and 
  # gets the result, if any
  def __run_statement(self, statement):
   if is_a_print_statement(statement):
     result = self.__execute_print_statement(statement)
   elif is_an_input_statement(statement):
     result = self.__execute_input_statement(statement)
   elif is_a_call_statement(statement):
     result = self.__execute_call_statement(statement)
   elif is_a_while_statement(statement):
     result = self.__execute_while_statement(statement)
   elif is_an_if_statement(statement):
     result = self.__execute_if_statement(statement)
   elif is_a_return_statement(statement):
     result = self.__execute_return_statement(statement)
   elif is_a_begin_statement(statement):
     result = self.__execute_all_sub_statements_of_begin_statement(statement) 
   …
   return result
'''
