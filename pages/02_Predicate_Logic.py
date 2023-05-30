import streamlit as st
from pred.formula import *
from pred.rules import *
from pred.proofs import *

st.title('Proofs for Predicate Logic')

st.markdown('')

class TextBox():
    all_textboxes = []

    def __init__(self, id, above_text_box, default_value, parsing_func, error_class, display_func, custom_error_message = None):
        self.id = id
        self.above_text_box = above_text_box
        self.default_value = default_value
        self.parsing_func = parsing_func
        self.error_class = error_class
        self.display_func = display_func
        self.custom_error_message = custom_error_message

        TextBox.all_textboxes.append(self)
    
    def deploy(self):

        new_input = st.text_input(self.above_text_box, key = self.id, disabled = st.session_state.textboxes[self.id]['disabled'])

        if len(new_input) == 0:
            st.session_state.textboxes[self.id]['value'] = self.default_value
            st.session_state.textboxes[self.id]['error'] = False
        if len(new_input) > 0:
            try:
                st.session_state.textboxes[self.id]['value'] = self.parsing_func(new_input)
                st.session_state.textboxes[self.id]['error'] = False
            except self.error_class as err:
                st.session_state.textboxes[self.id]['error'] = err
                st.session_state.textboxes[self.id]['value'] = self.default_value
        
        if isinstance(st.session_state.textboxes[self.id]['error'], Exception):
            if self.custom_error_message is None:
                st.markdown(f"{st.session_state.textboxes[self.id]['error']}")
            else:
                st.markdown(f"{self.custom_error_message}")
        elif st.session_state.textboxes[self.id]['value'] != self.default_value:
            st.latex(self.display_func(st.session_state.textboxes[self.id]['value']))

def assumptions_display(assumptions):
    assumptions_latex = ''
    for a in assumptions:
        assumptions_latex += a.latex() + ', '
    assumptions_latex = assumptions_latex[:-2]
    return (r'\{'+assumptions_latex+r'\}')

def special_parser(string):
    new_string = string

    p_balance = 0
    for i, char in enumerate(string):
        if char == '(':
            p_balance += 1
        elif char == ')':
            p_balance -= 1
        
        if p_balance == 0 and char == ',':
            new_string = new_string[:i] + ';' + new_string[i+1:]
    
    return list(map(Pred_Form.parse, new_string.split(';')))

pred_assumptions_textbox = TextBox(
    "pred_assumptions_textbox",
    "Premises",
    [], 
    special_parser,
    ParsingError,
    assumptions_display,
    custom_error_message="We can't parse the above formulas. Are you sure they're written in LaTeX and separated by commas?"
)

pred_conclusion_textbox = TextBox(
    "pred_conclusion_textbox",
    "Conclusion", 
    None, 
    Pred_Form.parse, 
    ParsingError, 
    Pred_Form.latex
    )

pred_new_line_textbox1 = TextBox(
    "pred_new_line_textbox1",
    "LaTeX Formula", 
    None, 
    Pred_Form.parse, 
    ParsingError, 
    Pred_Form.latex
    )

pred_new_line_textbox2 = TextBox(
    "pred_new_line_textbox2",
    "Deduction Rule", 
    None, 
    Rule.parse, 
    RuleError, 
    Rule.latex
    )

pred_subproof_assumption_textbox = TextBox(
    "pred_subproof_assumption_textbox",
    "Subproof Assumption", 
    None, 
    Pred_Form.parse, 
    ParsingError, 
    Pred_Form.latex
    )

def new_const_parsing_func(string):
    try:
        form = Pred_Term.parse(string)
    except ParsingError:
        raise ParsingError("We couldn't parse the above expression. Are you sure this is a constant name written in LaTeX?")
    if not form.ctgy == 'const':
        raise ParsingError('The above is interpreted as a variable or function-based expression, not a constant.')
    if form.value in st.session_state.main_proof.consts():
        raise ParsingError("This constant already appears in the proof.")
    return form

univ_intro_subproof_assumption_textbox = TextBox(
    "univ_intro_subproof_assumption_textbox",
    "New Constant Name", 
    None, 
    new_const_parsing_func, 
    ParsingError, 
    lambda t: r"\boxed{" + t.latex() + r'}'
    )

exist_elim_subproof_formula_textbox = TextBox(
    "exist_elim_subproof_formula_textbox",
    "LaTeX Formula", 
    None, 
    Pred_Form.parse, 
    ParsingError, 
    Pred_Form.latex
    )

exist_elim_subproof_constant_textbox = TextBox(
    "exist_elim_subproof_constant_textbox",
    "New Constant Name", 
    None, 
    new_const_parsing_func, 
    ParsingError, 
    lambda t: r"\boxed{" + t.latex() + r'}'
    )

