#!/bin/bash

# Script to generate fake BCL folder, based on Illumina's mkdata.sh from
# bcl2fastq v2.20.

# ---------------------------------------------------------------------------
# Preamble
# ---------------------------------------------------------------------------

# Inofficial Bash strict mode

set -euo pipefail

# Control verbosity / quietness

# Ensure that $QUIET and $VERBOSE are set or initialized with normal
# verbosity.
QUIET=${QUIET-0}
VERBOSE=${VERBOSE-0}

# Print commands back to user if in verbose mode.
if [[ $VERBOSE -eq 1 ]]; then
    set -x
fi


# ---------------------------------------------------------------------------
# Function print_sample_sheet()
# ---------------------------------------------------------------------------
#
# Print sample sheet to stdout.

print_sample_sheet()
{
cat <<-"EOF"
[Header],,,,
Investigator Name,Isabelle,,,
Project Name,Nova,,,
Experiment Name,Orbital death ray research volume LXXIV,,,
Date,5/27/2025,,,
Workflow,GenerateFASTQ,,,
,,,,
[Settings],,,,
MaskAdapter,CGCGTATACGCGTATA,,,
TrimAdapter,GCGCATATGCGCATAT,,,
,,,,
[Data],,,,
SampleID,SampleName,index,index2
AA,AA,AAAAAAAA,AAAAAAAA
CC,CC,CCCCCCCC,CCCCCCCC
GG,GG,GGGGGGGG,GGGGGGGG
TT,TT,TTTTTTTT,TTTTTTTT
XX,XX,ACGTACGT,ACGTACGT
EOF
}

# ---------------------------------------------------------------------------
# Function print_run_info_xml()
# ---------------------------------------------------------------------------
#
# Print run info XML

print_run_info_xml()
{
cat <<-"EOF"
<?xml version="1.0"?>
<RunInfo xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" Version="2">
  <Run Id="130820_CSSIM_0123_B_TESTEST_Fake_Data" Number="42">
    <Flowcell>TESTEST</Flowcell>
    <Instrument>CSSIM</Instrument>
    <Date>8/20/2013 3:29:17 PM</Date>
    <Reads>
      <Read Number="1" NumCycles="92" IsIndexedRead="N" />
      <Read Number="2" NumCycles="8" IsIndexedRead="Y" />
      <Read Number="3" NumCycles="8" IsIndexedRead="Y" />
      <Read Number="4" NumCycles="92" IsIndexedRead="N" />
    </Reads>
    <FlowcellLayout LaneCount="1" SurfaceCount="2" SwathCount="3" TileCount="6" SectionPerLane="3" LanePerSection="2" />
  </Run>
</RunInfo>
EOF
}

# ---------------------------------------------------------------------------
# Function print_run_paramters_xml()
# ---------------------------------------------------------------------------
#
# Print run parameters XML

print_run_parameters_xml()
{
cat <<-"EOF"
<?xml version="1.0"?>
<RunParameters xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <Setup>
    <Read1>92</Read1>
    <IndexRead1>8</IndexRead1>
    <IndexRead2>8</IndexRead2>
    <Read2>92</Read2>
    <RTAVersion>2.7.7</RTAVersion>
    <FCPosition>B</FCPosition>
    <ScanNumber>123</ScanNumber>
    <ExperimentName>Fake_Data</ExperimentName>
    <Reads>
      <Read Number="1" NumCycles="92" IsIndexedRead="N" />
      <Read Number="2" NumCycles="8" IsIndexedRead="Y" />
      <Read Number="3" NumCycles="8" IsIndexedRead="Y" />
      <Read Number="4" NumCycles="92" IsIndexedRead="N" />
    </Reads>
  </Setup>
  <Version>1</Version>
</RunParameters>
EOF
}

# ---------------------------------------------------------------------------
# Print config_xml()
# ---------------------------------------------------------------------------
#
# Print configuration XML

