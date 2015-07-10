import tkinter 
from scrolled_canvas import ScrolledCanvas

class SourcesView():
    """Manages the view for the list of matched sources.

    Attributes:
      frame(Frame): the containing frame for this view.
      _max_hashes_trace_var (IntVar): Update view on change.
      _skip_flagged_blocks_trace_var (IntVar): Update view on change.
    """

    def __init__(self, master, identified_data, trace_vars=[]):
        """Args:
          master(a UI container): Parent.
          identified_data(IdentifiedData): All data related to the block
            hash scan.
          trace_vars (list of trace vars): Update views when anything changes.
        """

        # make the containing frame
        self.frame = tkinter.Frame(master)

        # add the header text
        tkinter.Label(self.frame, text='Matched Sources') \
                                            .pack(side=tkinter.TOP)

        # make the frame to hold the canvas
        canvas_frame = tkinter.Frame(self.frame, bd=1, relief=tkinter.SUNKEN)
        canvas_frame.pack()

        # add the sources frame to contain the scrollable source list
        SOURCE_PIXEL_HEIGHT = 32
        frame_height = len(identified_data.identified_sources) * \
                                                SOURCE_PIXEL_HEIGHT
        sources_canvas = ScrolledCanvas(canvas_frame,
                              canvas_width=400, canvas_height=800,
                              frame_width=600, frame_height=frame_height)
        sources_frame = sources_canvas.scrolled_frame

        tkinter.Label(sources_frame, text="[TBD]").pack()


    def _handle_remove_hash(self):
        # TBD
        print("handle_remove_hash, TBD")

    def _handle_hash_detail(self):
        # TBD
        print("handle_hash_detail, TBD")
