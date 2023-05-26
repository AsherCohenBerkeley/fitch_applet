from connectives import *

class ParsingError(LogicError):
    note = "We couldn't parse the above formula. Are you sure it's written in LaTeX with lowercase letters?"
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
            if (ord('a') <= ord(string) <= ord('z')):
                return PropNode(string.lower(), [])
            else:
                raise ParsingError(ParsingError.note)
        
        for conn in zeroary:
            if string == conn:
                return PropNode(conn, [])
        
        if '(' in string:
            starting_index = string.index('(')
            p_balance = 1
            index = starting_index
            for char in string[starting_index+1:]:
                index += 1

                if char == '(':
                    p_balance += 1
                elif char == ')':
                    p_balance -= 1
                
                if p_balance < 0:
                    raise ParsingError(ParsingError.note)
                if p_balance == 0:
                    break
                if index == len(string)-1:
                    raise ParsingError(ParsingError.note)
            
            if index == starting_index:
                raise ParsingError(ParsingError.note)
            
            first_conn = string[:starting_index]
            mid = string[starting_index:index+1]
            conn_rest = string[index+1:]

            output = PropNode.parse(mid[1:-1])
            
            if len(first_conn) > 0:
                unary_conn = None
                for conn in unary:
                    if first_conn == conn:
                        unary_conn = conn
                        output = PropNode(unary_conn, [output])
                conn_before = None
                first = None
                for conn in binary:
                    if len(first_conn) > len(conn) and first_conn[-len(conn):] == conn:
                        conn_before = first_conn[-len(conn):]
                        first = first_conn[:-len(conn)]
                        output = PropNode(conn_before, [PropNode.parse(first), output])
                        break
                if unary_conn == None and conn_before == None:
                    raise ParsingError(ParsingError.note)

            if len(conn_rest) > 0:
                conn_after = None
                rest = None
                for conn in binary:
                    if len(conn_rest) > len(conn) and conn_rest[:len(conn)] == conn:
                        conn_after = conn_rest[:len(conn)]
                        rest = conn_rest[len(conn):]
                        output = PropNode(conn_after, [output, PropNode.parse(rest)])
                        break
                if conn_after == None:
                    raise ParsingError(ParsingError.note)
            
            return output

        for conn in binary:
            if len(string)>1 and (conn in string):
                idx = string.index(conn)
                first = string[:idx]
                main_conn = string[idx:idx+len(conn)]
                rest = string[idx+len(conn):]

                if len(first) == 0 or len(rest)==0:
                    raise ParsingError(ParsingError.note)

                return PropNode(main_conn, [PropNode.parse(first), PropNode.parse(rest)])
        
        for conn in unary:
            if len(string) > len(conn) and string[:len(conn)] == conn:
                return PropNode(conn, [PropNode.parse(string[len(conn):])])

        raise ParsingError(ParsingError.note)