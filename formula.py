from connectives import *

class ParsingError(LogicError):
    note = "We couldn't parse the above formula. Are you sure it's written in LaTeX?"
    pass

class PropNode():
    def __init__(self, name, sub):
        self.name = name
        self.sub = sub
    
    def eq_syntax(self, other):
        if not isinstance(other, PropNode):
            raise LogicError('trying to check eq_syntax for something other than a PropNode')
        if not (self.name == other.name):
            return False
        if len(self.sub) != len(other.sub):
            return False
        
        output = True
        for (self_subproof, other_subproof) in zip(self.sub, other.sub):
            output = output and self_subproof.eq_syntax(other_subproof)
        return output

    def latex(self):
        if len(self.sub) == 0:
            return self.name
        elif len(self.sub) == 1:
            return f'{self.name} {self.sub[0].latex()}'
        else:
            return f'({self.sub[0].latex()} {self.name} {self.sub[1].latex()})'
    
    def change(self, formula):
        self.name = formula.name
        self.sub = formula.sub
    
    def __repr__(self):
        output = f"PropNode('{self.name}', ["
        for subnode in self.sub:
            output += subnode.__repr__() + ', '
        if len(self.sub) != 0:
            output = output[:-2]
        output += '])'
        return output

    def parse(string):
        string = string.replace(' ', '')
        string = string.replace(r'\rightarrow', r'\to')

        if len(string) == 1:
            return PropNode(string, [])
        
        for conn in zeroary:
            if string == conn:
                return PropNode(conn, [])

        for conn in unary:
            if len(string) > len(conn) and string[:len(conn)] == conn:
                return PropNode(conn, [PropNode.parse(string[len(conn):])])
        
        if len(string)>0 and string[0] == '(':
            p_balance = 1
            index = 0
            for i, char in enumerate(string):
                if i == 0: continue

                if char == '(':
                    p_balance += 1
                elif char == ')':
                    p_balance -= 1
                
                if p_balance < 0:
                    raise ParsingError(ParsingError.note)
                if p_balance == 0:
                    index = i
                    break
                if i == len(string)-1:
                    raise ParsingError(ParsingError.note)
            
            first = string[:index+1]
            conn_rest = string[index+1:]

            if len(conn_rest) == 0:
                return PropNode.parse(first[1:-1])
            
            main_conn = None
            rest = None
            for conn in binary:
                if len(conn_rest) > len(conn) and conn_rest[0:len(conn)] == conn:
                    main_conn = conn_rest[:len(conn)]
                    rest = conn_rest[len(conn):]
                    break
            if main_conn == None:
                raise ParsingError(ParsingError.note)

            return PropNode(main_conn, [PropNode.parse(first), PropNode.parse(rest)])

        if len(string)>1 and string[1] == "\\":
            first = string[:1]
            conn_rest = string[1:]

            if len(conn_rest) == 0:
                return PropNode.parse(first[1:-1])
            
            main_conn = None
            rest = None
            for conn in binary:
                if len(conn_rest) > len(conn) and conn_rest[0:len(conn)] == conn:
                    main_conn = conn_rest[:len(conn)]
                    rest = conn_rest[len(conn):]
                    break
            if main_conn == None:
                raise ParsingError(ParsingError.note)

            return PropNode(main_conn, [PropNode.parse(first), PropNode.parse(rest)])

        raise ParsingError(ParsingError.note)