pred_change_line_textbox1 = TextBox(
    "pred_change_line_textbox1",
    "LaTeX Formula", 
    None, 
    Pred_Form.parse, 
    ParsingError, 
    Pred_Form.latex
    )

pred_change_line_textbox2 = TextBox(
    "pred_change_line_textbox2",
    "Deduction Rule", 
    None, 
    Rule.parse, 
    RuleError, 
    Rule.latex
    )
            
##########
# SET UP #
##########

def set_up():
    st.session_state.page = 'pred'

    st.session_state.textboxes = {}

    for textbox in TextBox.all_textboxes:
        st.session_state.textboxes[textbox.id] = {}
        st.session_state.textboxes[textbox.id]['value'] = textbox.default_value
        st.session_state.textboxes[textbox.id]['error'] = False
        st.session_state.textboxes[textbox.id]['disabled'] = False

    st.session_state.main_proof = None

    st.session_state.bad_comments = None

    st.session_state.reached_conclusion = None

if not ("page" in st.session_state and st.session_state.page == 'pred'):
    set_up()

#st.subheader("Step 1: Choose Assumptions")

#####################################
# CHOOSE ASSUMPTIONS AND CONCLUSION #
#####################################

col1, col2, col3 = st.columns([4, 2, 1.6])

with col1:

    pred_assumptions_textbox.deploy()

with col2:

    pred_conclusion_textbox.deploy()

with col3:
    st.markdown("")
        
    def when_assumptions_clicked():
        st.session_state.textboxes['pred_assumptions_textbox']['disabled'] = True
        st.session_state.textboxes['pred_conclusion_textbox']['disabled'] = True

    st.button('Start Natural Deduction Proof', on_click = when_assumptions_clicked, disabled=isinstance(st.session_state.textboxes['pred_assumptions_textbox']['error'], Exception) or st.session_state.textboxes['pred_assumptions_textbox']['disabled'] or (not isinstance(st.session_state.textboxes['pred_conclusion_textbox']['value'], Pred_Form)))

