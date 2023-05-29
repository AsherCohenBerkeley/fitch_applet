from pred.lines import *
from pred.comments import *

class ProofError(LogicError):
    pass

class Proof():
    def __init__(self, assumptions):
        self.assumptions = []

        for a in assumptions:
            if not isinstance(a, AssumptionLine):
                raise ProofError('wrong type for assumption')
            a.parent_proof = self
            self.assumptions.append(a)

        self.n_lines = len(self.assumptions)
        self.parent = None
        self.subproofs = []

    def __str__(self):
        def aux(self, n):
            output = ''
            for a in self.assumptions:
                output += '    '*n+ a.formula.latex() + '\n'
            output += '    '*n + '-----\n'
            for subproof in self.subproofs:
                if isinstance(subproof, DeductionLine):
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
                output += a.formula.latex() + r'\\'+ '\n'
            if len(self.assumptions) > 0:
                output += r'\hline'+ '\n'
            
            for subproof in self.subproofs:
                if isinstance(subproof, DeductionLine):
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

            for _ in self.assumptions:
                output += r'\\'+ '\n'
            
            for subproof in self.subproofs:
                if isinstance(subproof, DeductionLine):
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
        if isinstance(subproof, DeductionLine):
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
        
        if isinstance(self.subproofs[-1], DeductionLine):
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
            if isinstance(subproof, DeductionLine):
                output.append(subproof)
            else:
                output += subproof.pure_list()
        return output
    
    def find(self, n):
        try:
            return self.pure_list()[n-1]
        except IndexError:
            raise ProofError('trying to find with out of range line number')
    
    def find_line_number(self, proofline):
        return self.pure_list().index(proofline) + 1
    
    def first(self):
        return self.pure_list()[0]
    
    def last(self):
        return self.pure_list()[-1]
        
    def change(self, n, formula, rule):
        if isinstance(self.find(n), DeductionLine):
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
        if isinstance(main_line, AssumptionLine):
            return GoodComment()
        
        main_formula, rule_name, cit = main_line.formula, main_line.rule.name, main_line.rule.cit
        
        cit_split = cit.split(',')

        cit_line_numbers = [int(string) for string in cit_split if '-' not in string and len(string) > 0]

        #Deal with individual formulas

        cit_formulas = []
        for line_number in cit_line_numbers:
            if not self.accessible(line_number, n):
                    return BadComment(f'Line {line_number} is not accessible at this line.')
            line = self.find(line_number)
            cit_formulas.append(line.formula)

        #Deal with formula ranges

        cit_subproofs = []
        for string in cit_split:
            if '-' in string:
                line_number1, line_number2 = string.split('-')
                line_number1, line_number2 = int(line_number1), int(line_number2)

                if line_number1 >= n or line_number2 >= n:
                    return BadComment(f'The range {line_number1}-{line_number2} does not come strictly before the line on which it is cited.')

                line1 = self.find(line_number1)
                line2 = self.find(line_number2)
                if not (isinstance(line1, AssumptionLine) and isinstance(line2, DeductionLine)):
                    return BadComment(f'The range {line_number1}-{line_number2} does not encompass a subproof.')
                
                subproof = line2.parent_proof

                main_proof = subproof
                while isinstance(main_proof.parent, Proof):
                    main_proof = main_proof.parent

                if not (len(subproof.assumptions) == 1 and line1 == subproof.assumptions[0]): 
                    return BadComment(f'The range {line_number1}-{line_number2} does not encompass a subproof.')
                
                if not (subproof.parent.parent == None or self.accessible(main_proof.find_line_number(subproof.parent.first()), n)):
                    return BadComment(f'The subproof {line_number1}-{line_number2} is not accessible at this line.')
                
                cit_subproofs.append(subproof)
        
        #Logic of each individual rule

        if rule_name == r'R':
            if main_formula.eq_syntax(cit_formulas[0]):
                return GoodComment()
            else:
                return BadComment('The reiterated formula is different than the cited formula.')
        
        elif rule_name == r'\wedge E':
            cit_formula = cit_formulas[0]
            if not cit_formula.name == r'\wedge':
                return BadComment('The cited formula is not a conjunction.')
            
            if not (main_formula.eq_syntax(cit_formula.sub[0]) or main_formula.eq_syntax(cit_formula.sub[1])):
                return BadComment('The deduced formula is different than both conjuncts of the cited formula.')
            
            return GoodComment()
        
        elif rule_name == r'\wedge I':
            if not main_formula.name == r'\wedge':
                return BadComment('The deduced formula is not a conjunction.')
            
            if not (main_formula.eq_syntax(Pred_Form(r'\wedge',[cit_formulas[0], cit_formulas[1]])) or main_formula.eq_syntax(Pred_Form(r'\wedge',[cit_formulas[1], cit_formulas[0]]))):
                return BadComment('The deduced formula is not the conjunction of the two cited formulas.')
            
            return GoodComment()
        
        elif rule_name == r'\to E':
            impl_formulas = []
            for cit_formula in cit_formulas:
                if cit_formula.name == r'\to':
                    impl_formulas.append(cit_formula)
            
            if len(impl_formulas)==0:
                return BadComment('Neither cited formula is an implication.')
            
            final_impl_formula = None
            final_ant_formula = None

            for impl_formula in impl_formulas:
                ant_formula = [form for form in cit_formulas if form!=impl_formula][0]
                if impl_formula.sub[0].eq_syntax(ant_formula):
                    final_impl_formula = impl_formula
                    final_ant_formula = ant_formula
            
            if final_impl_formula is None:
                return BadComment('Neither cited formula is the antecedent of the other.')
                
            if final_impl_formula.sub[1].eq_syntax(main_formula):
                return GoodComment()
            else:
                return BadComment('The deduced formula is not the consequent of the relevant cited formula.')
        
        elif rule_name == r'\to I':
            if not main_formula.name == r'\to':
                return BadComment('The deduced formula is not an implication.')
            elif not main_formula.sub[0].eq_syntax(cit_subproofs[0].first().formula):
                return BadComment("The antecedent of the deduced formula is not the assumption of the cited subproof.")
            elif not main_formula.sub[1].eq_syntax(cit_subproofs[0].last().formula):
                return BadComment("The consequent of the deduced formula is not the last line of the cited subproof.")
            else:
                return GoodComment()
        
        elif rule_name == r'\leftrightarrow I':
            if not main_formula.name == r'\leftrightarrow':
                return BadComment('The deduced formula is not a biconditional.')
            elif not (cit_subproofs[0].last().formula.eq_syntax(cit_subproofs[1].first().formula)):
                return BadComment('The second subproof does not begin with the last line of the first subproof.')
            elif not (cit_subproofs[1].last().formula.eq_syntax(cit_subproofs[0].first().formula)):
                return BadComment('The second subproof does not end with the first line of the first subproof.')
            elif not ((cit_subproofs[0].first().formula.eq_syntax(main_formula.sub[0]) and cit_subproofs[0].last().formula.eq_syntax(main_formula.sub[1])) or (cit_subproofs[0].first().formula.eq_syntax(main_formula.sub[1]) and cit_subproofs[0].last().formula.eq_syntax(main_formula.sub[0]))):
                return BadComment('The subproofs do not begin and end with the conditionals of the deduced line.')
            else:
                return GoodComment()
        
        elif rule_name == r'\leftrightarrow E':
            bicond_formulas = []
            for cit_formula in cit_formulas:
                if cit_formula.name == r'\leftrightarrow':
                    bicond_formulas.append(cit_formula)
            
            if len(bicond_formulas) == 0:
                return BadComment('Neither cited formula is a biconditional.')

            final_bicond_formula = None
            final_other_formula = None
            for bicond_formula in bicond_formulas:
                other_formula = [formula for formula in cit_formulas if formula != bicond_formula][0]
                if bicond_formula.sub[0].eq_syntax(other_formula) or bicond_formula.sub[1].eq_syntax(other_formula):
                    final_bicond_formula = bicond_formula
                    final_other_formula = other_formula
            
            if not isinstance(final_bicond_formula, Pred_Form):
                return BadComment('The cited biconditional does not have the other cited formula as either of its conditionals.')
            
            if not ((final_bicond_formula.sub[0].eq_syntax(final_other_formula) and final_bicond_formula.sub[1].eq_syntax(main_formula))or(final_bicond_formula.sub[1].eq_syntax(final_other_formula) and final_bicond_formula.sub[0].eq_syntax(main_formula))):
                return 'The cited biconditional does not have as one conditional the cited line and as the other conditional the deduced line.'
            
            return GoodComment()
        
        elif rule_name == r'\neg E':
            cit_formula = cit_formulas[0]
            if not cit_formula.name == r'\neg':
                return BadComment('The cited formula is not a negation.')
            
            if not main_formula.name == r'\to':
                return BadComment('The deduced formula is not an implication.')
            
            if not (main_formula.sub[0].eq_syntax(cit_formula.sub[0])):
                return BadComment('The unnegated version of the cited formula is not the antecedent of the deduced formula.')
            
            return GoodComment()
        
        elif rule_name == r'EFQ':
            cit_formula = cit_formulas[0]
            if not (cit_formula.name == r'\wedge' and (cit_formula.sub[0].eq_syntax(Pred_Form(r'\neg',[cit_formula.sub[1]])) or cit_formula.sub[1].eq_syntax(Pred_Form(r'\neg',[cit_formula.sub[0]])))):
                return BadComment('The cited formula is the conjunction of a formula and its negation.')
            
            return GoodComment()
        
        elif rule_name == r'\bot E':
            cit_formula = cit_formulas[0]
            if not (cit_formula.name == r'\bot'):
                return BadComment('The cited formula is not bottom.')
            
            return GoodComment()
        
        elif rule_name == r'\bot I':
            if not (main_formula.name == r'\bot'):
                return BadComment('The deduced formula is not bottom.')
            
            if not (cit_formulas[0].eq_syntax(Pred_Form(r'\neg',[cit_formulas[1]])) or cit_formulas[1].eq_syntax(Pred_Form(r'\neg',[cit_formulas[0]]))):
                return GoodComment('Neither cited formula is the negation of the other.')

            return GoodComment()
        
        elif rule_name == r'\neg I':
            cit_subproof = cit_subproofs[0]

            if not (main_formula.eq_syntax(Pred_Form(r'\neg', [cit_subproof.first().formula]))):
                return BadComment("The deduced formula is not the negation of cited subproof's assumption.")
            
            if not(cit_subproof.last().formula.eq_syntax(Pred_Form(r'\bot', [])) or (cit_subproof.last().name == r'\wedge' and (cit_subproof.last().sub[0].eq_syntax(Pred_Form(r'\neg',[cit_subproof.last().sub[1]])) or cit_subproof.last().sub[1].eq_syntax(Pred_Form(r'\neg',[cit_subproof.last().sub[0]]))))):
                return BadComment('The last formula of the cited subproof is not bottom or the conjunction of a formula and its negation.')
            
            return GoodComment()
        
        elif rule_name == r'RAA':
            cit_subproof = cit_subproofs[0]

            if not (cit_subproof.first().formula.eq_syntax(Pred_Form(r'\neg', [main_formula]))):
                return BadComment("The cited subproof's assumption is not the negation of deduced formula.")
            
            if not(cit_subproof.last().formula.eq_syntax(Pred_Form(r'\bot', [])) or (cit_subproof.last().name == r'\wedge' and (cit_subproof.last().sub[0].eq_syntax(Pred_Form(r'\neg',[cit_subproof.last().sub[1]])) or cit_subproof.last().sub[1].eq_syntax(Pred_Form(r'\neg',[cit_subproof.last().sub[0]]))))):
                return BadComment('The last formula of the cited subproof is not bottom or the conjunction of a formula and its negation.')
            
            return GoodComment()
        
        elif rule_name == r'\vee I':
            cit_formula = cit_formulas[0]

            if not (main_formula.name == r'\vee'):
                return BadComment('The deduced formula is not a disjunction.')

            if main_formula.sub[0].eq_syntax(cit_formula) or main_formula.sub[1].eq_syntax(cit_formula):
                return GoodComment()
            else:
                return BadComment('The cited formula is different than both disjuncts of the deduced formula.')
            
        elif rule_name == r'\vee E':
            cit_formula = cit_formulas[0]

            if not (cit_formula.name == r'\vee'):
                return BadComment('The cited formula is not a disjunction.')

            if not ((cit_formula.sub[0].eq_syntax(cit_subproofs[0].first().formula) and cit_formula.sub[1].eq_syntax(cit_subproofs[1].first().formula)) or (cit_formula.sub[0].eq_syntax(cit_subproofs[1].first().formula) and cit_formula.sub[1].eq_syntax(cit_subproofs[0].first().formula))):
                return BadComment('The assumptions of the two cited subproofs are not the same as the disjuncts of the cited disjunction.')

            if not (cit_subproofs[0].last().formula.eq_syntax(cit_subproofs[1].last().formula)):
                return BadComment('The last line of the two cited subproofs are not the same.')
            
            if not (cit_subproofs[0].last().formula.eq_syntax(main_formula)):
                return BadComment('The deduced formula is not the same as the last line of the two cited subproofs.')
            
            return GoodComment()
        
        elif rule_name == '= I':
            if not main_formula.name == '=':
                return BadComment('The deduced formula is not an identity statement.')
            if not main_formula.sub[0].eq_syntax(main_formula.sub[1]):
                return BadComment('The left and right term of the deduced identity are not the same.')
            
            return GoodComment()
        
        elif rule_name == '= E':
            phi_prime = main_formula

            possible_eq = []
            for f in cit_formulas:
                if f.name == '=':
                    possible_eq.append(f)
            
            if len(possible_eq) == 0:
                return BadComment('Neither cited formula is an identity.')
            
            number_to_text = {
                1: 'not all variables in the substituted term are free in the cited formula.',
                2: 'the relevant term is not substitutable in the cited formula.',
                3: 'the deduced formula is not the result of replacing any number of instances of the first term with instances of the second term.'
            }

            comment_number = 0
            
            for eq in possible_eq:
                phi = [form for form in cit_formulas if form != eq][0]
                for t in eq.sub:
                    t1 = t
                    t2 = [term for term in eq.sub if term != t][0]

                    if not t1.free().issubset(phi.free()):
                        comment_number = max(comment_number, 1)
                        continue

                    able_to_substitute = True
                    for var_name in t1.free():
                        able_to_substitute = able_to_substitute and substitutable(phi, var_name, t2.free())
                    if not able_to_substitute:
                        comment_number = max(comment_number, 2)
                        continue
                    
                    equal_to_main_formula = False
                    for f in all_substitute_TT_form(phi, t1, t2):
                        equal_to_main_formula = equal_to_main_formula or phi_prime.eq_syntax(f)
                    if not equal_to_main_formula: 
                        comment_number = max(comment_number, 3)
                        continue

                    comment_number = 4
            
            if comment_number == 0:
                raise ProofError('problem not captured by =E checker')
            elif comment_number < 4:
                return BadComment(number_to_text[comment_number])
            else:
                return GoodComment()

        if rule_name in rules:
            raise ProofError('rule not covered by check_line method, fix by editing Proof.check_line')
        
        raise ProofError('ILLEGAL RULE ALLOWED THROUGH PARSING FUNCTION!!!!!')