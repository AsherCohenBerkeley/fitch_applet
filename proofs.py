from formula import *
from rules import *

class ProofError(LogicError):
    pass

class Blank():
    def __init__(self):
        pass

    def latex(self):
        return ''

class ProofLine():
    def __init__(self, formula, rule):
        if not (isinstance(formula, Blank) or isinstance(formula, PropNode)):
            raise ProofError('trying to create proofline with syntactically incorrect formula')
        if not (isinstance(rule, Blank) or isinstance(rule, Rule)):
            raise ProofError('trying to create proofline with syntactically incorrect rule')
        self.formula = formula
        self.rule = rule
    
    def __repr__(self):
        return f'ProofLine({self.formula.__repr__()}, {self.rule.__repr__()})'

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
        elif isinstance(subproof, Proof):
            n_new_lines = subproof.n_lines
            subproof.parent = self
        else:
            raise ProofError('adding object with wrong type to proof')
        self.subproofs.append(subproof)
        self.update_n_lines(n_new_lines)

    def remove_last(self):
        if len(self.subproofs) == 0:
            raise ProofError('trying to remove line from proof with no deduction lines')
        
        if isinstance(self.subproofs[-1], ProofLine):
            self.subproofs = self.subproofs[:-1]
            self.update_n_lines(-1)
        else:
            self.subproofs[-1].remove_last()

# z = Proof([PropNode.parse(r'\neg p')])
# z.add_last(ProofLine(PropNode.parse(r'p \to q'), Rule.parse(r'\neg E 2')))
# z.add_last(ProofLine(PropNode.parse(r'(p \to q) \to p'), Rule.parse(r'R 1')))
# z.add_last(ProofLine(PropNode.parse(r'p'), Rule.parse(r'\to E 3,4')))

# y = Proof([PropNode.parse(r'(p \to q) \to p')])

# x = Proof([])
# x.add_last(y)
# x.add_last(ProofLine(PropNode.parse(r'((p \to q) \to p) \to p'), Rule.parse(r'\to I 1-7')))

# y.add_last(z)
# y.add_last(ProofLine(PropNode.parse(r'p'), Rule.parse(r'RAA 2-6')))

# z.add_last(ProofLine(PropNode.parse(r'p \wedge \neg p'), Rule.parse(r'\wedge I 2,5')))