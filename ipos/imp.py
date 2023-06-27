# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/00_core.ipynb.

# %% auto 0
__all__ = ['Module', 'Loader', 'ModuleSpec', 'VariableDict', 'FallbackType', 'ImpItemsType', 'ImpSubSpecType', 'GlobalImport',
           'modjoin', 'is_mod', 'is_mod_imp', 'is_var_imp', 'is_mod_or_var', 'is_mod_avail', 'loader_from_spec',
           'module_from_str', 'getmodule', 'ImpItem', 'Fallbacks', 'BaseImp', 'ImpSubSpec', 'ImpSpec', 'Imp']

# %% ../nbs/00_core.ipynb 3
import sys, types, inspect, importlib, warnings, itertools
from importlib.util import (LazyLoader, find_spec, module_from_spec)
from importlib.abc import Loader
from importlib.machinery import ModuleSpec

from dataclasses import dataclass, field, KW_ONLY
from typing import Optional, Dict, Any, TypeAlias, Union, ClassVar, List, Tuple

# %% ../nbs/00_core.ipynb 5
@dataclass
class GlobalImport:
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

# %% ../nbs/00_core.ipynb 7
Module: TypeAlias = types.ModuleType

Loader: TypeAlias = importlib.abc.Loader

ModuleSpec: TypeAlias = importlib.machinery.ModuleSpec

VariableDict: TypeAlias = Dict[str, Any]

FallbackType: TypeAlias = Optional[Union['Fallbacks', VariableDict]]

ImpItemsType: TypeAlias = Optional[List['ImpItem']]

ImpSubSpecType : TypeAlias = Optional[List['ImpSubSpec']]

# %% ../nbs/00_core.ipynb 9
def modjoin(*parts: str) -> str:
    """
    Join module name parts into a valid module path.

    Parameters
    ----------
    *parts : str
        Name parts of the module to be joined.

    Returns
    -------
    str
        Valid module path.
    """
    return ('.'.join(parts)).rstrip('.')

def is_mod(module: Any) -> bool:
    """
    Check if a given object is a module.

    Parameters
    ----------
    module : Any
        Object to be checked.

    Returns
    -------
    bool
        True if the object is a module, False otherwise.
    """
    return isinstance(module, Module)

def is_mod_imp(name: str) -> bool:
    """
    Check if a given module name is in the system module list.

    Parameters
    ----------
    name : str
        Name of the module to be checked.

    Returns
    -------
    bool
        True if the module is in the system module list, False otherwise.
    """
    return name in sys.modules

def is_var_imp(name: str) -> bool:
    """
    Check if a given variable name exists in the global namespace.

    Parameters
    ----------
    name : str
        Name of the variable to be checked.

    Returns
    -------
    bool
        True if the variable exists in the global namespace, False otherwise.
    """
    return name in globals()


def is_mod_or_var(name: str):
    """
    Check if a given name exists either as a module or a variable.

    Parameters
    ----------
    name : str
        Name to be checked.

    Returns
    -------
    bool
        True if the name exists either as a module or a variable, False otherwise.
    """
    return is_var_imp(name) or is_mod_imp(name)

def is_mod_avail(name: str) -> bool:
    """
    Check if a given module name is available for import.

    Parameters
    ----------
    name : str
        Name of the module to be checked.

    Returns
    -------
    bool
        True if the module is available for import, False otherwise.
    """
    if is_mod_imp(name): return True
    elif find_spec(name) is not None: return True
    return False

def loader_from_spec(spec: ModuleSpec, lazy: bool = False) -> Loader:
    """
    Get a loader from a given module specification.

    Parameters
    ----------
    spec : ModuleSpec
        Module specification from which to get the loader.
    lazy : bool, optional
        If True, return a LazyLoader; if False, return the original loader.

    Returns
    -------
    Loader
        Loader for the module.
    """
    loader = spec.loader
    if lazy: loader = LazyLoader(loader)
    return loader

