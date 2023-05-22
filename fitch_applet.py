import streamlit as st
from formula import *
from rules import *
from proofs import *

st.title('Philosophy W12A Fitch-Style Proofs')

# st.latex(r"""
# \def\arraystretch{1.5}
# \begin{array}{l l}
# \begin{array}{l}
# 1 \\
# 2 \\
# 3 \\
# 4 \\
# 5 \\
# 6 \\
# 7 \\
# 8 \\
# \end{array}
# \begin{array}{|l}
#     \begin{array}{|l}
#     (p \to q) \to p  \\ \hline
#         \begin{array}{|l}
#         \neg p  \\ \hline
#         p \to q   \\
#         (p \to q) \to p  \\
#         p \\
#         p \wedge \neg p 
#         \end{array}  \\ 
#     p
#     \end{array}  \\ 
# ((p \to q) \to p) \to p \\
# \end{array}
# &
# \begin{array}{l}
#  \\
#  \\
# \neg E \; 2 \\
# R \; 1 \\
# \to \! E \; 3, 4 \\
# \wedge I \; 2,5 \\
# RAA \; 2\text{-}6 \\
# \leftrightarrow \! I \; 1\text{-}7 \\
# \end{array}
# \end{array}
# """)

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

assumptions_textbox = TextBox(
    "assumptions_textbox",
    "Proof Assumptions",
    [], 
    lambda string: list(map(PropNode.parse, string.split(','))),
    ParsingError,
    assumptions_display,
    custom_error_message="We can't parse the above formulas. Are you sure they're written in LaTeX and separated by commas?"
)

new_line_textbox1 = TextBox(
    "new_line_textbox1",
    "LaTeX Formula", 
    None, 
    PropNode.parse, 
    ParsingError, 
    PropNode.latex
    )

new_line_textbox2 = TextBox(
    "new_line_textbox2",
    "Deduction Rule", 
    None, 
    Rule.parse, 
    RuleError, 
    Rule.latex
    )

subproof_assumption_textbox = TextBox(
    "subproof_assumption_textbox",
    "Subproof Assumption", 
    None, 
    PropNode.parse, 
    ParsingError, 
    PropNode.latex
    )

change_line_textbox1 = TextBox(
    "change_line_textbox1",
    "LaTeX Formula", 
    None, 
    PropNode.parse, 
    ParsingError, 
    PropNode.latex
    )