print_config_xml()
{
cat <<-"EOF"
<?xml version="1.0" encoding="utf-8"?>
<BaseCallAnalysis xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <Run Name="BaseCalls">
    <TileSelection>
      <Lane Index="1">
        <Tile>1</Tile>
        <Tile>2</Tile>
      </Lane>
    </TileSelection>
  </Run>
</BaseCallAnalysis>
EOF
}

# ---------------------------------------------------------------------------
# Function create_fake_directory()
# ---------------------------------------------------------------------------
#
# Create the fake directory.

create_fake_directory()
(
    # Set variables for code from Illumina script from command line arguments.
    cycles_count=$((2 * $cycles_template + 2 * $cycles_barcode))
    cycle_index_start=$(($cycles_template - $cycles_barcode))
    cycle_index_end=$(($cycles_template + $cycles_barcode))

    # Setup auto-cleaned temporary directory
    export TMPDIR=$(mktemp -d)
    trap "rm -rf $TMPDIR" EXIT

    # Only create lane 1, create output directory
    mkdir -p $out_dir/Data/Intensities/{BaseCalls/,}L001

    # Go into output directory
    pushd $out_dir

    # Set various path variables
    tmp_bcl_filename=$TMPDIR/tmp.bci
    bci_filename='./Data/Intensities/BaseCalls/L001/s_1.bci'
    locs_filename='./Data/Intensities/L001/s_1.locs'
    filter_filename='./Data/Intensities/BaseCalls/L001/s_1.filter'
    rm -f "$bci_filename"

    # Generate lane cycle by cycle
    for cycle_no in $(seq 1 $cycles_count); do
        >&2 echo "Generating cycle: $cycle_no"

        if [[ $aggregate_tiles -eq 1 ]]; then
            bcl_filename=`printf './Data/Intensities/BaseCalls/L001/%04u.bcl.bgzf' $cycle_no`
            printf '0: %.8x' $clusters_count | sed -E 's/0: (..)(..)(..)(..)/0: \4\3\2\1/' | xxd -r -g0 > "$tmp_bcl_filename"
            gzip "$tmp_bcl_filename"
            cat "$tmp_bcl_filename.gz" > "$bcl_filename"
            rm "$tmp_bcl_filename.gz"

            if [[ $cycle_no -eq 1 ]]; then
                printf '0: 010000000000803f' | xxd -r -g0 > "$locs_filename"
                printf '0: %.8x' $clusters_count | sed -E 's/0: (..)(..)(..)(..)/0: \4\3\2\1/' | xxd -r -g0 >> "$locs_filename"

                printf '0: 0000000003000000' | xxd -r -g0 > "$filter_filename"
                printf '0: %.8x' $clusters_count | sed -E 's/0: (..)(..)(..)(..)/0: \4\3\2\1/' | xxd -r -g0 >> "$filter_filename"
            fi
        else
            bcl_dir=`printf './Data/Intensities/BaseCalls/L001/C%d.1/' $cycle_no`
            mkdir -p "$bcl_dir"
        fi

        tile_idx=0
        cluster_idx=0
        clusters_on_current_tile=3
        while [[ $cluster_idx -lt $clusters_count ]]; do
            tile_cluster_idx=0
            while [[ $cluster_idx -lt $clusters_count ]] && [[ $tile_cluster_idx -lt $clusters_on_current_tile ]]; do
                if [[ $cycle_no -ge $cycle_index_start ]] && [[ $cycle_no -le $cycle_index_end ]]; then
                    base=$(($cluster_idx % 4))
                    quality=0x3F
                else
                    base=$(($(($cluster_idx + $cycle_no - 1)) % 0x04))
                    quality=$(($(($cluster_idx + $cycle_no - 1)) % 0x3F))
                fi
                printf '0: %.2x' $(($(($quality << 2)) | $base)) | xxd -r -g0 >> "$tmp_bcl_filename"

                if [[ $cycle_no -eq 1 ]]; then
                    printf '0: cdcc8c3f9a99993f' | xxd -r -g0 >> "$locs_filename"
                    filter=1;
                    if [[ $(($cluster_idx % 8)) -eq 0 ]] || [[ $(($cluster_idx % 4)) -eq 3 ]]; then
                            filter=0;
                    fi
                    printf '0: %.2x' $filter | xxd -r -g0 >> "$filter_filename"
                    #printf '0: 01' | xxd -r -g0 >> "$filter_filename"
                fi

                tile_cluster_idx=$(($tile_cluster_idx + 1))
                cluster_idx=$(($cluster_idx + 1))
            done
            if [[ $aggregate_tiles -eq 1 ]]; then
                gzip "$tmp_bcl_filename"
                cat "$tmp_bcl_filename.gz" >> "$bcl_filename"
                rm "$tmp_bcl_filename.gz"
            else
                tile_number=$(($tile_idx + 1))
                bcl_filename=`printf '%s/s_1_%d.bcl.gz' $bcl_dir $tile_number`
                printf '0: %.8x' $tile_cluster_idx | sed -E 's/0: (..)(..)(..)(..)/0: \4\3\2\1/' | xxd -r -g0 > "$tmp_bcl_filename.h"
                cat "$tmp_bcl_filename" >> "$tmp_bcl_filename.h"
                rm "$tmp_bcl_filename"
                gzip "$tmp_bcl_filename.h"
                cat "$tmp_bcl_filename.h.gz" > "$bcl_filename"
                rm "$tmp_bcl_filename.h.gz"

                if [[ $cycle_no -eq 1 ]]; then
                    correct_filter_filename=`printf "./Data/Intensities/BaseCalls/L001/s_1_%d.filter" $tile_number`
                    printf '0: %.8x' $tile_cluster_idx | sed -E 's/0: (..)(..)(..)(..)/0: \4\3\2\1/' | xxd -r -g0 > "$correct_filter_filename"
                    cat "$filter_filename" >> "$correct_filter_filename"
                    rm "$filter_filename"

                    correct_locs_filename=`printf "./Data/Intensities/L001/s_1_%d.locs" $tile_number`
                    printf '0: 01000000 0000803f' | xxd -r -g0 > "$correct_locs_filename"
                    printf '0: %.8x' $tile_cluster_idx | sed -E 's/0: (..)(..)(..)(..)/0: \4\3\2\1/' | xxd -r -g0 >> "$correct_locs_filename"
                    cat "$locs_filename" >> "$correct_locs_filename"
                    rm "$locs_filename"
                fi
            fi

            tile_idx=$(($tile_idx + 1))
            if [[ $cycle_no -eq 1 ]] && [[ $write_bci -eq 1 ]]; then
                printf '0: %.8x' $tile_idx | sed -E 's/0: (..)(..)(..)(..)/0: \4\3\2\1/' | xxd -r -g0 >> "$bci_filename"
                printf '0: %.8x' $tile_cluster_idx | sed -E 's/0: (..)(..)(..)(..)/0: \4\3\2\1/' | xxd -r -g0 >> "$bci_filename"
            fi

            clusters_on_current_tile=$(($clusters_on_current_tile * 3))
        done
    done
)