def module_from_str(
    name: str, 
    lazy: bool = False, 
    alias: Optional[str] = None,
    inject: Optional[bool] = True,
    inject_both: Optional[bool] = False,
) -> Module:
    """
    Import a module from a given string name.

    Parameters
    ----------
    name : str
        Name of the module to import.
    lazy : bool, optional
        If True, use lazy import; if False, use regular import.
    alias : str, optional
        Alias to use for the module.
    inject : bool, optional
        If True, inject the module into sys.modules.
    inject_both : bool, optional
        If True, inject the module into sys.modules with both its original name and alias.

    Returns
    -------
    Module
        The imported module.
    """
    spec = find_spec(name)    
    loader = loader_from_spec(spec, lazy=lazy)
    
    module = module_from_spec(spec)    
    modname = name if alias is None else alias
    
    if inject_both: inject = True
    if inject:
        sys.modules[modname] = module
    if inject_both:
        sys.modules[name] = module

    loader.exec_module(module)
    return module

def getmodule(
    name: str, lazy: Optional[bool] = False, 
    alias: Optional[str] = None, 
    inject: Optional[bool] = True,
    inject_both: Optional[bool] = False,
) -> Module:
    """
    Get a module by name, importing it if necessary.

    Parameters
    ----------
    name : str
        Name of the module to get.
    lazy : bool, optional
        If True, use lazy import; if False, use regular import.
    alias : str, optional
        Alias to use for the module.
    inject : bool, optional
        If True, inject the module into sys.modules.
    inject_both : bool, optional
        If True, inject the module into sys.modules with both its original name and alias.

    Returns
    -------
    Module
        The requested module.

    Raises
    ------
    ModuleNotFoundError
        If the module cannot be found.
    """
    if is_mod_avail(name):
        return module_from_str(name, lazy, alias, inject, inject_both)
    raise ModuleNotFoundError


# %% ../nbs/00_core.ipynb 12
@dataclass
class ImpItem:
    """
    A class to represent an item in the import specification.

    Attributes
    ----------
    item : str
        The item to be imported.
    name : Optional[str]
        The name of the item to be imported. Derived from `item` during post-initialization.
    nick : Optional[str]
        The nickname of the item to be imported. Derived from `item` during post-initialization.
    """
    item: str = field(repr=False, default='')
    name: Optional[str] = field(init=False, repr=True)
    nick: Optional[str] = field(init=False, repr=True)

    def __post_init__(self):
        name, _, nick = self.item.strip().partition(' as ')
        self.name = name
        self.nick = nick        
        return self
    
    def __eq__(self, other: Any) -> bool:
        if isinstance(other, str):
            return self.varname == other
        elif isinstance(other, ImpItem):
            return self.varname == other.varname
        return False
    
    @property
    def has_alias(self) -> bool:
        return bool(self.nick)
    
    @property
    def varname(self) -> bool:
        varname = self.name if not self.nick else self.nick
        return varname

# %% ../nbs/00_core.ipynb 14
@dataclass
class Fallbacks(dict):

    @classmethod
    def from_items(cls, items: ImpItemsType = None) -> 'Fallbacks':
        instance = cls()
        items = items or []
        for imp_item in items:
            varname = imp_item.varname
            instance[varname] = None                        
        return instance
    
    @classmethod
    def from_dict(cls, other: FallbackType = None) -> 'Fallbacks':
        instance = cls()
        instance.update(other)        
        return instance
    
    @classmethod
    def from_imp(
        cls, 
        other: FallbackType = None, 
        items: ImpItemsType = None,
        fitler: Optional[bool] = True,
    ):
        instance = cls()

        items = items or []
        other = other or dict()
        
        fb_items = cls.from_items(items)
        fb_other = cls.from_dict(other)
        
        instance.update(fb_items)
        instance.update(fb_other)
        
        if fitler and len(items):
            instance = instance.keep(items, True)
        
        return instance
    
    def give(self, other: Optional[VariableDict] = None) -> VariableDict:
        other = (other or dict())
        for name, fallback in self.items():
            if name not in other and not is_mod_or_var(name):
                other[name] = fallback
        return other
    
    def take(
        self, other: FallbackType = None, items: ImpItemsType = None, 
        inplace: Optional[bool] = False
    ) -> 'Fallbacks':
        other = other or self.default_fallbacks(items)
        if inplace:
            self.update(other)
            return self
        else:
            instance = self.copy()
            instance.update(other)
            return instance
        return self
    
    def keep(self, items: ImpItemsType = None, inplace: Optional[bool] = False) -> 'Fallbacks':
        items = items or []
        if len(items) == 0: return self if inplace else self.copy()

        filtered = {k: v for k, v in self.items() if k in items}
        if inplace:
            bad_keys = [k for k in self.keys() if k not in filtered]
            for k in bad_keys:
                del self[k]
            return self
        return Fallbacks(filtered)

