from intbase import *
from items import *


class ObjectDefinition:
    # ObjectDefinition constructor
    def __init__(self):
        self.obj_fields = dict()
        self.obj_methods = dict()

    def add_field(self, field_name, field_value):
        field_value = self.__get_value(field_value, dict())
        self.obj_fields[field_name] = Field(field_name, field_value)

    def add_method(self, method):
        self.obj_methods[method.method_name] = method

    def __get_value(self, name, parameter_vals, interpreter=None):
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
                interpreter.error(ErrorType.NAME_ERROR, "Variable does not exist: {}".format(
                    name))

    def __set_value(self, name, value, parameter_vals, interpreter):
        if name in parameter_vals:
            parameter_vals[name] = value
        elif name in self.obj_fields:
            self.obj_fields[name].value = value
        else:
            interpreter.error(ErrorType.NAME_ERROR, "Variable does not exist: {}".format(
                name))

    # Process method call
    def call_method(self, method_name, parameters, object_name, interpreter, existing_parameter_vals=dict()):
        if object_name == "me":
            object = self
        elif object_name in self.obj_fields and isinstance(self.obj_fields[object_name].value, ObjectDefinition):
            object = self.obj_fields[object_name].value
        elif object_name in existing_parameter_vals and isinstance(existing_parameter_vals[object_name], ObjectDefinition):
            object = existing_parameter_vals[object_name]
        else:
            interpreter.error(ErrorType.FAULT_ERROR, "Object does not exist: {}".format(
                object_name))

        # Check that method exists
        if method_name not in object.obj_methods:
            interpreter.error(ErrorType.NAME_ERROR, "Method does not exist: {}".format(
                method_name))

        # Check that correct number of parameters are given
        cur_method = object.obj_methods[method_name]
        if len(parameters) != len(cur_method.parameters):
            interpreter.error(ErrorType.TYPE_ERROR, "Incorrect number of parameters to: {}".format(
                method_name))

        # Create parameter dict
        parameter_vals = dict()
        for index, parameter in enumerate(cur_method.parameters):
            parameter_vals[parameter] = parameters[index]

        # Execute statement with the given parameters
        result, ret_flag = object.__run_statement(
            cur_method.statement, parameter_vals, interpreter)
        return result

    def __run_statement(self, statement, parameter_vals,  interpreter):
        print(statement)
        # Check if statement is a value
        if not isinstance(statement, list):
            result = self.__get_value(statement, parameter_vals, interpreter)
            return result, False

        # Execute statements
        if statement[0] == "print":
            output = ""
            for item in statement[1:]:
                cur_output, ret_flag = self.__run_statement(
                    item, parameter_vals,  interpreter)

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
                    interpreter.error(ErrorType.TYPE_ERROR, "Invalid type for print: {}".format(
                        type(cur_output)))

                output += cur_output
            interpreter.output(output)
            return None, False
        elif statement[0] == "inputi":
            input = interpreter.get_input()
            input = self.__get_value(input, parameter_vals, interpreter)
            self.__set_value(
                statement[1], input, parameter_vals, interpreter)
            return None, False
        elif statement[0] == "inputs":
            input = interpreter.get_input()
            input = '"' + input + '"'
            input = self.__get_value(input, parameter_vals, interpreter)
            self.__set_value(statement[1], input,
                             parameter_vals, interpreter)
            return None, False
        elif statement[0] == "set":
            value, ret_flag = self.__run_statement(
                statement[2], parameter_vals,  interpreter)
            self.__set_value(
                statement[1], value, parameter_vals, interpreter)
            return None, False
        elif statement[0] == "call":
            # Evaluate parameters if needed
            parameters = statement[3:]
            for index, parameter in enumerate(parameters):
                parameters[index], ret_flag = self.__run_statement(
                    parameter, parameter_vals,  interpreter)

            result = self.call_method(statement[2], parameters,
                                      statement[1], interpreter, parameter_vals)
            return result, False
        elif statement[0] == "while":
            while self.__evaluate_conditional(statement[1], parameter_vals,  interpreter):
                result, ret_flag = self.__run_statement(
                    statement[2], parameter_vals,  interpreter)
                if ret_flag:
                    return result, True
            return None, False
        elif statement[0] == "if":
            if self.__evaluate_conditional(statement[1], parameter_vals,  interpreter):
                result, ret_flag = self.__run_statement(
                    statement[2], parameter_vals,  interpreter)
                if ret_flag:
                    return result, True
            elif len(statement) > 3:
                result, ret_flag = self.__run_statement(
                    statement[3], parameter_vals,  interpreter)
                if ret_flag:
                    return result, True
            return None, False
        elif statement[0] == "return":
            # Return nothing
            if len(statement) == 1:
                return None, True

            # Return a value
            result, ret_flag = self.__run_statement(
                statement[1], parameter_vals,  interpreter)
            return result, True
        elif statement[0] == "begin":
            for statement in statement[1:]:
                result, ret_flag = self.__run_statement(
                    statement, parameter_vals,  interpreter)
                if ret_flag:
                    return result, True
            return None, False
        elif statement[0] == "new":
            return interpreter.create_object(statement[1]), False
        else:
            result = self.__evaluate_expression(statement, parameter_vals,
                                                interpreter)
            return result, False

    def __evaluate_conditional(self, conditional, parameter_vals,  interpreter):
        # Evaluate condition
        result, ret_flag = self.__run_statement(
            conditional, parameter_vals,  interpreter)

        # Check that result is a boolean
        if not isinstance(result, bool):
            interpreter.error(ErrorType.TYPE_ERROR, "Value is not a boolean: {}".format(
                result))

        return result

    def __evaluate_expression(self, expression, parameter_vals,  interpreter):
        # Get operands
        if len(expression) == 2:
            operand, ret_flag = self.__run_statement(
                expression[1], parameter_vals,  interpreter)
        else:
            operand1, ret_flag = self.__run_statement(
                expression[1], parameter_vals,  interpreter)
            operand2, ret_flag = self.__run_statement(
                expression[2], parameter_vals,  interpreter)

        match expression[0]:
            case '+':
                # Check if operands are different types
                if type(operand1) != type(operand2):
                    interpreter.error(
                        ErrorType.TYPE_ERROR, "Incompatible types: {} + {}".format(operand1, operand2))

                try:
                    return operand1 + operand2
                except:
                    interpreter.error(ErrorType.TYPE_ERROR, "Operation failed: {} {} {}".format(
                        operand1, expression[0], operand2))
            case '-':
                # Check if operands are different types
                if type(operand1) != type(operand2):
                    interpreter.error(
                        ErrorType.TYPE_ERROR, "Incompatible types: {} - {}".format(operand1, operand2))

                try:
                    return operand1 - operand2
                except:
                    interpreter.error(ErrorType.TYPE_ERROR, "Operation failed: {} {} {}".format(
                        operand1, expression[0], operand2))
            case '*':
                # Check if operands are different types
                if type(operand1) != type(operand2):
                    interpreter.error(
                        ErrorType.TYPE_ERROR, "Incompatible types: {} * {}".format(operand1, operand2))

                try:
                    return operand1 * operand2
                except:
                    interpreter.error(ErrorType.TYPE_ERROR, "Operation failed: {} {} {}".format(
                        operand1, expression[0], operand2))
            case '/':
                # Check if operands are different types
                if type(operand1) != type(operand2):
                    interpreter.error(
                        ErrorType.TYPE_ERROR, "Incompatible types: {} / {}".format(operand1, operand2))

                try:
                    return operand1 // operand2
                except:
                    interpreter.error(ErrorType.TYPE_ERROR, "Operation failed: {} {} {}".format(
                        operand1, expression[0], operand2))
            case '%':
                # Check if operands are different types
                if type(operand1) != type(operand2):
                    interpreter.error(
                        ErrorType.TYPE_ERROR, "Incompatible types: {} % {}".format(operand1, operand2))

                try:
                    return operand1 % operand2
                except:
                    interpreter.error(ErrorType.TYPE_ERROR, "Operation failed: {} {} {}".format(
                        operand1, expression[0], operand2))
            case '==':
                try:
                    if operand1 == operand2:
                        return True
                    else:
                        return False
                except:
                    interpreter.error(ErrorType.TYPE_ERROR, "Operation failed: {} {} {}".format(
                        operand1, expression[0], operand2))
            case '!=':
                try:
                    if operand1 != operand2:
                        return True
                    else:
                        return False
                except:
                    interpreter.error(ErrorType.TYPE_ERROR, "Operation failed: {} {} {}".format(
                        operand1, expression[0], operand2))
            case '<':
                try:
                    if operand1 < operand2:
                        return True
                    else:
                        return False
                except:
                    interpreter.error(ErrorType.TYPE_ERROR, "Operation failed: {} {} {}".format(
                        operand1, expression[0], operand2))
            case '>':
                try:
                    if operand1 > operand2:
                        return True
                    else:
                        return False
                except:
                    interpreter.error(ErrorType.TYPE_ERROR, "Operation failed: {} {} {}".format(
                        operand1, expression[0], operand2))
            case '<=':
                try:
                    if operand1 <= operand2:
                        return True
                    else:
                        return False
                except:
                    interpreter.error(ErrorType.TYPE_ERROR, "Operation failed: {} {} {}".format(
                        operand1, expression[0], operand2))
            case '>=':
                try:
                    if operand1 >= operand2:
                        return True
                    else:
                        return False
                except:
                    interpreter.error(ErrorType.TYPE_ERROR, "Operation failed: {} {} {}".format(
                        operand1, expression[0], operand2))
            case '&':
                if not isinstance(operand1, bool) or not isinstance(operand2, bool):
                    interpreter.error(ErrorType.TYPE_ERROR, "Operation failed: {} {} {}".format(
                        operand1, expression[0], operand2))

                try:
                    if operand1 and operand2:
                        return True
                    else:
                        return False
                except:
                    interpreter.error(ErrorType.TYPE_ERROR, "Operation failed: {} {} {}".format(
                        operand1, expression[0], operand2))
            case '|':
                if not isinstance(operand1, bool) or not isinstance(operand2, bool):
                    interpreter.error(ErrorType.TYPE_ERROR, "Operation failed: {} {} {}".format(
                        operand1, expression[0], operand2))

                try:
                    if operand1 or operand2:
                        return True
                    else:
                        return False
                except:
                    interpreter.error(ErrorType.TYPE_ERROR, "Operation failed: {} {} {}".format(
                        operand1, expression[0], operand2))
            case '!':
                if not isinstance(operand, bool):
                    interpreter.error(ErrorType.TYPE_ERROR, "Operation failed: {} {} {}".format(
                        operand1, expression[0], operand2))

                try:
                    if operand:
                        return False
                    else:
                        return True
                except:
                    interpreter.error(ErrorType.TYPE_ERROR, "Operation failed: {} {}".format(
                        expression[0], operand))

    def __str__(self):
        return "Fields: {}\n Methods: {}".format(self.obj_fields, self.obj_methods)
