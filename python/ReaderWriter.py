__author__ = 'Brian M Anderson'

# Created on 12/31/2020
import os
from tqdm import tqdm
import typing
from glob import glob
import pydicom
import numpy as np
from pydicom.tag import Tag
import SimpleITK as sitk
from skimage.measure import label, regionprops, find_contours
from threading import Thread
from multiprocessing import cpu_count
from queue import *
import pandas as pd
import copy
import cv2
from typing import List

import matplotlib.pyplot as plt


def plot_scroll_Image(x):
    '''
    :param x: input to view of form [rows, columns, # images]
    :return:
    '''
    if x.dtype not in ['float32','float64']:
        x = copy.deepcopy(x).astype('float32')
    if len(x.shape) > 3:
        x = np.squeeze(x)
    if len(x.shape) == 3:
        if x.shape[0] != x.shape[1]:
            x = np.transpose(x,[1,2,0])
        elif x.shape[0] == x.shape[2]:
            x = np.transpose(x, [1, 2, 0])
    fig, ax = plt.subplots(1, 1)
    if len(x.shape) == 2:
        x = np.expand_dims(x,axis=-1)
    tracker = IndexTracker(ax, x)
    fig.canvas.mpl_connect('scroll_event', tracker.onscroll)
    return fig,tracker
    #Image is input in the form of [#images,512,512,#channels]

def contour_worker(A):
    q, kwargs = A
    point_maker = PointOutputMakerClass(**kwargs)
    while True:
        item = q.get()
        if item is None:
            break
        else:
            point_maker.make_output(**item)
        q.task_done()


def worker_def(A):
    q, pbar = A
    while True:
        item = q.get()
        if item is None:
            break
        else:
            iteration, index, out_path, key_dict = item
            base_class = DicomReaderWriter(**key_dict)
            try:
                base_class.set_index(index)
                base_class.get_images_and_mask()
                base_class.__set_iteration__(iteration)
                base_class.write_images_annotations(out_path)
            except:
                print('failed on {}'.format(base_class.series_instances_dictionary[index]['Image_Path']))
                fid = open(os.path.join(base_class.series_instances_dictionary[index]['Image_Path'], 'failed.txt'),
                           'w+')
                fid.close()
            pbar.update()
            q.task_done()


def folder_worker(A):
    q, pbar = A
    while True:
        item = q.get()
        if item is None:
            break
        else:
            dicom_adder = AddDicomToDictionary()
            dicom_path, images_dictionary, rt_dictionary, rd_dictionary, rp_dictionary, verbose = item
            try:
                if verbose:
                    print('Loading from {}'.format(dicom_path))
                dicom_adder.add_dicom_to_dictionary_from_path(dicom_path=dicom_path,
                                                              images_dictionary=images_dictionary,
                                                              rt_dictionary=rt_dictionary,
                                                              rd_dictionary=rd_dictionary,
                                                              rp_dictionary=rp_dictionary)
            except:
                print('failed on {}'.format(dicom_path))
            pbar.update()
            q.task_done()


class PointOutputMakerClass(object):
    def __init__(self, image_size_rows: int, image_size_cols: int, PixelSize, contour_dict, RS):
        self.image_size_rows, self.image_size_cols = image_size_rows, image_size_cols
        self.PixelSize = PixelSize
        self.contour_dict = contour_dict
        self.RS = RS

    def make_output(self, annotation, i, dicom_handle):
        self.contour_dict[i] = []
        regions = regionprops(label(annotation))
        for ii in range(len(regions)):
            temp_image = np.zeros([self.image_size_rows, self.image_size_cols])
            data = regions[ii].coords
            rows = []
            cols = []
            for iii in range(len(data)):
                rows.append(data[iii][0])
                cols.append(data[iii][1])
            temp_image[rows, cols] = 1
            contours = find_contours(temp_image, level=0.5, fully_connected='low', positive_orientation='high')
            for contour in contours:
                contour = np.squeeze(contour)
                with np.errstate(divide='ignore'):
                    slope = (contour[1:, 1] - contour[:-1, 1]) / (contour[1:, 0] - contour[:-1, 0])
                slope_index = None
                out_contour = []
                for index in range(len(slope)):
                    if slope[index] != slope_index:
                        out_contour.append(contour[index])
                    slope_index = slope[index]
                contour = [[float(c[1]), float(c[0]), float(i)] for c in out_contour]
                contour = np.asarray([dicom_handle.TransformContinuousIndexToPhysicalPoint(zz) for zz in contour])
                self.contour_dict[i].append(np.asarray(contour))


def poly2mask(vertex_row_coords: np.array, vertex_col_coords: np.array,
              shape: tuple) -> np.array:
    """[converts polygon coordinates to filled boolean mask]
    Args:
        vertex_row_coords (np.array): [row image coordinates]
        vertex_col_coords (np.array): [column image coordinates]
        shape (tuple): [image dimensions]
    Returns:
        [np.array]: [filled boolean polygon mask with vertices at
                     (row, col) coordinates]
    """
    xy_coords = np.array([vertex_col_coords, vertex_row_coords])
    coords = np.expand_dims(xy_coords.T, 0)
    mask = np.zeros(shape)
    cv2.fillPoly(mask, coords, 1)
    return np.array(mask, dtype=np.bool)


def add_images_to_dictionary(images_dictionary, dicom_names, sitk_dicom_reader,
                             path: typing.Union[str, bytes, os.PathLike]):
    """
    :param images_dictionary: dictionary of series instance UIDs for images
    :param sitk_dicom_reader: sitk.ImageFileReader()
    :param path: path to the images or structure in question
    """
    series_instance_uid = sitk_dicom_reader.GetMetaData("0020|000e")
    if series_instance_uid not in images_dictionary:
        patientID = sitk_dicom_reader.GetMetaData("0010|0020")
        while len(patientID) > 0 and patientID[-1] == ' ':
            patientID = patientID[:-1]
        description, pixel_spacing_x, pixel_spacing_y, slice_thickness = None, None, None, None
        meta_keys = sitk_dicom_reader.GetMetaDataKeys()
        if "0008|103e" in meta_keys:
            description = sitk_dicom_reader.GetMetaData("0008|103e")
        if "0028|0030" in meta_keys:
            pixel_spacing_x, pixel_spacing_y = sitk_dicom_reader.GetMetaData("0028|0030").strip(' ').split('\\')
            pixel_spacing_x, pixel_spacing_y = float(pixel_spacing_x), float(pixel_spacing_y)
        if "0018|0050" in meta_keys:
            slice_thickness = float(sitk_dicom_reader.GetMetaData("0018|0050"))
        study_instance_uid = sitk_dicom_reader.GetMetaData("0020|000d")
        temp_dict = {'PatientID': patientID, 'SeriesInstanceUID': series_instance_uid, 'Files': dicom_names,
                     'StudyInstanceUID': study_instance_uid, 'RTs': {}, 'RDs': {}, 'RPs': {},
                     'Image_Path': path, 'Description': description, 'Pixel_Spacing_X': pixel_spacing_x,
                     'Pixel_Spacing_Y': pixel_spacing_y, 'Slice_Thickness': slice_thickness}
        images_dictionary[series_instance_uid] = temp_dict


def add_rp_to_dictionary(ds, path: typing.Union[str, bytes, os.PathLike], rp_dictionary):
    try:
        series_instance_uid = ds.SeriesInstanceUID
        if series_instance_uid not in rp_dictionary:
            refed_structure_uid = ds.ReferencedStructureSetSequence[0].ReferencedSOPInstanceUID
            refed_dose_uid = ds.DoseReferenceSequence[0].DoseReferenceUID
            temp_dict = {'Path': path, 'SOPInstanceUID': ds.SOPInstanceUID,
                         'ReferencedStructureSetSOPInstanceUID': refed_structure_uid,
                         'ReferencedDoseSOPUID': refed_dose_uid, 'Description': ds.StudyDescription}
            rp_dictionary[series_instance_uid] = temp_dict
    except:
        print("Had an error loading " + path)


