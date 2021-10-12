import glob
import os
import sys
import pandas

from mass_spec_utils.data_import.mzml import MZMLFile
from pandas import DataFrame
from evaluate import topn_evaluate

TABLE_HEADS = ['N', 'Nscans', 'Nscans_MS1', 'Nscans_MS2', 'Scans per sec', 'First MS2',
               'First MS2 block', 'Evaluation']


def get_summary(mzml_file_path):
    summary = {}
    mzml_file = MZMLFile(mzml_file_path)
    scan_sub = mzml_file.scans

    # find the first block of ms2 scans
    pos = 0
    while pos < len(scan_sub) and scan_sub[pos].ms_level == 1:
        pos += 1
    start_pos = pos

    while pos < len(scan_sub) and scan_sub[pos].ms_level == 2:
        pos += 1
    end_pos = pos

    summary['N'] = end_pos - start_pos
    summary['First MS2'] = start_pos
    summary['First MS2 block'] = end_pos - start_pos
    summary['Nscans'] = len(scan_sub)
    summary['Scans per sec'] = len(scan_sub) / (scan_sub[-1].rt_in_seconds - scan_sub[0].rt_in_seconds)

    ms1_scans = list(filter(lambda x: x.ms_level == 1, scan_sub))
    ms2_scans = list(filter(lambda x: x.ms_level == 2, scan_sub))
    summary['Nscans_MS1'] = len(ms1_scans)
    summary['Nscans_MS2'] = len(ms2_scans)

    counts = topn_evaluate(mzml_file_path)
    summary['Evaluation'] = counts

    return summary

def make_dataframe(file_list, heads=TABLE_HEADS):
    summaries = []
    for mzml_file_path in file_list:
        summary = get_summary(mzml_file_path)
        row = []
        for head in heads:
            row.append(summary[head])
        summaries.append(row)
    df = DataFrame(summaries, columns=heads)
    return df

def make_table(mzml_path):
    if os.path.isdir(mzml_path):
        file_list = glob.glob(os.path.join(mzml_path, '*.mzML'))
        summary_table = make_dataframe(file_list)
    else:
        summary_table = make_dataframe([mzml_path])
    return summary_table