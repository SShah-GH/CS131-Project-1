from intbase import *
from items import *


class ObjectDefinition:
    # ObjectDefinition constructor
    def __init__(self, obj_name="main"):
        self.obj_name = obj_name
        self.obj_fields = dict()
        self.obj_methods = dict()

    def add_field(self, field_name, field_value):
        field_value = self.__get_value(field_value, dict())
        self.obj_fields[field_name] = Field(field_name, field_value)

    def add_method(self, method):
        self.obj_methods[method.method_name] = method

    def __get_value(self, name, parameter_vals, error_handler=None):
        if name == 'true':
            return True
        elif name == 'false':
            return False
        elif name == 'null':
            return None
        elif name[0] == '"' and name[-1] == '"':
            return name[1:-1]
        elif name.isnumeric() or (name[0] == '-' and name[1:].isnumeric()):
            return int(name)
        else:
            if name in parameter_vals:
                return parameter_vals[name]
            elif name in self.obj_fields:
                return self.obj_fields[name].value
            else:
                error_handler(ErrorType.NAME_ERROR, "Variable does not exist: {}".format(
                    name))

    def __set_value(self, name, value, parameter_vals, error_handler=None):
        if name in parameter_vals:
            parameter_vals[name] = value
        elif name in self.obj_fields:
            self.obj_fields[name].value = value
        else:
            error_handler(ErrorType.NAME_ERROR, "Variable does not exist: {}".format(
                name))

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
        print(statement)
        # Check if statement is a value
        if not isinstance(statement, list):
            result = self.__get_value(statement, parameter_vals)
            return result

        # Execute statements
        if statement[0] == "print":
            output = ""
            for item in statement[1:]:
                cur_output = self.__run_statement(
                    item, parameter_vals, objects, error_handler, input_handler, output_handler, object_handler)

                # Convert to Brewin type
                if isinstance(cur_output, bool):
                    if cur_output:
                        cur_output = "true"
                    else:
                      cur_output = "false"
                elif cur_output is None:
                    cur_output = "null"
                elif isinstance(cur_output, int):
                    cur_output = str(cur_output)
                elif isinstance(cur_output, str):
                    # No change needed
                    cur_output = cur_output
                else:
                    error_handler(ErrorType.TYPE_ERROR, "Invalid type for print: {}".format(
                        type(cur_output)))

                output += cur_output
            output_handler(output)
        elif statement[0] == "inputi":
            input = input_handler()
            input = self.__get_value(input, parameter_vals, error_handler)
            self.__set_value(
                statement[1], input, parameter_vals, error_handler)
        elif statement[0] == "inputs":
            input = input_handler()
            input = '"' + input + '"'
            input = self.__get_value(input, parameter_vals, error_handler)
            self.__set_value(statement[1], input, parameter_vals, error_handler)
        elif statement[0] == "set":
            value = self.__run_statement(
                statement[2], parameter_vals, objects, error_handler, input_handler, output_handler, object_handler)
            self.__set_value(
                statement[1], value, parameter_vals, error_handler)
        # TODO: parameter statements handled correctly?
        elif statement[0] == "call":
            # Evaluate parameters if needed
            parameters = statement[3:]
            for index, parameter in enumerate(parameters):
                parameters[index] = self.__run_statement(
                    parameter, parameter_vals, objects, error_handler, input_handler, output_handler, object_handler)

            return self.call_method(statement[2], parameters, objects,
                                    statement[1], error_handler, input_handler, output_handler, object_handler)
        elif statement[0] == "while":
            while self.__evaluate_conditional(statement[1], parameter_vals, objects, error_handler, input_handler, output_handler, object_handler):
                self.__run_statement(
                    statement[2], parameter_vals, objects, error_handler, input_handler, output_handler, object_handler)
        elif statement[0] == "if":
            if self.__evaluate_conditional(statement[1], parameter_vals, objects, error_handler, input_handler, output_handler, object_handler):
                return self.__run_statement(
                    statement[2], parameter_vals, objects, error_handler, input_handler, output_handler, object_handler)
            elif len(statement) > 3:
                return self.__run_statement(
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
            return self.__evaluate_expression(statement, parameter_vals, objects,
                                              error_handler, input_handler, output_handler, object_handler)

    def __evaluate_conditional(self, conditional, parameter_vals, objects, error_handler=None, input_handler=None, output_handler=None, object_handler=None):
        # Evaluate condition
        result = self.__run_statement(
            conditional, parameter_vals, objects, error_handler, input_handler, output_handler, object_handler)

        print(result)
        # Check that result is a boolean
        if not isinstance(result, bool):
            error_handler(ErrorType.TYPE_ERROR, "Value is not a boolean: {}".format(
                result))

        return result

    def __evaluate_expression(self, expression, parameter_vals, objects, error_handler=None, input_handler=None, output_handler=None, object_handler=None):
        match expression[0]:
            case '+':
                operand1 = self.__run_statement(
                    expression[1], parameter_vals, objects, error_handler, input_handler, output_handler, object_handler)
                operand2 = self.__run_statement(
                    expression[2], parameter_vals, objects, error_handler, input_handler, output_handler, object_handler)

                # Check if operands are different types
                if type(operand1) != type(operand2):
                    error_handler(
                        ErrorType.TYPE_ERROR, "Incompatible types: {} + {}".format(operand1, operand2))

                try:
                    print(operand1 + operand2)
                    return operand1 + operand2
                except:
                    error_handler(ErrorType.TYPE_ERROR, "Operation failed: {} {} {}".format(
                        operand1, expression[0], operand2))
            case '-':
                operand1 = self.__run_statement(
                    expression[1], parameter_vals, objects, error_handler, input_handler, output_handler, object_handler)
                operand2 = self.__run_statement(
                    expression[2], parameter_vals, objects, error_handler, input_handler, output_handler, object_handler)

                # Check if operands are different types
                print(type(operand1))
                print(type(operand2))
                if type(operand1) != type(operand2):
                    error_handler(
                        ErrorType.TYPE_ERROR, "Incompatible types: {} - {}".format(operand1, operand2))

                try:
                    return operand1 - operand2
                except:
                    error_handler(ErrorType.TYPE_ERROR, "Operation failed: {} {} {}".format(
                        operand1, expression[0], operand2))
            case '*':
                operand1 = self.__run_statement(
                    expression[1], parameter_vals, objects, error_handler, input_handler, output_handler, object_handler)
                operand2 = self.__run_statement(
                    expression[2], parameter_vals, objects, error_handler, input_handler, output_handler, object_handler)

                # Check if operands are different types
                if type(operand1) != type(operand2):
                    error_handler(
                        ErrorType.TYPE_ERROR, "Incompatible types: {} * {}".format(operand1, operand2))

                try:
                    return operand1 * operand2
                except:
                    error_handler(ErrorType.TYPE_ERROR, "Operation failed: {} {} {}".format(
                        operand1, expression[0], operand2))
            case '/':
                operand1 = self.__run_statement(
                    expression[1], parameter_vals, objects, error_handler, input_handler, output_handler, object_handler)
                operand2 = self.__run_statement(
                    expression[2], parameter_vals, objects, error_handler, input_handler, output_handler, object_handler)
                
                # Check if operands are different types
                if type(operand1) != type(operand2):
                    error_handler(
                        ErrorType.TYPE_ERROR, "Incompatible types: {} / {}".format(operand1, operand2))

                try:
                    return operand1 // operand2
                except:
                    error_handler(ErrorType.TYPE_ERROR, "Operation failed: {} {} {}".format(
                        operand1, expression[0], operand2))
            case '%':
                operand1 = self.__run_statement(
                    expression[1], parameter_vals, objects, error_handler, input_handler, output_handler, object_handler)
                operand2 = self.__run_statement(
                    expression[2], parameter_vals, objects, error_handler, input_handler, output_handler, object_handler)
                
                # Check if operands are different types
                if type(operand1) != type(operand2):
                    error_handler(
                        ErrorType.TYPE_ERROR, "Incompatible types: {} % {}".format(operand1, operand2))

                try:
                    return operand1 % operand2
                except:
                    error_handler(ErrorType.TYPE_ERROR, "Operation failed: {} {} {}".format(
                        operand1, expression[0], operand2))
            case '==':
                operand1 = self.__run_statement(
                    expression[1], parameter_vals, objects, error_handler, input_handler, output_handler, object_handler)
                operand2 = self.__run_statement(
                    expression[2], parameter_vals, objects, error_handler, input_handler, output_handler, object_handler)

                try:
                    if operand1 == operand2:
                        return True
                    else:
                        return False
                except:
                    error_handler(ErrorType.TYPE_ERROR, "Operation failed: {} {} {}".format(
                        operand1, expression[0], operand2))
            case '!=':
                operand1 = self.__run_statement(
                    expression[1], parameter_vals, objects, error_handler, input_handler, output_handler, object_handler)
                operand2 = self.__run_statement(
                    expression[2], parameter_vals, objects, error_handler, input_handler, output_handler, object_handler)
                try:
                    if operand1 != operand2:
                        return True
                    else:
                        return False
                except:
                    error_handler(ErrorType.TYPE_ERROR, "Operation failed: {} {} {}".format(
                        operand1, expression[0], operand2))
            case '<':
                operand1 = self.__run_statement(
                    expression[1], parameter_vals, objects, error_handler, input_handler, output_handler, object_handler)
                operand2 = self.__run_statement(
                    expression[2], parameter_vals, objects, error_handler, input_handler, output_handler, object_handler)
                try:
                    if operand1 < operand2:
                        return True
                    else:
                        return False
                except:
                    error_handler(ErrorType.TYPE_ERROR, "Operation failed: {} {} {}".format(
                        operand1, expression[0], operand2))
            case '>':
                operand1 = self.__run_statement(
                    expression[1], parameter_vals, objects, error_handler, input_handler, output_handler, object_handler)
                operand2 = self.__run_statement(
                    expression[2], parameter_vals, objects, error_handler, input_handler, output_handler, object_handler)
                try:
                    if operand1 > operand2:
                        return True
                    else:
                        return False
                except:
                    error_handler(ErrorType.TYPE_ERROR, "Operation failed: {} {} {}".format(
                        operand1, expression[0], operand2))
            case '<=':
                operand1 = self.__run_statement(
                    expression[1], parameter_vals, objects, error_handler, input_handler, output_handler, object_handler)
                operand2 = self.__run_statement(
                    expression[2], parameter_vals, objects, error_handler, input_handler, output_handler, object_handler)
                try:
                    if operand1 <= operand2:
                        return True
                    else:
                        return False
                except:
                    error_handler(ErrorType.TYPE_ERROR, "Operation failed: {} {} {}".format(
                        operand1, expression[0], operand2))
            case '>=':
                operand1 = self.__run_statement(
                    expression[1], parameter_vals, objects, error_handler, input_handler, output_handler, object_handler)
                operand2 = self.__run_statement(
                    expression[2], parameter_vals, objects, error_handler, input_handler, output_handler, object_handler)
                try:
                    if operand1 >= operand2:
                        return True
                    else:
                        return False
                except:
                    error_handler(ErrorType.TYPE_ERROR, "Operation failed: {} {} {}".format(
                        operand1, expression[0], operand2))
            case '&':
                operand1 = self.__run_statement(
                    expression[1], parameter_vals, objects, error_handler, input_handler, output_handler, object_handler)
                operand2 = self.__run_statement(
                    expression[2], parameter_vals, objects, error_handler, input_handler, output_handler, object_handler)

                if not isinstance(operand1, bool) or not isinstance(operand2, bool):
                    error_handler(ErrorType.TYPE_ERROR, "Operation failed: {} {} {}".format(
                        operand1, expression[0], operand2))

                try:
                    if operand1 and operand2:
                        return True
                    else:
                        return False
                except:
                    error_handler(ErrorType.TYPE_ERROR, "Operation failed: {} {} {}".format(
                        operand1, expression[0], operand2))
            case '|':
                operand1 = self.__run_statement(
                    expression[1], parameter_vals, objects, error_handler, input_handler, output_handler, object_handler)
                operand2 = self.__run_statement(
                    expression[2], parameter_vals, objects, error_handler, input_handler, output_handler, object_handler)

                if not isinstance(operand1, bool) or not isinstance(operand2, bool):
                    error_handler(ErrorType.TYPE_ERROR, "Operation failed: {} {} {}".format(
                        operand1, expression[0], operand2))

                try:
                    if operand1 or operand2:
                        return True
                    else:
                        return False
                except:
                    error_handler(ErrorType.TYPE_ERROR, "Operation failed: {} {} {}".format(
                        operand1, expression[0], operand2))
            case '!':
                operand = self.__run_statement(
                    expression[1], parameter_vals, objects, error_handler, input_handler, output_handler, object_handler)

                if not isinstance(operand, bool):
                    error_handler(ErrorType.TYPE_ERROR, "Operation failed: {} {} {}".format(
                        operand1, expression[0], operand2))

                try:
                    if operand:
                        return False
                    else:
                        return True
                except:
                    error_handler(ErrorType.TYPE_ERROR, "Operation failed: {} {}".format(
                        expression[0], operand))

    def __str__(self):
        return "Object Name: {}\n Fields: {}\n Methods: {}".format(self.obj_name, self.obj_fields, self.obj_methods)
