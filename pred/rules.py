from prop.symbols import *

rules = {
    r'\wedge E': '%s',
    r'\wedge I': '%s, %s',
    r'\vee E': '%s, %s-%s, %s-%s',
    r'\vee I': '%s',
    r'\to E': '%s, %s',
    r'\to I': '%s-%s',
    r'\neg E': '%s',
    r'\neg I': '%s-%s',
    r'\leftrightarrow E': '%s, %s',
    r'\leftrightarrow I': '%s-%s, %s-%s',
    r'\bot E': '%s',
    r'\bot I': '%s, %s',
    r'RAA': '%s-%s',
    r'EFQ': '%s',
    r'R': '%s',
    r'= I': '',
    r'= E': '%s, %s',
    r'\forall I': '%s-%s',
    r'\forall E': '%s',
    r'\exists I': '%s',
    r'\exists E': '%s, %s-%s',
}

class RuleError(LogicError):
    pass

class CitationError(RuleError):
    pass

class Rule():
    def __init__(self, name, cit_lines):
        if name not in rules:
            raise RuleError("can't recognize rule name")
        self.name = name
        self.cit_lines = cit_lines
        try:
            if '%s' in rules[name]:
                self.cit = rules[name]%cit_lines
            else:
                self.cit = ''
        except TypeError:
            raise RuleError(f'incorrect number of lines for rule {name}')
    
    def latex_name(name):
        return name.replace(r'\to', r'\to \!').replace(r'=', r'= \!').replace(r'\leftrightarrow', r'\leftrightarrow \!')

    def latex(self):
        name = Rule.latex_name(self.name)
        citation = self.cit.replace(r'-', r'\text{-}')
        return f'{name}\; {citation}'
    
    def __repr__(self):
        return f'Rule({self.name}, {self.cit})'
    
    def parse(string):
        original = string
        string = string.replace(' ', '')
        name = None
        for rule_name in rules:
            rule_name_no_space = rule_name.replace(' ', '')
            if string[:len(rule_name_no_space)] == rule_name_no_space:
                string = string[len(rule_name_no_space):]
                name = rule_name
                break
        if name == None:
            raise RuleError("We couldn't parse this rule name.")
        
        if len(string) > 0 and string[0] == ',': string = string[1:]

        original_format = string

        citation_error_message = f"""We couldn't parse the line citation "{original_format}". As a reminder, the line citation for ${Rule.latex_name(name)}$ should be of the form {rules[name]%(('#',)*rules[name].count('%s'))} where # is a line number."""

        if rules[name] == '':
            citation_error_message = f"""We couldn't parse the line citation "{original_format}". As a reminder, there should be no lines cited for ${Rule.latex_name(name)}$."""
            if string != '':
                raise CitationError(citation_error_message)
            else:
                return Rule(name, ())

        original_format2 = string
        original_format3 = string

        overall_check = string
        for i in range(10):
            overall_check = overall_check.replace(str(i), '')
        overall_check = overall_check.replace(',', '').replace('-', '')

        if len(overall_check) > 0:
            raise CitationError(citation_error_message)

        format = rules[name].replace(' ', '').replace('%s', '')  
        for i in range(10):
            string = string.replace(str(i), '')

        if len(format) != len(string):
            raise CitationError(citation_error_message) 
        for format_char, string_char in zip(format, string):
            if format_char=='_':
                continue
            if format_char != string_char:
                raise CitationError(citation_error_message)
        
        number_pieces_string = original_format2.replace('-',',').split(',')
        number_pieces_format = rules[name].replace(' ', '').replace('-',',').split(',')
        if len(number_pieces_string)!=len(number_pieces_format):
            raise CitationError(citation_error_message)
        for piece in number_pieces_string:
            if len(piece) == 0:
                raise CitationError(citation_error_message)

        commas_sep_list = original_format3.replace(' ', '').split(',')
        already_seen = []
        for el in commas_sep_list:
            if '-' in el:
                continue
            if el in already_seen:
                raise CitationError('You cannot cite the same line twice.')
            else:
                already_seen.append(el)
        
        format_tuple = tuple(original_format.replace('-', ',').split(','))
        return Rule(name, format_tuple)