# %% ../nbs/00_core.ipynb 18
@dataclass
class BaseImp:
    """
    Import Module class.
    
    This class facilitates dynamic import of modules and their attributes.
    
    Parameters
    ----------
    name : str
        The name of the module to import.
    
    nick : Optional[str], default=None
        The alias of the module to import.
    
    subspecs : Optional[List[ImpSubSpec]], default=list()
        A list of `ImpSubSpec` objects representing additional specifications for import.
    
    fallbacks : Optional[Dict[str, Any]], default=dict()
        A dictionary of fallback values for import failures.
    
    lazy : Optional[bool], default=True
        Whether or not to use lazy import.

    namespace: Optional[VariableDict], default=globals
        The namespace in which to import the module.
        
    """    
    _ : KW_ONLY
    namespace: VariableDict = field(default_factory=globals, repr=False)
    _updates: VariableDict = field(default_factory=dict, repr=False, init=False)

    def update_fallbacks(self, other: FallbackType = None, items: ImpItemsType = None) -> 'BaseImp':
        fbnew = Fallbacks.from_imp(other, items)
        self.fallbacks.update(fbnew)
        return self
    
    def give_updates_fallbacks(self, updates: Optional[VariableDict] = dict()) -> VariableDict:
        oldvals = getattr(self, '_updates', (updates or dict()))
        oldvals.update(updates)
        updates = self.fallbacks.give(oldvals)                
        return updates
    
    def update_namespace(
        self, 
        updates: Optional[VariableDict] = None,
        namespace: Optional[VariableDict] = None,
    ) -> VariableDict:        
        updates = getattr(self, '_updates', updates)
        namespace = getattr(self, 'namespace', namespace)
        namespace = namespace or globals()
        namespace.update(updates)
        self.namespace = namespace
        return namespace
    
    def squash_name_error(self, name:str, default: Optional[Any] = None) -> 'BaseImp':
        namespace = getattr(self, 'namespace', None)
        namespace = namespace or globals()
        
        update = dict()
        update[name] = namespace.get(name, default)

        namespace.update(update)
        self.namespace = namespace
        return self

# %% ../nbs/00_core.ipynb 20
@dataclass
class ImpSubSpec(BaseImp):
    """
    A class to represent a sub-specification of the import.

    Attributes
    ----------
    name : str
        The name of the module from which items are imported.
    stub : str
        The sub-module path.
    items : List[ImpItem]
        A list of items to import.
    fallbacks : Optional[Fallbacks]
        A mapping of fallback values for each item.
    """
    name: str
    stub: str
    items: ImpItemsType = field(default_factory=list)
    fallbacks: FallbackType = field(default_factory=Fallbacks, repr=False)
        
    def __post_init__(self):
        """
        Override the post-initialization method to create fallbacks for the instance.
        """        
        self.fallbacks.keep(self.items, inplace=True)

    def items_from_str(self, items: str) -> 'ImpSubSpec':
        """
        Converts a string of comma-separated items into a list of ImpItems.
        
        Parameters
        ----------
        items : str
            A string of comma-separated items.
        
        Returns
        -------
        self : 'ImpSubSpec'
            The current instance of the ImpSubSpec.
        """
        items = [ImpItem(item) for item in items.split(',')]
        return self

    @classmethod
    def from_str(cls, items: str) -> 'ImpSubSpec':
        mods, _, items = items.strip().partition(' import ')        
        _from, _, mods = mods.partition('from ')        
        name, *stub = mods.split('.')
        stub = '.'.join(stub)
        items = [ImpItem(item) for item in items.split(',')]
        return cls(name, stub, items)
    
    @property
    def path(self) -> str:
        """
        Returns the full path of the module by joining the name and stub.

        Returns
        -------
        str
            The full path of the module.
        """
        return modjoin(self.name, self.stub)
    
    def getitem(self, item: ImpItem) -> Tuple[str, Any]:
        """
        Attempts to import an item from the module. 

        Parameters
        ----------
        item : ImpItem
            The item to be imported.
        
        Returns
        -------
        Tuple[str, Any]
            The name of the item and its value, or None if import fails.
        """
        varname = item.varname                
        try:                
            submod = getmodule(self.path, inject=False)
            varval = getattr(submod, item.name, None)
            return varname, varval
        except ImportError or ModuleNotFoundError:
            warnings.warn(f'Could not import {varname} from  {self.path}')
            return varname, None
    
    def fetch(self) -> VariableDict:
        """
        Fetches all the items in the import specification.

        Returns
        -------
        VariableDict
            A dictionary mapping the names of the items to their values.
        """
        updates = dict()
        for imp_item in self.items:
            varname, varval = self.getitem(imp_item)

            updates[varname] = varval
            if varval is None:
                updates[varname] = self.fallbacks.get(varname, None)        
        return updates
    
    def get_updates(self) -> VariableDict:
        """
        Fetches all updates.

        Returns
        -------
        VariableDict
            A dictionary mapping the names of the items to their updated values.
        """
        # print('get_updates')
        updates = self.fetch()
        # print('get_updates', updates)
        updates = self.give_updates_fallbacks(updates)
        # print('get_updates > failsafed', updates)
        self._updates = updates
        return updates
    
    def update_globals(self):
        """
        Updates the global namespace with the fetched updates.
        
        Returns
        -------
        self : 'ImpSubSpec'
            The current instance of the ImpSubSpec.
        """
        updates = self.get_updates()
        self.update_namespace(updates, self.namespace)     
        return self
    
    def expected_items(self) -> List[str]:
        """
        Returns a list of expected names for the import.

        Returns
        -------
        List[str]
            A list of expected names for the import.
        """
        return [imp_item.varname for imp_item in self.items]    

