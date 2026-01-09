from langchain_community.document_loaders import UnstructuredPDFLoader

loader = UnstructuredPDFLoader("docs/doc5.pdf")
text_document = loader.load()
from langchain_text_splitters import CharacterTextSplitter

text_splitter = CharacterTextSplitter(
    separator="\n\n",
    chunk_size=1000,
    chunk_overlap=200,
    length_function=len,
    is_separator_regex=False,
)
texts = text_splitter.create_documents([text_document[0].page_content])
for i, text in enumerate(texts):
    print(f"--- Chunk {i+1} ---")
    print(text.page_content)
    print()

print(f"Number of text chunks: {len(texts)}")
print(f"Length of document: {len(text_document[0].page_content)}")