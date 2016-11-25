import collections 

def parse(input):
    FALSE = { "type": "bool", "value": False }
    # TODO precedence

    def is_punc(ch):
        token = input.peek()
        return token and token['type'] == 'punc' and ( (not ch) or  token['value'] == ch) and token

    def is_kw(kw):
        token = input.peek()
        return token and token['type'] == 'punc' and ( (not kw) or  token['value'] == kw) and token

    def is_op(op):
        token = input.peek()
        return token and token['type'] == 'punc' and ( (not op) or  token['value'] == op) and token

    def skip_punc(ch):
        if is_punc(ch):
            input.next()
        else:
            input.exit("Expecting punctuation: " + ch)

    def skip_kw(kw):
        if is_kw(kw):
            input.next()
        else:
            input.exit("Expecting keyword: " + kw)

    def skip_op(op):
        if is_op(op):
            input.next()
        else:
            input.exit("Expecting operator: " + op)

    def unexpected():
        input.exit("Unexpected token: " + input.peek())

    def maybe_binary(left, my_prec):
        # TODO pretty sure this is gonna break...
        token = is_op()
        if token:
            his_prec = PRECEDENCE[token['value']]
            if his_prec > my_prec:
                input.next()
                right = maybe_binary(parse_atom(), his_prec)
                binary = { 'type': 'assign' if token['value'] == '=' else 'binary',
                            'operator': token['value'],
                            'left': left,
                            'right': right
                }

                return maybe_binary(binary, my_prec)

        return left

    def delimited(start, stop, separator, parser):
        a = []
        first = True
        skip_punc(start)
        while not input.eof():
            if is_punc(stop):
                break

            if first:
                first = False
            else:
                skip_punc(separator)

            if is_punc(stop):
                break

            a.append(parser())

        skip_punc(stop)

        return a

    def parse_call(func):
        return { 'type': 'call', 'func': func, 'args': delimited('(', ')', ',', parse_expression) }

    def parse_varname():
        name = input.next()
        if name['type'] != 'var':
            input.exit('Expecting variable name')

        return name['value']

    def parse_if():
        pass

    def parse_bool():
        pass

    def maybe_call(expr):
        expr = expr()
        return parse_call(expr) if is_punc('(') else expr

    def parse_atom():
        def inner_atom():
            if is_punc('('):
                input.next()
                exp = parse_expression()
                skip_punc(')')
                return exp

            if is_punc('{'):
                return parse_prog()

            # TODO other things

            token = input.next()
            if token['type'] == 'var' or token['type'] == 'num' or token['type'] == 'str':
                return token

            unexpected()
                
        return maybe_call(inner_atom)

    def parse_toplevel():
        prog = []
        while not input.eof():
            prog.append(parse_expression())
            if not input.eof():
                skip_punc(';')

        return { "type": "prog", "prog": prog }

    def parse_prog():
        prog = delimited('{', '}', ';', parse_expression)
        if len(prog) == 0:
            return FALSE
        if len(prog) == 1:
            return prog[0]
        return { 'type': 'prog', 'prog': prog }

    def parse_expression():
        def inner_expr():
            return maybe_binary(parse_atom(), 0)
        return maybe_call(maybe_binary(inner_expr))
        
    return parse_toplevel()

def input_stream(string):
    pos = 0
    line = 1
    col = 0

    def next():
        pos+=1
        ch = string[pos]
        if ch == "\n":
            line += 1
            col = 0
        else:
            col += 1
        return ch

    def peek():
        return string[pos]

    def eof():
        return pos >= len(string)
        
    def exit(msg):
        raise SyntaxError(msg + " (" + line + ":" + col + ")")

def tokenize(input):
    current = None
    keywords = ["meas", "new", "let", "if", "then", "else", "in"]

    def is_keyword(x):
        return x in keywords

    def is_digit(ch):
        return ch in '0123456789'

    def is_id_start(ch):
        return ch in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'

    def is_id(ch):
        return is_id_start(ch)

    def is_op_char(ch):
        return ch in "*="

    def is_punc(ch):
        return ch in '.;(){}' 

    def is_whitespace(ch):
        return ch in ' \t\n' 

    def read_while(predicate):
        str = []
        while (not input.eof()) and predicate(input.peek()):
            str.append(input.next())
        return ''.join(str)

    def read_number():
        has_dot = False
        number = read_while(valid_num)

        def valid_num(ch):
            if ch == '.':
                if has_dot:
                    return False

                has_dot = True
                return True

            return is_digit(ch)

        return { "type": "num", "value": parseFloat(number) }

    def read_ident(): 
        id = read_while(is_id)
        return  { "type": "kw" if is_keyword(id) else "var", "value": id }

    def read_next():
        read_while(is_whitespace)
        if(input.eof()):
            return None

        ch = input.peek()
        if is_digit(ch):
            return read_number()
        if is_ident(ch):
            return read_ident()
        if is_punc(ch):
            return { "type": "punc", "value": input.next() }
        if is_op_char(char):
            return { "type": "op", "value": read_while(is_op_char) }

        input.exit("Can't handle char: " + ch)

    def peek():
        if current:
            return current
        current = read_next()
        return current

    def next():
        token = current
        current = None
        return token or read_next()

    def eof():
        return peek() is None

    return collections.namedtuple('tokenize', ['next', 'peek', 'eof', 'exit'])(next, peek, eof, exit)

def qpl_eval(string):
    ast = parse(tokenize(input_stream(string)))
    return ast

def repl():
    while True:
        inp = raw_input(">>> ")
        print qpl_eval(inp)

repl()