# %% ../nbs/00_core.ipynb 25
@dataclass
class ImpSpec(ModuleSpec, BaseImp):
    """
    A class to represent an import specification.

    Attributes
    ----------
    name : str
        The name of the module to import.
    nick : Optional[str]
        An optional nickname for the module.
    lazy : Optional[bool]
        Whether to perform a lazy import. Defaults to True.
    subspecs : Optional[List[ImpSubSpec]]
        A list of sub-specifications for the import.
    fallbacks : Optional[Fallbacks]
        A mapping of fallback values for each item.
    origin : ClassVar[Optional[Any]]
        The origin of the module. Defaults to None.
    is_package : ClassVar[Optional[bool]]
        Whether the module is a package. Defaults to False.
    submodule_search_locations : ClassVar[Optional[List[str]]]
        Search locations for the submodules. Defaults to an empty list.
    """
    name: str
    nick: Optional[str] = field(default=None)
    lazy: Optional[bool] = field(default=True)
    subspecs: ImpSubSpecType = field(default_factory=list, repr=False)
    fallbacks: FallbackType = field(default_factory=dict, repr=False)

    _: KW_ONLY
    origin: ClassVar[Optional[Any]] = field(default=None, repr=False)
    is_package: ClassVar[Optional[bool]] = field(default=False, repr=False)
    submodule_search_locations: ClassVar[Optional[List[str]]] = field(default=list, repr=False)

    def _get_loader(self, spec:ModuleSpec) -> Loader:
        return loader_from_spec(spec, lazy=self.lazy)

    def __post_init__(self):
        spec = find_spec(self.name)
        loader = self._get_loader(spec)
        self.submodule_search_locations = spec.submodule_search_locations
        for subspec in self.subspecs:
            subspec.update_fallbacks(self.fallbacks, subspec.items)
            
        super().__init__(self.name, loader)
        
    def _imp_main(self):
        try:
            mod = getmodule(self.name, lazy=self.lazy, alias=self.nick, inject_both=True)
            self._module = mod

        except ImportError or ModuleNotFoundError:
            sys.modules[self.name] = self.fallbacks.get(self.name, None)
            sys.modules[self.nick] = self.fallbacks.get(self.nick, None)
            warnings.warn(f'Could not import {self.name}')
            return
        
    def _imp_subs(self):
        updates = dict()
        for subspec in self.subspecs:
            updates.update(subspec.get_updates())

        # print('updates', updates, 'fallbacks', self.fallbacks.items())
        updates = self.fallbacks.give(updates)
        # print('updates', updates, 'fallbacks', self.fallbacks.items())
        
        self._updates = updates
        self.update_namespace(updates, self.namespace)
        return updates
    
    def _import(self) -> VariableDict:
        self._imp_main()
        updates = self._imp_subs()
        self._updates = updates
        self.update_namespace(updates, self.namespace)
        return updates
    
    def all_expected_items(self):
        expected_items = []
        for subspec in self.subspecs:
            expected_items.extend(subspec.expected_items())
        return expected_items
    
    def squash_all_name_errors(self):
        for name in self.all_expected_items():
            self.squash_name_error(name)    
        return self    

