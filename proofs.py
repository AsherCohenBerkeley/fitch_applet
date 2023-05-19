from formula import *
from rules import *

class ProofError(LogicError):
    pass

class Blank():
    def __init__(self):
        pass

    def latex(self):
        return ''

class Comment():
    def __init__(self, line_number, comment):
        self.comment = comment

class GoodComment(Comment):
    def __init__(self, line_number, comment=None):
        self.comment = f'Everything good on line {line_number}. ✅'

class BadComment(Comment):
    pass

class ProofLine():
    def __init__(self, formula, rule):
        if not (isinstance(formula, Blank) or isinstance(formula, PropNode)):
            raise ProofError('trying to create proofline with syntactically incorrect formula')
        if not (isinstance(rule, Blank) or isinstance(rule, Rule)):
            raise ProofError('trying to create proofline with syntactically incorrect rule')
        self.formula = formula
        self.rule = rule
        self.parent_proof = None
    
    def __repr__(self):
        return f'ProofLine({self.formula.__repr__()}, {self.rule.__repr__()})'
    
    def change(self, formula, rule):
        self.formula = formula
        self.rule = rule

class Proof():
    def __init__(self, assumptions):
        self.assumptions = []

        for a in assumptions:
            if not isinstance(a, PropNode):
                raise ProofError('wrong type for assumption')
            self.assumptions.append(a)

        self.n_lines = len(self.assumptions)
        self.parent = None
        self.subproofs = []

    def __str__(self):
        def aux(self, n):
            output = ''
            for a in self.assumptions:
                output += '    '*n+ a.latex() + '\n'
            output += '    '*n + '-----\n'
            for subproof in self.subproofs:
                if isinstance(subproof, ProofLine):
                    output += ('    '*n + subproof.formula.latex() + ' || ' +  subproof.rule.latex() + '\n') 
                elif isinstance(subproof, Proof):
                    output += aux(subproof, n+1)
            return output
        return aux(self, 0)
    
    def latex(self):
        def first(self):
            output = ''
            output += r"\begin{array}{l}" + '\n'
            for i in range(self.n_lines):
                output += rf"{i+1} \\" + '\n'
            output += r"\end{array}"+ '\n'
            return output
        
        def second(self):
            output = ''
            output += r"\begin{array}{|l}"+ '\n'

            for a in self.assumptions:
                output += a.latex() + r'\\'+ '\n'
            if len(self.assumptions) > 0:
                output += r'\hline'+ '\n'
            
            for subproof in self.subproofs:
                if isinstance(subproof, ProofLine):
                    output += subproof.formula.latex()
                else:
                    output += second(subproof)
                output += r'\\'+ '\n'
            
            output += r"\end{array}"+ '\n'
            return output
        
        def third(self):
            output = ''

            if self.parent == None:
                output += r'\begin{array}{l}'+ '\n'

            for a in self.assumptions:
                output += r'\\'+ '\n'
            
            for subproof in self.subproofs:
                if isinstance(subproof, ProofLine):
                    output += subproof.rule.latex() + r'\\'+ '\n'
                else:
                    output += third(subproof)
            
            if self.parent == None:
                output += r'\end{array}'+ '\n'
            
            return output
        
        return r"\def\arraystretch{1.5}\begin{array}{l l}" + '\n' + first(self) + '\n' + second(self) + '\n' + '&' + '\n' + third(self) + '\n' +  r"\end{array}"

    def update_n_lines(self, n_new_lines):
        self.n_lines += n_new_lines
        if self.parent is not None:
            self.parent.update_n_lines(n_new_lines)

    def add_last(self, subproof):
        if isinstance(subproof, ProofLine):
            n_new_lines = 1
            subproof.parent_proof = self  
        elif isinstance(subproof, Proof):
            n_new_lines = subproof.n_lines
            subproof.parent = self
        else:
            raise ProofError('adding object with wrong type to proof')
        self.subproofs.append(subproof)
        self.update_n_lines(n_new_lines)

    def remove_last(self):
        if len(self.subproofs) == 0:
            raise ProofError('trying to remove lines from main proof when there are no lines to remove')
        
        if isinstance(self.subproofs[-1], ProofLine):
            self.subproofs = self.subproofs[:-1]
            self.update_n_lines(-1)
            return self
        else:
            return self.subproofs[-1].remove_last()
    
    def self_delete(self):
        if self.parent is None:
            raise ProofError('trying to delete main proof')
        
        self.update_n_lines(-self.n_lines)

        self.parent.subproofs.remove(self)
    
    def pure_list(self):
        output = []
        output += self.assumptions
        for subproof in self.subproofs:
            if isinstance(subproof, ProofLine):
                output.append(subproof)
            else:
                output += subproof.pure_list()
        return output
    
    def find(self, n):
        try:
            return self.pure_list()[n-1]
        except IndexError:
            raise ProofError('trying to find with out of range line number')
        
    def change(self, n, formula, rule):
        if isinstance(self.find(n), ProofLine):
            self.find(n).change(formula, rule)
        else:
            self.find(n).change(formula)
    
    def accessible(self, line_number1, line_number2):
        """
        Checks that line_number1 is accessible from line_number2
        """
        if line_number1 >= line_number2:
            return False
        try:
            line1 = self.find(line_number1)
            line2 = self.find(line_number2)
            parental_proof2 = line2.parent_proof
        except:
            raise ProofError('trying to assess accessibility for assumption line')
        while isinstance(parental_proof2, Proof):
            if line1 in parental_proof2.assumptions+parental_proof2.subproofs:
                return True
            parental_proof2 = parental_proof2.parent
        return False
    
    def check_line(self, n):
        main_line = self.find(n)
        if isinstance(main_line, PropNode):
            return ProofError('checking assumption line')
        
        main_formula, rule_name, cit_line_numbers = main_line.formula, main_line.rule.name, main_line.rule.cit_lines
        
        cit_line_numbers = [int(string) for string in cit_line_numbers]

        cit_formulas = []
        for line_number in cit_line_numbers:
            line = self.find(line_number)
            if isinstance(line, ProofLine):
                line = line.formula
            cit_formulas.append(line)

        if rule_name == r'R':
            for line_number in cit_line_numbers:
                if not self.accessible(line_number, n):
                    return False
            return main_formula.eq_syntax(cit_formulas[0])
        
        elif rule_name == r'\wedge E':
            for line_number in cit_line_numbers:
                if not self.accessible(line_number, n):
                    return False
            return main_formula.eq_syntax(cit_formulas[0].sub[0]) or main_formula.eq_syntax(cit_formulas[0].sub[1])
        
        elif rule_name == r'\wedge I':
            for line_number in cit_line_numbers:
                if not self.accessible(line_number, n):
                    return False
            return main_formula.eq_syntax(PropNode(r'\wedge',[cit_formulas[0], cit_formulas[1]])) or main_formula.eq_syntax(PropNode(r'\wedge',[cit_formulas[1], cit_formulas[0]]))
        
        elif rule_name == r'\to E':
            for line_number in cit_line_numbers:
                if not self.accessible(line_number, n):
                    return False
            for cit_formula in cit_formulas:
                impl_formula = cit_formula
                ant_formula = [form for form in cit_formulas if form!=cit_formula][0]
                if impl_formula.name == r'\to' and impl_formula.sub[0].eq_syntax(ant_formula) and impl_formula.sub[1].eq_syntax(main_formula):
                    return True
            return False

        





        if rule_name in rules:
            return ProofError('rule not covered by check_line method')

            


        



####################
# A GOOD TEST CASE #
####################

z = Proof([PropNode.parse(r'\neg p')])
z.add_last(ProofLine(PropNode.parse(r'p \to q'), Rule.parse(r'\neg E 2')))
z.add_last(ProofLine(PropNode.parse(r'(p \to q) \to p'), Rule.parse(r'R 1')))
z.add_last(ProofLine(PropNode.parse(r'p'), Rule.parse(r'\to E 3,4')))

y = Proof([PropNode.parse(r'(p \to q) \to p')])

x = Proof([])
x.add_last(y)
x.add_last(ProofLine(PropNode.parse(r'((p \to q) \to p) \to p'), Rule.parse(r'\to I 1-7')))

y.add_last(z)
y.add_last(ProofLine(PropNode.parse(r'p'), Rule.parse(r'RAA 2-6')))

z.add_last(ProofLine(PropNode.parse(r'p \wedge \neg p'), Rule.parse(r'\wedge I 2,5')))

print(x)
print(x.check_line(5))