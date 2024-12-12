import h5py
import numpy as np
import csv
import os
from PIL import Image
import copy

# try: # Used to patch an error in the generation of the documentation
import sys
sys.path.insert(0, "/Users/pierrebouvet/Documents/Code/HDF5_BLS_v1/HDF5_BLS")
from load_data import load_general, load_dat_file, load_tiff_file
from treat import Treat
# except:
#     from HDF5_BLS.load_data import load_general, load_dat_file, load_tiff_file
#     from HDF5_BLS.treat import Treat
    

BLS_HDF5_Version = "0.0"

class WrapperError(Exception):
    def __init__(self, msg) -> None:
        self.message = msg
        super().__init__(self.message)

class Wrapper:
    """
    This object is used to store data and attributes in a unified structure.

    Attributes
    ----------
    attributes: dic
        The attributes of the data
    data: dic
        The data arrays (raw data, treated data, abscissa, other measures)
    data_attributes: dic
        The attributes specific to an array
    """
    def __init__(self, attributes = {}, data = {}, data_attributes = {}):
        self.attributes = attributes # Dictionnary storing all the attributes
        self.data = data # Dictionnary storing all the datasets or wrapper objects, group "Data" of HDF5 file
        self.data_attributes = data_attributes # Dictionnary storing all the attributes of all the data elements

    def add_hdf5_to_wrapper(self, filepath, parent_group = "Data", create_group = True):
        """Adds an hdf5 file to the wrapper by specifying in which group the data have to be stored. Default is the "Data" group. When adding the data, the attributes of the HDF5 file are only added to the created group if they are different from the parent's attribute.

        Parameters
        ----------
        filepath : str
            The filepath of the hdf5 file to add.
        parent_group : str, optional
            The parent group where to store the data of the HDF5 file, by default the parent group is the top group "Data". The format of this group should be "Data.Data_0.Data_0_0"
        create_group : bool, default True
            This parameter should be set to False if different techniques were used to acquire different datasets. This is particularly usefull if fluorescent images are taken after or during the same experiment. Note that only data of same shape, and sharing the same abscissa can be used in a given group. 
        """
        # Create a wrapper object with the contents of the hdf5 file
        wrp_h5 = load_hdf5_file(filepath)

        # Find the position where to add the spectrum
        loc = parent_group.split(".")
        loc.pop(0)
        par = self.data 

        while len(loc)>0:
            temp = loc[0]
            try:
                par = par[temp]
            except:
                par[temp] = {}
                par = par[temp]
            loc.pop(0)

        # Inspects the structure of the parent group and decides if to create a sub-group or not based on the create_group parameter
        if "Data_0" in par.keys():
            i = 0
            while f"Data_{i}" in par.keys():
                i+=1
            par[f"Data_{i}"] = wrp_h5
        else:
            self.attributes, self.data, self.data_attributes = merge_wrappers([self,wrp_h5])
    
    def add_data_group_to_wrapper(self, data, parent_group = None, name = None):
        """Adds data to the wrapper by creating a new group.

        Parameters
        ----------
        data : np.ndarray
            The data to add to the wrapper.
        parent_group : str, optional
            The parent group where to store the data of the HDF5 file, by default the parent group is the top group "Data". The format of this group should be "Data.Data_0.Data_0" or "Data/Data_0/Data_0".
        name : str, optional
            The name of the data group, by default the name is the identifier of the group "Data_i".
        """
        # Find the position where to add the spectrum
        par = self.data 
        if parent_group is not None:
            loc = parent_group.split(".")
            while len(loc)>0:
                temp = loc[0]
                if not temp in par.keys():
                    par[temp] = Wrapper()
                par = par[temp].data
                loc.pop(0)
        
        # Getting the i number of Data_i where to store the data
        i = 0
        while f"Data_{i}" in par.keys(): i+=1

        # Adding the data and the abscissa to the wrapper
        if name is None: name = f"Data_{i}"
        par[f"Data_{i}"] = Wrapper(attributes = {"ID": f"Data_{i}", "Name":name},
                                   data = {"Raw_data": data},
                                   data_attributes = {})
        for j, e in enumerate(data.shape): par[f"Data_{i}"].data[f"Abscissa_{j}"] = np.arange(e)
    
    def add_data_to_group(self, data, group, name = None):
        """Adds an array to an existing data group.

        Parameters
        ----------
        data : np.ndarray
            The data to add to the wrapper.
        group : str
            The group where to store the data.
        name : str, optional
            The name of the data group, by default the name is the identifier of the group "Data_i".
        """
        # Find the position where to add the spectrum
        par = self.data 
        par_attr = self.data_attributes
        loc = group.split(".")
        print(loc)
        par = self.data 
        loc = group.split(".")
        while len(loc)>0:
            temp = loc[0]
            if not temp in par.keys():
                par[temp] = Wrapper()
            par = par[temp].data
            par_attr = par_attr[temp].data_attributes
            loc.pop(0)
        
        # Checking the shape of the data
        shape = par[f"Raw_data"].shape
        assert data.shape == shape, WrapperError(f"The shape of the data to add to the data object ({data.shape}) is different from the shape of the raw data in the group ({shape}).")

        # Getting the i number of Data_i where to store the data
        i = 0
        while f"Raw_data_{i}" in par.keys(): i+=1

        # Adding the data to the wrapper
        par[f"Raw_data_{i}"] = data

        # Adding the attributes of the data and the abscissa to the wrapper
        if name is not None: par_attr[f"Raw_data_{i}"]["Name"] = name

    def assign_name_all_abscissa(self, abscissa):
        """Adds as attributes of the abscissas and the raw data, the names of the abscissas

        Parameters
        ----------
        abscissa : str
            The names of the abscissas
        
        Raises
        ------
        WrapperError
            If the length of the abscissa is different from the dimensionality of the data.
        """
        # Adds the names of the abscissas to the attributes of the Raw data
        abscissa = abscissa.split(",")
        if len(abscissa) != len(self.data["Raw_data"].shape):
            raise WrapperError("The names provided for the abscissa do not match the shape of the raw data")
        else:
            for i, e in enumerate(abscissa): self.data_attributes[f"Abscissa_{i}"]["Name"] = e 
            self.attributes["MEASURE.Abscissa_Names"] = ','.join(abscissa)
        
    def assign_name_one_abscissa(self, abscissa_nb, name):
        """Adds as attributes of the abscissas and the raw data, the names of the abscissas

        Parameters
        ----------
        abscissa_nb : str
            The number of the abscissa to rename ("i" or "i-j")
        name : str
            The new name of the abscissa to rename
        """
        # Adds the names of the abscissas to the attributes of the Raw data
        abscissa = []
        for k in self.data_attributes.keys():
            if k.split("_")[-1] == abscissa_nb:
                self.data_attributes[f"Abscissa_{abscissa_nb}"]["Name"] = name
            abscissa.append(self.data_attributes[f"Abscissa_{abscissa_nb}"]["Name"])
        self.attributes["MEASURE.Abscissa_Names"] = ','.join(abscissa)

    def create_abscissa_1D_min_max(self, dimension, min, max, name = None):
        """Creates an abscissa from a minimal and maximal value

        Parameters
        ----------
        dimension : int
            The dimension of the data that we are changing (first dimension is 0)
        min : float
            The minimal value of the abscissa range (included)
        max : float
            The maximal value of the abscissa range (included)
        name : str, optional
            The name of the abscissa axis, by default None

        Raises
        ------
        WrapperError
            If the dimension given is higher than the dimension of the data
        """
        if dimension >= len(self.data["Raw_data"].shape):
            raise WrapperError("The dimension provided for the abscissa is too large considering the size of the raw data")
        self.data[f"Abscissa_{dimension}"] = np.linspace(min, max, self.data["Raw_data"].shape[dimension])
        if not name is None:
            self.data_attributes[f"Abscissa_{dimension}"]["Name"] = name
            temp = self.attributes["MEASURE.Abscissa_Names"].split(",")
            temp[dimension] = name
            self.attributes["MEASURE.Abscissa_Names"] = ",".join(temp)
        else:
            self.data_attributes[f"Abscissa_{dimension}"]["Name"] = "Abscissa"
            temp = self.attributes["MEASURE.Abscissa_Names"].split(",")
            temp[dimension] = "Abscissa"
            self.attributes["MEASURE.Abscissa_Names"] = ",".join(temp)
    
    def import_abscissa_1D(self, dimension, filepath, name = None):
        """Creates an abscissa from a minimal and maximal value

        Parameters
        ----------
        dimension : int
            The dimension of the data that we are changing (first dimension is 0)
        filepath : str
            The filepath containing the values of the abscissa
        name : str, optional
            The name of the abscissa axis, by default None
        
        Raises
        ------
        WrapperError
            If the dimension given is higher than the dimension of the data
        """
        if dimension >= len(self.data["Raw_data"].shape):
            raise WrapperError("The dimension provided for the abscissa is too large considering the size of the raw data")
        self.data[f"Abscissa_{dimension}"], _ = load_general(filepath)
        if not name is None:
            self.data_attributes[f"Abscissa_{dimension}"]["Name"] = name
            temp = self.attributes["MEASURE.Abscissa_Names"].split(",")
            temp[dimension] = name
            self.attributes["MEASURE.Abscissa_Names"] = ",".join(temp)

    def import_properties_data(self, filepath):
        """Imports properties from a CSV file into a dictionary.
    
        Parameters
        ----------
        filepath_csv : str                           
            The filepath to the csv storing the properties of the measure. This csv is meant to be made once to store all the properties of the spectrometer and then minimally adjusted to the sample being measured.
        
        Returns
        -------
        self.attributes : dic
            The dictionnary containing all the attributes
        """
        with open(filepath, mode='r') as csv_file:
            csv_reader = csv.reader(csv_file)
            for row in csv_reader:
                key, value = row
                self.attributes[key] = value
        return self.attributes

    def open_data(self, filepath, store_filepath = True):
        """Opens a raw data file based on its file extension and stores the filepath.
    
        Parameters
        ----------
        filepath : str                           
            The filepath to the raw data file
        store_filepath: bool, default True
            A boolean parameter to store the original filepath of the raw data in the attributes of "Raw_data"
        """
        # Opens the raw file and retrieve the retrievable attributes
        data, attributes = load_general(filepath)

        # Add the raw data to the "Raw_data" dataset of the wrapper and writes the dimensionnality of the data
        self.data["Raw_data"] = data
        self.data_attributes["Raw_data"] = {"ID":"Raw_data"}
        if store_filepath: self.data_attributes["Raw_data"]["Filepath"] = filepath
        attributes["MEASURE.Dimensionnality_of_measure"]=len(data.shape)
        self.data_attributes["Raw_data"]["Name"] = "Raw data"
        
        # Generate the abscissa corresponding to the different dimensions
        abscissa_name = ""
        for i, k in enumerate(data.shape):
            self.data[f"Abscissa_{i}"] = np.arange(k)
            self.data_attributes[f"Abscissa_{i}"] = {"ID":f"Abscissa_{i}"}
            abscissa_name = abscissa_name+"_,"
        attributes["MEASURE.Abscissa_Names"] = abscissa_name[:-1]

        #Indicates the version of the BLS_HDF5 library
        attributes["FILEPROP.BLS_HDF5_Version"] = BLS_HDF5_Version
        
        # Storing the retrieved attributes
        self.attributes = attributes

    def save_as_hdf5(self,filepath):
        """Saves the data and attributes to an HDF5 file.
    
        Parameters
        ----------
        save_filepath : str                           
            The filepath where to save the hdf5 file
        
        Raises
        -------
        WrapperError
            Raises an error if the file could not be saved
        """
        def save_group(parent, group, id_group):
            data_group = parent.create_group(id_group)
            for key, value in group.attributes.items():
                data_group.attrs[key] = value
            for key in group.data.keys():
                if type(group.data[key]) == np.ndarray:
                    dg = data_group.create_dataset(key, data=group.data[key])
                    for k, v in group.data_attributes[key].items():
                        dg.attrs[k] = v
                elif type(group[key]) == Wrapper:
                    save_group(data_group, group[key], key)
                else:
                    raise WrapperError("Cannot add the selected type to HDF5 file")
                

        try:
            with h5py.File(filepath, 'w') as hdf5_file:
                # Save attributes
                for key, value in self.attributes.items():
                    hdf5_file.attrs[key] = value
                
                # Create Data group
                data_group = hdf5_file.create_group("Data")

                # Save datasets 
                for key in self.data.keys():
                    if type(self.data[key]) == np.ndarray:
                        dg = data_group.create_dataset(key, data=self.data[key])
                    elif type(self.data[key]) == Wrapper:
                        save_group(data_group, self.data[key], key)
                    else:
                        raise WrapperError("Cannot add the selected type to HDF5 file")
                    for k, v in self.data_attributes[key].items():
                        dg.attrs[k] = v
        except:
            raise WrapperError("The wrapper could not be saved as a HDF5 file")


