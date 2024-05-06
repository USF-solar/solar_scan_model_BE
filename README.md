# Solar Scan
This project automates the data ingestion and prediction processes to identify potential customers for small and medium-sized solar panel installation companies.

### 1. Key Features
**1.1 Data Ingestion Pipeline**: 
1. Takes user-provided zip code, city, and state as input
2. Filter potential locations based on projected max panel count (using Solar API) to optimize processing
3. Geocode remaining addresses for accurate location data 
4. Retrieve raw satellite images from Google Maps Static API
<br>

**1.2 Prediction Pipeline**:
1. Analyzes retrieved satellite images using a pre-trained object detection model (OWLv2 from HuggingFace)
2. Labels potential customer locations without existing solar panels or with pools (proxy for energy consumption)
3. Cache outputs for efficiency (stored in Google Cloud Storage)
4. Return outputs to front end including:
   - Object Detection results (pool and/or solar panels)
   - Output image with bounding boxes (base64 encoded for efficient transmission)

### 2. Deployment and Usage
**2.1 Deployment**:
- The endpoints are generated with flask and the application is deployed on Google Cloud Run using a Docker container. This ensures easy access and scalability.
  
**2.2 Accessing Endpoint**:
- Since the app is deployed on Google Cloud Run, it should be ready to use as is 
- URL Parameters:
    - `zip_code`: US postal code (i.e. 95123)
    - `city`: Name of city in zip code (i.e. San Jose)
    - `state`: US state of city and zip code (i.e. CA)

Example request URL: `https://solar-scan-app-z6nwk7pxdq-uw.a.run.app/output?zip_code=95123&city=San%20Jose&state=CA`
