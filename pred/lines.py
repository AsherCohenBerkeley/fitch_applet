from pred.formula import *
from pred.rules import *

class LineError(LogicError):
    pass

class Blank():
    def __init__(self):
        pass

    def latex(self):
        return ''

class ProofLine():
    pass

class AssumptionLine():
    pass

class NormalAssumptionLine(AssumptionLine):
    def __init__(self, formula):
        if not (isinstance(formula, Blank) or isinstance(formula, Pred_Form)):
            raise LineError('trying to create proofline with syntactically incorrect formula')
        self.formula = formula
        self.parent_proof = None
    
    def __repr__(self):
        return f'NormalAssumptionLine({self.formula.__repr__()})'
    
    def change(self, formula):
        self.formula = formula

    def consts(self):
        return self.formula.consts()
    
class UnivIntroAssumptionLine(AssumptionLine):
    def __init__(self, const_name):
        self.const_name = const_name
        self.parent_proof = None
    
    def __repr__(self):
        return f'UnivIntroAssumptionLine({self.const_name})'
    
    def change(self, const_name):
        self.const_name = const_name
    
    def consts(self):
        return [self.const_name]

class DeductionLine(ProofLine):
    def __init__(self, formula, rule):
        if not (isinstance(formula, Blank) or isinstance(formula, Pred_Form)):
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
    
    def consts(self):
        return self.formula.consts()