"""
Data Ingestion:
- Input: zip code, city, state 
1. Retrieve list addresses 
2. Filter with Solar API 
3. Geocode remaining addresses -> lat, lon
4. Retrieve the raw satellite images 
5. Load into the tmp/ directory 
"""
import os
import sys
import requests
from dotenv import load_dotenv
from src.exception import CustomException
from src.logger import logging
from src.utils import geocode, generate_hash

load_dotenv()
API_KEY = os.environ.get('API_KEY')

class DataIngestionConfig:
    """
    Class with methods to process the input and 
    writes the raw satellite image data to tmp/
    and returns the coordinate dictionary. 

    Coordinate dictionary contains the address, coordinates, 
    solar info, and hash value
    """
    def __init__(self) -> None:
        """
        Empty init
        """

    def initiate_data_ingestion(self, zip_code, city, state):
        """
        1. From the input, retrieve the list of addresses
        2. Filter with the Solar API
        3. Geocode remaining addresses to lat,lon coordinates
        4. Retrieve the raw satellite images 
        5. Load into the tmp/ directory
        """
        logging.info('Data Ingestion Initiated')

        try:
            # Step 1: Retrieve list of addresses
            query = f"""
                [out:json][timeout:25];
                nwr["building"="house"]["addr:postcode"="{zip_code}"]["addr:city"="{city}"];
                out geom;
            """

            url_encoded_query = {'data': query}
            osm_response = requests.post('https://overpass-api.de/api/interpreter', data=url_encoded_query)
            address_list = list()

            if osm_response.status_code == 200:
                logging.info('Successfully retrieved addresses')
                for element in osm_response.json()['elements']:
                    tag = element['tags']
                    address = f"{tag['addr:housenumber']} {tag['addr:street']} {city} {state}"
                    address_list.append(address)

            # Step 2: Filter address list with Solar API
            solar_api_url = "http://54.160.173.202:8080/getSolarData"
            api_urls = [f"{solar_api_url}?address={addr.replace(' ', '%20')}" for addr in address_list[:100]] #### Take out for implementation
            solar_api_outputs = list()
            
            for addr, url in zip(address_list, api_urls):
                solar_response = requests.get(url)
                if solar_response.status_code == 200:
                    output = solar_response.json()
                    solar_api_outputs.append((addr, output))

            #top10_percentile_idx = len(solar_api_outputs) // 10
            top5 = sorted(solar_api_outputs, key=lambda x: x[1]['Max Panel Count'], reverse=True)[:5]
            top5 = {addr: solar_output for addr, solar_output in top5}

            # Step 3: Geocode addresses
            coordinate_dict = {
                addr: {
                    'coords': geocode(addr),
                    'solar_info': top5[addr],
                } for addr in top5
            }

            # Step 4: Retrieve raw images 
            for addr in coordinate_dict:
                hash_value = generate_hash(addr)
                coordinate_dict[addr]['hash'] = hash_value
                lat, lon = coordinate_dict[addr]['coords']

                base_url = "https://maps.googleapis.com/maps/api/staticmap"
                query = f"?center={lat},{lon}&zoom=21&size=600x600&maptype=satellite&key={API_KEY}"
                search_url = base_url + query
                maps_response = requests.get(search_url)

            # Step 5: Write to tmp/ directory
                if maps_response.status_code == 200:
                    os.makedirs('tmp', exist_ok=True)

                    with open(f'tmp/{hash_value}.png', 'wb') as f:
                        f.write(maps_response.content)
            
            logging.info('Images successfully retrieved')

            return coordinate_dict

        except Exception as e:
            return CustomException(e, sys)
        
if __name__ == "__main__":
    obj = DataIngestionConfig()
    obj.initiate_data_ingestion('95123', 'San Jose', 'CA')