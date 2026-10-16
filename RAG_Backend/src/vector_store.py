import hashlib
import logging
import os
import threading
from pathlib import Path

import numpy as np
from dotenv import load_dotenv
from fastembed import TextEmbedding
from fastembed.common.model_description import ModelSource, PoolingType
from huggingface_hub import snapshot_download
from langchain_core.embeddings import Embeddings
from langchain_community.vectorstores import FAISS
from src.config import VECTOR_STORE_DIR, RETRIEVER_K, EMBEDDING_MODEL_NAME

load_dotenv()

logger = logging.getLogger(__name__)

_retriever = None
_retriever_lock = threading.Lock()
_EXPECTED_ARTIFACT_HASHES = {
    "index.faiss": "6e8be20813ece1ec3faa97993d56db37fb0f91813e0b2116ec28fc113ca3d3ab",
    "index.pkl": "eeaa64ddbb4e3145804f6bd108cd3adfd2bcec8e8fb4a925223dd2afdd3a4459",
}
_EMBEDDING_MODEL_ID = "local/all-MiniLM-L6-v2-pinned"
_EMBEDDING_MODEL_REPO = f"sentence-transformers/{EMBEDDING_MODEL_NAME}"
_EMBEDDING_MODEL_REVISION = "1110a243fdf4706b3f48f1d95db1a4f5529b4d41"
_EMBEDDING_MODEL_SHA256 = "6fd5d72fe4589f189f8ebc006442dbb529bb7ce38f8082112682524616046452"
_EMBEDDING_MODEL_FILE = "onnx/model.onnx"
_EMBEDDING_MODEL_FILES = [
    _EMBEDDING_MODEL_FILE,
    "config.json",
    "tokenizer.json",
    "tokenizer_config.json",
    "special_tokens_map.json",
]
_EMBEDDING_DIMENSION = 384


def _load_embedding_model() -> TextEmbedding:
    model_path = os.environ.get("EMBEDDING_MODEL_PATH")
    if model_path:
        model_dir = Path(model_path)
    else:
        model_dir = Path(
            snapshot_download(
                repo_id=_EMBEDDING_MODEL_REPO,
                revision=_EMBEDDING_MODEL_REVISION,
                allow_patterns=_EMBEDDING_MODEL_FILES,
            )
        )

    model_file = model_dir / _EMBEDDING_MODEL_FILE
    digest = hashlib.sha256()
    try:
        with model_file.open("rb") as artifact:
            for block in iter(lambda: artifact.read(1024 * 1024), b""):
                digest.update(block)
    except OSError as error:
        raise RuntimeError("The pinned ONNX embedding model is unavailable.") from error
    if digest.hexdigest() != _EMBEDDING_MODEL_SHA256:
        raise RuntimeError("Embedding model integrity verification failed.")

    registered_models = {
        model["model"] for model in TextEmbedding.list_supported_models()
    }
    if _EMBEDDING_MODEL_ID not in registered_models:
        TextEmbedding.add_custom_model(
            model=_EMBEDDING_MODEL_ID,
            pooling=PoolingType.MEAN,
            normalization=False,
            sources=ModelSource(hf=_EMBEDDING_MODEL_REPO),
            dim=_EMBEDDING_DIMENSION,
            model_file=_EMBEDDING_MODEL_FILE,
            description="Pinned all-MiniLM-L6-v2 ONNX export with mean pooling.",
            license="apache-2.0",
            size_in_gb=0.09,
            additional_files=_EMBEDDING_MODEL_FILES[1:],
        )
    return TextEmbedding(
        model_name=_EMBEDDING_MODEL_ID,
        specific_model_path=str(model_dir),
        threads=1,
        providers=["CPUExecutionProvider"],
    )


class LocalONNXEmbeddings(Embeddings):
    def __init__(self, model: TextEmbedding) -> None:
        self.model = model

    def embed_query(self, text: str) -> list[float]:
        vector = next(self.model.query_embed(text))
        if vector.shape != (_EMBEDDING_DIMENSION,):
            raise ValueError("The local embedding model returned an unexpected shape.")
        return np.asarray(vector, dtype=np.float32).tolist()

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [
            np.asarray(vector, dtype=np.float32).tolist()
            for vector in self.model.passage_embed(texts)
        ]


def _verify_index_artifacts() -> None:
    for filename, expected_hash in _EXPECTED_ARTIFACT_HASHES.items():
        path = os.path.join(VECTOR_STORE_DIR, filename)
        digest = hashlib.sha256()
        try:
            with open(path, "rb") as artifact:
                for block in iter(lambda: artifact.read(1024 * 1024), b""):
                    digest.update(block)
        except OSError as error:
            raise RuntimeError(f"Required vector index artifact is unavailable: {filename}") from error
        if digest.hexdigest() != expected_hash:
            raise RuntimeError(
                f"Vector index integrity verification failed for {filename}."
            )


def get_retriever():
    global _retriever
    if _retriever is not None:
        return _retriever

    with _retriever_lock:
        if _retriever is not None:
            return _retriever

        _verify_index_artifacts()
        embeddings = LocalONNXEmbeddings(_load_embedding_model())
        vectorstore = FAISS.load_local(
            folder_path=VECTOR_STORE_DIR,
            embeddings=embeddings,
            allow_dangerous_deserialization=True
        )

        if vectorstore.index.d != _EMBEDDING_DIMENSION:
            raise RuntimeError("The loaded vector index has an unexpected dimension.")

        _retriever = vectorstore.as_retriever(search_kwargs={"k": RETRIEVER_K})
        logger.info("Verified FAISS index loaded (%d vectors).", vectorstore.index.ntotal)
        return _retriever
