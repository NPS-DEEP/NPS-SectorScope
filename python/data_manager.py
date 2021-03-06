from collections import defaultdict
from math import floor
from helpers import size_string
from copy import copy
from timestamp import ts0, ts
try:
    import tkinter
except ImportError:
    import Tkinter as tkinter

class DataManager():
    """Contains calculated data and methods for calculating that data.
    """

    # change type signaled: data_changed, filter_changed
    change_type = ""

    # scan attributes
    scan_file = ""
    media_size = 0
    media_filename = ""
    hashdb_dir = ""
    sector_size = 0
    hash_block_size = 0
    media_offsets = list()
    hashes = dict()
    sources = dict()
 
    len_media_offsets = 0
    len_hashes = 0
    len_sources = 0

    # annotation
    annotatioin_types = list()
    annotations = list()
    annotation_load_status = ""

    # filters
    ignore_entropy_below = 0
    ignore_entropy_above = 0
    ignore_max_hashes = 0
    ignore_flagged_blocks = True
    ignored_sources = set()
    ignored_hashes = set()
    highlighted_sources = set()
    highlighted_hashes = set()

    def __init__(self):
        self._data_manager_changed = tkinter.BooleanVar()

    def set_data(self, data_reader):
        # copy scan attributes from data reader
        self.scan_file = data_reader.scan_file
        self.media_size = data_reader.media_size
        self.media_filename = data_reader.media_filename
        self.hashdb_dir = data_reader.hashdb_dir
        self.sector_size = data_reader.sector_size
        self.hash_block_size = data_reader.hash_block_size
        self.media_offsets = data_reader.media_offsets
        self.hashes = data_reader.hashes
        self.sources = data_reader.sources
        self.len_media_offsets = len(data_reader.media_offsets)
        self.len_hashes = len(data_reader.hashes)
        self.len_sources = len(data_reader.sources)

        # clear any filter settings
        self.ignore_entropy_below = 0
        self.ignore_entropy_above = 0
        self.ignore_max_hashes = 0
        self.ignore_flagged_blocks = True
        self.ignored_sources.clear()
        self.ignored_hashes.clear()
        self.highlighted_sources.clear()
        self.highlighted_hashes.clear()

        # annotations
        self.annotation_types = data_reader.annotation_types
        self.annotations = data_reader.annotations
        self.annotation_load_status = data_reader.annotation_load_status
        print("annotation load status:", self.annotation_load_status)

        self._fire_change("data_changed")

    def set_callback(self, f):
        """Register function f to be called on histogram mouse change."""
        self._data_manager_changed.trace_variable('w', f)

    def _fire_change(self, change_type):
        self.change_type = change_type
        self._data_manager_changed.set(True)

    # ############################################################
    # scan data
    # ############################################################
    def calculate_hash_counts(self):
        """Calculate hash counts based on identified data and filter
          settings.  Data in this hash counts map is used to calculate
          bucket data plotted in the frequency histogram.

        Returns:
          hash_counts(map<hash, (count, is_ignored, is_highlighted)>):
            Count information keyed by hash.
        """

        t0 = ts0("data_manager.calculate_hash_counts start")

        # optimization: make local references to filter variables
        ignore_entropy_below = self.ignore_entropy_below
        ignore_entropy_above = self.ignore_entropy_above
        ignore_max_hashes = self.ignore_max_hashes
        ignore_flagged_blocks = self.ignore_flagged_blocks
        ignored_sources = self.ignored_sources
        ignored_hashes = self.ignored_hashes
        highlighted_sources = self.highlighted_sources
        highlighted_hashes = self.highlighted_hashes

        # tuple counts of hashes: map<hash, (count, is_ignored, is_highlighted)>
        hash_counts = dict()

        # calculate hash_counts based on identified data
        for block_hash, hash_data in self.hashes.items():

            count = hash_data["count"]
            entropy = hash_data["k_entropy"] / 1000.0
            hash_counts[block_hash] = (
                # count
                count,

                # is_ignored
                ignore_entropy_below != 0 and entropy < ignore_entropy_below or
                ignore_entropy_above != 0 and entropy > ignore_entropy_above or
                ignore_max_hashes != 0 and count > ignore_max_hashes or
                block_hash in ignored_hashes or
                ignore_flagged_blocks and len(hash_data["block_label"]) or
                len(ignored_sources.intersection(hash_data["source_hashes"])),

                # is_highlighted
                block_hash in highlighted_hashes or
                len(highlighted_sources.intersection(
                                             hash_data["source_hashes"])))

        ts("data_manager.calculate_hash_counts done", t0)
        return hash_counts

    def calculate_bucket_data(self, hash_counts, start_offset,
                                              bytes_per_bucket, num_buckets):
        """Buckets show number of sources that map to them.
          Call _calculate_hash_counts first to define hash_counts.

        Returns:
          source_buckets(List): List of num_buckets sorce count values.
          ignored_source_buckets(List): List of num_buckets sorce count
            values.
          highlighted_source_buckets(List): List of num_buckets sorce
            count values.
        """
        t0 = ts0("data_manager.calculate_bucket_data.start")
        # initialize empty buckets for each data type tracked
        source_buckets = [0] * num_buckets
        ignored_source_buckets = [0] * num_buckets
        highlighted_source_buckets = [0] * num_buckets

        if bytes_per_bucket == 0:
            # no data
            ts("data_manager.calculate_bucket_data none", t0)
            return (source_buckets, ignored_source_buckets,
                                        highlighted_source_buckets)


        # calculate the histogram
        for offset, block_hash in self.media_offsets:
            bucket = int((offset - start_offset) // bytes_per_bucket)

            if bucket < 0 or bucket >= num_buckets:
                # offset is out of range of buckets
                continue

            # set values for buckets
            count, is_ignored, is_highlighted = hash_counts[block_hash]

            # hash and source buckets
            source_buckets[bucket] += count

            # ignored hash and source buckets
            if is_ignored:
                ignored_source_buckets[bucket] += count

            # highlighted hash and source buckets
            if is_highlighted:
                highlighted_source_buckets[bucket] += count

        ts("data_manager.calculate_bucket_data done", t0)
        return (source_buckets, ignored_source_buckets,
                highlighted_source_buckets)

    # ############################################################
    # filter actions
    # ############################################################
    def fire_filter_change(self):
        """Use this when directly changing filter state."""
        self._fire_change("filter_changed")

    def calculate_sources_and_hashes_in_range(self, start_byte, stop_byte):
        """ Calculate sources and hashes in range.
        Returns:
          sources_in_range(set): Set of source hashes in range.
          hashes_in_range(set): Set of block hashes in range.
        """
        t0 = ts0("data_manager.calculate_sources_and_hashes_in_range start")
        # clear sources and hashes in any previous range
        sources_in_range = set()
        hashes_in_range = set()

        # done if no range
        if start_byte == stop_byte or start_byte == stop_byte + 1:
            ts("data_manager.calculate_sources_and_hashes_in_range.none", t0)
            return(sources_in_range, hashes_in_range)

        # iterate through media_offsets and gather data about the range
        hashes = self.hashes
        for media_offset, block_hash in self.media_offsets:
            offset = int(media_offset)

            # skip if not in range
            if offset < start_byte or offset >= stop_byte:
                continue

            # append source hashes from this block hash to sources in range
            if not hashes[block_hash]["source_hashes"].issubset(
                                              sources_in_range):
                sources_in_range = sources_in_range.union(
                                     hashes[block_hash]["source_hashes"])

            # add block hash to hashes in range
            hashes_in_range.add(block_hash)

        ts("data_manager.calculate_sources_and_hashes_in_range done", t0)
        return(sources_in_range, hashes_in_range)

    # ignore hashes in range
    def ignore_hashes_in_range(self, start_byte, stop_byte):
        # get sources and hashes in range
        _, hashes = self.calculate_sources_and_hashes_in_range(
                                                      start_byte, stop_byte)

        # set filters based on hashes
        self.ignored_hashes = self.ignored_hashes.union(hashes)
        self.highlighted_hashes = self.highlighted_hashes.difference(hashes)

        # fire filter change
        self._fire_change("filter_changed")

    # ignore sources in range
    def ignore_sources_with_hashes_in_range(self, start_byte, stop_byte):
        sources, _ = self.calculate_sources_and_hashes_in_range(
                                                      start_byte, stop_byte)
        self.ignored_sources = self.ignored_sources.union(sources)
        self.highlighted_sources = self.highlighted_sources.difference(sources)

        # fire filter change
        self._fire_change("filter_changed")

    # clear ignored hashes
    def clear_ignored_hashes(self):
        # clear ignored hashes and signal change
        self.ignored_hashes.clear()

        # fire filter change
        self._fire_change("filter_changed")

    # clear ignored sources
    def clear_ignored_sources(self):
        # clear ignored sources and signal change
        self.ignored_sources.clear()

        # fire filter change
        self._fire_change("filter_changed")

    # highlight hashes in range
    def highlight_hashes_in_range(self, start_byte, stop_byte):
        _, hashes = self.calculate_sources_and_hashes_in_range(
                                                      start_byte, stop_byte)
        self.ignored_hashes = self.ignored_hashes.difference(hashes)
        self.highlighted_hashes = self.highlighted_hashes.union(hashes)

        # fire filter change
        self._fire_change("filter_changed")

    # highlight sources with hashes in range
    def highlight_sources_with_hashes_in_range(self, start_byte, stop_byte):
        sources, _ = self.calculate_sources_and_hashes_in_range(
                                                      start_byte, stop_byte)
        self.ignored_sources = self.ignored_sources.difference(sources)
        self.highlighted_sources = self.highlighted_sources.union(sources)

        # fire filter change
        self._fire_change("filter_changed")

    # clear highlighted hashes
    def clear_highlighted_hashes(self):
        # clear highlighted hashes and signal change
        self.highlighted_hashes.clear()

        # fire filter change
        self._fire_change("filter_changed")

    # clear highlighted sources
    def clear_highlighted_sources(self):
        # clear highlighted sources and signal change
        self.highlighted_sources.clear()

        # fire filter change
        self._fire_change("filter_changed")

    # ############################################################
    # sources list
    # ############################################################
    def calculate_sources_list(self):
        """Calculate the sources list tuple to be rendered in the
        sources table.

        Returns:
          sources_list(list<(source_hash, percent_found, text)>): List of
            tuple of sources found.
        """
        # similar to calculate_hash_counts()
        ignore_entropy_below = self.ignore_entropy_below
        ignore_entropy_above = self.ignore_entropy_above
        ignore_max_hashes = self.ignore_max_hashes
        ignore_flagged_blocks = self.ignore_flagged_blocks
        ignored_sources = self.ignored_sources
        ignored_hashes = self.ignored_hashes
        highlighted_sources = self.highlighted_sources
        highlighted_hashes = self.highlighted_hashes

        # data to calculate
        sources_offsets = defaultdict(int)
        highlighted_sources_offsets = defaultdict(int)

        # calculate the data
        for block_hash, hash_data in self.hashes.items():

            # skip ignored hashes

            # skip entropy outside range
            entropy = hash_data["k_entropy"] / 1000.0
            if ignore_entropy_below != 0 and entropy < ignore_entropy_below:
                continue
            if ignore_entropy_above != 0 and entropy > ignore_entropy_above:
                continue

            # hash count exceeds ignore_max_hashes
            if ignore_max_hashes != 0 and \
                               hash_data["count"] > ignore_max_hashes:
                continue

            # hash has entropy label flag
            if ignore_flagged_blocks and len(hash_data["block_label"]) > 0:
                continue

            # hash is in filter ignored set
            if block_hash in ignored_hashes:
                continue

            # track sources
            source_sub_counts = hash_data["source_sub_counts"]
            for source_hash, sub_count in zip(source_sub_counts[0::2],
                                              source_sub_counts[1::2]):

                # track sources not in ignored sources
                if source_hash not in ignored_sources:
                    sources_offsets[source_hash] += sub_count

                # track highlighted sources
                if block_hash in highlighted_hashes or \
                                     source_hash in highlighted_sources:
                    highlighted_sources_offsets[source_hash] += sub_count

        # now calculte the tuple of source table information

        # create a list of source information to make the sorted list from
        sources_list = list()
        _sector_size = self.sector_size
        for source_hash, source in self.sources.items():

            # compose the source text

            # calculate percent of this source file found
            file_sectors = (source["filesize"] + _sector_size - 1) // \
                                                             _sector_size

            percent_found = sources_offsets[source_hash] / \
                                                float(file_sectors) * 100

#                print ("len source: ", sources_offsets[sources], source["filesize"], int(source["filesize"]), _sector_size)

            text = '\t%.1f%%\t%d\t%d\t%s\t%s\t%s\n' \
                            %(percent_found,
                              sources_offsets[source_hash],
                              highlighted_sources_offsets[source_hash],
                              size_string(source["filesize"]),
                              source["name_pairs"][0], # just show first source
                              source["name_pairs"][1])

            # append source information tuple
            sources_list.append((source_hash, percent_found, text))

        return sources_list

