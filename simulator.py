import os.path

import streamlit as st
import ipyparallel as ipp
from vimms.Controller import *
from vimms.MassSpec import IndependentMassSpectrometer
from vimms.Environment import Environment
from params import *

def run_topN(chems, params, time_dict, file_name, out_dir):
    fname = os.path.splitext(file_name)[0]
    out_file = '%s_%s_%s.mzML' % (params['controller_name'], fname, params['N'])
    controller = TopNController(params['ionisation_mode'], params['N'], params['isolation_width'], params['mz_tol'],
                                params['rt_tol'], params['min_ms1_intensity'])
    mass_spec = IndependentMassSpectrometer(params['ionisation_mode'], chems, None, scan_duration_dict=time_dict)
    env = Environment(mass_spec, controller, params['min_rt'], params['max_rt'], progress_bar=True, out_dir=out_dir,
                      out_file=out_file)
    env.run()


def run_single_SmartROI(chems, params, time_dict, file_name, out_dir):
    fname = os.path.splitext(file_name)[0]
    out_file = 'SMART_{}_{}_{}.mzml'.format(fname, params['iif_values'], params['dp_values'])

    intensity_increase_factor = params['iif_values']  # fragment ROI again if intensity increases 10 fold
    drop_perc = params['dp_values'] / 100
    reset_length_seconds = 1e6  # set so reset never happens

    controller = TopN_SmartRoiController(params['ionisation_mode'], params['isolation_width'], params['mz_tol'],
                                         params['min_ms1_intensity'], params['min_roi_intensity'],
                                         params['min_roi_length'], N=params['N'], rt_tol=params['rt_tol'],
                                         min_roi_length_for_fragmentation=params[
                                             'min_roi_length_for_fragmentation'],
                                         reset_length_seconds=reset_length_seconds,
                                         intensity_increase_factor=intensity_increase_factor,
                                         drop_perc=drop_perc)

    mass_spec = IndependentMassSpectrometer(params['ionisation_mode'], chems,
                                            scan_duration_dict=time_dict)
    env = Environment(mass_spec, controller, params['min_rt'], params['max_rt'], progress_bar=True,
                      out_dir=out_dir, out_file=out_file)
    env.run()


def run_single_WeightedDEW(chems, params, time_dict, file_name, out_dir):
    fname = os.path.splitext(file_name)[0]
    out_file = 'WeightedDEW_{}_{}_{}.mzml'.format(fname, params['t0_values'], params['rt_tol_values'])
    if params['t0_values'] > params['rt_tol_values']:
        logger.warning('Impossible combination')
        return

    controller = WeightedDEWController(params['ionisation_mode'], params['N'], params['isolation_width'],
                                       params['mz_tol'], params['rt_tol_values'], params['min_ms1_intensity'],
                                       exclusion_t_0=params['t0_values'], log_intensity=True)
    mass_spec = IndependentMassSpectrometer(params['ionisation_mode'], chems,
                                            scan_duration_dict=time_dict)
    env = Environment(mass_spec, controller, params['min_rt'], params['max_rt'], progress_bar=True,
                      out_dir=out_dir, out_file=out_file)
    env.run()


