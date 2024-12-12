import pytest
from HDF5_BLS.wrapper import Wrapper
import numpy as np


def test_create_wrapper_empty():
    from HDF5_BLS.wrapper import Wrapper
    wrp = Wrapper()
    assert wrp.attributes == {}, "FAIL - test_create_wrapper_empty - attributes"
    assert wrp.data == {}, "FAIL - test_create_wrapper_empty - data"
    assert wrp.data_attributes == {}, "FAIL - test_create_wrapper_empty - data_attributes"
    
def test_create_wrapper_with_data():
    wrp = Wrapper({"Name": "test"}, {"Raw_data": np.array(1), "Abscissa_0": np.array([0])}, {"Name": "test"})
    assert wrp.attributes == {"Name": "test"}, "FAIL - test_create_wrapper_with_data - attributes"
    assert wrp.data == {"Raw_data": np.array(1), "Abscissa_0": np.array([0])}, "FAIL - test_create_wrapper_with_data - data"
    assert wrp.data_attributes == {"Name": "test"}, "FAIL - test_create_wrapper_with_data - data_attributes"
    
def test_add_data_group_to_wrapper():    
    wrp_0_0 = Wrapper({"ID": "Data_0","Name": "t = 1s"},
                       {"Raw_data": np.array([1]), "Abscissa_0": np.array([0])},  
                       {})
    
    wrp_0 = Wrapper({"ID": "Data_0", "Name": "Time series"},
                       {"Data_0": wrp_0_0},  
                       {})
    
    wrp = Wrapper({"ID": "Data", "Name": "Main Wrapper"},
                       {"Data_0": wrp_0},  
                       {})

    wrp.add_data_group_to_wrapper(np.array([[2]]), parent_group = "Data_0", name = "t = 2s")

    assert len(wrp.data.keys()) == 1, "FAIL - test_add_data_group_to_wrapper - Groups were added to the wrapper and ahould not"
    assert len(wrp.data["Data_0"].data.keys()) == 2, "FAIL - test_add_data_group_to_wrapper - Group was not created at the given position"
    assert type(wrp.data["Data_0"].data["Data_1"]) == Wrapper, "FAIL - test_add_data_group_to_wrapper - The element is not a wrapper"
    assert wrp.data["Data_0"].data["Data_1"].data == {"Raw_data": np.array([[2]]), "Abscissa_0": np.array([0]), "Abscissa_1": np.array([0])}, "FAIL - test_add_data_group_to_wrapper - The wrapper is not right"
    assert wrp.data["Data_0"].data["Data_1"].attributes == {"ID": "Data_1", "Name": "t = 2s"}, "FAIL - test_add_data_group_to_wrapper - The name given to the data is wrong"

def test_add_data_to_group():
    wrp_0_0 = Wrapper({"ID": "Data_0", "Name": "t = 1s"},
                    {"Raw_data": np.array([[1]]), "Abscissa_0": np.array([0]), "Abscissa_1": np.array([0])},
                    {})
    
    wrp_0 = Wrapper({"ID": "Data_0", "Name": "t = 1s"},
                    {"Data_0": wrp_0_0},
                    {})
    
    wrp_1 = Wrapper({"ID": "Data_1", "Name": "t = 2s"},
                    {"Raw_data": np.array([[2]]), "Abscissa_0": np.array([0]), "Abscissa_1": np.array([0])},
                    {})

    wrp = Wrapper({"Name": "Time series"}, 
                  {"Data_0": wrp_0,
                  "Data_1": wrp_1})
    
    wrp.add_data_to_group(np.array([[3]]), group = "Data_0.Data_0", name = "Treated")