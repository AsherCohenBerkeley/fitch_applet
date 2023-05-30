import streamlit as st

from pred.rules import *

st.title(':books: Getting Started')

st.write("Hello, everyone! Welcome to Philos W12A's interface for writing and checking Fitch-style natural deduction proofs! If you're still feeling shaky about natural deduction even after watching the lectures, don't worry. The practice you get from this website should really help solidify a lot of the key concepts taught in the course.")

st.write("To familiarize yourself with the basics of how to use this applet, we recommend you read the entirety of this 'Getting Started' page before you start writing your natural deduction proofs. Not to mention, reading this page will help review some key concepts from the course.")

st.subheader("LaTeX")

st.write("This website uses LaTeX as the required syntax for inputting formulas and rules into Fitch-style proofs. Hopefully, over the last couple weeks, you have gotten comfortable with LaTeX in the context of typesetting common logical expressions. Nevertheless, for convenience, we have constructed the table below to help remind you of several important LaTeX commands.")

st.write('')
st.markdown(f"<center><b>Propositional Logic</b></center>", unsafe_allow_html=True)

expressions = [
    r"\neg p", 
    r"(p \wedge q)", 
    r"(p \vee q)",
    r"(p \to q)",
    r"(p \leftrightarrow q)",
]

for e in expressions:
    col1, col2, col3, col4 = st.columns(4)
    with col2:
        st.markdown('')
        st.markdown(f"<center>{e}</center>", unsafe_allow_html=True)
        st.markdown('')
    with col3:
        st.latex(e)

st.write('')
st.write('')

st.markdown(f"<center><b>Predicate Logic</b></center>", unsafe_allow_html=True)

expressions = [
    r"\forall x P(x)", 
    r"\exists x P(x)", 
    r"x = y",
]
for e in expressions:
    col1, col2, col3, col4 = st.columns(4)
    with col2:
        st.markdown('')
        st.markdown(f"<center>{e}</center>", unsafe_allow_html=True)
        st.markdown('')
    with col3:
        st.latex(e)
st.write('')
st.write('')

st.write('In this applet, whenever you want to type in a list of formulas (like when you want to input several premises for your proof), simply seperate each formula by a comma.')

st.write("Additionally, so far in the course, we've only talked about using LaTeX for logical formulas. To use this website however, you'll also have to learn how to type out our various natural deduction rules in LaTeX. This works exactly as you might expect: simply replace each logical symbol by its corresponding LaTeX command.")

st.write('')
st.markdown(f"<center><b>Deduction Rule Examples</b></center>", unsafe_allow_html=True)
st.write('')

expressions = [
    r"\wedge I 5,8", 
    r"\to I 3-7", 
    r"\neg E 3",
    r"RAA 1-10",
    r"\forall E 1",
    r"\exists E 3, 10-19",
    r"= I"
]

for e in expressions:
    col1, col2, col3, col4 = st.columns(4)

    with col2:
            st.markdown('')
            st.markdown(f"<center>{e}</center>", unsafe_allow_html=True)
            st.markdown('')

    with col3:
            st.latex(Rule.parse(e).latex())
st.write('')
st.write('')

st.subheader("Supported Deduction Rules")

st.write("This website supports exactly those deduction rules taught in Philosophy W12A. Remember that this set of rules is complete with respect to the semantics taught in class, meaning you should never need more rules than what we've shown you to prove that a given form of argument is valid.")

st.write("For convenience, here is a comprehensive list of all those rules taught in class where # stands in for some line number.")

prop_rules = {rule: cit for (rule, cit) in rules.items() if not ('=' in rule or r'\forall' in rule or r'\exists' in rule)}

per_col = 4

n_rules = len(prop_rules)
n_cols = n_rules // per_col
if n_rules % per_col != 0: n_cols += 1

cols = st.columns(n_cols)

idx_col = 0
i = 0
for name, cit in prop_rules.items():
    with cols[idx_col]:
        st.latex(Rule(name, ('\#',)*cit.count('%s')).latex().replace('-', '--'))
    i += 1
    if i == per_col:
        idx_col += 1
        i = 0

st.markdown('')
st.markdown('')

pred_rules = {rule: cit for (rule, cit) in rules.items() if ('=' in rule or r'\forall' in rule or r'\exists' in rule)}

per_col = 2

n_rules = len(pred_rules)
n_cols = n_rules // per_col
if n_rules % per_col != 0: n_cols += 1

cols = st.columns(n_cols+2, gap='large')

idx_col = 0
i = 0
for name, cit in pred_rules.items():
    with cols[idx_col+1]:
        st.latex(Rule(name, ('\#',)*cit.count('%s')).latex().replace('-', '--'))
    i += 1
    if i == per_col:
        idx_col += 1
        i = 0

st.write('')
st.write("**IMPORTANT NOTE**: All of the above rules can be used 'liberally' as discussed in class. **:red[Do not add an 'L' to the beginning of the rule name even if you are using it liberally.]** The rule should work liberally even without the L.")

st.subheader("Writing and Checking Proofs")

st.write("Otherwise, everything should work as described in lecture. Start with some premises, and then use a clever combination of opening subproofs and applying deduction rules to arrive at your desired conclusion.")

st.write("But the most useful feature of this applet is its **automatic proof checker**. Recall from class that an important property of our proof system is that there exists an algorithm, which, in a finite amount of time, can decide whether a purported proof is in fact a correct syntactic proof. Well, this website has exactly that algorithm built into it! At any time (either while you're writing your proof or once you think you've finished), feel free to click the **'Check Proof' button**. If your proof is right, the proof checker will give you a big green check mark as congratulations (:white_check_mark:). And if your proof is wrong, the proof checker will tell you exactly what lines are faulty!")

st.write("**IMPORTANT NOTE**: Even if the proof checker only signals that a couple lines are faulty, that does not mean those are the only lines that need to be changed in order to arrive at a correct proof. Incorrect proofs often require substantial reorganization before they are syntactically correct.")

st.subheader("Additional Help")

st.write("If at any point you're having trouble with any part of this website, please feel free to make a post on Ed Discussion. We (the course staff) would be more than happy to help.")

st.write("This website was also developed very recently, so it's possible there are some bugs in the underlying code. If you think you may have noticed a bug, again please make a post on Ed Discussion, detailing exactly what you did to arrive at the bug, ideally including screenshots.")

st.write('')
st.write("Thank you so much for reading along, and good luck with your Fitch-style proofs!")