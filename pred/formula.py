from pred.symbols import *
import random

class ParsingError(LogicError):
    note = "We couldn't parse the above formula. Are you sure it's written in LaTeX with lowercase letters?"
    pass

class TermError(ParsingError):
    pass

class FormulaError(ParsingError):
    pass

class Pred_Term:
    def __init__(self, ctgy, value, sub):
        self.ctgy = ctgy
        self.value = value
        self.sub = sub
    def __repr__(self):
        return f'Pred_Term({self.ctgy, self.value, self.sub})'
    def latex(self):
        if self.ctgy == 'func':
            output = f'{self.value}('
            for sub in self.sub:
                output += sub.latex() + ','
            output = output[:-1] + ')'
            return output
        else:
            return self.value
    def free(self):
        if self.ctgy == 'const':
            return set([])
        elif self.ctgy == 'var':
            return {self.value}
        elif self.ctgy == 'func':
            output = set([])
            for sub in self.sub:
                output = output | sub.free()
            return output
    def eq_syntax(self, other):
        return self.latex() == other.latex()
    def parse(string):
        string = string.replace(' ', '')
        if len(string) == 0:
            raise TermError(ParsingError.note)
        if string[0] == 'c' and len(string) <= 3:
            return Pred_Term('const', string, None)
        elif len(string) == 1:
            return Pred_Term('var', string, None)
        elif string[1] == '(' and string[-1] == ')':
            try:
                return Pred_Term('func', string[0], list(map(Pred_Term.parse, string[2:-1].split(','))))
            except TermError:
                return Pred_Term('func', string[0], [Pred_Term.parse(string[2:-1])])
        raise TermError(ParsingError.note)

def indices(string, sub):
	if sub not in string:
		return []
	else:
		first_idx = string.index(sub)
		output = [first_idx]
		for idx in indices(string[first_idx+len(sub):], sub):
			output.append(first_idx+len(sub)+idx)
		return output

class Pred_Form:
    def __init__(self, ctgy, value, sub):
        self.ctgy = ctgy
        self.name = value
        self.value = value
        self.sub = sub
    def __repr__(self):
        return f'Pred_Form({self.ctgy, self.value, self.sub})'
    def eq_syntax(self1,self2):
        return self1.latex() == self2.latex()
    def latex(self):
        if self.ctgy == 'identity':
            return f'{self.sub[0].latex()} = {self.sub[1].latex()}'
        if self.ctgy == 'pred':
            output = f'{self.value}('
            for sub in self.sub:
                output += sub.latex() + ','
            output = output[:-1] + ')'
            return output
        if self.ctgy == 'quant':
            return f'{self.value[:-1]} {self.sub[0].latex()}'
        if self.ctgy == 'conn':
            if self.value in zeroary:
                return self.value
            elif self.value in unary:
                return rf'{self.value} {self.sub[0].latex()}'
            else:
                return f'({self.sub[0].latex()} {self.value} {self.sub[1].latex()})'
    def free(self):
        def aux(self, bound_so_far):
            if self.ctgy == 'identity':
                return (self.sub[0].free()|self.sub[1].free()) - bound_so_far
            if self.ctgy == 'pred':
                output = set([])
                for sub in self.sub:
                    output = output | sub.free()
                return output - bound_so_far
            if self.ctgy == 'quant':
                return aux(self.sub[0],bound_so_far|{self.value[-2]})
            if self.ctgy == 'conn':
                output = set([])
                for sub in self.sub:
                    output = output | aux(sub, bound_so_far)
                return output
        return aux(self, set([]))
    def parse(string):
        string = string.replace(' ', '')
        string = string.replace(r'\rightarrow', r'\to')
        string = string.replace(r'\all', r'\forall')

        for conn in zeroary:
            if string == conn:
                return Pred_Form('conn', conn, [])

        if len(string) <= 2:
            raise FormulaError(ParsingError.note)

        p_balance = 0
        for char in string:

            if char == '(':
                p_balance += 1
            elif char == ')':
                p_balance -= 1
            
            if p_balance < 0:
                raise FormulaError(ParsingError.note)
        if p_balance != 0:
            FormulaError(ParsingError.note)

        if string[0] == '(' and string[-1] == ')':
            try:
                return Pred_Form.parse(string[1:-1])
            except ParsingError:
                pass

        for conn in binary:
            for conn_idx in indices(string, conn):
                before_conn = string[:conn_idx]
                after_conn = string[conn_idx+len(conn):]
                try:
                    return Pred_Form('conn', conn, [Pred_Form.parse(before_conn), Pred_Form.parse(after_conn)])
                except ParsingError:
                    pass
        
        for conn in unary:
            if len(string) > len(conn) and conn == string[:len(conn)]:
                try:
                    return Pred_Form('conn', conn, [Pred_Form.parse(string[len(conn):])])
                except ParsingError:
                    pass

        for q in quants:
            if len(string) > len(q)+2 and q == string[:len(q)]:
                try:
                    return Pred_Form('quant', f'{q} {string[len(q)]}.', [Pred_Form.parse(string[len(q)+1:])])
                except ParsingError:
                    pass

        if string[1] == '(' and string[-1] == ')':
            pred_name = string[0]
            if (ord('A') <= ord(pred_name) <= ord('Z')):
                try:
                    return Pred_Form('pred', pred_name, list(map(Pred_Term.parse, string[2:-1].split(','))))
                except ParsingError:
                    pass

        if '=' in string:
            eq_idx = string.index('=')
            before_eq = string[:eq_idx]
            after_eq = string[eq_idx+1:]
            try:
                return Pred_Form('identity', '=', [Pred_Term.parse(before_eq), Pred_Term.parse(after_eq)])
            except ParsingError:
                pass
        
        raise FormulaError(ParsingError.note)

