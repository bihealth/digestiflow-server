class BaseMaskConfigException(Exception):
    """Raise if base mask for demux_reads is malformed"""

    pass


def split_bases_mask(bases_mask):
    """Parse a picard style bases mask and return a list of tuples
    >>> split_bases_mask("100T8B8B100T")
    [('T', 100), ('B', 8), ('B', 8), ('T', 100)]
    """
    splitat = []
    for i, c in enumerate(bases_mask):
        if c.isalpha():
            splitat.append(i)

    # Check that mask is well-behaved
    if splitat[0] == 0:
        raise BaseMaskConfigException("Mask must start with number of cycles, not type")
    # Check that no letters appear next to each other
    diffs = []
    for i in range(len(splitat) - 1):
        diffs.append(splitat[i + 1] - splitat[i])
    if (0 in diffs) or (1 in diffs):
        raise BaseMaskConfigException("Type characters must be separated by a number (of cycles)")

    result = []
    num = ""
    for i, _character in enumerate(bases_mask):
        if i not in splitat:
            num += bases_mask[i]
        elif int(num) == 0:
            pass
        else:
            result.append((bases_mask[i].upper(), int(num)))
            num = ""

    return result


def bases_mask_length(bases_mask):
    """Return number of bases indicated in ``bases_mask``."""

    if isinstance(bases_mask, str):
        bases_mask = split_bases_mask(bases_mask)
    return sum([count for _, count in bases_mask])


def compare_bases_mask(planned_reads, bases_mask):
    """Match user input bases mask to planned_reads from flowcell and decide if compatible.
    Return list of lists of tuples with type and number of cycles"""

    planned = split_bases_mask(planned_reads)
    mask = split_bases_mask(bases_mask)

    if not bases_mask_length(planned) == bases_mask_length(mask):
        raise BaseMaskConfigException(
            "Your base mask has more or fewer cycles than planned (%d vs. %d)"
            % (bases_mask_length(planned), bases_mask_length(mask))
        )

    matched_mask = []
    for _type, cycles in planned:
        read = []
        s = 0
        while s < cycles:
            i = mask.pop(0)
            read.append(i)
            s += i[1]
        if s > cycles:
            raise BaseMaskConfigException(
                "Your base mask has more or fewer cycles than planned for a read (%d vs. %d)"
                % (s, cycles)
            )
        matched_mask.append(read)

    return matched_mask


def translate_tuple_to_basemask(tup, demux_tool):
    """Return illumina or picard-style base mask string"""

    picard_to_illumina = {"T": "y", "S": "n", "B": "I"}

    if demux_tool == "bcl2fastq":
        return picard_to_illumina[tup[0]] + str(tup[1])
    else:
        return str(tup[1]) + tup[0]


def return_bases_mask(planned_reads, demux_reads, demux_tool="bcl2fastq"):
    """Parse planned_reads and demux_reads (user-configured base mask), compare for compatiblity
    and return a string to either give to bcl2fastq or picard"""

    if "M" in demux_reads and demux_tool == "bcl2fastq":
        raise BaseMaskConfigException("You cannot assign UMIs ('M') if using bcl2fastq")

    mask_list = compare_bases_mask(planned_reads, demux_reads)

    new_mask = []
    for lst in mask_list:
        substr = [translate_tuple_to_basemask(t, demux_tool) for t in lst]
        new_mask.append("".join(substr))
    return ",".join(new_mask) if demux_tool == "bcl2fastq" else "".join(new_mask)
