from abc import ABC, abstractmethod


#: Lists of field names for tuples returned by Backend API methods.
FIELDS = {
    'get_nodes': ('region', 'mapped_to', 'parent', 'hierarchy'),
    'get_scenarios': ('model', 'scenario', 'scheme', 'is_default',
                      'is_locked', 'cre_user', 'cre_date', 'upd_user',
                      'upd_date', 'lock_user', 'lock_date', 'annotation',
                      'version'),
    'ts_get': ('region', 'variable', 'unit', 'year', 'value'),
    'ts_get_geo': ('region', 'variable', 'time', 'year', 'value', 'unit',
                   'meta'),
}


class Backend(ABC):
    """Abstract base class for backends."""
    # NB non-abstract methods like close_db() are marked '# pragma: no cover'.
    #    In order to cover these with tests, define a MemoryBackend or similar
    #    that provides implementations of all the abstract methods but does
    #    NOT override the non-abstract methods; then call those.

    def __init__(self):  # pragma: no cover
        """Initialize the backend."""
        pass

    def close_db(self):  # pragma: no cover
        """OPTIONAL: Close database connection(s).

        Close any database connection(s), if open.
        """
        pass

    def get_auth(self, user, models, kind):  # pragma: no cover
        """OPTIONAL: Return user authorization for *models*.

        If the Backend implements access control,

        Parameters
        ----------
        user : str
            User name or identifier.
        models : list of str
            Model names.
        kind : str
            Type of permission being requested

        Returns
        -------
        dict
            Mapping of `model name (str)` → `bool`; :obj:`True` if the user is
            authorized for the model.
        """
        return {model: True for model in models}

    @abstractmethod
    def get_nodes(self):
        """Iterate over all nodes stored on the Platform.

        Yields
        -------
        tuple
            The members of each tuple are:

            ========= =========== ===
            ID        Type        Description
            ========= =========== ===
            region    str         Node name or synonym for node
            mapped_to str or None Node name
            parent    str         Parent node name
            hierarchy str         Node hierarchy ID
            ========= =========== ===
        """

    @abstractmethod
    def get_scenarios(self, default, model, scenario):
        """Iterate over TimeSeries stored on the Platform.

        Scenarios, as subclasses of TimeSeries, are also included.

        Parameters
        ----------
        default : bool
           :obj:`True` to include only TimeSeries versions marked as default.
        model : str or None
           Model name to filter results.
        scenario : str or None
           Scenario name to filter results.

        Yields
        ------
        tuple
            The members of each tuple are:

            ========== ==== ===
            ID         Type Description
            ========== ==== ===
            model      str  Model name.
            scenario   str  Scenario name.
            scheme     str  Scheme name.
            is_default bool :obj:`True` if `version` is the default.
            is_locked  bool :obj:`True` if read-only.
            cre_user   str  Name of user who created the TimeSeries.
            cre_date   str  Creation datetime.
            upd_user   str  Name of user who last modified the TimeSeries.
            upd_date   str  Modification datetime.
            lock_user  str  Name of user who locked the TimeSeries.
            lock_date  str  Lock datetime.
            annotation str  Description of the TimeSeries.
            version    int  Version.
            ========== ==== ===
        """

    @abstractmethod
    def get_units(self):
        """Return all registered units of measurement.

        Returns
        -------
        list of str
        """

    def open_db(self):  # pragma: no cover
        """OPTIONAL: (Re-)open database connection(s).

        A backend MAY connect to a database server. This method opens the
        database connection if it is closed.
        """
        pass

    def set_log_level(self, level):  # pragma: no cover
        """OPTIONAL: Set logging level for the backend and other code.

        Parameters
        ----------
        level : int or Python logging level
        """
        pass

    @abstractmethod
    def set_node(self, name, parent=None, hierarchy=None, synonym=None):
        """Add a node name to the Platform.

        This method MUST be callable in one of two ways:

        - With `parent` and `hierarchy`: `name` is added as a child of `parent`
          in the named `hierarchy`.
        - With `synonym`: `synonym` is added as an alias for `name`.

        Parameters
        ----------
        name : str
           Node name.
        parent : str, optional
           Parent node name.
        hierarchy : str, optional
           Node hierarchy ID.
        synonym : str, optional
           Synonym for node.
        """

    @abstractmethod
    def set_unit(self, name, comment):
        """Add a unit of measurement to the Platform.

        Parameters
        ----------
        name : str
            Symbol of the unit.
        comment : str
            Description of the change.
        """

    # Methods for ixmp.TimeSeries

    @abstractmethod
    def ts_init(self, ts, annotation=None):
        """Initialize the TimeSeries *ts*.

        The method MAY:

        - Modify the version attr of the returned object.
        """

    @abstractmethod
    def ts_check_out(self, ts, timeseries_only):
        """Check out *ts* for modifications.

        Parameters
        ----------
        timeseries_only : bool
            ???
        """

    @abstractmethod
    def ts_commit(self, ts, comment):
        """Commit changes to *ts*.

        The method MAY:

        - Modify the version attr of *ts*.
        """

    @abstractmethod
    def ts_get(self, ts, region, variable, unit, year):
        """Retrieve time-series data.

        Parameters
        ----------
        region : list of str
        variable : list of str
        unit : list of str
        year : list of str

        Yields
        ------
        tuple
            The five members of each tuple are:

            1. region: str.
            2. variable: str.
            3. unit: str.
            4. year: int.
            5. value: float.
        """

    @abstractmethod
    def ts_get_geo(self, ts):
        """Retrieve time-series 'geodata'.

        Yields
        ------
        tuple
            The seven members of each tuple are:

            1. region: str.
            2. variable: str.
            3. time: str.
            4. year: int.
            5. value: str.
            6. unit: str.
            7. meta: int.
        """

    @abstractmethod
    def ts_set(self, ts, region, variable, data, unit, meta):
        """Store *data* in *ts*.

        Parameters
        ----------
        region, variable, time, unit : str
            Indices for the data.
        data : dict (int -> float)
            Mapping from year to value.
        meta : bool
            Metadata flag.
        """

    @abstractmethod
    def ts_set_geo(self, ts, region, variable, time, year, value, unit, meta):
        """Store time-series 'geodata'.

        Parameters
        ----------
        region, variable, time, unit : str
            Indices for the data.
        year : int
            Year index.
        value : str
            Data.
        meta : bool
            Metadata flag.
        """

    @abstractmethod
    def ts_delete(self, ts, region, variable, years, unit):
        """Remove data values from *ts*."""

    @abstractmethod
    def ts_delete_geo(self, ts, region, variable, time, years, unit):
        """Remove 'geodata' values from *ts*."""

    @abstractmethod
    def ts_discard_changes(self, ts):
        """Discard changes to *ts* since the last commit."""

    @abstractmethod
    def ts_set_as_default(self, ts):
        """Set *ts* as the default version."""

    @abstractmethod
    def ts_is_default(self, ts):
        """Return :obj:`True` if *ts* is the default version.

        Returns
        -------
        bool
        """

    @abstractmethod
    def ts_last_update(self, ts):
        """Return the date of the last modification of the *ts*."""

    @abstractmethod
    def ts_run_id(self, ts):
        """Return the run ID for the *ts*."""

    def ts_preload(self, ts):  # pragma: no cover
        """OPTIONAL: Load *ts* data into memory."""
        pass

    # Methods for ixmp.Scenario

    @abstractmethod
    def s_clone(self, s, target_backend, model, scenario, annotation,
                keep_solution, first_model_year=None):
        """Clone *s*.

        Parameters
        ----------
        target_backend : :class:`ixmp.backend.base.Backend`
            Target backend. May be the same as `s.platform._backend`.
        model : str
        scenario : str
        annotation : str
        keep_solution : bool
        first_model_year : int or None
        """

    @abstractmethod
    def s_init(self, s, annotation=None):
        """Initialize the Scenario *s*.

        The method MAY:

        - Modify the version attr of the returned object.
        """

    @abstractmethod
    def s_has_solution(self, s):
        """Return :obj:`True` if Scenario *s* has been solved.

        If :obj:`True`, model solution data is available from the Backend.
        """

    @abstractmethod
    def s_list_items(self, s, type):
        """Return a list of items of *type* in Scenario *s*."""

    @abstractmethod
    def s_init_item(self, s, type, name):
        """Initialize an item *name* of *type* in Scenario *s*."""

    @abstractmethod
    def s_delete_item(self, s, type, name):
        """Remove an item *name* of *type* in Scenario *s*."""

    @abstractmethod
    def s_item_index(self, s, name, sets_or_names):
        """Return the index sets or names of item *name*.

        Parameters
        ----------
        sets_or_names : 'sets' or 'names'
        """

    @abstractmethod
    def s_item_elements(self, s, type, name, filters=None, has_value=False,
                        has_level=False):
        """Return elements of item *name* in Scenario *s*.

        The return type varies according to the *type* and contents:

        - Scalars vs. parameters.
        - Lists, e.g. set elements.
        - Mapping sets.
        - Multi-dimensional parameters, equations, or variables.
        """
        # TODO exactly specify the return types in the docstring using MUST,
        # MAY, etc. terms

    @abstractmethod
    def s_add_set_elements(self, s, name, elements):
        """Add elements to set *name* in Scenario *s*.

        Parameters
        ----------
        elements : iterable of 2-tuples
            The tuple members are, respectively:

            1. Key: str or list of str. The number and order of key dimensions
               must match the index of *name*, if any.
            2. Comment: str or None. An optional description of the key.

        Raises
        ------
        ValueError
            If *elements* contain invalid values, e.g. for an indexed set,
            values not in the index set(s).
        Exception
            If the Backend encounters any error adding the key.
        """

    @abstractmethod
    def s_add_par_values(self, s, name, elements):
        """Add values to parameter *name* in Scenario *s*.

        Parameters
        ----------
        elements : iterable of 4-tuples
            The tuple members are, respectively:

            1. Key: str or list of str or (for a scalar, or 0-dimensional
               parameter) None.
            2. Value: float.
            3. Unit: str or None.
            4. Comment: str or None.

        Raises
        ------
        ValueError
            If *elements* contain invalid values, e.g. key values not in the
            index set(s).
        Exception
            If the Backend encounters any error adding the parameter values.
        """

    @abstractmethod
    def s_item_delete_elements(self, s, type, name, key):
        """Remove elements of item *name*."""

    @abstractmethod
    def s_get_meta(self, s):
        """Return all metadata."""

    @abstractmethod
    def s_set_meta(self, s, name, value):
        """Set a single metadata key."""

    @abstractmethod
    def s_clear_solution(self, s, from_year=None):
        """Remove data associated with a model solution."""

    # Methods for message_ix.Scenario

    @abstractmethod
    def ms_cat_list(self, ms, name):
        """Return list of categories."""

    @abstractmethod
    def ms_cat_get_elements(self, ms, name, cat):
        """Get elements of a category mapping."""

    @abstractmethod
    def ms_cat_set_elements(self, ms, name, cat, keys, is_unique):
        """Add elements to category mapping."""

    @abstractmethod
    def ms_year_first_model(self, ms):
        """Return the first model year."""

    @abstractmethod
    def ms_years_active(self, ms, node, tec, year_vintage):
        """Return a list of years in which *tec* is active."""
