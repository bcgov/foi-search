from dataclasses import dataclass
import os
from typing import Optional


@dataclass
class SolrConfig:
    solr_url: str = None
    collection: str = None
    timeout: float = None
    max_retries: int = None
    retry_delay: float = None
    verify_ssl: bool = None

    username: Optional[str] = None
    password: Optional[str] = None

    document_id_prefix: str = None
    batch_size: int = None

    def __post_init__(self):
        if not self.solr_url:
            self.solr_url = os.getenv("SOLR_URL", "http://localhost:8983/solr")
        if not self.collection:
            self.collection = os.getenv("SOLR_COLLECTION", "vector_collection_384")
        if self.timeout is None:
            self.timeout = float(os.getenv("SOLR_TIMEOUT", "30.0"))
        if self.max_retries is None:
            self.max_retries = int(os.getenv("SOLR_MAX_RETRIES", "3"))
        if self.retry_delay is None:
            self.retry_delay = float(os.getenv("SOLR_RETRY_DELAY", "1.0"))
        if self.verify_ssl is None:
            self.verify_ssl = os.getenv("SOLR_VERIFY_SSL", "true").lower() in ("true", "1", "yes")
        if not self.username:
            self.username = os.getenv("SOLR_USERNAME")
        if not self.password:
            self.password = os.getenv("SOLR_PASSWORD")
        if not self.document_id_prefix:
            self.document_id_prefix = os.getenv("SOLR_DOC_PREFIX", "doc")
        if self.batch_size is None:
            self.batch_size = int(os.getenv("SOLR_BATCH_SIZE", "100"))
