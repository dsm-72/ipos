# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/03_gimp.ipynb.

# %% auto 0
__all__ = ['GImp']

# %% ../nbs/03_gimp.ipynb 3
import inspect
from dataclasses import dataclass

# %% ../nbs/03_gimp.ipynb 5
@dataclass
class GImp:
    '''
    Notes
    -----
    - Taken from rafał grabie: https://stackoverflow.com/a/52856976/5623899
    
    '''
    def __enter__(self):
        # The __enter__ method does nothing but return the context manager itself.
        return self
    
    def __call__(self):    
        # first gets the current execution frame
        currentframe = inspect.currentframe()
        
        # then it gets all outer frames from the current frame
        outerframes  = inspect.getouterframes(currentframe)
        
        # then the outer frame immediately surrounding the current frame is 
        # obtained by indexing the outerframes with [1].frame.
        outerframe   = outerframes[1].frame
        
        # The local variables in that frame are then collected
        # which returns a dictionary of local variables in the outer frame.         
        self.collector = inspect.getargvalues(outerframe).locals

    def __exit__(self, *args):
        # Called when `with` block ends and it takes the dictionary of 
        # local variables (stored in self.collector) and adds it to the 
        # global namespace using globals().update(self.collector). 
        # This makes all local variables in the outer frame globally accessible.
        globals().update(self.collector)
