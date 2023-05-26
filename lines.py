from formula import *
from rules import *

class LineError(LogicError):
    pass

class Blank():
    def __init__(self):
        pass

    def latex(self):
        return ''

class ProofLine():
    pass

class AssumptionLine(ProofLine):
    def __init__(self, formula):
        if not (isinstance(formula, Blank) or isinstance(formula, PropNode)):
            raise LineError('trying to create proofline with syntactically incorrect formula')
        self.formula = formula
        self.parent_proof = None
    
    def __repr__(self):
        return f'AssumptionLine({self.formula.__repr__()})'
    
    def change(self, formula):
        self.formula = formula

class DeductionLine(ProofLine):
    def __init__(self, formula, rule):
        if not (isinstance(formula, Blank) or isinstance(formula, PropNode)):
            raise LineError('trying to create proofline with syntactically incorrect formula')
        if not (isinstance(rule, Blank) or isinstance(rule, Rule)):
            raise LineError('trying to create proofline with syntactically incorrect rule')
        self.formula = formula
        self.rule = rule
        self.parent_proof = None
    
    def __repr__(self):
        return f'DeductionLine({self.formula.__repr__()}, {self.rule.__repr__()})'
    
    def change(self, formula, rule):
        self.formula = formula
        self.rule = rule