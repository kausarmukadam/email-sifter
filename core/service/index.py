"""This is the logic for ingesting Notion data into LangChain."""
from pathlib import Path

from langchain.document_loaders import UnstructuredEmailLoader
from dataclasses import dataclass
from langchain.vectorstores import FAISS
from langchain.embeddings import OpenAIEmbeddings
import pickle
import glob


@dataclass
class Config:
    path: str
    chunk_size: int
    separator: "\n"
    index_location: str
    store_location: str

def read_data(path):
    data = []
    ps = list(glob.glob(path))
    for filepath in ps:
        print(filepath)
        loader = UnstructuredEmailLoader(filepath)
        email = loader.load()
        data.append(email)
    return data

def create_and_store_vectors(data, metadata, index_location, store_location):
    # Here we create a vector store from the documents and save it to disk.
    store = FAISS.from_texts(data, OpenAIEmbeddings(), metadatas=metadata)
    faiss.write_index(store.index, index_location)
    store.index = None
    with open(store_location, "wb") as f:
        pickle.dump(store, f)


email_config = Config("../../data/*.eml", 1500, "\n", "docs.index", "faiss_store.pkl")

data = read_data(email_config.path)
print(data[0])

# # Here we split the documents, as needed, into smaller chunks.
# # We do this due to the context limits of the LLMs.
# text_splitter = CharacterTextSplitter(chunk_size=email_config.chunk_size, separator=email_config.separator)
# docs = []
# metadata = []
# for i, d in enumerate(data):
#     splits = text_splitter.split_text(d)
#     docs.extend(splits)
#     metadata.extend([{"source": email_config.path + " {}".format(i)}] * len(splits))
#
# print(docs[0])
# print(metadata[0])

# create_and_store_vectors("docs.index", "faiss_store.pkl")
