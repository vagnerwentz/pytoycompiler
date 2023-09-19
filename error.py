from string_with_arrows import *

class Error:
    def __init__(self, position_start, position_end, error_name, details):
        self.position_start = position_start
        self.position_end = position_end
        self.error_name = error_name
        self.details = details
        
    def as_string(self):
        result = f'{self.error_name}: {self.details}'
        result += f'\nArquivo {self.position_start.file_name}, linha {self.position_start.line + 1}'
        result += '\n\n' + string_with_arrows(self.position_start.file_text, self.position_start, self.position_end)
        return result