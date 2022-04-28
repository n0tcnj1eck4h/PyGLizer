class Argument:
    def __init__(self, string: str):
        string = string.replace('*', ' * ')  # Pointers are a part of the type and nobody can tell me otherwise
        elements = string.split()
        self.type = ' '.join(elements[0:-1])
        self.name = elements[-1]

    def __str__(self):
        return f'{self.type} {self.name}'

