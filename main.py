import json
from flask import Flask, request, render_template
from flask_cors import CORS
from src.data_ingestion import DataIngestionConfig
from src.predict_pipeline import CustomData, PredictPipeline
from src.utils import base64_convert, upload_gcs, gsc_path_exists, read_gcs_json

app = Flask(__name__, template_folder='templates')
CORS(app)

@app.route('/')
def index():
    render_template('index.html')

@app.route('/output')
def get_output():
    zip_code = request.args.get('zip_code')
    city = request.args.get('city')
    state = request.args.get('state')

    # Step 1: Chekc if prevously queried 
    bucket_name = 'solar-scan-storage'
    check_path = f"{state}/{zip_code}/{city}.json"

    if gsc_path_exists(bucket_name, check_path):
        return read_gcs_json(bucket_name, check_path)

    else:
        # Step 2: Get image information and write to tmp/
        data_obj = DataIngestionConfig()
        information_dict = data_obj.initiate_data_ingestion(zip_code, city, state)

        # Step 3: Read the images from tmp/
        image_dir = 'tmp/'
        custom_data = CustomData(image_dir)
        image_obj_list = custom_data.get_data()

        # Step 4: Process the images and convert to base64 string
        predict_pipeline = PredictPipeline()
        output_images, results = predict_pipeline.predict(image_obj_list, custom_data.image_paths)

        string_encoded_images = [base64_convert(img) for img in output_images]
        
        response_data = dict()

        for idx, addr in enumerate(information_dict):
            response_data[addr] = dict()
            response_data[addr]['has_solar'] = 0 in results[idx]['labels']
            response_data[addr]['has_pool'] = 1 in results[idx]['labels']
            response_data[addr]['base64_image'] = string_encoded_images[idx]

        # Step 5: Store outputs in GCS 
        ### Write the output to GCP in zipcode directory
        response_json = json.dumps(response_data, indent=4)
        object_name = f'{state}/{zip_code}/{city}.json'
        upload_gcs(bucket_name, response_json, object_name)


        return response_json

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)