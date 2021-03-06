from helpers import size_string, offset_string
import colors
import helpers
try:
    import tkinter
except ImportError:
    import Tkinter as tkinter

class ScanStatisticsWindow():
    """Provides a window to show opened scan attributes.
    """
    def __init__(self, master, data_manager, preferences):
        """Args:
          master(a UI container): Parent.
          data_manager(DataManager): Manages scan data and filters.
         """
        # variables
        self._data_manager = data_manager
        self._preferences = preferences

        # make toplevel window
        self._root_window = tkinter.Toplevel(master)
        self._root_window.title("Scan Statistics")
        self._root_window.transient(master)
        self._root_window.protocol('WM_DELETE_WINDOW', self._hide)

        # make the containing frame
        f = tkinter.Frame(self._root_window, padx=18, pady=18,
                                                       bg=colors.BACKGROUND)
        f.pack()

        # scan file path
        self._scan_file_text = tkinter.Label(f, bg=colors.BACKGROUND)
        self._scan_file_text.pack(side=tkinter.TOP, anchor="w")

        # media image
        self._media_text = tkinter.Label(f, bg=colors.BACKGROUND)
        self._media_text.pack(side=tkinter.TOP, anchor="w")

        # media image size
        self._media_size_text = tkinter.Label(f, bg=colors.BACKGROUND)
        self._media_size_text.pack(side=tkinter.TOP, anchor="w")

        # hashdb database path
        self._database_text = tkinter.Label(f, bg=colors.BACKGROUND)
        self._database_text.pack(side=tkinter.TOP, anchor="w")

        # sector size
        self._sector_size_text = tkinter.Label(f, bg=colors.BACKGROUND)
        self._sector_size_text .pack(side=tkinter.TOP, anchor="w")

        # hash block size
        self._hash_block_size_text = tkinter.Label(f, bg=colors.BACKGROUND)
        self._hash_block_size_text .pack(side=tkinter.TOP, anchor="w")

        # matched paths
        self._matched_paths_text = tkinter.Label(f, bg=colors.BACKGROUND)
        self._matched_paths_text .pack(side=tkinter.TOP, anchor="w")

        # matched hashes
        self._matched_hashes_text = tkinter.Label(f, bg=colors.BACKGROUND)
        self._matched_hashes_text .pack(side=tkinter.TOP, anchor="w")

        # matched sources
        self._matched_sources_text = tkinter.Label(f, bg=colors.BACKGROUND)
        self._matched_sources_text .pack(side=tkinter.TOP, anchor="w")

        # register to receive data manager change events
        data_manager.set_callback(self._handle_data_manager_change)

        # register to receive preferences change events
        preferences.set_callback(self._handle_data_manager_change)

        # set initial state
        self._handle_data_manager_change()

        # start with window hidden
        self._root_window.withdraw()

    def _round_up_to_block(self, size):
        sector_size = self._data_manager.sector_size
        if sector_size == 0:
            return 0
        if size % sector_size == 0:
            return size
        return size + sector_size - (size % sector_size)

    # this function is registered to and called by IdentifiedData
    def _handle_data_manager_change(self, *args):
        if self._data_manager.media_filename:
            # data_manager opened
            self._scan_file_text["text"] = 'Scan file: %s' % \
                               self._data_manager.scan_file
            self._media_text["text"] = 'Media: %s' % \
                               self._data_manager.media_filename
            self._media_size_text["text"] = 'Media size: %s  (%s)' % (
                               size_string(self._data_manager.media_size),
                               offset_string(self._round_up_to_block(
                                             self._data_manager.media_size),
                                      self._preferences.offset_format,
                                      self._data_manager.sector_size))
            self._database_text["text"] = 'Database: %s' % \
                               self._data_manager.hashdb_dir
            self._sector_size_text["text"] = 'Sector size: %s' % (
                                      self._data_manager.sector_size)
            self._hash_block_size_text["text"] = 'Hash block size: %s' % (
                                      self._data_manager.hash_block_size)
            self._matched_paths_text["text"] = 'Matched paths: %s' % (
                                      self._data_manager.len_media_offsets)
            self._matched_hashes_text["text"] = 'Matched hashes: %s' % (
                                      self._data_manager.len_hashes)
            self._matched_sources_text["text"] = 'Matched sources: %s' % (
                                      self._data_manager.len_sources)

        else:
            # data_manager not opened
            self._scan_file_text["text"] = 'Scan file: Not opened'
            self._media_text["text"] = 'Media: Not opened'
            self._media_size_text["text"] = 'Media size: Not opened'
            self._database_text["text"] = 'Database: Not opened'
            self._sector_size_text["text"] = 'Sector size: Not opened'
            self._hash_block_size_text["text"] = 'Hash block size: Not opened'
            self._matched_paths_text["text"] = 'Matched paths: Not opened'
            self._matched_hashes_text["text"] = 'Matched hashes: Not opened'
            self._matched_sources_text["text"] = 'Matched sources: Not opened'

    def show(self):
        self._root_window.deiconify()
        self._root_window.lift()

    def _hide(self):
        self._root_window.withdraw()