def load_hdf5_file(filepath):
    """Loads HDF5 files

    Parameters
    ----------
    filepath : str                           
        The filepath to the HDF5 file
    
    Returns
    -------
    wrp : Wrapper
        The wrapper associated to the HDF5 file
    """
    def load_group(group):
        """Loads a group from an HDF5 file

        Parameters
        ----------
        group : HDF5 group
            The group to load

        Returns
        -------
        Wrapper
            The wrapper associated to the HDF5 group

        Raises
        ------
        WrapperError
            Raises an error if the group is not a group or a dataset
        """
        attributes, data_attributes, data = {}, {}, {}

        for k, v in group.items(): # Iterate over the group's items
            if isinstance(v, h5py._hl.dataset.Dataset): data[k] = v # If the item is a dataset, add it to the data dictionary
            elif isinstance(v, h5py._hl.group.Group):  data[k] = load_group(v) # If the item is a group, add it to the data dictionary
            else: raise WrapperError("Trying to add an object that is neither a group nor a dataset")

            data_attributes[k] = {}
            for ka, va in group[k].attrs.items():  data_attributes[k][ka] = va

        for k, v in group.attrs.items(): attributes[k] = v

        return Wrapper(attributes, data, data_attributes)
     
    attributes, data_attributes, data = {}, {}, {} 

    with h5py.File(filepath, 'r') as hdf5_file:
        for k in hdf5_file.keys():
            h5 = hdf5_file[k]

            if isinstance(h5, h5py._hl.dataset.Dataset): data[k] = h5
            elif isinstance(h5, h5py._hl.group.Group): data[k] = load_group(h5)
            else: raise WrapperError("Trying to add an object that is neither a group nor a dataset")
            
            data_attributes[k] = {}
            for ka, va in h5.attrs.items(): data_attributes[k][ka] = va

    return Wrapper(attributes, data, data_attributes)