# ---------------------------------------------------------------------------
# Function print_help()
# ---------------------------------------------------------------------------
#
# Print help screen to stderr.

print_help()
{
    >&2 echo "USAGE: fake-bcl-folder.sh [options] {hiseq|novaseq} <directory>"
    >&2 echo ""
    >&2 echo "Options"
    >&2 echo ""
    >&2 echo "  -h                 display this help"
    >&2 echo "  -t [cycles]        length of template reads to simulate"
    >&2 echo "  -b [cycles]        number of barcode cycles to simulate"
    >&2 echo "  -c [clusters]      number of clusters to simulate"
    >&2 echo ""
    >&2 echo ""
    >&2 echo "Arguments"
    >&2 echo ""
    >&2 echo "  {hiseq|novaseq}    Create fake HiSeq or NovaSeq folder"
    >&2 echo "  <directory>        Path to directory to create; follow the"
    >&2 echo "                     Illumina flow cell names for correct"
    >&2 echo "                     creation of XML files etc."
    >&2 echo ""
    >&2 echo "The following environment variables are interpreted (default):"
    >&2 echo ""
    >&2 echo "  QUIET   (0)        Quiet mode"
    >&2 echo "  VERBOSE (0)        Verbose mode, mostly useful for debugging"
    >&2 echo ""
    >&2 echo "This code is based on the mkdata.sh script shipped with"
    >&2 echo "Illumina's bcl2fastq.  The output will have the following"
    >&2 echo "properties:"
    >&2 echo ""
    >&2 echo "- clusters are assigned to samples A,C,G,T periodically and in"
    >&2 echo "  this order"
    >&2 echo "- all clusters for samples C and G have filter flag set to true"
    >&2 echo "- all clusters for sample T have filter flag set to false"
    >&2 echo "- filter flag for clusters of sample A is alternating between"
    >&2 echo "  true and false periodically"
    >&2 echo "- there are 10000 clusters on 9 tiles"
    >&2 echo "- tiles contain following number of clusters: 3,9,27,81,etc. "
    >&2 echo "  (since 10000 is not divisible by 3, 9th tile contains only"
    >&2 echo "  160 clusters)"
    >&2 echo "- sample sheet, runinfo XML and config XML (last one only for "
    >&2 echo "  hiseq/miseq) need to be created by hand (examples below are "
    >&2 echo "  compatible with above described data)"
}

