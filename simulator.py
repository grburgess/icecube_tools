import numpy as np
from astropy.coordinates import SkyCoord
from astropy import units as u
import h5py

from tqdm.autonotebook import tqdm as progress_bar

from detector import Detector
from source_model import Source, DIFFUSE, POINT
from neutrino_calculator import NeutrinoCalculator

"""
Module for running neutrino production 
and detection simulations.
"""


class Simulator():

    def __init__(self, sources, detector):
        """
        Class for handling simple neutrino production
        and detection simulations.

        :param sources: List of/single Source object.
        """

        if not isinstance(sources, list):
            sources = [sources]
            
        self._sources = sources

        self._detector = detector

        self.max_cosz = 1 

        self.time = 1 # year

        
    @property
    def sources(self):

        return self._sources

    
    @source.setter
    def source(self, value):

        if not isinstance(value, Source):

            raise ValueError(str(value) + ' is not an instance of Source.')

        else:

            self._sources.append(source)

            
    @property
    def detector(self):

        return self._detector

    
    @detector.setter
    def detector(self):

        if not isinstance(value, Detector):

            raise ValueError(str(value) + ' is not an instance of Detector')

        self._detector = detector

        
    def _get_expected_number(self):
        """
        Find the expected number of neutrinos.
        """
        
        nu_calc = NeutrinoCalculator(self.sources, self.detector.effective_area)

        self._Nex = nu_calc(time=self.time, max_cosz=self.max_cosz)

        self._source_weights = np.array(self._Nex) / sum(self._Nex)
        
        
    def run(self, N=None):
        """
        Run a simulation for the given set of sources 
        and detector configuration.
        
        The expected number of neutrinos will be
        calculated for each source. If total N is forced, 
        then the number from each source will be weighted
        accordingly.

        :param N: Set expected number of neutrinos manually.
        """

        self._get_expected_number()

        if not N:                    
        
            self.N = np.random.poisson(sum(self._Nex))           
            
        else:

            self.N = int(N)
            
        self.true_energy = []
        self.reco_energy = []
        self.coordinate = []
        self.ra = []
        self.dec = []
        self.source_label = []
        
        for i in progress_bar(range(self.N), desc='Sampling'):

            label = np.random.choice(range(len(self.sources)), p=self._source_weights)
            
            accepted = False
            
            while not accepted:

                max_energy = self.source[label].flux_model._upper_energy
                
                Etrue = self.source[label].flux_model.sample(1)[0]
                
                ra, dec = sphere_sample()
                cosz = -np.sin(dec)

                if cosz > self.max_cosz:

                    detection_prob = 0

                else:
                
                    detection_prob = float(self.detector.effective_area.detection_probability(Etrue, cosz, max_energy))

                accepted = np.random.choice([True, False], p=[detection_prob, 1-detection_prob])
                
            self.true_energy.append(Etrue)

            Ereco = self.detector.energy_resolution.sample(Etrue)
            self.reco_energy.append(Ereco)
            
            if self.source[label].source_type == DIFFUSE:

                self.coordinate.append(SkyCoord(ra*u.rad, dec*u.rad, frame='icrs'))
                self.ra.append(ra)
                self.dec.append(dec)
                
            else:

                reco_ra, reco_dec = self.detector.angular_resolution.sample(Etrue, ra, dec)
                self.coordinate.append(SkyCoord(reco_ra*u.rad, reco_dec*u.rad, frame='icrs'))
                self.ra.append(ra)
                self.dec.append(dec)
                

    def save(self, filename):
        """
        Save the output to filename.
        """

        self._filename = filename

        with h5py.File(filename, 'w') as f:

            f.create_dataset('true_energy', data=self.true_energy)

            f.create_dataset('reco_energy', data=self.reco_energy)

            f.create_dataset('ra', data=self.ra)

            f.create_dataset('dec', data=self.dec)

            f.create_dataset('index', data=self.source.flux_model._index)

            f.create_dataset('source_type', data=self.source.source_type)

                
def sphere_sample(radius=1):
    """
    Sample points uniformly on a sphere.
    """

    u = np.random.uniform(0, 1)
    v = np.random.uniform(0, 1)
            
    phi = 2 * np.pi * u
    theta = np.arccos(2 * v - 1)

    ra, dec = spherical_to_icrs(theta, phi)
    
    return ra, dec


def spherical_to_icrs(theta, phi):
    """
    convert spherical coordinates to ICRS
    ra, dec.
    """

    ra = phi

    dec = np.pi/2 - theta

    return ra, dec


def lists_to_tuple(list1, list2):

    return  [(list1[i], list2[i]) for i in range(0, len(list1))] 
