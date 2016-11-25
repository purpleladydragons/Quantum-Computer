import collections 

FALSE = { "type": "bool", "value": False }
class Parser:
    def __init__(self, input):
        self.input = input
        # TODO precedence

    def is_punc(self, ch):
        token = self.input.peek()
        return token and token['type'] == 'punc' and ( (not ch) or  token['value'] == ch) and token

    def is_kw(self, kw):
        token = self.input.peek()
        return token and token['type'] == 'punc' and ( (not kw) or  token['value'] == kw) and token

    def is_op(self, op):
        token = self.input.peek()
        return token and token['type'] == 'punc' and ( (not op) or  token['value'] == op) and token

    def skip_punc(self, ch):
        if self.is_punc(ch):
            self.input.next()
        else:
            self.input.exit("Expecting punctuation: " + ch)

    def skip_kw(self, kw):
        if self.is_kw(kw):
            self.input.next()
        else:
            self.input.exit("Expecting keyword: " + kw)

    def skip_op(self, op):
        if self.is_op(op):
            self.input.next()
        else:
            self.input.exit("Expecting operator: " + op)

    def unexpected(self):
        self.input.exit("Unexpected token: " + input.peek())

    def maybe_binary(self, left, my_prec):
        # TODO pretty sure this is gonna break...
        token = self.is_op(left)
        if token:
            his_prec = PRECEDENCE[token['value']]
            if his_prec > my_prec:
                self.input.next()
                right = self.maybe_binary(self.parse_atom(), his_prec)
                binary = { 'type': 'assign' if token['value'] == '=' else 'binary',
                            'operator': token['value'],
                            'left': left,
                            'right': right
                }

                return self.maybe_binary(binary, my_prec)

        return left

    def delimited(self, start, stop, separator, parser):
        a = []
        first = True
        self.skip_punc(start)
        while not self.input.eof():
            if self.is_punc(stop):
                break

            if first:
                first = False
            else:
                self.skip_punc(separator)

            if self.is_punc(stop):
                break

            a.append(parser())

        self.skip_punc(stop)

        return a

    def parse_call(self, func):
        return { 'type': 'call', 'func': func, 'args': self.delimited('(', ')', ',', self.parse_expression) }

    def parse_varname(self):
        name = self.input.next()
        if name['type'] != 'var':
            self.input.exit('Expecting variable name')

        return name['value']

    def parse_if():
        pass

    def parse_bool():
        pass

    def maybe_call(self, expr):
        expr = expr()
        return self.parse_call(expr) if self.is_punc('(') else expr

    def parse_atom(self):
        def inner_atom():
            if self.is_punc('('):
                self.input.next()
                exp = self.parse_expression()
                self.skip_punc(')')
                return exp

            if self.is_punc('{'):
                return self.parse_prog()

            # TODO other things

            token = self.input.next()
            if token['type'] == 'var' or token['type'] == 'num' or token['type'] == 'str':
                return token

            self.unexpected()
                
        return self.maybe_call(inner_atom)

    def parse_toplevel(self):
        prog = []
        while not self.input.eof():
            prog.append(self.parse_expression())
            if not self.input.eof():
                self.skip_punc(';')

        return { "type": "prog", "prog": prog }

    def parse_prog(self):
        prog = self.delimited('{', '}', ';', self.parse_expression)
        if len(prog) == 0:
            return FALSE
        if len(prog) == 1:
            return prog[0]
        return { 'type': 'prog', 'prog': prog }

    def parse_expression(self):
        def inner_expr():
            return self.maybe_binary(self.parse_atom(), 0)

        return self.maybe_call(inner_expr)
        
    def parse(self):
        return self.parse_toplevel()
    
class InputStream:
    def __init__(self, string):
        self.pos = 0
        self.line = 1
        self.col = 0
        self.string = string

    def next(self):
        ch = self.string[self.pos]
        self.pos+=1
        if ch == "\n":
            self.line += 1
            self.col = 0
        else:
            self.col += 1
        return ch

    def peek(self):
        return self.string[self.pos]

    def eof(self):
        return self.pos >= len(self.string)
        
    def exit(msg):
        raise SyntaxError(msg + " (" + self.line + ":" + self.col + ")")

class Tokenizer: 
    def __init__(self, input):
        self.current = None
        self.keywords = ["meas", "new", "let", "if", "then", "else", "in"]
        self.input = input

    def is_keyword(self, x):
        return x in self.keywords

    def is_digit(self, ch):
        return ch in '0123456789'

    def is_id_start(self, ch):
        return ch in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'

    def is_id(self, ch):
        return self.is_id_start(ch)

    def is_op_char(self, ch):
        return ch in "*="

    def is_punc(self, ch):
        return ch in '.;(){}' 

    def is_whitespace(self, ch):
        return ch in ' \t\n' 

    def read_while(self, predicate):
        str = []
        while (not self.input.eof()) and predicate(self.input.peek()):
            str.append(self.input.next())
        return ''.join(str)

    def read_number(self):

        def valid_num(ch):
            if ch == '.':
                if has_dot:
                    return False

                has_dot = True
                return True

            return self.is_digit(ch)

        has_dot = False
        number = self.read_while(valid_num)

        return { "type": "num", "value": float(number) }

    def read_ident(self): 
        id = self.read_while(self.is_id)
        return  { "type": "kw" if self.is_keyword(id) else "var", "value": id }

    def read_next(self):
        self.read_while(self.is_whitespace)
        if(self.input.eof()):
            return None

        ch = self.input.peek()
        if self.is_digit(ch):
            return self.read_number()
        if self.is_id_start(ch):
            return self.read_ident()
        if self.is_punc(ch):
            return { "type": "punc", "value": self.input.next() }
        if self.is_op_char(char):
            return { "type": "op", "value": self.read_while(self.is_op_char) }

        self.input.exit("Can't handle char: " + ch)

    def peek(self):
        if self.current:
            return self.current
        self.current = self.read_next()
        return self.current

    def next(self):
        token = self.current
        self.current = None
        return token or self.read_next()

    def eof(self):
        return self.peek() is None

def qpl_eval(string):
    p = Parser(Tokenizer(InputStream(string)))
    ast = p.parse()

    return ast

def repl():
    while True:
        inp = raw_input(">>> ")
        print qpl_eval(inp)

repl()
