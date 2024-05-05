# Solar Scan
This repo demonstrates a data ingestion and prediction pipeline implemented using Flask, and deployed using Google Cloud Run. The data ingestion pipeline takes zip code, city, and state as inputs. The data is processed to retrieve raw satellite images, which are then passed to the prediction pipeline. The prediction pipleine then performs object detection and returns the results and output images (with bounding boxes). The outputs are accessed through endpoints generated with Flask, served and deployed using Google Cloud Run. 

### Pipelines
**Data Ingestion**: 
1. Take zip code, city, and state as input
2. Filter based on projected max panel count (to decrease number of images have to process)
3. Retrieve raw satellite images
**Prediction**:
1. Take raw images and pass through model
2. Cache outputs of previous queries to GCS 

### Usage
**Accessing Endpoint**:
- The app is deployed on Google Cloud Run using a Docker container, so it should be ready to use as is. 
- URL Parameters:
    - `zip_code`: US postal code
    - `city`: Name of city in zip code
    - `state`: US state of city and zip code

Example request URL: `https://solar-scan-app-z6nwk7pxdq-uw.a.run.app/output?zip_code=95123&city=San%20Jose&state=CA`