def add_rt_to_dictionary(ds, path: typing.Union[str, bytes, os.PathLike], rt_dictionary):
    """
    :param ds: pydicom data structure
    :param path: path to the images or structure in question
    """
    try:
        series_instance_uid = ds.SeriesInstanceUID
        sop_instance_uid = ds.SOPInstanceUID
        if series_instance_uid not in rt_dictionary:
            for referenced_frame_of_reference in ds.ReferencedFrameOfReferenceSequence:
                for referred_study_sequence in referenced_frame_of_reference.RTReferencedStudySequence:
                    for referred_series in referred_study_sequence.RTReferencedSeriesSequence:
                        refed_series_instance_uid = referred_series.SeriesInstanceUID
                        if Tag((0x3006, 0x020)) in ds.keys():
                            ROI_Structure = ds.StructureSetROISequence
                        else:
                            ROI_Structure = []
                        rois_in_structure = {}
                        rois = []
                        for Structures in ROI_Structure:
                            rois.append(Structures.ROIName.lower())
                            if Structures.ROIName not in rois_in_structure:
                                rois_in_structure[Structures.ROIName] = Structures.ROINumber
                        temp_dict = {'Path': path, 'ROI_Names': rois, 'ROIs_in_structure': rois_in_structure,
                                     'SeriesInstanceUID': refed_series_instance_uid, 'Plans': {}, 'Doses': {},
                                     'SOPInstanceUID': sop_instance_uid}
                        rt_dictionary[series_instance_uid] = temp_dict
    except:
        print("Had an error loading " + path)


def add_rd_to_dictionary(sitk_dicom_reader, rd_dictionary):
    """
    :param ds: pydicom data structure
    :param path: path to the images or structure in question
    """
    try:
        ds = pydicom.read_file(sitk_dicom_reader.GetFileName())
        series_instance_uid = sitk_dicom_reader.GetMetaData("0020|000e")
        rt_sopinstance_uid = ds.ReferencedStructureSetSequence[0].ReferencedSOPInstanceUID
        rp_sopinstance_uid = ds.ReferencedRTPlanSequence[0].ReferencedSOPInstanceUID
        if series_instance_uid not in rd_dictionary:
            study_instance_uid = sitk_dicom_reader.GetMetaData("0020|000d")
            description = None
            if "0008|103e" in sitk_dicom_reader.GetMetaDataKeys():
                description = sitk_dicom_reader.GetMetaData("0008|103e")
            temp_dict = {'Path': sitk_dicom_reader.GetFileName(), 'StudyInstanceUID': study_instance_uid,
                         'SOPInstanceUID': sitk_dicom_reader.GetMetaData("0008|0018"),
                         'Description': description, 'ReferencedStructureSetSOPInstanceUID': rt_sopinstance_uid,
                         'ReferencedPlanSOPInstanceUID': rp_sopinstance_uid}
            rd_dictionary[series_instance_uid] = temp_dict
    except:
        print("Had an error loading " + sitk_dicom_reader.GetFileName())


def add_sops_to_dictionary(sitk_dicom_reader, series_instances_dictionary):
    """
    :param sitk_dicom_reader: sitk.ImageSeriesReader()
    :param series_instances_dictionary: dictionary of series instance UIDs
    """
    series_instance_uid = sitk_dicom_reader.GetMetaData(0, "0020|000e")
    keys = []
    series_instance_uids = []
    for key, value in series_instances_dictionary.items():
        keys.append(key)
        series_instance_uids.append(value['SeriesInstanceUID'])
    index = keys[series_instance_uids.index(series_instance_uid)]
    sopinstanceuids = [sitk_dicom_reader.GetMetaData(i, "0008|0018") for i in
                       range(len(sitk_dicom_reader.GetFileNames()))]
    temp_dict = {'SOP_Instance_UIDs': sopinstanceuids}
    series_instances_dictionary[index].update(temp_dict)


def return_template_dictionary():
    template_dictionary = {'Image_Path': None, 'PatientID': None, 'RTs': {}, 'RDs': {}, 'RPs': {}, 'Description': None,
                           'SOP_Instance_UIDs': None, 'SeriesInstanceUID': None, 'Files': None}
    return template_dictionary


def add_to_mask(mask, z_value, r_value, c_value, mask_value=1):
    mask[int(np.floor(z_value)), int(np.floor(r_value)), int(np.floor(c_value))] = mask_value
    mask[int(np.floor(z_value)), int(np.ceil(r_value)), int(np.floor(c_value))] = mask_value
    mask[int(np.floor(z_value)), int(np.floor(r_value)), int(np.ceil(c_value))] = mask_value
    mask[int(np.floor(z_value)), int(np.ceil(r_value)), int(np.ceil(c_value))] = mask_value
    mask[int(np.ceil(z_value)), int(np.floor(r_value)), int(np.floor(c_value))] = mask_value
    mask[int(np.ceil(z_value)), int(np.ceil(r_value)), int(np.floor(c_value))] = mask_value
    mask[int(np.ceil(z_value)), int(np.floor(r_value)), int(np.ceil(c_value))] = mask_value
    mask[int(np.ceil(z_value)), int(np.ceil(r_value)), int(np.ceil(c_value))] = mask_value
    return None


class AddDicomToDictionary(object):
    def __init__(self):
        self.image_reader = sitk.ImageFileReader()
        self.image_reader.LoadPrivateTagsOn()
        self.reader = sitk.ImageSeriesReader()
        self.reader.GlobalWarningDisplayOff()

    def add_dicom_to_dictionary_from_path(self, dicom_path, images_dictionary, rt_dictionary, rd_dictionary, rp_dictionary):
        fileList = glob(os.path.join(dicom_path, '*.dcm'))
        series_ids = self.reader.GetGDCMSeriesIDs(dicom_path)
        all_names = []
        for series_id in series_ids:
            dicom_names = self.reader.GetGDCMSeriesFileNames(dicom_path, series_id)
            all_names += dicom_names
            self.image_reader.SetFileName(dicom_names[0])
            self.image_reader.Execute()
            modality = self.image_reader.GetMetaData("0008|0060")
            if modality.lower().find('rtdose') != -1:
                add_rd_to_dictionary(sitk_dicom_reader=self.image_reader,
                                     rd_dictionary=rd_dictionary)
            else:
                add_images_to_dictionary(images_dictionary=images_dictionary, dicom_names=dicom_names,
                                         sitk_dicom_reader=self.image_reader, path=dicom_path)
        RT_Files = [file for file in fileList if file not in all_names]
        for lstRSFile in RT_Files:
            rt = pydicom.read_file(lstRSFile)
            modality = rt.Modality
            if modality.lower().find('struct') != -1:
                add_rt_to_dictionary(ds=rt, path=lstRSFile, rt_dictionary=rt_dictionary)
            elif modality.lower().find('plan') != -1:
                add_rp_to_dictionary(ds=rt, path=lstRSFile, rp_dictionary=rp_dictionary)
        xxx = 1


