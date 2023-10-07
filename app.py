from flask import Flask, json, request, jsonify
from flask_cors import CORS
import subprocess, time, requests

import urllib.request
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
CORS(app)

command='nougat_api'
url = 'http://127.0.0.1:8503/predict/'


UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() == 'pdf'

@app.route('/upload_image_path', methods=['POST'])
def trigger_nougat():
    
    if 'files[]' not in request.files:
        resp = jsonify({
            "message": "No file part in request",
            "status": "failed"
        })
        resp.status_code = 400
        return resp
    
    files = request.files.getlist('files[]')
    print(files)
    
    file_paths = []
    success = False
    
    # Iterate through files and check if: A) it exists, and B) it is allowed
    for file in files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            
            # Add filename to our /upload folder in /static directory
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            
            file.save(file_path)
            file_paths.append(file_path)        
            
            try: 
                payload = {'file': (file_path, open(file_path, 'rb'), 'application/pdf')}
                process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                time.sleep(16)
            
                while True:
                    output_line = process.stdout.readline().decode('utf-8')
                    print(output_line, end='')
                    
                    if "Uvicorn running on http://127.0.0.1:8503" in output_line:

                        print(output_line, end='', flush='true')
                        
                        response = requests.post(url, files=payload)
                        
                        ocr_result = response.text
                        
                        print(ocr_result)
                        
                        success = True
                        
                        break
                result ={'message': 'API CALL TO NOUGAT DONE'}
                return jsonify(result), 200
            except Exception as e:
                return str(e), 500            
            
            
        # If not true, display fail message
        else:
            resp = jsonify({
                'message': 'File type is not allowed',
                'status': 'Failure'
            })    
            return resp
        
    if success:
        resp = jsonify({
            "message": "Files successfully uploaded",
            "status": "success",
            "file_paths": file_paths
        })
        resp.status_code = 201
        return resp
    
    return resp

if __name__ == "__main__":
    app.run(debug=True, port=3400) 