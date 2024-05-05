"""
Stores functions used across the app
"""
import os
import io
import json
import hashlib
import base64
import requests 
from dotenv import load_dotenv
from google.cloud import storage

load_dotenv()
API_KEY = os.environ.get('API_KEY')

def geocode(address):
    """
    Returns lat, lon from an address.
    """
    base_url = "https://maps.googleapis.com/maps/api/geocode/json?"
    query = f"address={address}&key={API_KEY}"
    search_url = base_url + query

    response = requests.get(search_url)
    data = response.json()

    if data["status"] == "OK":
        coords = data['results'][0]['geometry']['location']
        lat, lon = coords['lat'], coords['lng']

        return lat, lon

def generate_hash(address):
    """
    Given an address, generates a hash to use as file name
    for privacy.
    """
    enc_data = address.encode('utf-8')
    hash_value = hashlib.sha256(enc_data).hexdigest()

    return hash_value

def base64_convert(image_obj):
    with io.BytesIO() as buffer:
        image_obj.save(buffer, format='PNG')
        image_data = buffer.getvalue()

    image_base64 = base64.b64encode(image_data).decode('utf-8')

    return image_base64

def upload_gcs(bucket_name, json_data, destination_blob_name):
    """
    Uploads a local file (source_file_path) to GCP bucket (bucket_name)
    as destination_blob_name
    """
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_string(json_data.encode('utf-8'))
    #blob.upload_from_filename(source_file_path)

def read_gcs(bucket_name, object_name, local_file_path):
    """
    Reads file (object_name) from GCP bucket (bucket_name)
    and stores in local_file_path
    """
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(object_name)
    blob.download_to_filename(local_file_path)

def read_gcs_json(bucket_name, object_name):
    """
    Reads file (object_name) from GCP bucket (bucket_name)
    and stores in local_file_path
    """
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(object_name)
    data = blob.download_as_string()
    return json.loads(data)

def gsc_path_exists(bucket_name, path):
    """
    Check if a path within a GCS bucket exists
    """
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blobs = bucket.list_blobs(prefix=path, max_results=1)

    return next(iter(blobs), None) is not None