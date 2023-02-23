import os
from datetime import timedelta
from typing import Callable, Dict, List, Optional

from google.cloud import exceptions, storage

from dstack.backend.base.storage import SIGNED_URL_EXPIRATION, CloudStorage
from dstack.core.storage import StorageFile
from dstack.utils.common import removeprefix


class GCPStorage(CloudStorage):
    def __init__(self, project_id: str, bucket_name: str):
        self.storage_client = self._get_client(project_id)
        self.bucket_name = bucket_name

    def configure(self):
        self.bucket = self._get_or_create_bucket(self.bucket_name)

    def put_object(self, key: str, content: str, metadata: Optional[Dict] = None):
        blob = self.bucket.blob(key)
        blob.metadata = metadata
        blob.upload_from_string(content)

    def get_object(self, key: str) -> Optional[str]:
        blob = self.bucket.get_blob(key)
        if blob is None:
            return None
        with blob.open() as f:
            return f.read()

    def delete_object(self, key: str):
        try:
            self.bucket.delete_blob(key)
        except exceptions.NotFound:
            pass

    def list_objects(self, keys_prefix: str) -> List[str]:
        # TODO pagination
        blobs = self.bucket.client.list_blobs(self.bucket.name, prefix=keys_prefix)
        object_names = [blob.name for blob in blobs]
        return object_names

    def list_files(self, dirpath: str) -> List[StorageFile]:
        prefix = dirpath
        blobs = self.bucket.client.list_blobs(self.bucket.name, prefix=prefix)
        files = []
        for blob in blobs:
            file = StorageFile(
                filepath=removeprefix(blob.name, prefix),
                filesize_in_bytes=blob.size,
            )
            files.append(file)
        return files

    def download_file(self, source_path: str, dest_path: str, callback: Callable[[int], None]):
        blob = self.bucket.blob(source_path)
        blob.download_to_filename(dest_path)
        callback(os.path.getsize(dest_path))

    def upload_file(self, source_path: str, dest_path: str, callback: Callable[[int], None]):
        blob = self.bucket.blob(dest_path)
        blob.upload_from_filename(source_path)
        callback(os.path.getsize(source_path))

    def get_signed_download_url(self, key: str) -> str:
        blob = self.bucket.blob(key)
        url = blob.generate_signed_url(expiration=timedelta(seconds=SIGNED_URL_EXPIRATION))
        return url

    def get_signed_upload_url(self, key: str) -> str:
        blob = self.bucket.blob(key)
        url = blob.generate_signed_url(
            expiration=timedelta(seconds=SIGNED_URL_EXPIRATION),
            method="PUT",
        )
        return url

    def _get_client(self, project_id: str) -> storage.Client:
        return storage.Client(project=project_id)

    def _get_or_create_bucket(self, bucket_name: str):
        try:
            return self.storage_client.create_bucket(bucket_name)
        except exceptions.Conflict:
            return self.storage_client.bucket(bucket_name)