if st.session_state.textboxes['pred_assumptions_textbox']['disabled']:

    ##############################
    # DISPLAY PROOF AND COMMENTS #
    ##############################

    if st.session_state.main_proof is None:
        st.session_state.main_proof = Proof(list(map(lambda x: NormalAssumptionLine(x),st.session_state.textboxes['pred_assumptions_textbox']['value'])))
        st.session_state.current_subproof = st.session_state.main_proof

    st.session_state.current_subproof.add_last(DeductionLine(Blank(), Blank()))
    st.latex(st.session_state.main_proof.latex())
    st.session_state.current_subproof.remove_last()

    col1, col2 = st.columns([3,1])
    
    with col2:

        st.markdown('')

        def check_proof_button():
            comments = []
            for line_number in range(1, st.session_state.main_proof.n_lines + 1):
                comments.append(st.session_state.main_proof.check_line(line_number))
            
            st.session_state.bad_comments = [(i+1, comment) for (i, comment) in enumerate(comments) if isinstance(comment, BadComment)]

            st.session_state.reached_conclusion = st.session_state.current_subproof == st.session_state.main_proof and len(st.session_state.main_proof.subproofs) > 0 and st.session_state.main_proof.find(st.session_state.main_proof.n_lines).formula.eq_syntax(st.session_state.textboxes["pred_conclusion_textbox"]["value"])
            
        st.button('Check Proof', on_click=check_proof_button)

    if isinstance(st.session_state.bad_comments, list):
        if len(st.session_state.bad_comments) == 0 and st.session_state.reached_conclusion:
            st.markdown('All lines look good! This proof is correct. :white_check_mark:')
        elif len(st.session_state.bad_comments) == 0 and not st.session_state.reached_conclusion:
            st.markdown("The proof is correct so far! You just haven't reached the desired conclusion yet.")
        else:
            st.markdown("Unfortunately, this proof is not correct. Here are some specific errors.")
            col1, col2 = st.columns([1, 10])
            with col2:
                for (line_number, comment) in st.session_state.bad_comments:
                    st.markdown(f"Line {line_number}: {comment.text.lower()}")

    ###################
    # CREATE NEW LINE #
    ###################

    st.subheader("Either create a new line...")
    
    st.markdown('')

    col1, col2 = st.columns(2)

    with col1:

        pred_new_line_textbox1.deploy()   

    with col2:

        pred_new_line_textbox2.deploy()

    st.markdown('')

    o1, o2, o3, o4 = 3, 0.4, 1, 0.5

    x3, x4 = 1.5, 0.1

    x2 = o2*(x3+x4)/(o3+o4)

    x1 = o1*(x3+x4)/(o3+o4)

    col1, col2, col3, col4 = st.columns([x1, x2, x3, x4])

    with col1:
    
        formula_and_rule_in_place = isinstance(st.session_state.textboxes["pred_new_line_textbox1"]['value'], Pred_Form) and isinstance(st.session_state.textboxes["pred_new_line_textbox2"]['value'], Rule)

        def add_line_button(formula, rule):
            st.session_state.current_subproof.add_last(DeductionLine(formula, rule))
            st.session_state.bad_comments = None
        st.button('Add Line', on_click=add_line_button, args=(st.session_state.textboxes["pred_new_line_textbox1"]['value'], st.session_state.textboxes["pred_new_line_textbox2"]['value']), disabled = not formula_and_rule_in_place)
        
        def delete_last_line_button():
            st.session_state.current_subproof = st.session_state.current_subproof.remove_last()
            st.session_state.bad_comments = None
        st.button('Delete Last Line', on_click=delete_last_line_button, disabled = len(st.session_state.current_subproof.subproofs) == 0)
    
    st.markdown('')

    ########################
    # CHANGE EXISTING LINE #
    ########################

    st.subheader("Change an existing line...")
    
    st.markdown('')

    col1a, col1, col1b, col2, col3a, col3, col3b, col4, col5, col6 = st.columns([
        0.6, 
        3,
        0.2,
        4,
        0.5,
        1,
        0.3,
        4,
        4,
        4,
    ])

    with col1:
        st.markdown('')
        st.markdown('')
        st.markdown('Change line')

    with col2:
        default_string = '---'
        changeable_line_numbers = []
        for l_num in range(len(st.session_state.main_proof.assumptions)+1, st.session_state.main_proof.n_lines+1):
            line = st.session_state.main_proof.find(l_num)
            if isinstance(line, DeductionLine) or isinstance(line, NormalAssumptionLine):
                changeable_line_numbers.append(l_num)
        line_number = st.selectbox('Line Number', tuple([default_string] + changeable_line_numbers))
        if line_number != default_string:
            line_number = int(line_number)

    with col3:
        st.markdown('')
        st.markdown('')
        st.markdown('to')

    with col4:
        pred_change_line_textbox1.deploy()

    if isinstance(line_number, str) or (isinstance(line_number, int) and isinstance(st.session_state.main_proof.find(line_number), DeductionLine)):
        with col5:
            pred_change_line_textbox2.deploy()

    with col6:
        st.markdown('')
        st.markdown('')
        def change_line_button(line_number, formula, rule):
            st.session_state.main_proof.change(line_number, formula, rule)
            st.session_state.bad_comments = None
            
        st.button("Change Line", 
                    on_click=change_line_button, 
                    args = (line_number, 
                            st.session_state.textboxes["pred_change_line_textbox1"]["value"],
                            st.session_state.textboxes["pred_change_line_textbox2"]["value"],),
                    disabled= not(
                        isinstance(line_number, int) 
                        and isinstance(st.session_state.textboxes["pred_change_line_textbox1"]["value"], Pred_Form)
                        and (isinstance(st.session_state.main_proof.find(line_number), Pred_Form) or isinstance(st.session_state.textboxes["pred_change_line_textbox2"]["value"], Rule))
                        )
                    )

    st.markdown('')

    ######################
    # START NEW SUBPROOF #
    ######################

    st.subheader("Or start a new subproof!")

    x3, x4 = 1.5, 0.1

    x2 = o2*(x3+x4)/(o3+o4)

    x1 = o1*(x3+x4)/(o3+o4)

    tab1, tab2, tab3 = st.tabs(["Normal Subproof", "Universal Introduction Subproof", "Existential Elimination Subproof"])

    with tab1:

        col1, col2, col3, col4 = st.columns([x1, x2, x3, x4])

        with col1:
            st.markdown('')
            pred_subproof_assumption_textbox.deploy()

        with col3:

            def start_new_subproof_button(formula):
                new_subproof = Proof([NormalAssumptionLine(formula)])
                st.session_state.current_subproof.add_last(new_subproof)
                st.session_state.current_subproof = new_subproof
                st.session_state.bad_comments = None
            st.button("Start New Subproof", 
                    on_click=start_new_subproof_button, 
                    args=(st.session_state.textboxes['pred_subproof_assumption_textbox']['value'],),
                    disabled=not isinstance(st.session_state.textboxes['pred_subproof_assumption_textbox']['value'], Pred_Form))
        
            def delete_current_subproof_button():
                st.session_state.current_subproof.self_delete()
                st.session_state.current_subproof = st.session_state.current_subproof.parent
                st.session_state.bad_comments = None
                
            st.button("Delete Current Subproof", 
                    on_click=delete_current_subproof_button, 
                    disabled=st.session_state.current_subproof.parent is None)
            
            def exit_current_subproof_button():
                st.session_state.current_subproof = st.session_state.current_subproof.parent
                st.session_state.bad_comments = None
                
            st.button("Exit Current Subproof", 
                    on_click=exit_current_subproof_button, 
                    disabled=(st.session_state.current_subproof.parent is None) or len(st.session_state.current_subproof.subproofs) == 0)
    
    with tab2:

        col1, col2, col3, col4 = st.columns([x1, x2, x3, x4])

        with col1:
            st.markdown('')
            univ_intro_subproof_assumption_textbox.deploy()

        with col3:

            def univ_intro_start_new_subproof_button(term):
                new_subproof = Proof([UnivIntroAssumptionLine(term.value)])
                st.session_state.current_subproof.add_last(new_subproof)
                st.session_state.current_subproof = new_subproof
                st.session_state.bad_comments = None
            st.button("Start New Subproof", 
                      key='univ_intro_start_new_subproof_button',
                    on_click=univ_intro_start_new_subproof_button, 
                    args=(st.session_state.textboxes['univ_intro_subproof_assumption_textbox']['value'],),
                    disabled=not isinstance(st.session_state.textboxes['univ_intro_subproof_assumption_textbox']['value'], Pred_Term))
        
            def univ_intro_delete_current_subproof_button():
                st.session_state.current_subproof.self_delete()
                st.session_state.current_subproof = st.session_state.current_subproof.parent
                st.session_state.bad_comments = None
                
            st.button("Delete Current Subproof", 
                      key = 'univ_intro_delete_current_subproof_button',
                    on_click=univ_intro_delete_current_subproof_button, 
                    disabled=st.session_state.current_subproof.parent is None)
            
            def univ_intro_exit_current_subproof_button():
                st.session_state.current_subproof = st.session_state.current_subproof.parent
                st.session_state.bad_comments = None
                
            st.button("Exit Current Subproof", 
                      key='univ_intro_exit_current_subproof_button',
                    on_click=univ_intro_exit_current_subproof_button, 
                    disabled=(st.session_state.current_subproof.parent is None) or len(st.session_state.current_subproof.subproofs) == 0)

    with tab3:

        col0, col1, col2, col3, col4 = st.columns([x1/2, x1/2, x2, x3, x4])

        with col0:
            st.markdown('')
            exist_elim_subproof_formula_textbox.deploy()

        with col1:
            st.markdown('')
            exist_elim_subproof_constant_textbox.deploy()

        with col3:

            def exist_elim_start_new_subproof_button(form, term):
                new_subproof = Proof([ExistElimAssumptionLine(form, term.value)])
                st.session_state.current_subproof.add_last(new_subproof)
                st.session_state.current_subproof = new_subproof
                st.session_state.bad_comments = None
            st.button("Start New Subproof", 
                      key='exist_elim_start_new_subproof_button',
                    on_click=exist_elim_start_new_subproof_button, 
                    args=(st.session_state.textboxes['exist_elim_subproof_formula_textbox']['value'],st.session_state.textboxes['exist_elim_subproof_constant_textbox']['value']),
                    disabled=not (isinstance(st.session_state.textboxes['exist_elim_subproof_formula_textbox']['value'], Pred_Form) and isinstance(st.session_state.textboxes['exist_elim_subproof_constant_textbox']['value'], Pred_Term)))
        
            def exist_elim_delete_current_subproof_button():
                st.session_state.current_subproof.self_delete()
                st.session_state.current_subproof = st.session_state.current_subproof.parent
                st.session_state.bad_comments = None
                
            st.button("Delete Current Subproof", 
                      key = 'exist_elim_delete_current_subproof_button',
                    on_click=exist_elim_delete_current_subproof_button, 
                    disabled=st.session_state.current_subproof.parent is None)
            
            def exist_elim_exit_current_subproof_button():
                st.session_state.current_subproof = st.session_state.current_subproof.parent
                st.session_state.bad_comments = None
                
            st.button("Exit Current Subproof", 
                      key='exist_elim_exit_current_subproof_button',
                    on_click=exist_elim_exit_current_subproof_button, 
                    disabled=(st.session_state.current_subproof.parent is None) or len(st.session_state.current_subproof.subproofs) == 0)
            
    st.button('Start Over', on_click=set_up)