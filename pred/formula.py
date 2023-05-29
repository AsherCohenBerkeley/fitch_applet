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
            return Pred_Term('func', string[0], list(map(Pred_Term.parse, string[2:-1].split(','))))
        raise TermError(ParsingError.note)

def random_pred_term_tree(min_depth = 0, max_depth = 2, var = None, const = None, func = None):
    #default values
    if var == None: var = ["x", "y", "z"] #lowercase, single letter
    if const == None: const = [] #lowercase, multi letter
    if func == None: func = [] #(uppercase, int) tuple

    n = random.randint(min_depth, max_depth)

    #base case
    if n == 0 or func == []: 
        #store formula
        form = random.choice(var+const)
        #store free vars
        free = set()
        #if form is a variable, add to free variables 
        if form in var: 
            free |= {form}
            return (Pred_Term("var",form,None), free)
        else:
            return (Pred_Term("const",form,None), free)
    #recursive call
    else:
        (func_sym, arity) = random.choice(func)
        inputs = []
        free = set()
        for i in range(arity):
            (sub_form, sub_free) = random_pred_term_tree(max(0,min_depth-1),max_depth-1, var, const, func)
            inputs.append(sub_form)
            free |= sub_free
        return (Pred_Term("func", func_sym, inputs), free)

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
            if self.value == r'\neg':
                return rf'\neg {self.sub[0].latex()}'
            return f'({self.sub[0].latex()} {self.value} {self.sub[1].latex()})'
    def parse(string):
        string = string.replace(' ', '')
        string = string.replace(r'\rightarrow', r'\to')
        string = string.replace(r'\all', r'\forall')

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
            return Pred_Form.parse(string[1:-1])

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
                return Pred_Form('conn', conn, [Pred_Form.parse(string[len(conn):])])

        for q in quants:
            if len(string) > len(q)+2 and q == string[:len(q)]:
                return Pred_Form('quant', f'{q} {string[len(q)]}.', [Pred_Form.parse(string[len(q)+1:])])

        if string[1] == '(' and string[-1] == ')':
            pred_name = string[0]
            if not (ord('A') <= ord(pred_name) <= ord('Z')):
                raise FormulaError(ParsingError.note)
            return Pred_Form('pred', pred_name, list(map(Pred_Term.parse, string[2:-1].split(','))))

        if '=' in string:
            eq_idx = string.index('=')
            before_eq = string[:eq_idx]
            after_eq = string[eq_idx+1:]
            try:
                return Pred_Form('identity', '=', [Pred_Term.parse(before_eq), Pred_Term.parse(after_eq)])
            except ParsingError:
                pass
        
        raise FormulaError(ParsingError.note)

def identical_twins_pred(tree):
    if tree.ctgy == 'identity':
        return tree.sub[0].__repr__() == tree.sub[1].__repr__()
    if tree.ctgy == 'pred':
        return False
    if tree.ctgy == 'quant':
        return identical_twins_pred(tree.sub[0])
    if tree.ctgy == 'conn':
        if tree.value == '-':
            return identical_twins_pred(tree.sub[0])
        return identical_twins_pred(tree.sub[0]) or tree.sub[0].__repr__() == tree.sub[1].__repr__() or identical_twins_pred(tree.sub[1])

def random_pred_form_tree(min_depth = 0, max_depth = 2, var = None, const = None, func = None, pred = None, identity = False):
    #language basics
    connectives = ['-', '&', '|', ' -> ', ' <-> ']
    quantifiers = ["all", "exists"]

    #default values
    if var == None: var = ["x", "y"] #lowercase, single letter
    if const == None: const = [] #lowercase, multi letter
    if func == None: func = [] #(uppercase, int) tuple
    if pred == None: pred = [("pred_P", 1), ("pred_Q", 1)] #(lowercase multi letter starting with pred_, int) tuple

    #skew towards more complicated formulas
    n = random.randint(min_depth, max_depth)

    #atomic formula
    if n == 0:
        if identity: m = random.random()
        else: m = 1
        # 50% chance of identity statement (if identity is True)
        if m < 0.5:
            (term1, free1) = random_pred_term_tree(max(0, min_depth-1), max(0,max_depth-1), var, const, func)
            (term2, free2) = random_pred_term_tree(max(0, min_depth-1), max(0,max_depth-1), var, const, func)
            return (Pred_Form("identity", "=", [term1, term2]), free1 | free2)
        else:
            (pred_sym, arity) = random.choice(pred)
            inputs = []
            free = set()
            for i in range(arity):
                (sub_term, sub_free) = random_pred_term_tree(max(0, min_depth-1), max(0,max_depth-1), var, const, func)
                inputs.append(sub_term)
                free |= sub_free
            return (Pred_Form("pred",pred_sym,inputs), free)
    #complex formula
    else:
        m = random.random()
        #generate one subformula at random
        (sub1, free1) = random_pred_form_tree(max(0, min_depth-1), max_depth-1, var, const, func, pred, identity)
        #80% chance of getting a quantifier
        if m < 0.8 and free1 != set():
            quant = random.choice(quantifiers)
            variable = random.choice(list(free1))
            return (Pred_Form("quant",f"{quant} {variable}.", [sub1]), free1 - {variable})
        else:
            con = random.choice(connectives)
            if con == "-":
                return (Pred_Form("conn","-",[sub1]), free1)
            else:
                (sub2, free2) = random_pred_form_tree(max(0, min_depth-1), max_depth-1, var, const, func, pred, identity)
                return (Pred_Form("conn",con,[sub1,sub2]), free1 | free2)

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
            if tree.value == "-":
                return aux(tree.sub[0], var, term_free, bound_so_far)
            return aux(tree.sub[0], var, term_free, bound_so_far) and aux(tree.sub[1], var, term_free, bound_so_far)
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

def substitute_form(tree, var, term, term_free):
    if not substitutable(tree, var, term_free): return "not substitutable"
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
            list(map(lambda subterm: substitute_form(subterm, var, term, term_free), tree.sub))
            )
    if tree.ctgy == "quant":
        variable = tree.value.split(" ")[1][:-1]
        if variable in term_free: return tree
        if variable == var: return tree
        else: return Pred_Form(
            tree.ctgy, 
            tree.value, 
            list(map(lambda subterm: substitute_form(subterm, var, term, term_free), tree.sub))
            )