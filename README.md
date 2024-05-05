# Solar Scan
This repo implements data ingestion and prediction pipeline to detect pools and existing solar panels from satellite image data, in order to prioritize leads for small/medium solar panel installation companies. The data ingestion pipeline takes zip code, city, and state as inputs. The data is processed to retrieve raw satellite images, which are then passed to the prediction pipeline. The prediction pipleine then performs object detection using the OWLv2 model from HuggingFace. It returns whether the objects of interest were detecte and output images with bounding boxes (which are then base64 encoded). Currently, the output is limited to 5 due to latency in calling the model. The endpoints are generated with Flask and scaled with Google Cloud Run. 

### Pipelines
**Data Ingestion**: 
1. Input: zip code, city, and state
2. Filter based on projected max panel count (to decrease number of images have to process) from Solar API
3. Geocode remaining addresses
4. Retrieve raw satellite images from Maps Static API
**Prediction**:
1. Take raw images and pass through model
2. Cache outputs of previous queries to GCS
3. Return outputs

### Usage
**Accessing Endpoint**:
- The app is deployed on Google Cloud Run using a Docker container, so it should be ready to use as is 
- URL Parameters:
    - `zip_code`: US postal code
    - `city`: Name of city in zip code
    - `state`: US state of city and zip code

Example request URL: `https://solar-scan-app-z6nwk7pxdq-uw.a.run.app/output?zip_code=95123&city=San%20Jose&state=CA`