# ---------------------------------------------------------------------------
# Program entry point.
# ---------------------------------------------------------------------------

# Number of template cycles
cycles_template=100
# Number of barcode cycles
cycles_barcode=8
# Number of clusters
clusters_count=10000

# Parse command line options
while getopts ":ht:b:c:" opt; do
  echo opt=$opt
  case $opt in
    h)
      print_help
      exit 0
      ;;
    t)
      cycles_template=$OPTARG
      ;;
    b)
      cycles_barcode=$OPTARG
      ;;
    c)
      clusters_count=$OPTARG
      ;;
    \?)
      echo "Invalid option: -$OPTARG" >&2
      exit 1
      ;;
  esac
done
shift $((OPTIND-1))

# Get positional argument #1
if [[ $# -eq 0 ]]; then
    >&2 echo "ERROR: No machine model given!"
    >&2 echo
    print_help
    exit 1
elif [[ $1 != "hiseq" ]] && [[ $1 != "novaseq" ]]; then
    >&2 echo "ERROR: Invalid machine model $1!"
    >&2 echo
    print_help
    exit 1
fi

model=$1
[[ $QUIET -ne 0 ]] || >&2 echo "Machine model is $model"
if [[ $model == hiseq ]]; then
    aggregate_tiles=0
    # bci => nextseq
    write_bci=0
else
    aggregate_tiles=1
    # bci => nextseq
    write_bci=0
fi
shift

# Get positional argument #2
if [[ $# -eq 0 ]]; then
    >&2 echo "ERROR: No output directory given!"
    >&2 echo
    print_help
    exit 1
fi

out_dir=$1
[[ $QUIET -ne 0 ]] || >&2 echo "Output directory is $out_dir"
shift

# Guard against too many positional arguments
if [[ $# -gt 0 ]]; then
    >&2 echo "Too many arguments: $*"
    >&2 echo
    print_help
    exit 1
fi

if [[ $QUIET -eq 0 ]]; then
    >&2 echo "template cycles:   $cycles_template"
    >&2 echo "barcode cycles:    $cycles_barcode"
    >&2 echo "cluster count:     $clusters_count"
    >&2 echo "tile aggregation:  $aggregate_tiles"
fi

# Guard against overwriting anything
if [[ -e $out_dir ]]; then
    >&2 echo "Cowardly refusing to overwrite $out_dir which already exists."
    exit 1
fi

mkdir -p $out_dir

print_run_info_xml > $out_dir/RunInfo.xml
if [[ $model == hiseq ]]; then
    print_run_parameters_xml > $out_dir/runParameters.xml
    mkdir -p $out_dir/Data/Intensities/BaseCalls
    print_config_xml >$out_dir/Data/Intensities/BaseCalls/config.xml
else
    print_run_parameters_xml > $out_dir/RunParameters.xml
fi

create_fake_directory

exit 0

