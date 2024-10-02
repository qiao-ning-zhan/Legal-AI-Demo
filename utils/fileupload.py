import streamlit as st
from utils.ai import textEmbedding
import os
from docx import Document
import io

class FileLoader:
    def __init__(self, file):
        self.docName = os.path.splitext(file.name)[0]
        self.__file_content = self.__read_file(file)
        self.__chunks = []
        self.chunk_embeddings = {}

    def __read_file(self, file):
        file_extension = os.path.splitext(file.name)[1].lower()
        if file_extension == '.docx':
            return self.__read_docx(file)
        elif file_extension == '.txt':
            return file.read().decode("utf-8")
        else:
            raise ValueError(f"Unsupported file type: {file_extension}")

    def __read_docx(self, file):
        doc = Document(io.BytesIO(file.read()))
        return ' '.join([paragraph.text for paragraph in doc.paragraphs])

    def __textSplitNaive(self, chunkSize):
        words = self.__file_content.split()
        return [' '.join(words[i:i+chunkSize]) for i in range(0, len(words), chunkSize)]

    def textSplit(self, method="naive", chunkSize=100):
        if method == "naive":
            self.__chunks = self.__textSplitNaive(chunkSize)
        return self.__chunks

# Streamlit app
st.title("Document Loader and Splitter")

uploaded_file = st.file_uploader("Choose a file", type=['txt', 'docx'])

if uploaded_file is not None:
    try:
        loader = FileLoader(uploaded_file)
        st.write(f"File '{loader.docName}' loaded successfully.")

        chunk_size = st.slider("Select chunk size", min_value=50, max_value=500, value=100, step=50)
        
        if st.button("Split Text"):
            chunks = loader.textSplit(chunkSize=chunk_size)
            st.write(f"Text split into {len(chunks)} chunks.")
            for i, chunk in enumerate(chunks):
                st.text_area(f"Chunk {i+1}", chunk, height=100)
    except ValueError as e:
        st.error(str(e))
