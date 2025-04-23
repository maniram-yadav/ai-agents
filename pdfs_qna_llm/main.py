import streamlit as st
from agent_chain import create_agent_chain 
from query_processor import Query

query = Query()

st.set_page_config(page_title="Doc Searcher", page_icon=":robot:")
st.header("Query PDF Source")
form_input = st.text_input("Enter Query")
submit = st.button("Generate")

if submit :
    st.write(query.chain(form_input))
    # st.write(form_input)
