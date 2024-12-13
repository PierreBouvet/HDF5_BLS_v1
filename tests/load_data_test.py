import pytest
import sys
import os

sys.path.insert(0, "/Users/pierrebouvet/Documents/Code/HDF5_BLS_v1")
from HDF5_BLS.load_data import load_dat_file

def test_load_dat_file():
    filepath = os.path.join(os.path.dirname(__file__), "test_data", "example_GHOST.DAT")
    data, attributes = load_dat_file(filepath)

    dic_verif = {'FILEPROP.Name': 'example_GHOST', 'MEASURE.Sample': '', 'MEASURE.Date': '', 'SPECTROMETER.Scanning_Strategy': 'point_scanning', 'SPECTROMETER.Type': 'TFP', 'SPECTROMETER.Illumination_Type': 'CW', 'SPECTROMETER.Detector_Type': 'Photon Counter', 'SPECTROMETER.Filtering_Module': 'None', 'SPECTROMETER.Wavelength_nm': '532', 'SPECTROMETER.Scan_Amplitude': '20.1257', 'SPECTROMETER.Spectral_Resolution': '0.0393080078125'}

    assert attributes == dic_verif, "FAIL - test_load_dat_file - attributes are not correct"
    assert data.shape == (512,), "FAIL - test_load_dat_file - data shape is not correct"

def test_load_tiff_file():
    pass


test_load_dat_file()