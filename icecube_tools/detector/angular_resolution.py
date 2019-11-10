import numpy as np
from abc import ABC, abstractmethod

"""
Module for handling the angular resolution
of IceCube based on public data.
"""

R2018_ANG_RES_FILENAME = "AngRes.txt"


class IceCubeAngResReader(ABC):
    """
    Abstract base class for different input files
    from the IceCube website.
    """

    def __init__(self, filename):
        """
        Abstract base class for different input files
        from the IceCube website.
        
        :param filename: Name of file to read.
        """

        self._filename = filename

        self.ang_res_values = None

        self.true_energy_bins = None
        
        self.read()
        
        super().__init__()
        

    @abstractmethod
    def read(self):

        pass


class R2018AngResReader(IceCubeAngResReader):
    """
    Reader for the 2018 Oct 18 release.
    Link: https://icecube.wisc.edu/science/data/PS-3years.
    """

    def read(self):

        import pandas as pd
        
        self.year = int(self._filename[-15:-11])
        self.nu_type = 'nu_mu'
         
        filelayout = ['E_min [GeV]', 'E_max [GeV]', 'Med. Resolution[deg]']
        output = pd.read_csv(self._filename, comment='#',
                             delim_whitespace=True,
                             names=filelayout).to_dict()
        
        true_energy_lower = set(output['E_min [GeV]'].values())
        true_energy_upper = set(output['E_max [GeV]'].values())
    
        self.true_energy_bins = np.array( list(true_energy_upper.union(true_energy_lower)) )
        self.true_energy_bins.sort()
                
        self.ang_res_values = np.array( list(output['Med. Resolution[deg]'].values()) )
        

class AngularResolution():

    def __init__(self, filename):

        self._filename = filename
        
        self._reader = self.get_reader()

        self.values = self._reader.ang_res_values

        self.true_energy_bins = self._reader.true_energy_bins

        self.sigma = sigma

    def get_reader(self):
        """
        Define an IceCubeAeffReader based on the filename.
        """      

        if R2018_ANG_RES_FILENAME in self._filename:

            return R2018AngResReader(self._filename)

        else:

            raise ValueError(self._filename + ' is not recognised as one of the known angular resolution files.')
        

    def _get_angular_resolution(self, Etrue):
        """
        Get the median angular resolution for the 
        given Etrue.
        """

        true_energy_bin_cen = (self.true_energy_bins[:-1] + self.true_energy_bins[1:]) / 2

        ang_res = np.interp(np.log(Etrue), np.log(true_energy_bin_cen), self.values)

        return ang_res

    
    def sample(self, Etrue, ra, dec):
        """
        Sample new ra, dec values given a true energy
        and direction.
        """

        unit_vector = icrs_to_unit_vector(ra, dec)

        ang_res = self._get_angular_resolution()

        kappa = 7552 * np.power(np.rad2deg(ang_res))

        new_unit_vector = sample_VMF(unit_vector, kappa, 1) 
        
        new_ra, new_dec = unit_vector_to_icrs(new_unit_vector)

        return new_ra, new_dec
        

class FixedAngularResolution():

    def __init__(self, sigma=1.0):
        """
        Simple fixed angular resolution.

        :param sigma: Resolution [deg].
        """

        self.sigma = sigma

        
    def sample(self, coord):
        """
        Sample reconstructed coord given original position.

        :coord: ra, dec in [rad].
        """

        ra, dec = coord

        new_ra = np.random.normal(ra, np.deg2rad(self.sigma))

        new_dec = np.random.normal(dec, np.deg2rad(self.sigma))

        return new_ra, new_dec
    
    
def icrs_to_unit_vector(ra, dec):
    """
    Convert to unit vector.
    """

    theta = np.pi/2 - dec
    phi = ra
    
    x = np.sin(theta) * np.cos(phi)
    y = np.sin(theta) * np.sin(phi)
    z = np.cos(theta)

    return np.array([x, y, z])


def unit_vector_to_icrs(unit_vector):
    """
    Convert to ra, dec.
    """

    x = unit_vector[0]
    y = unit_vector[1]
    z = unit_vector[2]

    phi = np.arctan(y / x)
    theta = np.arccos(z)

    ra = phi
    dec = np.pi/2 - theta
    
    return ra, dec