def merge_wrappers(list_wrappers, name = None, abscissa_from_attributes = None):
        """ Merges a list of wrappers into a single wrapper, combining their common attributes.

        Parameters
        ----------
        list_wrappers : list of Wrapper objects
            The list of Wrapper objects to merge into a single Wrapper object.
        name: None or str, optional
            The name given to the file resulting of the merging of the wrappers
        abscissa_from_attributes: None or list of str, optional
            The name of the attributes from which to extract values to create an abscissa
        
        Returns
        -------
        attributes : dic
            The attributes of the merged wrapper
        data : dic
            The data of the merged wrapper
        data_attributes : dic
            The attributes of the data of the merged wrapper
        """
        # Initializing the parameters of the new wrapper
        attributes = list_wrappers[0].attributes.copy()
        data, data_attributes = {}, {}

        # Extracting the common attributes by joining the attributes and deleting the attributes that are not the same for all the wrappers
        for wrp in list_wrappers[1:]:
            old_attributes = attributes.copy()
            for k,v in old_attributes.items():
                if wrp.attributes[k] != v: del attributes[k]
        
        # Creating the new abscissa from the attributes of the wrappers
        if abscissa_from_attributes is not None:
            assert type(abscissa_from_attributes) is list, WrapperError("The abscissa_from_attributes parameter should be a list of strings")
            for i, ab in enumerate(abscissa_from_attributes):
                ab_temp = [wrp.attributes[ab] for wrp in list_wrappers]

                try: data[f"Abscissa_{i}"] = np.array(ab_temp).astype(float)
                except: data[f"Abscissa_{i}"] = np.array(ab_temp).astype(str)

                data_attributes[f"Abscissa_{i}"] = {"Name": ab}
        
        # Adding the wrappers to the "Data" of the parent wrapper
        for i, wrp in enumerate(list_wrappers): data[f"Data_{i}"] = copy.copy(wrp)
        
        # Adding the name of the new wrapper
        attributes["Name"] = name

        return attributes, data, data_attributes

