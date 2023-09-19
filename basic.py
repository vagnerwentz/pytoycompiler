from error import *

DIGITS = '0123456789'

TT_INT			= 'INT'
TT_FLOAT    	= 'FLOAT'
TT_STRING		= 'STRING'
TT_IDENTIFIER	= 'IDENTIFIER'
TT_KEYWORD		= 'KEYWORD'
TT_PLUS     	= 'PLUS'
TT_MINUS    	= 'MINUS'
TT_MUL      	= 'MUL'
TT_DIV      	= 'DIV'
TT_POW			= 'POW'
TT_EQ			= 'EQ'
TT_LPAREN   	= 'LPAREN'
TT_RPAREN   	= 'RPAREN'
TT_LSQUARE      = 'LSQUARE'
TT_RSQUARE      = 'RSQUARE'
TT_EE			= 'EE'
TT_NE			= 'NE'
TT_LT			= 'LT'
TT_GT			= 'GT'
TT_LTE			= 'LTE'
TT_GTE			= 'GTE'
TT_COMMA		= 'COMMA'
TT_ARROW		= 'ARROW'
TT_NEWLINE		= 'NEWLINE'
TT_EOF			= 'EOF'
    
class IllegalCharError(Error):
    def __init__(self, position_start, position_end, details):
        super().__init__(position_start, position_end, 'Caractere inválido', details)
        
class InvalidSyntaxError(Error):
    def __init__(self, position_start, position_end, details):
        super().__init__(position_start, position_end, 'Sintáxe invalida', details)
        
class Position:
    def __init__(self, index, line, column, file_name, file_text):
        self.index = index
        self.line = line
        self.column = column
        self.file_name = file_name
        self.file_text = file_text
        
    def advance(self, currenct_character):
        self.index += 1
        self.column += 1
        
        if currenct_character == '\n':
            self.line += 1
            self.column = 0
            
        return self
    
    def copy(self):
        return Position(self.index, self.line, self.column, self.file_name, self.file_text)

class Token:
    def __init__(self, type_, value=None):
        self.type = type_
        self.value = value
        
    def __repr__(self):
        if self.value: return f'{self.type}:{self.value}'
        return f'{self.type}'
    
class Lexer:
    def __init__(self, file_name, text):
        self.file_name = file_name
        self.text = text
        self.position = Position(-1, 0, -1, file_name, text)
        self.current_character = None
        self.advance()
        
    def advance(self):
        self.position.advance(self.current_character)
        self.current_character = self.text[self.position.index] if self.position.index < len(self.text) else None
        
    def make_tokens(self):
        tokens = []
        
        while self.current_character != None:
            if self.current_character in ' \t':
                self.advance()
            elif self.current_character in DIGITS:
                tokens.append(self.make_numbers())
            elif self.current_character == '+':
                tokens.append(Token(TT_PLUS))
                self.advance()
            elif self.current_character == '-':
                tokens.append(Token(TT_MINUS))
                self.advance()
            elif self.current_character == '*':
                tokens.append(Token(TT_MUL))
                self.advance()
            elif self.current_character == '/':
                tokens.append(Token(TT_DIV))
                self.advance()
            elif self.current_character == '(':
                tokens.append(Token(TT_LPAREN))
                self.advance()
            elif self.current_character == ')':
                tokens.append(Token(TT_RPAREN))
                self.advance()
            else:
                position_start = self.position.copy()
                char = self.current_character
                self.advance()
                return [], IllegalCharError(position_start, self.position, "'" + char + "'")
                
        
        return tokens, None

    def make_numbers(self):
        num_str = ''
        dot_count = 0
        
        while self.current_character != None and self.current_character in DIGITS + '.':
            if self.current_character == '.':
                if dot_count == 1: break
                dot_count += 1
                num_str += '.'
            else:
                num_str += self.current_character
            self.advance()
            
        if dot_count == 0:
            return Token(TT_INT, int(num_str))
        else:
            return Token(TT_FLOAT, float(num_str))
        
class NumberNode:
    def __init__(self, token):
        self.token = token
        
    def __repr__(self):
        return f'{self.token}'
    
class BinOperationNode:
    def __init__(self, left_node, operation_token, right_node):
        self.left_node = left_node
        self.operation_token = operation_token
        self.right_node = right_node
        
    def __repr__(self):
        return f'({self.left_node}, {self.operation_token}, {self.right_node})'
        
class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.token_index = -1
        self.advance()
        
    def advance(self):
        self.token_index += 1
        if self.token_index < len(self.tokens):
            self.current_token = self.tokens[self.token_index]
        return self.current_token
    
    def parse(self):
        result = self.expression()
        return result
    
    def factor(self):
        token = self.current_token
        
        if token.type in (TT_INT, TT_FLOAT):
            self.advance()
            return NumberNode(token)
        
    def term(self):
        return self.binary_operation(self.factor, (TT_MUL, TT_DIV))
            
        
    def expression(self):
        return self.binary_operation(self.term, (TT_PLUS, TT_MINUS))
    
    def binary_operation(self, function, operation):
        left = function()
        
        while self.current_token.type in operation:
            operation_token = self.current_token
            self.advance()
            right = function()
            left = BinOperationNode(left, operation_token, right)
        
        return left

def run(file_name, text):
    # Gerando tokens
    lexer = Lexer(file_name, text)
    tokens, error = lexer.make_tokens()
    
    if error: return None
    
    # Gerar a AST
    parser = Parser(tokens)
    ast = parser.parse()
    return ast, error