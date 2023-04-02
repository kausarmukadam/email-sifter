"""Generates a stored index based on raw emails"""

from langchain.document_loaders import UnstructuredEmailLoader
from dataclasses import dataclass
from langchain.vectorstores import FAISS
from langchain.embeddings import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
import pickle
import faiss
import glob


@dataclass
class SourceConfig:
    path: str
    format: str

@dataclass
class PreprocessingConfig:
    chunk_size: int
    separator: "\n"


def read_data(config: SourceConfig):
    """
    Ingests data based on format provided.
    :param config: SourceConfig describing the raw data to be ingested
    """
    data = []
    ps = list(glob.glob(config.path))

    # Get data loader based on format
    loader = None
    if config.format == 'email':
        loader = UnstructuredEmailLoader
    else:
        raise Exception("Format not supported.")

    # Read data
    for filepath in ps:
        print(filepath)
        data.append(loader(filepath).load())
    return data


def create_and_store_vectors(prepared_data, metadata, index_location, store_location):
    """
    Create & store vector embeddings from the data
    :param prepared_data: Pre-processed data for creating vectors
    :param metadata: Metadata used for vector generation
    :param index_location: Path where the generated index is stored
    :param store_location: Path where the generated vectors are stored
    :return: -
    """
    store = FAISS.from_texts(prepared_data, OpenAIEmbeddings(), metadatas=metadata)
    faiss.write_index(store.index, index_location)
    store.index = None
    with open(store_location, "wb") as f:
        pickle.dump(store, f)


def data_prep(data, config: PreprocessingConfig):
    """
    Perform any preprocessing needed to get data ready for model training. For example, breaking it into smaller
    chunks.
    :param data:
    :param config:
    """
    text_splitter = CharacterTextSplitter(chunk_size=config.chunk_size, separator=config.separator)
    docs = []
    metadata = []
    for i, d in enumerate(data):
        splits = text_splitter.split_text(d)
        docs.extend(splits)
        metadata.extend([{"source": email_config.path + " {}".format(i)}] * len(splits))
    print(len(metadata))
    return docs, metadata


# Load stored data
email_config = SourceConfig("../../data/*.eml", format="email")
data = read_data(email_config)
print(data[0])

# Prep data for model training
prep_config = PreprocessingConfig(chunk_size=1500, separator="\n")
processed_data, _ = data_prep(data, prep_config)

# Vector generation
create_and_store_vectors(processed_data, "docs.index", "faiss_store.pkl")