def add_data_to_wrapper(wrapper, file_path, data_attributes, abscissa_from_attributes):
    """
    Add data from a file to a wrapper
    
    Parameters
    ----------
    wrapper : Wrapper
        The wrapper to add the data to
    file_path : str
        The path to the file to add
    data_attributes : dict
        The attributes of the data to add
    abscissa_from_attributes : list
        The attributes to use as abscissa
    
    Returns
    -------
    None
    """
    # Opening the file
    wrp = Wrapper()
    wrp.open_data(file_path)
    
    # Adding the attributes
    for k,v in data_attributes.items():
        if k not in wrapper.data_attributes.keys():
            wrapper.data_attributes[k] = v
        else:
            print(f"Attribute {k} already exists in the wrapper")
            
    # Adding the data
    for k,v in wrp.data.items():
        if k not in wrapper.data.keys():
            wrapper.data[k] = v
        else:
            print(f"Data {k} already exists in the wrapper")
            
    # Adding the abscissa
    for k,v in wrp.data_attributes.items():
        if k not in wrapper.data_attributes.keys():
            wrapper.data_attributes[k] = v
        else:
            print(f"Attribute {k} already exists in the wrapper")
            
    # Adding the abscissa
    for k,v in wrp.data_attributes.items():
        if k not in wrapper.data_attributes.keys():
            wrapper.data_attributes[k] = v
        else:    
            print(f"Attribute {k} already exists in the wrapper")    
            
    return wrapper       
