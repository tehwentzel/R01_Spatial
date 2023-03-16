import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import  glob
from Constants import Const
import joblib
import matplotlib as mpl
import os
import pickle 
import simplejson
import pydicom

def np_converter(obj):
    #converts stuff to vanilla python  for json since it gives an error with np.int64 and arrays
    if isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.float):
        return round(float(obj),3)
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

def get_finished_pids(root=None):
    if root is None:
        root = Const.pointcloud_dir
    files = glob.glob(root + 'pclouds_*.json')
    pids = []
    for file in files:
        pid = file.replace( root+'pclouds_','').replace('.json','')
        if pid.isnumeric():
            pids.append(int(pid))
        else:
            print('bad pid',pid)
    return pids

def get_all_dicom_ids(root = None):
    if root is None:
        root = Const.unprocessed_dicoms
    files = glob.glob(root+'*/')
    ids = []
    for f  in files:
        pid = f.replace(root,'').replace('/','')
        if pid.isnumeric():
            ids.append(int(pid))
        else:
            print('bad pid',pid)
    return ids

def load_patient_folder(root,pid,as_dict=True,file_types=None):
    files = glob.glob(root+str(pid) + '/**/**')
    entry = {}
    pids = set([])
    pid2 = False
    for f in files:
        p = pydicom.dcmread(f)
        pid2 = str(p.PatientName)
        pids.add(pid2)
        dtype = str(p.SOPClassUID.name)
        if file_types is not None and dtype not in file_types:
            continue
        subentry = entry.get(dtype,[])
        subentry.append(p)
        entry[dtype] = subentry
    if len(pids) > 1:
        print('mutilple ids',pids)
    if as_dict:
        return {int(pid2): entry}
    return entry, pid2

def sample_pids(sample_size=10,skip_finished=True,skip_3045918834 = True):
    potential_ids = get_all_dicom_ids()
    if skip_3045918834:
        potential_ids = [pid for pid in potential_ids if int(pid) != 3045918834]
    if skip_finished:
        to_skip = get_finished_pids()
        potential_ids = [pid for pid in potential_ids if pid not in to_skip]
    if sample_size is not None and sample_size < len(potential_ids):
        potential_ids = potential_ids[:sample_size]
    return potential_ids

def load_dicoms(skip_finished=True,sample_size=10):
    root = Const.unprocessed_dicoms
    to_skip = []
    potential_ids = sample_pids(sample_size=sample_size,skip_finished=skip_finished)
    dicom_files = {}
    files = []
    for pid in potential_ids:
        pentry,new_pid = load_patient_folder(root,pid,as_dict=False)
        if str(new_pid) != str(pid):
            print('id mismatch',pid,new_pid)
        dicom_files[int(new_pid)] = pentry

    return dicom_files

def load_dicoms_by_ids(pids):
    dicom_files = {}
    for pid in pids:
        pentry, newpid = load_patient_folder(Const.unprocessed_dicoms,pid,as_dict=False)
        if str(newpid) != str(pid):
            print('id mismatch',pid,newpid)
        dicom_files[int(newpid)] = pentry
    return dicom_files

def get_element(ds,string,default=False):
    try:
        return ds.data_element(string).value
    except:
        return default
    
def fix_roi_name(roi):
    roi = roi.lower()
    if roi not in Const.organ_associations:
        if 'gtv' in roi:
            if 'gtvn' in roi or 'node' in roi or 'nodal' in roi:
                return 'gtvn'
            else:
                return 'gtv'
        if 'ptv' in roi:
            return 'ptv'
        if 'ctv' in roi:
            return 'ctv'
        if 'rtv' in roi:
            return 'rtv'
        if 'cavity_oral' in roi:
            return 'oral_cavity'
        return Const.organ_associations.get(roi.replace(' ','_'),roi)
    return Const.organ_associations.get(roi,roi)

def read_rt_struct(rtstruct,contour_dict = None,associations=None):
    #this should read an rtstruct file, clean the names
    #returns a dict of {roi: [pointcloud,pointclouds...]}
    #multiple pointclouds if there are different contours that are name varaints of a single organ (list gtv)
    
    #pass contour dict if there are mutliple rt struct files?
    if contour_dict is None:
        contour_dict = {}
    if associations is None:
        associations=Const.organ_associations
        
    struct_name = get_element(rtstruct,'StructureSetLabel')

    rseq_list = get_element(rtstruct,'ROIContourSequence',[])
    roi_list = get_element(rtstruct,'StructureSetROISequence',[])
    if len(rseq_list) < 1 or len(roi_list) < 1:
        return False
    assert(len(rseq_list) == len(roi_list))
    for rcseq,roi in zip(rseq_list,roi_list):
        try:
            
            name = fix_roi_name(roi.ROIName)
            number = roi.ROINumber
            if 'ContourSequence' in rcseq:
                cs = rcseq.ContourSequence
                #each contourSequence is at a different z-height, so Imma just merge them
                contours = [np.array(s.ContourData).reshape(-1,3) for s in rcseq.ContourSequence if len(s.ContourData) > 0]
                contours = np.vstack(contours)
                curr_entry = contour_dict.get(name,[])
                curr_entry.append(contours)
                contour_dict[name] = curr_entry
        except Exception as e:
            print('error in read_rt_struct',e)
            
    #so the files with gtvs etc are hand done, and we need the tumor contours but not the other ones
    #because the other file has standardized contours which is better
    gtv_organs = ['gtv','ctv','gtvn','ptv']
    has_gtv = False
    
    for o in gtv_organs:
        if o in contour_dict.keys():
            has_gtv = True
            break
    if has_gtv: 
        contour_dict = {k: v for k, v in contour_dict.items() if k in gtv_organs}
#     else:
#         print(struct_name, contour_dict.keys())
    #check if it's the wrong file
    if not has_gtv and 'HNPF' not in struct_name:
        print('wrong file', struct_name, get_element(rtstruct,'PatientID'))
    return contour_dict

def load_pcloud(pid):
    fname =Const.pointcloud_dir + 'pclouds_' + str(int(pid)) + '.json'
    try:
        with open(fname,'r') as f:
            data = simplejson.load(f)
        return data
    except Exception as e:
        print(e)
        return False
    
def save_individual_patient(pdict,folder=None):
    folder = Const.pointcloud_dir if folder is None else folder
    fname = folder + 'pclouds_' + str(pdict['patient_id'])
    contour_name = folder + 'contours_' + str(pdict['patient_id'])
    to_keep = ['patient_id',
               'study_uid',
               'series_uid',
               'spacing','contours',
               'contour_pointclouds',
               'missing_rois',
               'extra_rois'
              ]
    entry = {k:pdict.get(k) for k in to_keep}
    with open(fname+'.json','w') as f:
        simplejson.dump(entry,f,default=np_converter)
    with open(contour_name+'.json','w') as f2:
        simplejson.dump(pdict['dose_pointcloud'],f2,default=np_converter)
    
    return True