class DicomReaderWriter(object):
    def __init__(self, description='', Contour_Names=None, associations=None, arg_max=True, verbose=True,
                 create_new_RT=True, template_dir=None, delete_previous_rois=True,
                 require_all_contours=True, iteration=0, get_dose_output=False,
                 flip_axes=(False, False, False), index=0, series_instances_dictionary=None):
        """
        :param description: string, description information to add to .nii files
        :param delete_previous_rois: delete the previous RTs within the structure when writing out a prediction
        :param Contour_Names: list of contour names
        :param template_dir: default to None, specifies path to template RT structure
        :param arg_max: perform argmax on the mask
        :param create_new_RT: boolean, if the Dicom-RT writer should create a new RT structure
        :param require_all_contours: Boolean, require all contours present when making nifti files?
        :param associations: dictionary of associations {'liver_bma_program_4': 'liver'}
        :param iteration: what iteration for writing .nii files
        :param get_dose_output: boolean, collect dose information
        :param flip_axes: tuple(3), axis that you want to flip, defaults to (False, False, False)
        :param index: index to reference series_instances_dictionary, default 0
        :param series_instances_dictionary: dictionary of series instance UIDs of images and RTs
        """
        self.rt_dictionary = {}
        self.images_dictionary = {}
        self.rd_dictionary = {}
        self.rp_dictionary = {}
        if Contour_Names is None:
            Contour_Names = []
        if associations is None:
            associations = {}
        if series_instances_dictionary is None:
            series_instances_dictionary = {}
        self.series_instances_dictionary = series_instances_dictionary
        self.get_dose_output = get_dose_output
        self.require_all_contours = require_all_contours
        self.flip_axes = flip_axes
        self.create_new_RT = create_new_RT
        self.associations = associations
        self.Contour_Names = Contour_Names
        self.set_contour_names_and_associations(Contour_Names=Contour_Names, associations=associations,
                                                check_contours=False)
        self.__set_description__(description)
        self.__set_iteration__(iteration)
        self.arg_max = arg_max
        self.dose_handle = None
        if template_dir is None or not os.path.exists(template_dir):
            template_dir = os.path.join(os.path.split(__file__)[0], 'template_RS.dcm')
        self.template_dir = template_dir
        self.template = True
        self.delete_previous_rois = delete_previous_rois
        self.reader = sitk.ImageSeriesReader()
        self.image_reader = sitk.ImageFileReader()
        self.image_reader.LoadPrivateTagsOn()
        self.reader.MetaDataDictionaryArrayUpdateOn()
        self.reader.LoadPrivateTagsOn()
        self.reader.SetOutputPixelType(sitk.sitkFloat32)
        self.verbose = verbose
        self.dicom_handle_uid = None
        self.dicom_info_uid = None
        self.RS_struct_uid = None
        self.rd_study_instance_uid = None
        self.index = index
        self.all_RTs = {}
        self.RTs_with_ROI_Names = {}
        self.all_rois = []
        self.indexes_with_contours = []

    def set_index(self, index: int):
        self.index = index

    def __compile__(self):
        """
        The goal of this is to combine image, rt, and dose dictionaries based on the SeriesInstanceUIDs
        """
        if self.verbose:
            print('Compiling dictionaries together...')
        series_instance_uids = []
        for key, value in self.series_instances_dictionary.items():
            series_instance_uids.append(value['SeriesInstanceUID'])
        index = 0
        image_keys = list(self.images_dictionary.keys())
        image_keys.sort()
        for series_instance_uid in image_keys:  # Will help keep things in order later
            if series_instance_uid not in series_instance_uids:
                while index in self.series_instances_dictionary:
                    index += 1
                self.series_instances_dictionary[index] = self.images_dictionary[series_instance_uid]
                series_instance_uids.append(series_instance_uid)
        for rt_series_instance_uid in self.rt_dictionary:
            series_instance_uid = self.rt_dictionary[rt_series_instance_uid]['SeriesInstanceUID']
            rt_dictionary = self.rt_dictionary[rt_series_instance_uid]
            path = rt_dictionary['Path']
            self.all_RTs[path] = rt_dictionary['ROI_Names']
            for roi in rt_dictionary['ROI_Names']:
                if roi not in self.RTs_with_ROI_Names:
                    self.RTs_with_ROI_Names[roi] = [path]
                else:
                    self.RTs_with_ROI_Names[roi].append(path)
            if series_instance_uid in series_instance_uids:
                index = series_instance_uids.index(series_instance_uid)
                self.series_instances_dictionary[index]['RTs'].update({rt_series_instance_uid: self.rt_dictionary[rt_series_instance_uid]})
            else:
                while index in self.series_instances_dictionary:
                    index += 1
                template = return_template_dictionary()
                template['RTs'].update({rt_series_instance_uid: self.rt_dictionary[rt_series_instance_uid]})
                self.series_instances_dictionary[index] = template
        for rd_series_instance_uid in self.rd_dictionary:
            added = False
            struct_ref = self.rd_dictionary[rd_series_instance_uid]['ReferencedStructureSetSOPInstanceUID']
            for image_series_key in self.series_instances_dictionary:
                rts = self.series_instances_dictionary[image_series_key]['RTs']
                for rt_key in rts:
                    structure_sop_uid = rts[rt_key]['SOPInstanceUID']
                    if struct_ref == structure_sop_uid:
                        rts[rt_key]['Doses'][rd_series_instance_uid] = self.rd_dictionary[rd_series_instance_uid]
                        self.series_instances_dictionary[image_series_key]['RDs'].update({rd_series_instance_uid:
                                                                                              self.rd_dictionary[rd_series_instance_uid]})
                    added = True
            if not added:
                while index in self.series_instances_dictionary:
                    index += 1
                template = return_template_dictionary()
                template['RDs'].update({rd_series_instance_uid: self.rd_dictionary[rd_series_instance_uid]})
                self.series_instances_dictionary[index] = template
        for rp_series_instance_uid in self.rp_dictionary:
            added = False
            struct_ref = self.rp_dictionary[rp_series_instance_uid]['ReferencedStructureSetSOPInstanceUID']
            for image_series_key in self.series_instances_dictionary:
                rts = self.series_instances_dictionary[image_series_key]['RTs']
                for rt_key in rts:
                    structure_sop_uid = rts[rt_key]['SOPInstanceUID']
                    if struct_ref == structure_sop_uid:
                        rts[rt_key]['Plans'][rp_series_instance_uid] = self.rp_dictionary[rp_series_instance_uid]
                        self.series_instances_dictionary[image_series_key]['RPs'].update({rp_series_instance_uid:
                                                                                              self.rp_dictionary[rp_series_instance_uid]})
                    added = True
            if not added:
                while index in self.series_instances_dictionary:
                    index += 1
                template = return_template_dictionary()
                template['RPs'].update({rp_series_instance_uid: self.rp_dictionary[rp_series_instance_uid]})
                self.series_instances_dictionary[index] = template

    def __manual_compile_based_on_folders__(self, reset_series_instances_dict=False):
        """
        The goal of this is to combine image, rt, and dose dictionaries based on folder location
        AKA, if the RT structure and images are in the same folder
        :return:
        """
        print("Don't use this unless you know why you're doing it...")
        if reset_series_instances_dict:
            self.series_instances_dictionary = {}
        if self.verbose:
            print('Compiling dictionaries together...')
        folders = []
        for key, value in self.series_instances_dictionary.items():
            folders.append(value['Image_Path'])
        index = 0
        image_keys = list(self.images_dictionary.keys())
        image_keys.sort()
        for series_instance_uid in image_keys:  # Will help keep things in order later
            folder = self.images_dictionary[series_instance_uid]['Image_Path']
            if folder not in folders:
                while index in self.series_instances_dictionary:
                    index += 1
                self.series_instances_dictionary[index] = self.images_dictionary[series_instance_uid]
                folders.append(folder)
        for rt_series_instance_uid in self.rt_dictionary:
            rt_path = os.path.split(self.rt_dictionary[rt_series_instance_uid]['Path'])[0]
            rt_dictionary = self.rt_dictionary[rt_series_instance_uid]
            path = rt_dictionary['Path']
            self.all_RTs[path] = rt_dictionary['ROI_Names']
            for roi in rt_dictionary['ROI_Names']:
                if roi not in self.RTs_with_ROI_Names:
                    self.RTs_with_ROI_Names[roi] = [path]
                else:
                    self.RTs_with_ROI_Names[roi].append(path)
            if rt_path in folders:
                index = folders.index(rt_path)
                self.series_instances_dictionary[index]['RTs'].update({rt_series_instance_uid: self.rt_dictionary[rt_series_instance_uid]})
            else:
                while index in self.series_instances_dictionary:
                    index += 1
                template = return_template_dictionary()
                template['RTs'].update({rt_series_instance_uid: self.rt_dictionary[rt_series_instance_uid]})
                self.series_instances_dictionary[index] = template
        for rd_series_instance_uid in self.rd_dictionary:
            added = False
            struct_ref = self.rd_dictionary[rd_series_instance_uid]['ReferencedStructureSetSOPInstanceUID']
            for image_series_key in self.series_instances_dictionary:
                rts = self.series_instances_dictionary[image_series_key]['RTs']
                for rt_key in rts:
                    structure_sop_uid = rts[rt_key]['SOPInstanceUID']
                    if struct_ref == structure_sop_uid:
                        rts[rt_key]['Doses'][rd_series_instance_uid] = self.rd_dictionary[rd_series_instance_uid]
                        self.series_instances_dictionary[image_series_key]['RDs'].update({rd_series_instance_uid:
                                                                                              self.rd_dictionary[rd_series_instance_uid]})
                    added = True
            if not added:
                while index in self.series_instances_dictionary:
                    index += 1
                template = return_template_dictionary()
                template['RDs'].update({rd_series_instance_uid: self.rd_dictionary[rd_series_instance_uid]})
                self.series_instances_dictionary[index] = template
        for rp_series_instance_uid in self.rp_dictionary:
            added = False
            struct_ref = self.rp_dictionary[rp_series_instance_uid]['ReferencedStructureSetSOPInstanceUID']
            for image_series_key in self.series_instances_dictionary:
                rts = self.series_instances_dictionary[image_series_key]['RTs']
                for rt_key in rts:
                    structure_sop_uid = rts[rt_key]['SOPInstanceUID']
                    if struct_ref == structure_sop_uid:
                        rts[rt_key]['Plans'][rp_series_instance_uid] = self.rp_dictionary[rp_series_instance_uid]
                        self.series_instances_dictionary[image_series_key]['RPs'].update({rp_series_instance_uid:
                                                                                              self.rp_dictionary[rp_series_instance_uid]})
                    added = True
            if not added:
                while index in self.series_instances_dictionary:
                    index += 1
                template = return_template_dictionary()
                template['RPs'].update({rp_series_instance_uid: self.rp_dictionary[rp_series_instance_uid]})
                self.series_instances_dictionary[index] = template
        self.__check_if_all_contours_present__()

    def __reset__(self):
        self.__reset_RTs__()
        self.rd_study_instance_uid = None
        self.dicom_handle_uid = None
        self.dicom_info_uid = None
        self.series_instances_dictionary = {}
        self.rt_dictionary = {}
        self.images_dictionary = {}

    def __reset_RTs__(self):
        self.all_rois = []
        self.indexes_with_contours = []
        self.RS_struct_uid = None
        self.RTs_with_ROI_Names = {}

    def set_contour_names_and_associations(self, Contour_Names=None, associations=None, check_contours=True):
        if Contour_Names is not None:
            self.__set_contour_names__(Contour_Names=Contour_Names)
        if associations is not None:
            self.__set_associations__(associations=associations)
        if check_contours:  # I don't want to run this on the first build..
            self.__check_if_all_contours_present__()

    def __set_associations__(self, associations=None):
        if associations is not None:
            keys = list(associations.keys())
            for key in keys:
                associations[key.lower()] = associations[key].lower()
            if self.Contour_Names is not None:
                for name in self.Contour_Names:
                    if name not in associations:
                        associations[name] = name
            self.associations, self.hierarchy = associations, {}

    def __set_contour_names__(self, Contour_Names: List[str]):
        self.__reset_RTs__()
        Contour_Names = [i.lower() for i in Contour_Names]
        for name in Contour_Names:
            if name not in self.associations:
                self.associations[name] = name
        self.Contour_Names = Contour_Names

    def __set_description__(self, description: str):
        self.desciption = description

    def __set_iteration__(self, iteration=0):
        self.iteration = str(iteration)

    def __check_if_all_contours_present__(self):
        self.indexes_with_contours = []
        for index in self.series_instances_dictionary:
            if self.series_instances_dictionary[index]['Image_Path'] is None:
                continue
            RTs = self.series_instances_dictionary[index]['RTs']
            true_rois = []
            self.rois_in_case = []
            for RT_key in RTs:
                RT = RTs[RT_key]
                ROI_Names = RT['ROI_Names']
                for roi in ROI_Names:
                    if roi.lower() not in self.RTs_with_ROI_Names:
                        self.RTs_with_ROI_Names[roi.lower()] = [RT['Path']]
                    elif RT['Path'] not in self.RTs_with_ROI_Names[roi.lower()]:
                        self.RTs_with_ROI_Names[roi.lower()].append(RT['Path'])
                    if roi.lower() not in self.rois_in_case:
                        self.rois_in_case.append(roi.lower())
                    if roi.lower() not in self.all_rois:
                        self.all_rois.append(roi.lower())
                    if self.Contour_Names:
                        if roi.lower() in self.associations:
                            true_rois.append(self.associations[roi.lower()])
                        elif roi.lower() in self.Contour_Names:
                            true_rois.append(roi.lower())
            all_contours_exist = True
            some_contours_exist = False
            lacking_rois = []
            for roi in self.Contour_Names:
                if roi not in true_rois:
                    lacking_rois.append(roi)
                else:
                    some_contours_exist = True
            if lacking_rois:
                all_contours_exist = False
                if self.verbose:
                    print('Lacking {} in index {}, location {}. Found {}'.format(lacking_rois, index,
                                                                                 self.series_instances_dictionary[index]
                                                                                 ['Image_Path'], self.rois_in_case))
            if index not in self.indexes_with_contours:
                if all_contours_exist:
                    self.indexes_with_contours.append(index)
                elif some_contours_exist and not self.require_all_contours:
                    self.indexes_with_contours.append(index)  # Add the index that have at least some of the contours

    def return_rois(self, print_rois=True) -> List[str]:
        if print_rois:
            print('The following ROIs were found')
            for roi in self.all_rois:
                print(roi)
        return self.all_rois

    def return_files_from_UID(self, UID: str) -> List[str]:
        """
        Args:
            UID: A string UID found in images_dictionary.
        Returns:
            file_list: A list of file paths that are associated with that UID, being images, RTs, RDs, and RPs
        """
        out_file_paths = list()
        if UID not in self.images_dictionary:
            print(UID + " Not found in dictionary")
            return out_file_paths
        image_dictionary = self.images_dictionary[UID]
        dicom_path = image_dictionary['Image_Path']
        image_reader = sitk.ImageFileReader()
        image_reader.LoadPrivateTagsOn()
        reader = sitk.ImageSeriesReader()
        reader.GlobalWarningDisplayOff()
        out_file_paths += reader.GetGDCMSeriesFileNames(dicom_path, UID)
        for key in ['RTs', 'RDs']:
            for structure_key in image_dictionary[key]:
                out_file_paths += [image_dictionary[key][structure_key]['Path']]
        return out_file_paths

    def return_files_from_index(self, index: int) -> List[str]:
        """
        Args:
            index: An integer index found in images_dictionary.
        Returns:
            file_list: A list of file paths that are associated with that index, being images, RTs, RDs, and RPs
        """
        out_file_paths = list()
        image_dictionary = self.series_instances_dictionary[index]
        UID = image_dictionary['SeriesInstanceUID']
        dicom_path = image_dictionary['Image_Path']
        image_reader = sitk.ImageFileReader()
        image_reader.LoadPrivateTagsOn()
        reader = sitk.ImageSeriesReader()
        reader.GlobalWarningDisplayOff()
        out_file_paths += reader.GetGDCMSeriesFileNames(dicom_path, UID)
        for key in ['RTs', 'RDs', 'RPs']:
            for structure_key in image_dictionary[key]:
                out_file_paths += [image_dictionary[key][structure_key]['Path']]
        return out_file_paths

    def return_files_from_patientID(self, patientID: str) -> List[str]:
        """
        Args:
            index: An integer index found in images_dictionary.
        Returns:
            file_list: A list of file paths that are associated with that index, being images, RTs, RDs, and RPs
        """
        out_file_paths = list()
        for index in self.series_instances_dictionary:
            if self.series_instances_dictionary[index]['PatientID'] == patientID:
                out_file_paths += self.return_files_from_index(index)
        return out_file_paths

    def where_are_RTs(self, ROIName: str) -> None:
        print('Please move over to using .where_is_ROI(), as this better represents the definition')
        self.where_is_ROI(ROIName=ROIName)

    def where_is_ROI(self, ROIName: str) -> None:
        if ROIName.lower() in self.RTs_with_ROI_Names:
            print('Contours of {} are located:'.format(ROIName.lower()))
            for path in self.RTs_with_ROI_Names[ROIName.lower()]:
                print(path)
        else:
            print('{} was not found within the set, check spelling or list all rois'.format(ROIName))

    def which_indexes_have_all_rois(self):
        if self.Contour_Names:
            print('The following indexes have all ROIs present')
            for index in self.indexes_with_contours:
                print('Index {}, located at {}'.format(index, self.series_instances_dictionary[index]['Image_Path']))
            print('Finished listing present indexes')
            return self.indexes_with_contours
        else:
            print('You need to first define what ROIs you want, please use'
                  ' .set_contour_names_and_associations()')

    def which_indexes_lack_all_rois(self):
        if self.Contour_Names:
            print('The following indexes are lacking all ROIs')
            indexes_lacking_rois = []
            for index in self.series_instances_dictionary:
                if index not in self.indexes_with_contours:
                    indexes_lacking_rois.append(index)
                    print('Index {}, located at '
                          '{}'.format(index, self.series_instances_dictionary[index]['Image_Path']))
            print('Finished listing lacking indexes')
            return indexes_lacking_rois
        else:
            print('You need to first define what ROIs you want, please use'
                  ' .set_contour_names_and_associations(roi_list)')

    def down_folder(self, input_path: typing.Union[str, bytes, os.PathLike]):
        print('Please move from down_folder() to walk_through_folders()')
        self.walk_through_folders(input_path=input_path)

    def walk_through_folders(self, input_path: typing.Union[str, bytes, os.PathLike],
                             thread_count=int(cpu_count() * 0.9 - 1)):
        """
        Iteratively work down paths to find DICOM files, if they are present, add to the series instance UID dictionary
        :param input_path: path to walk
        """
        paths_with_dicom = []
        for root, dirs, files in os.walk(input_path):
            dicom_files = [i for i in files if i.endswith('.dcm')]
            if dicom_files:
                paths_with_dicom.append(root)
                # dicom_adder.add_dicom_to_dictionary_from_path(dicom_path=root, images_dictionary=self.images_dictionary,
                #                                               rt_dictionary=self.rt_dictionary)
        if paths_with_dicom:
            q = Queue(maxsize=thread_count)
            pbar = tqdm(total=len(paths_with_dicom), desc='Loading through DICOM files')
            A = (q, pbar)
            threads = []
            for worker in range(thread_count):
                t = Thread(target=folder_worker, args=(A,))
                t.start()
                threads.append(t)
            for index, path in enumerate(paths_with_dicom):
                item = [path, self.images_dictionary, self.rt_dictionary, self.rd_dictionary, self.rp_dictionary,
                        self.verbose]
                q.put(item)
            for i in range(thread_count):
                q.put(None)
            for t in threads:
                t.join()
            self.__compile__()
        if self.verbose or len(self.series_instances_dictionary) > 1:
            for key in self.series_instances_dictionary:
                print('Index {}, description {} at {}'.format(key,
                                                              self.series_instances_dictionary[key]['Description'],
                                                              self.series_instances_dictionary[key]['Image_Path']))
            print('{} unique series IDs were found. Default is index 0, to change use '
                  'set_index(index)'.format(len(self.series_instances_dictionary)))
        self.__check_if_all_contours_present__()
        return None

    def write_parallel(self, out_path: typing.Union[str, bytes, os.PathLike],
                       excel_file: typing.Union[str, bytes, os.PathLike],
                       thread_count=int(cpu_count() * 0.9 - 1)):
        if not os.path.exists(out_path):
            os.makedirs(out_path)
        if not os.path.exists(excel_file):
            final_out_dict = {'PatientID': [], 'Path': [], 'Iteration': [], 'Folder': [], 'SeriesInstanceUID': [],
                              'Pixel_Spacing_X': [], 'Pixel_Spacing_Y': [], 'Slice_Thickness': []}
            for roi in self.Contour_Names:
                column_name = 'Volume_{} [cc]'.format(roi)
                final_out_dict[column_name] = []
            df = pd.DataFrame(final_out_dict)
            df.to_excel(excel_file, index=0)
        else:
            df = pd.read_excel(excel_file, engine='openpyxl')
        add_columns = False
        for roi in self.Contour_Names:
            column_name = 'Volume_{} [cc]'.format(roi)
            if column_name not in df.columns:
                df[column_name] = np.nan
                add_columns = True
        if add_columns:
            df.to_excel(excel_file, index=0)
        key_dict = {'series_instances_dictionary': self.series_instances_dictionary, 'associations': self.associations,
                    'arg_max': self.arg_max, 'require_all_contours': self.require_all_contours,
                    'Contour_Names': self.Contour_Names,
                    'description': self.desciption, 'get_dose_output': self.get_dose_output}
        rewrite_excel = False
        '''
        First, build the excel file that we will use to reference iterations, Series UIDs, and paths
        '''
        for index in self.indexes_with_contours:
            series_instance_uid = self.series_instances_dictionary[index]['SeriesInstanceUID']
            previous_run = df.loc[df['SeriesInstanceUID'] == series_instance_uid]
            if previous_run.shape[0] == 0:
                rewrite_excel = True
                iteration = 0
                while iteration in df['Iteration'].values:
                    iteration += 1
                temp_dict = {'PatientID': [self.series_instances_dictionary[index]['PatientID']],
                             'Path': [self.series_instances_dictionary[index]['Image_Path']],
                             'Iteration': [int(iteration)], 'Folder': [None],
                             'SeriesInstanceUID': [series_instance_uid],
                             'Pixel_Spacing_X': [self.series_instances_dictionary[index]['Pixel_Spacing_X']],
                             'Pixel_Spacing_Y': [self.series_instances_dictionary[index]['Pixel_Spacing_Y']],
                             'Slice_Thickness': [self.series_instances_dictionary[index]['Slice_Thickness']]}
                temp_df = pd.DataFrame(temp_dict)
                df = df.append(temp_df)
        if rewrite_excel:
            df.to_excel(excel_file, index=0)
        '''
        Next, read through the excel sheet and see if the out paths already exist
        '''
        items = []
        for index in self.indexes_with_contours:
            series_instance_uid = self.series_instances_dictionary[index]['SeriesInstanceUID']
            previous_run = df.loc[df['SeriesInstanceUID'] == series_instance_uid]
            if previous_run.shape[0] == 0:
                continue
            iteration = int(previous_run['Iteration'].values[0])
            folder = previous_run['Folder'].values[0]
            if pd.isnull(folder):
                folder = None
            write_path = out_path
            if folder is not None:
                write_path = os.path.join(out_path, folder)
            write_image = os.path.join(write_path, 'Overall_Data_{}_{}.nii.gz'.format(self.desciption, iteration))
            rerun = True
            if os.path.exists(write_image):
                print('Already wrote out index {} at {}'.format(index, write_path))
                rerun = False
                for roi in self.Contour_Names:
                    column_name = 'Volume_{} [cc]'.format(roi)
                    if pd.isnull(previous_run[column_name].values[0]):
                        rerun = True
                        print('Volume for {} was not defined at index {}.. so rerunning'.format(roi, index))
                        break
            if not rerun:
                continue
            item = [iteration, index, write_path, key_dict]
            items.append(item)
        if items:
            q = Queue(maxsize=thread_count)
            pbar = tqdm(total=len(items), desc='Writing nifti files...')
            A = (q, pbar)
            threads = []
            for worker in range(thread_count):
                t = Thread(target=worker_def, args=(A,))
                t.start()
                threads.append(t)
            for item in items:
                q.put(item)
            for i in range(thread_count):
                q.put(None)
            for t in threads:
                t.join()
            """
            Now, take the volumes that have been calculated during this process and add them to the excel sheet
            """
            for item in items:
                index = item[1]
                iteration = item[0]
                if 'Volumes' not in self.series_instances_dictionary[index].keys():
                    continue
                for roi_index, roi in enumerate(self.Contour_Names):
                    column_name = 'Volume_{} [cc]'.format(roi)
                    df.loc[df.Iteration == iteration, column_name] = \
                        self.series_instances_dictionary[index]['Volumes'][roi_index]
            df.to_excel(excel_file, index=0)

    def get_images_and_mask(self) -> None:
        assert self.index in self.series_instances_dictionary, \
            'Index is not present in the dictionary! Set it using set_index(index)'
        self.get_images()
        self.get_mask()
        if self.get_dose_output:
            self.get_dose()

    def get_all_info(self) -> None:
        """
        Print all of the keys and their respective values
        :return:
        """
        self.load_key_information_only()
        for key in self.image_reader.GetMetaDataKeys():
            print("{} is {}".format(key, self.image_reader.GetMetaData(key)))

    def return_key_info(self, key):
        """
        Return the dicom information for a particular key
        Example: "0008|0022" will return the date acquired in YYYYMMDD format
        :param key: dicom key "0008|0022"
        :return: value associated with the key
        """
        self.load_key_information_only()
        if not self.image_reader.HasMetaDataKey(key):
            print("{} is not present in the reader".format(key))
            return None
        return self.image_reader.GetMetaData(key)

    def load_key_information_only(self) -> None:
        assert self.index in self.series_instances_dictionary, \
            'Index is not present in the dictionary! Set it using set_index(index)'
        index = self.index
        series_instance_uid = self.series_instances_dictionary[index]['SeriesInstanceUID']
        if self.dicom_info_uid != series_instance_uid:  # Only load if needed
            dicom_names = self.series_instances_dictionary[index]['Files']
            self.image_reader.SetFileName(dicom_names[0])
            self.image_reader.ReadImageInformation()
            self.dicom_info_uid = series_instance_uid

    def get_images(self) -> None:
        assert self.index in self.series_instances_dictionary, \
            'Index is not present in the dictionary! Set it using set_index(index)'
        index = self.index
        series_instance_uid = self.series_instances_dictionary[index]['SeriesInstanceUID']
        if self.dicom_handle_uid != series_instance_uid:  # Only load if needed
            if self.verbose:
                print('Loading images for {} at \n {}\n'.format(self.series_instances_dictionary[index]['Description'],
                                                                self.series_instances_dictionary[index]['Image_Path']))
            dicom_names = self.series_instances_dictionary[index]['Files']
            self.ds = pydicom.read_file(dicom_names[0])
            self.reader.SetFileNames(dicom_names)
            self.dicom_handle = self.reader.Execute()
            add_sops_to_dictionary(sitk_dicom_reader=self.reader,
                                   series_instances_dictionary=self.series_instances_dictionary)
            if max(self.flip_axes):
                flipimagefilter = sitk.FlipImageFilter()
                flipimagefilter.SetFlipAxes(self.flip_axes)
                self.dicom_handle = flipimagefilter.Execute(self.dicom_handle)
            self.ArrayDicom = sitk.GetArrayFromImage(self.dicom_handle)
            self.image_size_cols, self.image_size_rows, self.image_size_z = self.dicom_handle.GetSize()
            self.dicom_handle_uid = series_instance_uid

    def get_dose(self) -> None:
        assert self.index in self.series_instances_dictionary, \
            'Index is not present in the dictionary! Set it using set_index(index)'
        index = self.index
        if self.dicom_handle_uid != self.series_instances_dictionary[index]['SeriesInstanceUID']:
            print('Loading images for index {}, since mask was requested but image loading was '
                  'previously different\n'.format(index))
            self.get_images()
        if self.rd_study_instance_uid == self.series_instances_dictionary[index]['StudyInstanceUID']:  # Already loaded
            return None
        self.rd_study_instance_uid = self.series_instances_dictionary[index]['StudyInstanceUID']
        RDs = self.series_instances_dictionary[index]['RDs']
        reader = sitk.ImageFileReader()
        output, spacing, direction, origin = None, None, None, None
        self.dose = None
        self.dose_handle = None
        for rd_series_instance_uid in RDs:
            rd = RDs[rd_series_instance_uid]
            dose_file = rd['Path']
            reader.SetFileName(dose_file)
            reader.ReadImageInformation()
            dose = reader.Execute()
            spacing = dose.GetSpacing()
            origin = dose.GetOrigin()
            direction = dose.GetDirection()
            scaling_factor = float(reader.GetMetaData("3004|000e"))
            dose = sitk.GetArrayFromImage(dose) * scaling_factor
            if output is None:
                output = dose
            else:
                output += dose
        if output is not None:
            self.dose = output
            output = sitk.GetImageFromArray(output)
            output.SetSpacing(spacing)
            output.SetDirection(direction)
            output.SetOrigin(origin)
            self.dose_handle = output

    def __mask_empty_mask__(self) -> None:
        self.mask = np.zeros(
            [self.dicom_handle.GetSize()[-1], self.image_size_rows, self.image_size_cols, len(self.Contour_Names) + 1],
            dtype='int8')

    def get_mask(self) -> None:
        assert self.index in self.series_instances_dictionary, \
            'Index is not present in the dictionary! Set it using set_index(index)'
        assert self.Contour_Names, 'If you want a mask, you need to set the contour names you are looking ' \
                                   'for, use set_contour_names_and_associations(list_of_roi_names).\nIf you just' \
                                   ' want to look at images  use get_images() not get_images_and_mask() or get_mask()'
        index = self.index
        if self.dicom_handle_uid != self.series_instances_dictionary[index]['SeriesInstanceUID']:
            print('Loading images for index {}, since mask was requested but image loading was '
                  'previously different\n'.format(index))
            self.get_images()
        if self.RS_struct_uid == self.series_instances_dictionary[index]['SeriesInstanceUID']:  # Already loaded
            return None
        self.__mask_empty_mask__()
        RTs = self.series_instances_dictionary[index]['RTs']
        for RT_key in RTs:
            RT = RTs[RT_key]
            ROIName_Number = RT['ROIs_in_structure']
            RS_struct = None
            self.structure_references = {}
            for ROI_Name in ROIName_Number.keys():
                true_name = None
                if ROI_Name in self.associations:
                    true_name = self.associations[ROI_Name].lower()
                elif ROI_Name.lower() in self.associations:
                    true_name = self.associations[ROI_Name.lower()]
                if true_name and true_name in self.Contour_Names:
                    if RS_struct is None:
                        self.RS_struct = RS_struct = pydicom.read_file(RT['Path'])
                        self.RS_struct_uid = self.series_instances_dictionary[index]['SeriesInstanceUID']
                    for contour_number in range(len(self.RS_struct.ROIContourSequence)):
                        self.structure_references[
                            self.RS_struct.ROIContourSequence[contour_number].ReferencedROINumber] = contour_number
                    structure_index = self.structure_references[ROIName_Number[ROI_Name]]
                    mask = self.contours_to_mask(structure_index)
                    self.mask[..., self.Contour_Names.index(true_name) + 1] += mask
                    self.mask[self.mask > 1] = 1
        if self.flip_axes[0]:
            self.mask = self.mask[:, :, ::-1, ...]
        if self.flip_axes[1]:
            self.mask = self.mask[:, ::-1, ...]
        if self.flip_axes[2]:
            self.mask = self.mask[::-1, ...]
        voxel_size = np.prod(self.dicom_handle.GetSpacing())/1000  # volume in cc per voxel
        volumes = np.sum(self.mask[..., 1:], axis=(0, 1, 2)) * voxel_size  # Volume in cc
        self.series_instances_dictionary[index]['Volumes'] = volumes
        if self.arg_max:
            self.mask = np.argmax(self.mask, axis=-1)
        self.annotation_handle = sitk.GetImageFromArray(self.mask.astype('int8'))
        self.annotation_handle.SetSpacing(self.dicom_handle.GetSpacing())
        self.annotation_handle.SetOrigin(self.dicom_handle.GetOrigin())
        self.annotation_handle.SetDirection(self.dicom_handle.GetDirection())
        return None

    def reshape_contour_data(self, as_array: np.array):
        as_array = np.asarray(as_array)
        if as_array.shape[-1] != 3:
            as_array = np.reshape(as_array, [as_array.shape[0] // 3, 3])
        matrix_points = np.asarray([self.dicom_handle.TransformPhysicalPointToIndex(as_array[i])
                                    for i in range(as_array.shape[0])])
        return matrix_points

    def return_mask(self, mask: np.array, matrix_points: np.array, geometric_type: str):
        col_val = matrix_points[:, 0]
        row_val = matrix_points[:, 1]
        z_vals = matrix_points[:, 2]
        if geometric_type != "OPEN_NONPLANAR":
            temp_mask = poly2mask(row_val, col_val, [self.image_size_rows, self.image_size_cols])
            # temp_mask[self.row_val, self.col_val] = 0
            mask[z_vals[0], temp_mask] += 1
        else:
            for point_index in range(len(z_vals) - 1, 0, -1):
                z_start = z_vals[point_index]
                z_stop = z_vals[point_index - 1]
                z_dif = z_stop - z_start
                r_start = row_val[point_index]
                r_stop = row_val[point_index - 1]
                r_dif = r_stop - r_start
                c_start = col_val[point_index]
                c_stop = col_val[point_index - 1]
                c_dif = c_stop - c_start

                step = 1
                if z_dif != 0:
                    r_slope = r_dif / z_dif
                    c_slope = c_dif / z_dif
                    if z_dif < 0:
                        step = -1
                    for z_value in range(z_start, z_stop + step, step):
                        r_value = r_start + r_slope * (z_value - z_start)
                        c_value = c_start + c_slope * (z_value - z_start)
                        add_to_mask(mask=mask, z_value=z_value, r_value=r_value, c_value=c_value)
                if r_dif != 0:
                    c_slope = c_dif / r_dif
                    z_slope = z_dif / r_dif
                    if r_dif < 0:
                        step = -1
                    for r_value in range(r_start, r_stop + step, step):
                        c_value = c_start + c_slope * (r_value - r_start)
                        z_value = z_start + z_slope * (r_value - r_start)
                        add_to_mask(mask=mask, z_value=z_value, r_value=r_value, c_value=c_value)
                if c_dif != 0:
                    r_slope = r_dif / c_dif
                    z_slope = z_dif / c_dif
                    if c_dif < 0:
                        step = -1
                    for c_value in range(c_start, c_stop + step, step):
                        r_value = r_start + r_slope * (c_value - c_start)
                        z_value = z_start + z_slope * (c_value - c_start)
                        add_to_mask(mask=mask, z_value=z_value, r_value=r_value, c_value=c_value)
        return mask

    def contour_points_to_mask(self, contour_points, mask=None):
        if mask is None:
            mask = np.zeros([self.dicom_handle.GetSize()[-1], self.image_size_rows, self.image_size_cols], dtype='int8')
        matrix_points = self.reshape_contour_data(contour_points)
        mask = self.return_mask(mask, matrix_points, geometric_type="CLOSED_PLANAR")
        return mask

    def contours_to_mask(self, index: int):
        mask = np.zeros([self.dicom_handle.GetSize()[-1], self.image_size_rows, self.image_size_cols], dtype='int8')
        Contour_data = self.RS_struct.ROIContourSequence[index].ContourSequence
        for i in range(len(Contour_data)):
            matrix_points = self.reshape_contour_data(Contour_data[i].ContourData[:])
            mask = self.return_mask(mask, matrix_points, geometric_type=Contour_data[i].ContourGeometricType)
        mask = mask % 2
        return mask

    def use_template(self) -> None:
        self.template = True
        if not self.template_dir:
            self.template_dir = os.path.join('\\\\mymdafiles', 'ro-admin', 'SHARED', 'Radiation physics', 'BMAnderson',
                                             'Auto_Contour_Sites', 'template_RS.dcm')
            if not os.path.exists(self.template_dir):
                self.template_dir = os.path.join('..', '..', 'Shared_Drive', 'Auto_Contour_Sites', 'template_RS.dcm')
        self.key_list = self.template_dir.replace('template_RS.dcm', 'key_list.txt')
        self.RS_struct = pydicom.read_file(self.template_dir)
        print('Running off a template')
        self.change_template()

    def write_images_annotations(self, out_path: typing.Union[str, bytes, os.PathLike]) -> None:
        image_path = os.path.join(out_path, 'Overall_Data_{}_{}.nii.gz'.format(self.desciption, self.iteration))
        annotation_path = os.path.join(out_path, 'Overall_mask_{}_y{}.nii.gz'.format(self.desciption, self.iteration))
        pixel_id = self.dicom_handle.GetPixelIDTypeAsString()
        if pixel_id.find('32-bit signed integer') != 0:
            self.dicom_handle = sitk.Cast(self.dicom_handle, sitk.sitkFloat32)
        sitk.WriteImage(self.dicom_handle, image_path)

        self.annotation_handle.SetSpacing(self.dicom_handle.GetSpacing())
        self.annotation_handle.SetOrigin(self.dicom_handle.GetOrigin())
        self.annotation_handle.SetDirection(self.dicom_handle.GetDirection())
        pixel_id = self.annotation_handle.GetPixelIDTypeAsString()
        if pixel_id.find('int') == -1:
            self.annotation_handle = sitk.Cast(self.annotation_handle, sitk.sitkUInt8)
        sitk.WriteImage(self.annotation_handle, annotation_path)
        if self.dose_handle is not None:
            dose_path = os.path.join(out_path, 'Overall_dose_{}_{}.nii.gz'.format(self.desciption, self.iteration))
            sitk.WriteImage(self.dose_handle, dose_path)
        fid = open(os.path.join(self.series_instances_dictionary[self.index]['Image_Path'],
                                '{}_Iteration_{}.txt'.format(self.desciption, self.iteration)), 'w+')
        fid.close()

    def prediction_array_to_RT(self, prediction_array: np.array, output_dir: typing.Union[str, bytes, os.PathLike],
                               ROI_Names: List[str]):
        """
        :param prediction_array: numpy array of prediction, expected shape is [#Images, Rows, Cols, #Classes + 1]
        :param output_dir: directory to pass RT structure to
        :param ROI_Names: list of ROI names equal to the number of classes
        :return:
        """
        assert ROI_Names is not None, 'You need to provide ROI_Names'
        assert prediction_array.shape[-1] == len(ROI_Names) + 1, 'Your last dimension of prediction array should be' \
                                                                 ' equal  to the number or ROI_names minus 1, channel' \
                                                                 ' 0 is background'
        assert self.index in self.series_instances_dictionary, \
            'Index is not present in the dictionary! Set it using set_index(index)'
        index = self.index
        if self.dicom_handle_uid != self.series_instances_dictionary[index]['SeriesInstanceUID']:
            self.get_images()
        self.SOPInstanceUIDs = self.series_instances_dictionary[index]['SOP_Instance_UIDs']

        if self.create_new_RT or len(self.series_instances_dictionary[index]['RTs']) == 0:
            self.use_template()
        elif self.RS_struct_uid != self.series_instances_dictionary[index]['SeriesInstanceUID']:
            RTs = self.series_instances_dictionary[index]['RTs']
            for uid_key in RTs:
                self.RS_struct = pydicom.read_file(RTs[uid_key]['Path'])
                self.RS_struct_uid = self.series_instances_dictionary[index]['SeriesInstanceUID']
                break

        prediction_array = np.squeeze(prediction_array)
        contour_values = np.max(prediction_array, axis=0)  # See what the maximum value is across the prediction array
        while len(contour_values.shape) > 1:
            contour_values = np.max(contour_values, axis=0)
        contour_values[0] = 1  # Keep background
        prediction_array = prediction_array[..., contour_values == 1]
        contour_values = contour_values[1:]
        not_contained = list(np.asarray(ROI_Names)[contour_values == 0])
        ROI_Names = list(np.asarray(ROI_Names)[contour_values == 1])
        if not_contained:
            print('RT Structure not made for ROIs {}, given prediction_array had no mask'.format(not_contained))
        self.image_size_z, self.image_size_rows, self.image_size_cols = prediction_array.shape[:3]
        self.ROI_Names = ROI_Names
        self.output_dir = output_dir
        if len(prediction_array.shape) == 3:
            prediction_array = np.expand_dims(prediction_array, axis=-1)
        if self.flip_axes[0]:
            prediction_array = prediction_array[:, :, ::-1, ...]
        if self.flip_axes[1]:
            prediction_array = prediction_array[:, ::-1, ...]
        if self.flip_axes[2]:
            prediction_array = prediction_array[::-1, ...]
        self.annotations = prediction_array
        self.mask_to_contours()

    def with_annotations(self, annotations: np.array, output_dir: typing.Union[str, bytes, os.PathLike],
                         ROI_Names=None) -> None:
        print('Please move over to using prediction_array_to_RT')
        self.prediction_array_to_RT(prediction_array=annotations, output_dir=output_dir, ROI_Names=ROI_Names)

    def mask_to_contours(self) -> None:
        self.PixelSize = self.dicom_handle.GetSpacing()
        current_names = []
        for names in self.RS_struct.StructureSetROISequence:
            current_names.append(names.ROIName)
        Contour_Key = {}
        xxx = 1
        for name in self.ROI_Names:
            Contour_Key[name] = xxx
            xxx += 1
        base_annotations = copy.deepcopy(self.annotations)
        temp_color_list = []
        color_list = [[128, 0, 0], [170, 110, 40], [0, 128, 128], [0, 0, 128], [230, 25, 75], [225, 225, 25],
                      [0, 130, 200], [145, 30, 180],
                      [255, 255, 255]]
        self.struct_index = 0
        new_ROINumber = 1000
        for Name in self.ROI_Names:
            new_ROINumber -= 1
            if not temp_color_list:
                temp_color_list = copy.deepcopy(color_list)
            color_int = np.random.randint(len(temp_color_list))
            print('Writing data for ' + Name)
            annotations = copy.deepcopy(base_annotations[:, :, :, int(self.ROI_Names.index(Name) + 1)])
            annotations = annotations.astype('int')

            make_new = 1
            allow_slip_in = True
            if (Name not in current_names and allow_slip_in) or self.delete_previous_rois:
                self.RS_struct.StructureSetROISequence.insert(0,
                                                              copy.deepcopy(self.RS_struct.StructureSetROISequence[0]))
            else:
                print('Prediction ROI {} is already within RT structure'.format(Name))
                continue
            self.RS_struct.StructureSetROISequence[self.struct_index].ROINumber = new_ROINumber
            self.RS_struct.StructureSetROISequence[self.struct_index].ReferencedFrameOfReferenceUID = \
                self.ds.FrameOfReferenceUID
            self.RS_struct.StructureSetROISequence[self.struct_index].ROIName = Name
            self.RS_struct.StructureSetROISequence[self.struct_index].ROIVolume = 0
            self.RS_struct.StructureSetROISequence[self.struct_index].ROIGenerationAlgorithm = 'SEMIAUTOMATIC'
            if make_new == 1:
                self.RS_struct.RTROIObservationsSequence.insert(0,
                                                                copy.deepcopy(
                                                                    self.RS_struct.RTROIObservationsSequence[0]))
                if 'MaterialID' in self.RS_struct.RTROIObservationsSequence[self.struct_index]:
                    del self.RS_struct.RTROIObservationsSequence[self.struct_index].MaterialID
            self.RS_struct.RTROIObservationsSequence[self.struct_index].ObservationNumber = new_ROINumber
            self.RS_struct.RTROIObservationsSequence[self.struct_index].ReferencedROINumber = new_ROINumber
            self.RS_struct.RTROIObservationsSequence[self.struct_index].ROIObservationLabel = Name
            
            if 'ctv' in Name.lower():
                self.RS_struct.RTROIObservationsSequence[self.struct_index].RTROIInterpretedType = 'CTV'
            elif 'ptv' in Name.lower():
                self.RS_struct.RTROIObservationsSequence[self.struct_index].RTROIInterpretedType = 'PTV'
            else:
                self.RS_struct.RTROIObservationsSequence[self.struct_index].RTROIInterpretedType = 'ORGAN'

            if make_new == 1:
                self.RS_struct.ROIContourSequence.insert(0, copy.deepcopy(self.RS_struct.ROIContourSequence[0]))
            self.RS_struct.ROIContourSequence[self.struct_index].ReferencedROINumber = new_ROINumber
            del self.RS_struct.ROIContourSequence[self.struct_index].ContourSequence[1:]
            self.RS_struct.ROIContourSequence[self.struct_index].ROIDisplayColor = temp_color_list[color_int]
            del temp_color_list[color_int]
            thread_count = int(cpu_count() * 0.9 - 1)
            contour_dict = {}
            q = Queue(maxsize=thread_count)
            threads = []
            kwargs = {'image_size_rows': self.image_size_rows, 'image_size_cols': self.image_size_cols,
                      'PixelSize': self.PixelSize, 'contour_dict': contour_dict, 'RS': self.RS_struct}

            A = [q, kwargs]
            # pointer_class = PointOutputMakerClass(**kwargs)
            for worker in range(thread_count):
                t = Thread(target=contour_worker, args=(A,))
                t.start()
                threads.append(t)
            contour_num = 0
            if np.max(annotations) > 0:  # If we have an annotation, write it
                image_locations = np.max(annotations, axis=(1, 2))
                indexes = np.where(image_locations > 0)[0]
                for index in indexes:
                    item = {'annotation': annotations[index], 'i': index, 'dicom_handle': self.dicom_handle}
                    # pointer_class.make_output(**item)
                    q.put(item)
                for i in range(thread_count):
                    q.put(None)
                for t in threads:
                    t.join()
                for i in contour_dict.keys():
                    for points in contour_dict[i]:
                        output = np.asarray(points).flatten('C')
                        if contour_num > 0:
                            self.RS_struct.ROIContourSequence[self.struct_index].ContourSequence.append(
                                copy.deepcopy(
                                    self.RS_struct.ROIContourSequence[self.struct_index].ContourSequence[0]))
                        self.RS_struct.ROIContourSequence[self.struct_index].ContourSequence[
                            contour_num].ContourNumber = str(contour_num)
                        self.RS_struct.ROIContourSequence[self.struct_index].ContourSequence[
                            contour_num].ContourGeometricType = 'CLOSED_PLANAR'
                        self.RS_struct.ROIContourSequence[self.struct_index].ContourSequence[
                            contour_num].ContourImageSequence[0].ReferencedSOPInstanceUID = self.SOPInstanceUIDs[i]
                        self.RS_struct.ROIContourSequence[self.struct_index].ContourSequence[
                            contour_num].ContourData = list(output)
                        self.RS_struct.ROIContourSequence[self.struct_index].ContourSequence[
                            contour_num].NumberOfContourPoints = len(output) // 3
                        contour_num += 1
        self.RS_struct.SOPInstanceUID += '.' + str(np.random.randint(999))
        if self.template or self.delete_previous_rois:
            for i in range(len(self.RS_struct.StructureSetROISequence), len(self.ROI_Names), -1):
                del self.RS_struct.StructureSetROISequence[-1]
            for i in range(len(self.RS_struct.RTROIObservationsSequence), len(self.ROI_Names), -1):
                del self.RS_struct.RTROIObservationsSequence[-1]
            for i in range(len(self.RS_struct.ROIContourSequence), len(self.ROI_Names), -1):
                del self.RS_struct.ROIContourSequence[-1]
            for i in range(len(self.RS_struct.StructureSetROISequence)):
                self.RS_struct.StructureSetROISequence[i].ROINumber = i + 1
                self.RS_struct.RTROIObservationsSequence[i].ReferencedROINumber = i + 1
                self.RS_struct.ROIContourSequence[i].ReferencedROINumber = i + 1
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        self.RS_struct.SeriesInstanceUID = pydicom.uid.generate_uid(prefix='1.2.826.0.1.3680043.8.498.')
        out_name = os.path.join(self.output_dir,
                                'RS_MRN' + self.RS_struct.PatientID + '_' + self.RS_struct.SeriesInstanceUID + '.dcm')
        if os.path.exists(out_name):
            out_name = os.path.join(self.output_dir,
                                    'RS_MRN' + self.RS_struct.PatientID + '_' + self.RS_struct.SeriesInstanceUID + '1.dcm')
        print('Writing out data...{}'.format(self.output_dir))
        pydicom.write_file(out_name, self.RS_struct)
        fid = open(os.path.join(self.output_dir, 'Completed.txt'), 'w+')
        fid.close()
        print('Finished!')
        return None

    def change_template(self):
        keys = self.RS_struct.keys()
        for key in keys:
            # print(self.RS_struct[key].name)
            if self.RS_struct[key].name == 'Referenced Frame of Reference Sequence':
                break
        self.RS_struct[key]._value[0].FrameOfReferenceUID = self.ds.FrameOfReferenceUID
        self.RS_struct[key]._value[0].RTReferencedStudySequence[0].ReferencedSOPInstanceUID = self.ds.StudyInstanceUID
        self.RS_struct[key]._value[0].RTReferencedStudySequence[0].RTReferencedSeriesSequence[
            0].SeriesInstanceUID = self.ds.SeriesInstanceUID
        for i in range(len(self.RS_struct[key]._value[0].RTReferencedStudySequence[0].RTReferencedSeriesSequence[
                               0].ContourImageSequence) - 1):
            del self.RS_struct[key]._value[0].RTReferencedStudySequence[0].RTReferencedSeriesSequence[
                0].ContourImageSequence[-1]
        fill_segment = copy.deepcopy(
            self.RS_struct[key]._value[0].RTReferencedStudySequence[0].RTReferencedSeriesSequence[
                0].ContourImageSequence[0])
        for i in range(len(self.SOPInstanceUIDs)):
            temp_segment = copy.deepcopy(fill_segment)
            temp_segment.ReferencedSOPInstanceUID = self.SOPInstanceUIDs[i]
            self.RS_struct[key]._value[0].RTReferencedStudySequence[0].RTReferencedSeriesSequence[
                0].ContourImageSequence.append(temp_segment)
        del \
            self.RS_struct[key]._value[0].RTReferencedStudySequence[0].RTReferencedSeriesSequence[
                0].ContourImageSequence[0]

        new_keys = open(self.key_list)
        keys = {}
        i = 0
        for line in new_keys:
            keys[i] = line.strip('\n').split(',')
            i += 1
        new_keys.close()
        for index in keys.keys():
            new_key = keys[index]
            try:
                self.RS_struct[new_key[0], new_key[1]] = self.ds[[new_key[0], new_key[1]]]
            except:
                continue
        return None

    def Make_Contour_From_directory(self, PathDicom: typing.Union[str, bytes, os.PathLike]):
        print('Please move over to using walk_through_folders() instead of Make_Contour_From_directory()')
        self.walk_through_folders(input_path=PathDicom)

    def make_contour_from_directory(self, dicom_path: typing.Union[str, bytes, os.PathLike]):
        print('Please move over to using walk_through_folders() instead of Make_Contour_From_directory()')
        self.walk_through_folders(input_path=dicom_path)
        return None

    def rewrite_RT(self, lstRSFile=None):
        if lstRSFile is not None:
            self.RS_struct = pydicom.read_file(lstRSFile)
        if Tag((0x3006, 0x020)) in self.RS_struct.keys():
            self.ROI_Structure = self.RS_struct.StructureSetROISequence
        else:
            self.ROI_Structure = []
        if Tag((0x3006, 0x080)) in self.RS_struct.keys():
            self.Observation_Sequence = self.RS_struct.RTROIObservationsSequence
        else:
            self.Observation_Sequence = []
        self.rois_in_case = []
        for i, Structures in enumerate(self.ROI_Structure):
            if Structures.ROIName in self.associations:
                new_name = self.associations[Structures.ROIName]
                self.RS_struct.StructureSetROISequence[i].ROIName = new_name
            self.rois_in_case.append(self.RS_struct.StructureSetROISequence[i].ROIName)
        for i, ObsSequence in enumerate(self.Observation_Sequence):
            if ObsSequence.ROIObservationLabel in self.associations:
                new_name = self.associations[ObsSequence.ROIObservationLabel]
                self.RS_struct.RTROIObservationsSequence[i].ROIObservationLabel = new_name
        self.RS_struct.save_as(self.lstRSFile)


class Dicom_to_Imagestack(DicomReaderWriter):
    def __init__(self, **kwargs):
        print('Please move from using Dicom_to_Imagestack to DicomReaderWriter, same arguments are passed')
        super().__init__(**kwargs)


# if __name__ == '__main__':
#     pass