change_line_textbox2 = TextBox(
    "change_line_textbox2",
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
    st.session_state.textboxes = {}

    for textbox in TextBox.all_textboxes:
        st.session_state.textboxes[textbox.id] = {}
        st.session_state.textboxes[textbox.id]['value'] = textbox.default_value
        st.session_state.textboxes[textbox.id]['error'] = False
        st.session_state.textboxes[textbox.id]['disabled'] = False

    st.session_state.main_proof = None

    st.session_state.overall_comment = None

if "main_proof" not in st.session_state:
    set_up()

#st.subheader("Step 1: Choose Assumptions")

######################
# CHOOSE ASSUMPTIONS #
######################

o1, o2, o3, o4 = 3, 0.4, 1, 0.5

col1, col2, col3, col4 = st.columns([o1, o2, o3, o4])

with col1:

    assumptions_textbox.deploy()

with col3:
    st.markdown("")

    if len(st.session_state.textboxes['assumptions_textbox']['value']) == 1:
        button_text = f"Proceed with {len(st.session_state.textboxes['assumptions_textbox']['value'])} assumption?"
    else:
        button_text = f"Proceed with {len(st.session_state.textboxes['assumptions_textbox']['value'])} assumptions?"
        
    def when_assumptions_clicked():
        st.session_state.textboxes['assumptions_textbox']['disabled'] = True

    st.button(button_text, on_click = when_assumptions_clicked, disabled=isinstance(st.session_state.textboxes['assumptions_textbox']['error'], Exception) or st.session_state.textboxes['assumptions_textbox']['disabled'])

if st.session_state.textboxes['assumptions_textbox']['disabled']:

    ##############################
    # DISPLAY PROOF AND COMMENTS #
    ##############################

    if st.session_state.main_proof is None:
        st.session_state.main_proof = Proof(st.session_state.textboxes['assumptions_textbox']['value'])
        st.session_state.current_subproof = st.session_state.main_proof

    st.session_state.current_subproof.add_last(ProofLine(Blank(), Blank()))
    st.latex(st.session_state.main_proof.latex())
    st.session_state.current_subproof.remove_last()

    col1, col2 = st.columns([3,1])
    
    with col2:

        ###
        # STILL TO DO: fix bug with overall_comment, test all rules (index error with \wedge E?), set up textbox for desired conclusion and incorporate into checking system
        ###

        st.markdown('')

        def check_proof_button():
            comments = []
            for line_number in range(1, st.session_state.main_proof.n_lines + 1):
                comments.append(st.session_state.main_proof.check_line(line_number))
            
            bad_comments = [(i+1, comment) for (i, comment) in enumerate(comments) if isinstance(comment, BadComment)]

            if len(bad_comments) == 0:
                st.session_state.overall_comment = 'All lines look good! This proof is correct. ✅'
            else:
                st.session_state.overall_comment = "Unfortunately, this proof is not correct. Here are some specific errors.\n"
                for (line_number, comment) in bad_comments:
                    st.session_state.overall_comment += f"Line {line_number}: {comment.text}\n"
            
        st.button('Check Proof', on_click=check_proof_button, disabled = not (st.session_state.current_subproof == st.session_state.main_proof and len(st.session_state.main_proof.subproofs) > 0))

    if isinstance(st.session_state.overall_comment, str):
        st.markdown('')
        st.markdown(st.session_state.overall_comment)
    else:
        st.markdown('')

    ###################
    # CREATE NEW LINE #
    ###################

    st.subheader("Either create a new line...")
    
    st.markdown('')

    col1, col2 = st.columns(2)

    with col1:

        new_line_textbox1.deploy()   

    with col2:

        new_line_textbox2.deploy()

    st.markdown('')

    x3, x4 = 1.5, 0.1

    x2 = o2*(x3+x4)/(o3+o4)

    x1 = o1*(x3+x4)/(o3+o4)

    col1, col2, col3, col4 = st.columns([x1, x2, x3, x4])

    with col1:
    
        formula_and_rule_in_place = isinstance(st.session_state.textboxes["new_line_textbox1"]['value'], PropNode) and isinstance(st.session_state.textboxes["new_line_textbox2"]['value'], Rule)

        def add_line_button(formula, rule):
            st.session_state.current_subproof.add_last(ProofLine(formula, rule))
        st.button('Add Line', on_click=add_line_button, args=(st.session_state.textboxes["new_line_textbox1"]['value'], st.session_state.textboxes["new_line_textbox2"]['value']), disabled = not formula_and_rule_in_place)
        
        def delete_last_line_button():
            st.session_state.current_subproof = st.session_state.current_subproof.remove_last()
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
        line_number = st.selectbox('Line Number', tuple([default_string] + list(range(len(st.session_state.main_proof.assumptions)+1, st.session_state.main_proof.n_lines+1))))
        if line_number != default_string:
            line_number = int(line_number)

    with col3:
        st.markdown('')
        st.markdown('')
        st.markdown('to')

    with col4:
        change_line_textbox1.deploy()

    if isinstance(line_number, str) or (isinstance(line_number, int) and isinstance(st.session_state.main_proof.find(line_number), ProofLine)):
        with col5:
            change_line_textbox2.deploy()

    with col6:
        st.markdown('')
        st.markdown('')
        def change_line_button(line_number, formula, rule):
            st.session_state.main_proof.change(line_number, formula, rule)
            
        st.button("Change Line", 
                    on_click=change_line_button, 
                    args = (line_number, 
                            st.session_state.textboxes["change_line_textbox1"]["value"],
                            st.session_state.textboxes["change_line_textbox2"]["value"],),
                    disabled= not(
                        isinstance(line_number, int) 
                        and isinstance(st.session_state.textboxes["change_line_textbox1"]["value"], PropNode)
                        and (isinstance(st.session_state.main_proof.find(line_number), PropNode) or isinstance(st.session_state.textboxes["change_line_textbox2"]["value"], Rule))
                        )
                    )

    st.markdown('')

    ######################
    # START NEW SUBPROOF #
    ######################

    st.subheader("Or start a new subproof!")
    
    st.markdown('')

    x3, x4 = 1.5, 0.1

    x2 = o2*(x3+x4)/(o3+o4)

    x1 = o1*(x3+x4)/(o3+o4)

    col1, col2, col3, col4 = st.columns([x1, x2, x3, x4])

    with col1:
        st.markdown('')
        subproof_assumption_textbox.deploy()

    with col3:

        def start_new_subproof_button(formula):
            new_subproof = Proof([formula])
            st.session_state.current_subproof.add_last(new_subproof)
            st.session_state.current_subproof = new_subproof
        st.button("Start New Subproof", 
                  on_click=start_new_subproof_button, 
                  args=(st.session_state.textboxes['subproof_assumption_textbox']['value'],),
                  disabled=not isinstance(st.session_state.textboxes['subproof_assumption_textbox']['value'], PropNode))
    
        def delete_current_subproof_button():
            st.session_state.current_subproof.self_delete()
            st.session_state.current_subproof = st.session_state.current_subproof.parent
            
        st.button("Delete Current Subproof", 
                  on_click=delete_current_subproof_button, 
                  disabled=st.session_state.current_subproof.parent is None)
        
        def exit_current_subproof_button():
            st.session_state.current_subproof = st.session_state.current_subproof.parent
            
        st.button("Exit Current Subproof", 
                  on_click=exit_current_subproof_button, 
                  disabled=(st.session_state.current_subproof.parent is None) or len(st.session_state.current_subproof.subproofs) == 0)


    st.button('Start Over', on_click=set_up)


