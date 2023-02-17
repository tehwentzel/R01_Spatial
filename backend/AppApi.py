import pickle
import simplejson
import numpy as np
import datetime
import glob

DICOM_DIR = '../data/DICOMS/ProcessedPatients/';

def jsonify_np_dict(d):
    def numpy_converter(obj):
        #converts stuff to vanilla python  for json since it gives an error with np.int64 and arrays
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, float):
            return round(float(obj),3)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, datetime.datetime):
            return obj.__str__()
        return obj
    return simplejson.dumps(d,default=numpy_converter)

def np_converter(obj):
    #converts stuff to vanilla python  for json since it gives an error with np.int64 and arrays
    if isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, float):
        return round(float(obj),3)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, np.bool_):
        return bool(obj)
    elif isinstance(obj, datetime.datetime) or isinstance(obj, datetime.time):
        return obj.__str__()
    print('np_converter cant encode obj of type', obj,type(obj))
    return obj
    
def np_dict_to_json(d,destination_file, nan_to_null = False):   
    try:
        with open(destination_file, 'w') as f:
            #nan_to_null makes it save it as null in the json instead of NaN
            #more useful when it's sent to a json but will be read back in python as None
            simplejson.dump(d,f,default = np_converter, ignore_nan = nan_to_null)
        return True
    except Exception as e:
        print(e)
        return False

def load_dicom_data():
    file = '../data/processed_dicoms.p'
    with open(file,'rb') as f:
        patient_list = pickle.load(f)
    return patient_list

def get_all_pids():
    files = glob.glob(DICOM_DIR + 'pcloud_*.json')
    pids = []
    for file in files:
        pid = file.replace('\\','/').replace(DICOM_DIR,'').replace('pcloud_','').replace('\\','').replace('/','').replace('.json','')
        if pid.isnumeric():
            pids.append(int(pid))
        else:
            print('bad pid',pid)
    return pids

def get_patient_parameters(pid):
    patient = get_patient_pcloud(pid)
    roi_map = patient['roi_mask_map']
    rois = list(roi_map.values())
    keys = list(patient.keys())
    pkeys = list(patient['point_clouds'].keys())
    ppkeys = list(patient['point_clouds'][rois[0]].keys())
    return {'rois': rois, 'roi_map': roi_map, 'field_keys': keys, 'pointcloud_keys': pkeys,'pointcloud_roi_keys': ppkeys}

def get_patient_pcloud(pid):
    try:
        file = DICOM_DIR + 'pcloud_' + str(int(pid)) + '.json'
        with open(file,'r') as f:
            pcloud = simplejson.load(f)
        return pcloud
    except:
        return

def get_patient_images(pid):
    file = DICOM_DIR + 'images_' + str(int(pid)) + '.json'
    try:
        with open(file,'r') as f:
            pdict = simplejson.load(f)
        return pdict
    except:
        return

def get_pclouds(pid_list):
    pclouds = [get_patient_pcloud(pid) for pid in pid_list]
    pclouds = [p for p in pclouds if p is not None]
    return pclouds

def get_p_images(pid_list):
    pdicts = [get_patient_images(pid) for pid in pid_list]
    pdicts = [p for p in pdicts if p is not None]
    return pdicts