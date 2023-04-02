"""Generates a stored index based on raw emails"""
from typing import Optional, Tuple, List

from langchain.document_loaders import UnstructuredEmailLoader
from dataclasses import dataclass
from langchain.vectorstores import FAISS
from langchain.embeddings import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
import pickle
import faiss
import glob

# TODO: Move this to a secret file
OPENAI_KEY = "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"
DATA_DIR = "../../data"


@dataclass
class SourceConfig:
    path: str
    format: str


@dataclass
class PreprocessingConfig:
    chunk_size: Optional[int]
    separator: Optional[str]


def read_data(config: SourceConfig):
    """
    Ingests data based on format provided.
    :param config: SourceConfig describing the raw data to be ingested
    """
    data = []
    ps = list(glob.glob(config.path))

    # Get data loader based on format
    loader = None
    if config.format != 'email':
        raise Exception("Format not supported.")

    # Read data
    for filepath in ps:
        split_emails = UnstructuredEmailLoader(filepath).load()
        data.extend(split_emails)
    return data, ps


def create_and_store_vectors(prepared_data, metadata, index_location, store_location, openai_key=OPENAI_KEY):
    """
    Create & store vector embeddings from the data
    :param prepared_data: Pre-processed data for creating vectors
    :param metadata: Metadata used for vector generation
    :param index_location: Path where the generated index is stored
    :param store_location: Path where the generated vectors are stored
    :return: -
    """
    store = FAISS.from_texts(prepared_data, OpenAIEmbeddings(openai_api_key=openai_key), metadatas=metadata)
    faiss.write_index(store.index, index_location)
    store.index = None
    with open(store_location, "wb") as f:
        pickle.dump(store, f)


def data_prep(data, sources, config: PreprocessingConfig) -> tuple[list[str], list[str]]:
    """
    Perform any preprocessing needed to get data ready for model training. For example, breaking it
     into smaller chunks. Langchain expects to see a source for every document, so metadata is not optional.
    :param data:
    :param config:
    """
    docs: list[str] = []
    metadata: list[dict] = []
    if config.chunk_size is not None:
        if config.separator is None:
            raise ValueError("Separator must be set with chunk size")
        text_splitter = CharacterTextSplitter(chunk_size=config.chunk_size, separator=config.separator)

        metadata = []
        for i, d in enumerate(data):
            splits = text_splitter.split_text(d.page_content)
            docs.extend(splits)
            metadata.extend([{"source": sources[i]}] * len(splits))
    return docs, metadata


# Load stored data
email_config = SourceConfig(DATA_DIR + "/raw_data/*.eml", format="email")
data, filenames = read_data(email_config)

# Prep data for model training
prep_config = PreprocessingConfig(1500, "\n")
processed_data, metadata = data_prep(data, filenames, prep_config)

# Vector generation
create_and_store_vectors(
    processed_data,
    metadata,
    DATA_DIR + "/model_data/docs.index",
    DATA_DIR + "/model_data/faiss_store.pkl"
)
print('Created and stored vectors!')