class SubstitutionError(LogicError):
    pass

def substitutable(tree, var, term_free):
    def aux(tree, var, term_free, bound_so_far):
        """substitute term for var in tree"""
        if tree.ctgy == "identity" or tree.ctgy == 'pred':
            if var in tree.__repr__():
                output = True
                for term_variable in term_free:
                    output = output and not (term_variable in bound_so_far)
                return output
            else:
                return True
        if tree.ctgy == "quant":
            y = tree.value.split(" ")[1][:-1]
            if y == var:
                return True
            else:
                return aux(tree.sub[0], var, term_free, bound_so_far|{y})
        if tree.ctgy == "conn":
            output = True
            for sub_tree in tree.sub:
                output = output and aux(sub_tree, var, term_free, bound_so_far)
            return output
    return aux(tree, var, term_free, set())

def substitute_term(tree, var, term):
    if tree.ctgy == "const":
        return tree
    if tree.ctgy == "var":
        if tree.value == var:
            return term
        else:
            return tree
    return Pred_Term(
        tree.ctgy,
        tree.value,
        list(
            map(
                lambda subtree: substitute_term(subtree, var, term),
                tree.sub
                )
            )
        )

def substitute_form(tree, var, term):
    term_free = term.free()
    if not substitutable(tree, var, term_free):
        raise SubstitutionError('trying to substitute something that is not substitutable')
    if tree.ctgy=="identity" or tree.ctgy == "pred":
        return Pred_Form(
            tree.ctgy, 
            tree.value, 
            list(map(lambda subterm: substitute_term(subterm, var, term), tree.sub))
            )
    if tree.ctgy=="conn":
        return Pred_Form(
            tree.ctgy, 
            tree.value, 
            list(map(lambda subterm: substitute_form(subterm, var, term), tree.sub))
            )
    if tree.ctgy == "quant":
        variable = tree.value.split(" ")[1][:-1]
        if variable in term_free: return tree
        if variable == var: return tree
        else: return Pred_Form(
            tree.ctgy, 
            tree.value, 
            list(map(lambda subterm: substitute_form(subterm, var, term), tree.sub))
            )

