from flask import Flask, jsonify, request
from flask_cors import CORS
import simplejson
import pickle
from AppApi import *

app = Flask(__name__)
CORS(app)
print('code start')
dicom_data = load_dicom_data()
FIELD_KEYS = list(dicom_data[0].keys())
PATIENT_IDS = sorted([d['id'] for d in dicom_data])
ROI_MAP = dicom_data[0]['roi_mask_map']
ROIS = list(ROI_MAP.values())
dicom_data = {i['id']: i for i in dicom_data}
print('data loaded')

def as_float(item):
    if item is None:
        return item
    try:
        item = float(item)
        return item
    except:
        return None

def responsify(dictionary):
    # djson = nested_responsify(dictionary) #simplejson.dumps(dictionary,default=np_converter,ignore_nan=True)
    djson = simplejson.dumps(dictionary,default=np_converter,ignore_nan=True)
    resp = app.response_class(
        response=djson,
        mimetype='application/json',
        status=200
    )
    return resp

@app.route('/')
def test():
    return 'test succesful'

@app.route('/parameters')
def get_parameters():
    data = {
        'fields': FIELD_KEYS[:],
        'patientIds': PATIENT_IDS[:],
        'roiMap': ROI_MAP,
        'rois': ROIS[:]
    }
    response = responsify(data)
    return response
    
@app.route('/patientdata',methods=['GET'])
def get_patient_data():
    print('getting patient data')
    patients = request.args.getlist('patientIds')
    fields = request.args.getlist('patientFields')
    if patients is None or len(patients) <= 0:
        patients = list(dicom_data.keys())[0:2]
    if fields is None or len(fields) <= 0:
        fields = ['id','contours','contour_values','distances']
    patients = [int(p) for p in patients if int(p) in dicom_data.keys()]
    fields = [f for f in fields if f in FIELD_KEYS]
    print('f and p',fields,patients)
    return_vals = [dicom_data[p] for p in patients]
    return_vals = [{f: x[f] for f in fields} for x in return_vals]
    print('return patient data',return_vals)
    data = responsify(return_vals)
    print('patient data',data)
    return data

@app.route('/pclouds',methods=['GET'])
def get_patient_clouds():
    patients = request.args.getlist('patientIds')
    if patients is None or len(patients) <= 0:
        patients = [1,2]
    patients = get_pclouds(patients)
    data = responsify(patients)
    print('patient clouds',data)
    return data

@app.route('/images',methods=['GET'])
def get_patient_images():
    patients = request.args.getlist('patientIds')
    if patients is None or len(patients) <= 0:
        patients = [1,2]
    patients = get_p_images(patients)
    data = responsify(patients)
    print('patient images',data)
    return data