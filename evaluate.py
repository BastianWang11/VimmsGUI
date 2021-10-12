import streamlit as st
import glob
import os
import xml.etree.ElementTree

from loguru import logger
from pathlib import Path
from mass_spec_utils.data_import.mzmine import load_picked_boxes, map_boxes_to_scans
from mass_spec_utils.data_import.mzml import MZMLFile

# out_dir = "/home/bastian/PycharmProjects/vimms-gui/results"
mzmine_output = "/home/bastian/PycharmProjects/vimms-gui/output"
# seed_file = "/home/bastian/PycharmProjects/vimms-gui/results/TopN_Fullscan_QCB_0.mzML"
mzmine_command = "/home/bastian/Programs/MZmine/startMZmine-Linux"
xml_file = "/home/bastian/PycharmProjects/vimms-gui/batch_files/config.xml"


def pick_peaks(file_list,
               xml_template='batch_files/PretermPilot2Reduced.xml',
               output_dir='/Users/simon/git/pymzmine/output',
               mzmine_command='/Users/simon/MZmine-2.40.1/startMZmine_MacOSX.command',
               add_name=None):
    et = xml.etree.ElementTree.parse(xml_template)
    # Loop over files in the list (just the firts three for now)
    for filename in file_list:
        logger.info("Creating xml batch file for {}".format(filename.split(os.sep)[-1]))
        root = et.getroot()
        for child in root:
            # Set the input filename
            if child.attrib['method'] == 'io.github.mzmine.modules.io.rawdataimport.RawDataImportModule':
                for e in child:
                    for g in e:
                        g.text = os.path.join(output_dir, filename)  # raw data file name
            # Set the csv export filename
            if child.attrib[
                'method'] == 'io.github.mzmine.modules.io.csvexport.CSVExportModule':  # TODO: edit / remove
                for e in child:
                    for g in e:
                        tag = g.tag
                        text = g.text
                        if tag == 'current_file' or tag == 'last_file':
                            if add_name is None:
                                csv_name = os.path.join(output_dir,
                                                        filename.split(os.sep)[-1].split('.')[0] + '_box.csv')
                            else:
                                csv_name = os.path.join(output_dir, filename.split(os.sep)[-1].split('.')[
                                    0] + '_' + add_name + '_box.csv')
                            g.text = csv_name
        # write the xml file for this input file
        if add_name is None:
            new_xml_name = os.path.join(output_dir, filename.split(os.sep)[-1].split('.')[0] + '.xml')
        else:
            new_xml_name = os.path.join(output_dir, filename.split(os.sep)[-1].split('.')[0] + '_' + add_name + '.xml')
        et.write(new_xml_name)
        # Run mzmine
        logger.info("Running mzMine for {}".format(filename.split(os.sep)[-1]))
        os.system(mzmine_command + ' "{}"'.format(new_xml_name))

@st.cache
def topn_evaluate(mzml_file_path):
    out_dir, filename = os.path.split(mzml_file_path)
    # print (filename)
    # print (out_dir)
    boxes = extract_boxes(filename, out_dir)
    counts = evaluate_boxes(boxes, out_dir)
    return counts

def extract_boxes(filename, out_dir):
    # construct the path to the resulting peak picked CSV
    seed_picked_peaks_csv = get_peak_picked_csv(filename, out_dir)
    logger.info('Peak picking, results will be in %s' % seed_picked_peaks_csv)

    # run peak picking using MzMine2
    pick_peaks([filename], xml_template=xml_file, output_dir=out_dir, mzmine_command=mzmine_command)

    # the peak picked csv must exist at this point
    assert Path(seed_picked_peaks_csv).is_file()
    boxes = load_picked_boxes(seed_picked_peaks_csv)
    logger.info('Loaded %d boxes from the seed file' % len(boxes))
    return boxes


def get_peak_picked_csv(filename, out_dir):
    """
    From the seed file returns the path to the peak picked csv file from mzmine
    :param seed_file: path to the seed file
    :return: path to the peak picked csv file from mzine
    """
    seed_picked_peaks = os.path.splitext(filename)[0] + '_box.csv'
    seed_picked_peaks_csv = os.path.join(out_dir, seed_picked_peaks)
    return seed_picked_peaks_csv

def evaluate_boxes(boxes, out_dir):
    counts = 0
    for filename in glob.glob(os.path.join(out_dir, '*.mzML')):
        mzml = MZMLFile(filename)
        scans2boxes, boxes2scans = map_boxes_to_scans(mzml, boxes, half_isolation_window=0)
        counts = len(boxes2scans)
    logger.debug(counts)
    return counts

# # construct the path to the resulting peak picked CSV
# seed_picked_peaks_csv = get_peak_picked_csv(seed_file)
# # logger.info('Peak picking, results will be in %s' % seed_picked_peaks_csv)
# pick_peaks(seed_file, xml_template=my_xml_file, output_dir=out_dir, mzmine_command=mzmine_command)
# assert Path(seed_picked_peaks_csv).is_file()
# boxes = load_picked_boxes(seed_picked_peaks_csv)