def substitute_TT_term(tree, t1, t2):
    """
    t1 old
    t2 new
    """
    if tree.eq_syntax(t1):
        return t2
    elif tree.sub == None:
        return tree
    else:
        return Pred_Term(
        tree.ctgy,
        tree.value,
        list(
            map(
                lambda subtree: substitute_TT_term(subtree, t1, t2),
                tree.sub
                )
            )
        )

def all_substitute_TT_term(tree, t1, t2):
    """
    t1 old
    t2 new
    """
    if tree.eq_syntax(t1):
        return [t2]
    elif tree.sub == None:
        return [tree]
    else:
        output = []
        for TF_lst in all_TF_lst(len(tree.sub)):
            new_sub = []
            for boolean, subtree in zip(TF_lst, tree.sub):
                if boolean:
                    new_sub.append(substitute_TT_term(subtree, t1, t2))
                else:
                    new_sub.append(subtree)
            output.append(Pred_Form(tree.ctgy, tree.value, new_sub))
        return output

def substitute_TT_form(tree, t1, t2):
    if tree.ctgy=="identity" or tree.ctgy == "pred":
        return Pred_Form(
        tree.ctgy,
        tree.value,
        list(
            map(
                lambda subtree: substitute_TT_term(subtree, t1, t2),
                tree.sub
                )
            )
        )
    if tree.ctgy=="conn":
        return Pred_Form(
        tree.ctgy,
        tree.value,
        list(
            map(
                lambda subtree: substitute_TT_form(subtree, t1, t2),
                tree.sub
                )
            )
        )
    if tree.ctgy == "quant":
        return Pred_Form(
        tree.ctgy,
        tree.value,
        list(
            map(
                lambda subtree: substitute_TT_form(subtree, t1, t2),
                tree.sub
                )
            )
        )

def all_substitute_TT_form(tree, t1, t2):
    if tree.ctgy=="identity" or tree.ctgy == "pred":
        output = []
        for TF_lst in all_TF_lst(len(tree.sub)):
            new_sub = []
            for boolean, subtree in zip(TF_lst, tree.sub):
                if boolean:
                    new_sub.append(substitute_TT_term(subtree, t1, t2))
                else:
                    new_sub.append(subtree)
            output.append(Pred_Form(tree.ctgy, tree.value, new_sub))
        return output
    if tree.ctgy=="conn":
        output = []
        for TF_lst in all_TF_lst(len(tree.sub)):
            new_sub = []
            for boolean, subtree in zip(TF_lst, tree.sub):
                if boolean:
                    new_sub.append(substitute_TT_form(subtree, t1, t2))
                else:
                    new_sub.append(subtree)
            output.append(Pred_Form(tree.ctgy, tree.value, new_sub))
        return output
    if tree.ctgy == "quant":
        output = []
        for TF_lst in all_TF_lst(len(tree.sub)):
            new_sub = []
            for boolean, subtree in zip(TF_lst, tree.sub):
                if boolean:
                    new_sub.append(substitute_TT_form(subtree, t1, t2))
                else:
                    new_sub.append(subtree)
            output.append(Pred_Form(tree.ctgy, tree.value, new_sub))
        return output

def all_TF_lst(n):
    if n == 0:
        return [[]]
    sub = all_TF_lst(n-1)
    output = []
    for lst in sub:
        output.append([True]+lst)
        output.append([False]+lst)
    return output

def all_substitute_term(tree, var, term):
    if tree.ctgy == "const":
        return tree
    if tree.ctgy == "var":
        output = [tree]
        if tree.value == var:
            output.append(term)
        return output
    if tree.ctgy =='func':
        output = []
        for TF_lst in all_TF_lst(len(tree.sub)):
            new_sub = []
            for boolean, subtree in zip(TF_lst, tree.sub):
                if boolean:
                    new_sub.append(substitute_term(subtree, var, term))
                else:
                    new_sub.append(subtree)
            output.append(Pred_Term(tree.ctgy, tree.value, new_sub))
        return output

