import tkinter 
from forensic_path import offset_string
from icon_path import icon_path
from tooltip import Tooltip
from offset_selection import OffsetSelection
from histogram_bar import HistogramBar

class HistogramView():
    """Renders the Image Match Histogram view.

    Attributes:
      frame(Frame): the containing frame for this view.
    """

    # pan state
    _pan_down_x = None
    _pan_down_start_offset = None

    def __init__(self, master, identified_data, filters, offset_selection,
                                                         range_selection):
        """Args:
          master(a UI container): Parent.
          identified_data(IdentifiedData): Identified data about the scan.
          filters(Filters): Filters that impact the view.
          offset_selection(OffsetSelection): The selected offset.
          range_selection(RangeSelection): The selected range.
        """

        # data variables
        self._identified_data = identified_data
        self._filters = filters
        self._offset_selection = offset_selection
        self._range_selection = range_selection

        # make the containing frame
        self.frame = tkinter.Frame(master)

        # add the title
        tkinter.Label(self.frame, text="Image Match Histogram").pack(
                                                       side=tkinter.TOP)

        # add the color legend
        legend_frame = tkinter.Frame(self.frame)
        legend_frame.pack(side=tkinter.TOP, pady=4)
        tkinter.Label(legend_frame,text="   ",background="#000066").pack(
                                                        side=tkinter.LEFT)
        tkinter.Label(legend_frame,text="All matches      ").pack(
                                                        side=tkinter.LEFT)
        tkinter.Label(legend_frame,text="   ",background="#660000").pack(
                                                        side=tkinter.LEFT)
        tkinter.Label(legend_frame,text="No filtered matches      ").pack(
                                                        side=tkinter.LEFT)
        tkinter.Label(legend_frame,text="   ",background="#004400").pack(
                                                        side=tkinter.LEFT)
        tkinter.Label(legend_frame,text="Filtered matches only").pack(
                                                        side=tkinter.LEFT)

        # create a bordered frame to contain the histogram and control buttons
        bordered_frame = tkinter.Frame(self.frame, relief=tkinter.SUNKEN, bd=1)
        bordered_frame.pack(side=tkinter.TOP)

        # add the histogram bar
        self._histogram_bar = HistogramBar(bordered_frame, identified_data,
                                 filters, offset_selection, range_selection)
        self._histogram_bar.frame.pack(side=tkinter.TOP)

        # add the frame for the button controls
        control_frame = tkinter.Frame(bordered_frame)
        control_frame.pack(side=tkinter.TOP, pady=(0,4))
        
        # pan
        self._pan_icon = tkinter.PhotoImage(file=icon_path("pan"))
        pan_button = tkinter.Button(control_frame, image=self._pan_icon, bd=0)
        pan_button.pack(side=tkinter.LEFT)
        pan_button.config(cursor="sb_h_double_arrow")
        Tooltip(pan_button, "Drag to pan")

        # bind pan control mouse events
        pan_button.bind('<Button-1>', self._handle_pan_press)
        pan_button.bind('<B1-Motion>', self._handle_pan_move)

        # zoom to fit image
        self._fit_image_icon = tkinter.PhotoImage(file=icon_path("fit_image"))
        fit_image_button = tkinter.Button(control_frame,
                                      image=self._fit_image_icon,
                                      command=self._histogram_bar.fit_image)
        fit_image_button.pack(side=tkinter.LEFT, padx=(0,8))
        Tooltip(fit_image_button, "Zoom to fit image")

        # zoom to fit range
        self._fit_range_icon = tkinter.PhotoImage(file=icon_path("fit_range"))
        self._fit_range_button = tkinter.Button(control_frame,
                                      image=self._fit_range_icon,
                                      command=self._histogram_bar.fit_range)
        self._fit_range_button.pack(side=tkinter.LEFT)
        Tooltip(self._fit_range_button, "Zoom to range")

        # filter sources in range
        self._filter_sources_in_range_icon = tkinter.PhotoImage(
                                  file=icon_path("filter_range"))
        self._filter_sources_in_range_button = tkinter.Button(control_frame,
                                  image=self._filter_sources_in_range_icon,
                                  command=self._handle_filter_sources_in_range)
        self._filter_sources_in_range_button.pack(side=tkinter.LEFT)
        Tooltip(self._filter_sources_in_range_button, "Filter sources in range")

        # filter all but sources in range
        self._filter_all_but_sources_in_range_icon = tkinter.PhotoImage(
                          file=icon_path("filter_all_but_range"))
        self._filter_all_but_sources_in_range_button = tkinter.Button(
                          control_frame,
                          image=self._filter_all_but_sources_in_range_icon,
                          command=self._handle_filter_all_but_sources_in_range)
        self._filter_all_but_sources_in_range_button.pack(side=tkinter.LEFT)
        Tooltip(self._filter_all_but_sources_in_range_button,
                          "Filter all but sources in range")

        # deselect range
        self._deselect_range_icon = tkinter.PhotoImage(
                                  file=icon_path("deselect_range"))
        self._deselect_range_button = tkinter.Button(control_frame,
                                  image=self._deselect_range_icon,
                                  command=self._handle_deselect_range)
        self._deselect_range_button.pack(side=tkinter.LEFT)
        Tooltip(self._deselect_range_button, "Deselect range")

        # register to receive range selection change events
        range_selection.set_callback(self._handle_range_selection_change)

    # this function is registered to and called by RangeSelection
    def _handle_range_selection_change(self, *args):
        if self._range_selection.is_selected:
            # button states
            self._fit_range_button.config(state=tkinter.NORMAL)
            self._filter_sources_in_range_button.config(state=tkinter.NORMAL)
            self._filter_all_but_sources_in_range_button.config(
                                                        state=tkinter.NORMAL)
            self._deselect_range_button.config(state=tkinter.NORMAL)

        else:
            # button states
            self._fit_range_button.config(state=tkinter.DISABLED)
            self._filter_sources_in_range_button.config(state=tkinter.DISABLED)
            self._filter_all_but_sources_in_range_button.config(
                                                        state=tkinter.DISABLED)
            self._deselect_range_button.config(state=tkinter.DISABLED)

    def _handle_pan_press(self, e):
        self._pan_down_x = e.x
        self._pan_down_start_offset = self._histogram_bar.start_offset

    def _handle_pan_move(self, e):
        self._histogram_bar.pan(self._pan_down_start_offset,
                                                      self._pan_down_x - e.x)

    def _handle_filter_sources_in_range(self):
        # clear existing filtered sources
        self._filters.filtered_sources.clear()

        # get start_byte and stop_byte range
        start_byte = self._range_selection.start_offset
        stop_byte = self._range_selection.stop_offset

        # get local references to identified data and filter
        hashes = self._identified_data.hashes
        filtered_sources = self._filters.filtered_sources
        
        # filter sources in range
        seen_hashes = set()
        for forensic_path, block_hash in \
                               self._identified_data.forensic_paths.items():
            offset = int(forensic_path)
            if offset >= start_byte and offset <= stop_byte:
                # hash is in range so filter its sources
                if block_hash in seen_hashes:
                    # do not reprocess this hash
                    continue

                # remember this hash
                seen_hashes.add(block_hash)

                # get sources associated with this hash
                sources = hashes[block_hash]

                # filter each source associated with this hash
                for source in sources:
                    filtered_sources.add(source["source_id"])

        # fire filter change
        self._filters.fire_change()

    def _handle_filter_all_but_sources_in_range(self):
        # start by filtering all sources
        for source_id, _ in self._identified_data.source_details.items():
            self._filters.filtered_sources.add(source_id)

        # get start_byte and stop_byte range
        start_byte = self._range_selection.start_offset
        stop_byte = self._range_selection.stop_offset

        # get local references to identified data and filter
        hashes = self._identified_data.hashes
        filtered_sources = self._filters.filtered_sources
        
        # unfilter sources in range
        seen_hashes = set()
        for forensic_path, block_hash in \
                               self._identified_data.forensic_paths.items():
            offset = int(forensic_path)
            if offset >= start_byte and offset <= stop_byte:
                # hash is in range so filter its sources
                if block_hash in seen_hashes:
                    # do not reprocess this hash
                    continue

                # remember this hash
                seen_hashes.add(block_hash)

                # get sources associated with this hash
                sources = hashes[block_hash]

                # unfilter each source associated with this hash
                for source in sources:
                    filtered_sources.discard(source["source_id"])

        # fire filter change
        self._filters.fire_change()

    def _handle_deselect_range(self):
        # deselect range
        self._range_selection.clear()

