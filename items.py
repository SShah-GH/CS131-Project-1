class Field:
    def __init__(self, field_name, value):
        self.field_name = field_name
        self.value = value

    def __str__(self):
        return "Field Name: {}, Value: {}\n".format(self.name, self.value)


class Method:
    def __init__(self, method_name, parameters, statement):
        self.method_name = method_name
        self.parameters = parameters
        self.statement = statement

    def __str__(self):
        return "Method Name: {}, Parameters: {}, Statement: {}\n".format(self.method_name, self.parameters, self.statement)
