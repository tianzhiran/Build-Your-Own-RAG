import json
import os

import faiss
import numpy as np

from config import TOP_K
from config import VECTOR_DIM
from config import VECTOR_INDEX_FILE
from config import VECTOR_METADATA_FILE


def ensure_parent_dir(file_path):
    parent_dir = os.path.dirname(file_path)

    if parent_dir:
        os.makedirs(parent_dir, exist_ok=True)


def create_index(vector_dim=VECTOR_DIM):
    return faiss.IndexFlatL2(vector_dim)


def load_index(index_file=VECTOR_INDEX_FILE, vector_dim=VECTOR_DIM):
    if os.path.exists(index_file):
        return faiss.read_index(index_file)

    return create_index(vector_dim)


def save_index(index, index_file=VECTOR_INDEX_FILE):
    ensure_parent_dir(index_file)
    faiss.write_index(index, index_file)


def load_metadata(metadata_file=VECTOR_METADATA_FILE):
    if not os.path.exists(metadata_file):
        return []

    with open(metadata_file, "r", encoding="utf-8") as file:
        return json.load(file)


def save_metadata(metadata, metadata_file=VECTOR_METADATA_FILE):
    ensure_parent_dir(metadata_file)

    with open(metadata_file, "w", encoding="utf-8") as file:
        json.dump(metadata, file, ensure_ascii=False, indent=2)


def prepare_vectors(vectors):
    prepared_vectors = np.asarray(vectors).astype("float32")

    if prepared_vectors.ndim == 1:
        prepared_vectors = prepared_vectors.reshape(1, -1)

    return prepared_vectors


def add_vectors(
    vectors,
    chunk_records,
    index_file=VECTOR_INDEX_FILE,
    metadata_file=VECTOR_METADATA_FILE,
    vector_dim=VECTOR_DIM
):
    prepared_vectors = prepare_vectors(vectors)

    if len(prepared_vectors) != len(chunk_records):
        raise ValueError("Vector count must match chunk record count.")

    index = load_index(index_file=index_file, vector_dim=vector_dim)
    metadata = load_metadata(metadata_file=metadata_file)
    start_index = index.ntotal

    index.add(prepared_vectors)

    new_metadata = []

    for offset, chunk_record in enumerate(chunk_records):
        vector_metadata = {
            "vector_index": start_index + offset,
            "chunk_id": chunk_record["chunk_id"],
            "document_id": chunk_record["document_id"]
        }

        metadata.append(vector_metadata)
        new_metadata.append(vector_metadata)

    save_index(index, index_file=index_file)
    save_metadata(metadata, metadata_file=metadata_file)

    return new_metadata


def search(
    query_vector,
    top_k=TOP_K,
    index_file=VECTOR_INDEX_FILE,
    metadata_file=VECTOR_METADATA_FILE,
    vector_dim=VECTOR_DIM
):
    index = load_index(index_file=index_file, vector_dim=vector_dim)

    if index.ntotal == 0:
        return []

    metadata = load_metadata(metadata_file=metadata_file)
    metadata_by_index = {
        item["vector_index"]: item
        for item in metadata
    }

    prepared_query = prepare_vectors(query_vector)
    distances, indices = index.search(prepared_query, top_k)

    results = []

    for distance, vector_index in zip(distances[0], indices[0]):
        if vector_index == -1:
            continue

        vector_metadata = metadata_by_index.get(int(vector_index))

        if not vector_metadata:
            continue

        results.append(
            {
                "vector_index": int(vector_index),
                "distance": float(distance),
                "chunk_id": vector_metadata["chunk_id"],
                "document_id": vector_metadata["document_id"]
            }
        )

    return results


def rebuild_index_from_metadata(
    retained_metadata,
    source_index,
    index_file=VECTOR_INDEX_FILE,
    metadata_file=VECTOR_METADATA_FILE,
    vector_dim=VECTOR_DIM
):
    rebuilt_index = create_index(vector_dim)
    rebuilt_metadata = []
    retained_vectors = []

    for item in retained_metadata:
        vector = source_index.reconstruct(item["vector_index"])
        retained_vectors.append(vector)

    if retained_vectors:
        rebuilt_index.add(prepare_vectors(retained_vectors))

    for new_index, item in enumerate(retained_metadata):
        rebuilt_metadata.append(
            {
                "vector_index": new_index,
                "chunk_id": item["chunk_id"],
                "document_id": item["document_id"]
            }
        )

    save_index(rebuilt_index, index_file=index_file)
    save_metadata(rebuilt_metadata, metadata_file=metadata_file)

    return rebuilt_metadata


def remove_document_vectors(
    document_id,
    index_file=VECTOR_INDEX_FILE,
    metadata_file=VECTOR_METADATA_FILE,
    vector_dim=VECTOR_DIM
):
    metadata = load_metadata(metadata_file=metadata_file)

    if not metadata:
        return 0

    retained_metadata = [
        item
        for item in metadata
        if item["document_id"] != document_id
    ]
    removed_count = len(metadata) - len(retained_metadata)

    if removed_count == 0:
        return 0

    source_index = load_index(index_file=index_file, vector_dim=vector_dim)
    rebuild_index_from_metadata(
        retained_metadata,
        source_index,
        index_file=index_file,
        metadata_file=metadata_file,
        vector_dim=vector_dim
    )

    return removed_count