def all_substitute_form(tree, var, term):
    term_free = term.free()
    if not substitutable(tree, var, term_free):
        raise SubstitutionError('trying to substitute something that is not substitutable')
    if tree.ctgy=="identity" or tree.ctgy == "pred":
        output = []
        for TF_lst in all_TF_lst(len(tree.sub)):
            new_sub = []
            for boolean, subtree in zip(TF_lst, tree.sub):
                if boolean:
                    new_sub.append(substitute_term(subtree, var, term))
                else:
                    new_sub.append(subtree)
            output.append(Pred_Form(tree.ctgy, tree.value, new_sub))
        return output
    if tree.ctgy=="conn":
        output = []
        for TF_lst in all_TF_lst(len(tree.sub)):
            new_sub = []
            for boolean, subtree in zip(TF_lst, tree.sub):
                if boolean:
                    new_sub.append(substitute_form(subtree, var, term))
                else:
                    new_sub.append(subtree)
            output.append(Pred_Form(tree.ctgy, tree.value, new_sub))
        return output
    if tree.ctgy == "quant":
        variable = tree.value.split(" ")[1][:-1]
        if variable in term_free: return [tree]
        if variable == var: return [tree]
        else: 
            output = []
            for TF_lst in all_TF_lst(len(tree.sub)):
                new_sub = []
                for boolean, subtree in zip(TF_lst, tree.sub):
                    if boolean:
                        new_sub.append(substitute_form(subtree, var, term))
                    else:
                        new_sub.append(subtree)
                output.append(Pred_Form(tree.ctgy, tree.value, new_sub))
            return output

def substitute_compare_term(unsubbed, subbed, var_name):
    if unsubbed.ctgy == 'const':
        if unsubbed.eq_syntax(subbed):
            return []
        else:
            return [None]
    elif unsubbed.ctgy == 'var':
        if unsubbed.value == var_name:
            return [subbed]
        else:
            if unsubbed.eq_syntax(subbed):
                return []
            else:
                return [None]
    else:
        if not (unsubbed.ctgy == subbed.ctgy):
            return [None]
        if not (len(unsubbed.sub) == len(subbed.sub)):
            return [None]
        output = []
        for unsubbed_sub, subbed_sub in zip(unsubbed.sub, subbed.sub):
            output += substitute_compare_term(unsubbed_sub, subbed_sub, var_name)
        return output
    
def substitute_compare_form(unsubbed, subbed, var_name):
    if unsubbed.ctgy=="identity" or unsubbed.ctgy == "pred":
        if not (unsubbed.ctgy == subbed.ctgy):
            return [None]
        if not (len(unsubbed.sub) == len(subbed.sub)):
            return [None]
        output = []
        for unsubbed_sub, subbed_sub in zip(unsubbed.sub, subbed.sub):
            output += substitute_compare_term(unsubbed_sub, subbed_sub, var_name)
        return output
    if unsubbed.ctgy=="conn":
        if not (unsubbed.ctgy == subbed.ctgy):
            return [None]
        if not (len(unsubbed.sub) == len(subbed.sub)):
            return [None]
        output = []
        for unsubbed_sub, subbed_sub in zip(unsubbed.sub, subbed.sub):
            output += substitute_compare_form(unsubbed_sub, subbed_sub, var_name)
        return output
    if unsubbed.ctgy == "quant":
        if not (unsubbed.ctgy == subbed.ctgy):
            return [None]
        quant_var = unsubbed.value[-2]
        if quant_var == var_name:
            if unsubbed.eq_syntax(subbed):
                return []
            else:
                return [None]
        else:
            if not (unsubbed.value == subbed.value):
                return [None]
            return substitute_compare_form(unsubbed.sub[0], subbed.sub[0], var_name)
        
def substitute_compare_total(unsubbed, subbed, var_name):
    lst = substitute_compare_form(unsubbed, subbed, var_name)
    if len(lst) == 0:
        return True
    if None in lst:
        return False
    output = True
    t = lst[0]
    for t_prime in lst[1:]:
        output = output and t.eq_syntax(t_prime)
    output = output and substitutable(unsubbed, var_name, t.free())
    return output

# print(substitute_compare_total(Pred_Form.parse(r'\forall y x = f(x)'), Pred_Form.parse(r'\forall y y = f(y)'), 'x'))