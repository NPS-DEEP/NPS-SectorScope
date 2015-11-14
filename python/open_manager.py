from error_window import ErrorWindow
try:
    import tkinter
    import tkinter.filedialog as fd
except ImportError:
    import Tkinter as tkinter
    import tkFileDialog as fd

class OpenManager():
    """Opens a bulk_extractor directory, sets data, and fires events.

    Attributes:
      frame(Frame): The containing frame for this view.
    """

    def __init__(self, master, data_manager, annotation_filter,
                 histogram_control, preferences):
        """Args:
          master(a UI container): Parent.
          data_manager(DataManager): Manages project data and filters.
          histogram_control(HistogramControl): Interfaces for controlling
            the histogram view.
           preferences(Preferences): Preference, namely the offset format.
        """

        # local references
        self._master = master
        self._data_manager = data_manager
        self._annotation_filter = annotation_filter
        self._histogram_control = histogram_control
        self._preferences = preferences

    """Open be_dir or if not be_dir open be_dir from chooser."""
    def open_be_dir(self, be_dir):
        if not be_dir:
            # get be_dir from chooser
            be_dir = fd.askdirectory(
                     title="Open bulk_extractor directory",
                     mustexist=True, initialdir=self._data_manager.be_dir)

        if not be_dir:
            # user did not choose, so abort
            return

        # read be_dir else show error window
        try:
            self._data_manager.read(be_dir)

        except Exception as e:
            ErrorWindow(self._master, "Open Error", e)
            return

        # clear annotation filter settings
        self._annotation_filter.set([])

        # clear any byte range selection
        self._histogram_control.clear_range()

        # reset preferences
        self._preferences.reset()

        # report if annotation reader failed
        if self._data_manager.annotation_load_status:
            ErrorWindow(self._master, "Annotation Read Error",
                              "Unable to read media image annotations.\n"
                              "Please check that TSK is installed "
                              "and that PATH is set.\n%s" % self._data_manager.annotation_load_status)

