import streamlit as st

from prop.rules import *

st.title(':books: Getting Started')

st.write("Hello, everyone! Welcome to Philos W12A's interface for writing and checking Fitch-style natural deduction proofs! If you're still feeling shaky about natural deduction even after watching the lectures, don't worry. The practice you get from this website should really help solidify a lot of the key concepts taught in the course.")

st.subheader("LaTeX")

st.write("This website uses LaTeX as the required syntax for inputting formulas and rules into Fitch-style proofs. Hopefully, over the last couple weeks, you have gotten comfortable with the LaTeX syntax used to write common logical expressions. For convenience, we have a table shown below, reminding you of several important LaTeX commands.")

st.write('')
st.markdown(f"<center><b>Propositional Logic</b></center>", unsafe_allow_html=True)
st.write('')

col1, col2, col3, col4 = st.columns(4)

expressions = [
    r"\neg p", 
    r"(p \wedge q)", 
    r"(p \vee q)",
    r"(p \to q)",
    r"(p \leftrightarrow q)",
]

with col2:
    for e in expressions:
        st.markdown('')
        st.markdown(f"<center>{e}</center>", unsafe_allow_html=True)
        st.markdown('')

with col3:
    for e in expressions:
        st.latex(e)

st.write('')
st.write('')

# st.markdown(f"<center><b>Predicate Logic</b></center>", unsafe_allow_html=True)
# st.write('')

# col1, col2, col3, col4 = st.columns(4)

# expressions = [
#     r"\forall x P(x)", 
#     r"\exists x P(x)", 
#     r"x = y",
#     r"x \neq y",
# ]

# with col2:
#     for e in expressions:
#         st.markdown('')
#         st.markdown(f"<center>{e}</center>", unsafe_allow_html=True)
#         st.markdown('')

# with col3:
#     for e in expressions:
#         st.latex(e)
# st.write('')
# st.write('')

st.write('To type in a list of formulas (like when you want to input several premises for your proof), simply seperate each formula by a comma.')

st.write("Additionally, so far in the course, we've only talked about using LaTeX for logical formulas. To use this website however, you'll also have to learn how to type out our various natural deduction rules in LaTeX. This works exactly as you might expect: simply replace each logical symbol by its corresponding LaTeX command.")


st.write('')
st.markdown(f"<center><b>Deduction Rule Examples</b></center>", unsafe_allow_html=True)
st.write('')

col1, col2, col3, col4 = st.columns(4)

expressions = [
    r"\wedge I 5,8", 
    r"\to I 3-7", 
    r"\neg E 3",
    r"RAA 1-10",
]

with col2:
    for e in expressions:
        st.markdown('')
        st.markdown(f"<center>{e}</center>", unsafe_allow_html=True)
        st.markdown('')

with col3:
    for e in expressions:
        st.latex(Rule.parse(e).latex())
st.write('')
st.write('')

st.subheader("Supported Deduction Rules")

st.write("This website supports exactly those deduction rules taught in Philosophy W12A. Remember that this set of rules is complete with respect to the semantics taught in class, meaning you should never need more rules than what we've shown you to prove a given valid form of argument.")

st.write("For convenience, here is a comprehensive list of all those rules taught in class where # stands in for some line number.")

per_col = 4

n_rules = len(rules)
n_cols = n_rules // per_col
if n_rules % per_col != 0: n_cols += 1

cols = st.columns(n_cols)

idx_col = 0
i = 0
for name, cit in rules.items():
    with cols[idx_col]:
        st.latex(Rule(name, ('\#',)*cit.count('%s')).latex().replace('-', '--'))
    i += 1
    if i == 4:
        idx_col += 1
        i = 0

st.write('')
st.write("**IMPORTANT NOTE**: All of the above rules can be used 'liberally' as discussed in class. **:red[Do not add an 'L' to the beginning of the rule name even if you are using it liberally.]** The rule should work liberally even without the L.")

st.subheader("Writing and Checking Proofs")

st.write("Otherwise, everything should work as described in lecture. Start with some premises, and then use a clever combination of opening subproofs and applying deduction rules as needed to hopefully arrive at your desired conclusion.")

st.write("But what's most useful about this applet is that it will allow you to **automatically check your proofs**! Recall from class that an important property of our proof system is that there exists an algorithm, which, in a finite amount of time, can decide whether a purported proof is in fact a correct syntactic proof. Well, this website has exactly that algorithm built into it! At any time (either while you're writing your proof or once you think you're finished), feel free to click the **'Check Proof' button**. If your proof is right, the proof checker will give you a big green check mark as congratulations (:white_check_mark:). And if your proof is wrong, the proof checker will tell you exactly what lines are faulty!")

st.write("**IMPORTANT NOTE**: Even if the proof checker only signals that a couple lines are faulty, that doesn't mean those are the only lines that need to be changed in order to arrive at a correct proof. Often, incorrect proofs may require substantial reorganization before they are syntactically correct.")

st.subheader("Additional Help")

st.write("If at any point, you're having trouble with any part of this website, please feel free to make a post on Ed Discussion. This website was also developed very recently, so it's possible there are some minor bugs in the underlying code. If you think you may have noticed a bug, again please make a post on Ed Discussion, detailing exactly what you did to arrive at the bug, ideally including screenshots.")

st.write("Thank you so much for reading along, and good luck with your Fitch-style proofs!")