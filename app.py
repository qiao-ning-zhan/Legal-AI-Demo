import streamlit as st
from utils.ai import chat
from utils.fileupload import FileLoader
from utils.chromadb import DBClient
from utils.cueword import Prompts
from css.layout import set_layout, set_header

set_layout()
set_header("Ask Me Anything About Law")

if 'start' not in st.session_state:
    st.session_state['start'] = False
if 'prompts' not in st.session_state:
    st.session_state['prompts'] = Prompts("You are a legal specialist.")

uploaded_file = st.file_uploader(
    "Upload your document", 
    type=["txt", "docx"],
)

if uploaded_file is not None:
    f = FileLoader(uploaded_file)
    chunks = f.textSplit()
    
    db = DBClient(f.docName)
    for chunk in chunks:
        db.DBAdd(chunk)

question = st.text_area(label="Your Question:", label_visibility="hidden", placeholder="Message Me")
if st.button("Ask"):
    if not st.session_state['start']:
        top_chunk = db.DBQuery(question, 1)
        p = f"""
            Based on the following text extracted from the legislation:
            <extracted text>
            {top_chunk}
            </extracted text>
            Answer the following question:
            <question>\
            {question}
            </question>
            Make sure to reference your answer according to the extracted text.
        """
        st.session_state['prompts'].userPrompt(p)
        st.session_state['start'] = True
    else:
        st.session_state['prompts'].userPrompt(question)
    
    answer = chat(st.session_state['prompts'].prompts)
    st.session_state['prompts'].assistantPrompt(answer)


st.session_state['prompts'].display()