# %% ../nbs/00_core.ipynb 27
@dataclass
class Imp(BaseImp):
    """
    Import Module class.
    
    This class facilitates dynamic import of modules and their attributes.
    
    Parameters
    ----------
    name : str
        The name of the module to import.
    nick : Optional[str], default=None
        The alias of the module to import.
    subspecs : Optional[List[ImpSubSpec]], default=list()
        A list of `ImpSubSpec` objects representing additional specifications for import.
    fallbacks : Optional[Dict[str, Any]], default=dict()
        A dictionary of fallback values for import failures.
    lazy : Optional[bool], default=True
        Whether or not to use lazy import.
    delay: Optional[bool], default=False
        Whether or not to delay import.

    Attributes
    ----------
    _module : Module
        The imported module.
    _spec : ImpSpec
        The specification used for import.

    Methods
    -------
    __enter__():
        Enter the runtime context for `Imp`.
    __exit__(exc_type, exc_value, traceback):
        Exit the runtime context for `Imp`.
    __getitem__(key: str) -> Any:
        Get an attribute from the imported module.
    """
    name: str
    nick: Optional[str] = field(default=None)
    subspecs: Optional[List[ImpSubSpec]] = field(default_factory=list, repr=False)
    fallbacks: Optional[Dict[str, Any]] = field(default_factory=dict, repr=False)
    lazy: Optional[bool] = field(default=True)
    delay: Optional[bool] = field(default=False)

    _ : KW_ONLY
    _module: Module = field(init=False, repr=False, default=None)
    _spec: ImpSpec = field(init=False, repr=False, default=None)
    _squash_name_errors: Optional[bool] = field(default=True)
    _reload: Optional[bool] = field(default=False)

    def _make_spec(self):
        spec = getattr(self, '_spec', None)
        if spec is not None:
            return spec
        
        spec = ImpSpec(self.name, self.nick, self.lazy, self.subspecs, self.fallbacks)
        self._spec = spec
        return spec
        
        

    def _import(self):
        self._spec = self._make_spec()

        prev = sys.modules.get(self.name, None)
        modq = getattr(self, '_module', None)
        if prev is not None:
            if modq is None:
                self._module = sys.modules[self.name]
                return self
            if not self._reload:
                return self
        
        self._updates = self._spec._import()
        self._module = sys.modules[self.name]
        self.update_namespace(self._updates, self.namespace)
        return self

    def load(self):
        self._import()
        if self._squash_name_errors:
            self.squash_all_name_errors()
        return self

    def __post_init__(self):
        if isinstance(self.fallbacks, dict):
            self.fallbacks = Fallbacks.from_dict(self.fallbacks)            
        if not self.delay:
            self.load()

    
    
    def __enter__(self):
        """
        Enter the runtime context for `Imp`.

        This method is called when the `with` statement is used with an `Imp` instance.
        """
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """
        Exit the runtime context for `Imp`.

        This method is called when exiting the `with` statement.

        Parameters
        ----------
        exc_type : Exception type
            The type of exception raised within the `with` block, if any.
        exc_value : Exception
            The instance of exception raised within the `with` block, if any.
        traceback : Traceback
            The traceback object encapsulating the call stack at the point where the exception was raised, if any.
        """
        # If you want to handle exceptions that happen inside the `with` block,
        # you can add the logic here.
        pass

    def __getitem__(self, key: str) -> Any:
        """
        Get an attribute from the imported module.

        Parameters
        ----------
        key : str
            The name of the attribute.

        Returns
        -------
        Any
            The attribute from the imported module.
        """
        return getattr(self._module, key, None)

    def squash_all_name_errors(self):
        spec = getattr(self, '_spec', None)
        if spec is None:
            spec = self._make_spec()
            self._spec = spec
        self._spec.squash_all_name_errors()
        return self

    def is_loaded(self):
        return is_mod(self._module)
    
