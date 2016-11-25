def parse(tokens):
    pass

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
        return ch in '.(){}' 

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

def qpl_eval(string):
    ast = tokenize(input_stream(string))
    return ast

def repl():
    while True:
        inp = raw_input(">>> ")
        print qpl_eval(inp)

repl()
