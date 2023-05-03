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
    def call_method(self, method_name, parameters, objects, object_name, error_handler=None, input_handler=None, output_handler=None, object_handler=None):
        if object_name == "me":
            object = self
        elif object_name in objects:
            object = objects[object_name]
        else:
            error_handler(ErrorType.FAULT_ERROR, "Object does not exist: {}".format(
                object_name))

        # Check that method exists
        if method_name not in object.obj_methods:
            error_handler(ErrorType.NAME_ERROR, "Method does not exist: {}".format(
                method_name))

        # Check that correct number of parameters are given
        cur_method = object.obj_methods[method_name]
        if len(parameters) != len(cur_method.parameters):
            error_handler(ErrorType.TYPE_ERROR, "Incorrect number of parameters to: {}".format(
                method_name))

        # Create parameter dict
        parameter_vals = dict()
        for index, parameter in enumerate(cur_method.parameters):
            parameter_vals[parameter] = parameters[index]

        # Execute statement with the given parameters
        return object.__run_statement(cur_method.statement, parameter_vals, objects, error_handler, input_handler, output_handler, object_handler)

    def __run_statement(self, statement, parameter_vals, objects, error_handler=None, input_handler=None, output_handler=None, object_handler=None):
        # Check if statement is a value
        if not isinstance(statement, list):
            return self.__get_value(statement, parameter_vals)

        # Execute statements
        if statement[0] == "print":
            output = ""
            for item in statement[1:]:
                cur_output = str(self.__run_statement(
                    item, parameter_vals, objects, error_handler, input_handler, output_handler, object_handler))

                # Remove quotes if needed
                if cur_output[0] == '"' and cur_output[-1] == '"':
                    cur_output = cur_output[1:-1]

                output += cur_output
            output_handler(output)
        # TODO: check if different handling needed for int vs string
        elif statement[0] == "inputi" or statement[0] == "inputs":
            self.__set_value(
                statement[1], input_handler(), parameter_vals, error_handler)
        elif statement[0] == "set":
            value = self.__run_statement(
                statement[2], parameter_vals, objects, error_handler, input_handler, output_handler, object_handler)
            self.__set_value(
                statement[1], value, parameter_vals, error_handler)
        # TODO: parameter statements handled correctly?
        elif statement[0] == "call":
            # Evaluate parameters if needed
            for index, parameter in enumerate(statement[3:], 3):
                statement[index] = self.__run_statement(
                    parameter, parameter_vals, objects, error_handler, input_handler, output_handler, object_handler)

            return self.call_method(statement[2], statement[3:], objects,
                                    statement[1], error_handler, input_handler, output_handler, object_handler)
        elif statement[0] == "while":
            while self.__evaluate_conditional(statement[1], parameter_vals, objects, error_handler, input_handler, output_handler, object_handler):
                self.__run_statement(
                    statement[2], parameter_vals, objects, error_handler, input_handler, output_handler, object_handler)
        elif statement[0] == "if":
            if self.__evaluate_conditional(statement[1], parameter_vals, objects, error_handler, input_handler, output_handler, object_handler):
                self.__run_statement(
                    statement[2], parameter_vals, objects, error_handler, input_handler, output_handler, object_handler)
            elif len(statement) > 3:
                self.__run_statement(
                    statement[3], parameter_vals, objects, error_handler, input_handler, output_handler, object_handler)
        elif statement[0] == "return":
            # Return nothing
            if len(statement) == 1:
                return

            # Return a value
            return self.__run_statement(statement[1], parameter_vals, objects, error_handler, input_handler, output_handler, object_handler)
        elif statement[0] == "begin":
            for statement in statement[1:]:
                self.__run_statement(
                    statement, parameter_vals, objects, error_handler, input_handler, output_handler, object_handler)
        elif statement[0] == "new":
            return object_handler(statement[1])
        else:
            # TODO: handle boolean unary NOT expression
            try:
                operand1 = self.__run_statement(
                    statement[1], parameter_vals, objects, error_handler, input_handler, output_handler, object_handler)
                operand2 = self.__run_statement(
                    statement[2], parameter_vals, objects, error_handler, input_handler, output_handler, object_handler)
                try:
                  expression = operand1 + statement[0] + operand2
                except:
                    print("Error: 1{} 2{} 3{}".format(operand1, statement[0], operand2))
                print("Expression: {}".format(expression))
                return eval(expression)
            except:
                error_handler(ErrorType.TYPE_ERROR, "Operation failed: {}".format(
                  expression))

    def __get_value(self, name, parameter_vals):
        if name in parameter_vals:
            return parameter_vals[name]
        elif name in self.obj_fields:
            return self.obj_fields[name].value
        else:
            return name

    def __set_value(self, name, value, parameter_vals, error_handler=None):
        if name in parameter_vals:
            parameter_vals[name] = value
        elif name in self.obj_fields:
            self.obj_fields[name].value = value
        else:
            error_handler(ErrorType.NAME_ERROR, "Variable does not exist: {}".format(
                name))

    def __evaluate_conditional(self, conditional, parameter_vals, objects, error_handler=None, input_handler=None, output_handler=None, object_handler=None):
        # Evaluate condition
        result = self.__run_statement(
            conditional, parameter_vals, objects, error_handler, input_handler, output_handler, object_handler)

        # Check that result is a boolean
        if not isinstance(result, bool):
            error_handler(ErrorType.TYPE_ERROR, "Value is not a boolean: {}".format(
                result))

        return result

    def __str__(self):
        return "Object Name: {}\n Fields: {}\n Methods: {}".format(self.obj_name, self.obj_fields, self.obj_methods)


# TODO: handle new keyword and expressions
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
