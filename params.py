import streamlit as st
from vimms.InSilicoSimulation import string_to_list

def roi_params():
    with st.form(key='roi_form'):
        cols = st.beta_columns(6)
        params_title = {'mz_tol', 'mz_units',
                        'min_length', 'min_intensity',
                        'start_rt', 'stop_rt'
                        }
        for i, col in enumerate(cols):
            col.number_input(f'params_title[i]', value=0, key='params_title[i]')
        submitted = st.form_submit_button('Submit')

def get_params():
    st.subheader("Extract ROIs")
    st.markdown('<style>description{colour: blue;}</style>', unsafe_allow_html=True)
    st.markdown("<description>Please set roi parameters " +
                "and click the button before running simulation. </description>",
                unsafe_allow_html=True)
    col1, col2, col3, = st.columns(3)
    with col1:
        st.number_input("ROI m/z tolerance", value=5, step=1, key='mz_tol')
        mz_tol = st.session_state.mz_tol
    with col2:
        st.selectbox('units of m/z tolerance', ["ppm", "scans"], key='mz_units')
        mz_units = st.session_state.mz_units
    with col3:
        st.number_input("minimum length of ROIs", value=1, step=1, key='min_length')
        min_length = st.session_state.min_length
    col4, col5, col6, = st.columns(3)
    with col4:
        st.number_input("minimum intensity", value=0, step=1, key='min_intensity')
        min_intensity = st.session_state.min_intensity
    with col5:
        st.number_input("start retention time", value=0, step=1, key='start_rt')
        start_rt = st.session_state.start_rt
    with col6:
        st.number_input("stop retention time", value=1440, step=1, key='stop_rt')
        stop_rt = st.session_state.stop_rt

    params_dict = {
        'mz_tol': mz_tol,
        'mz_units': mz_units,
        'min_length': min_length,
        'min_intensity': min_intensity,
        'start_rt': start_rt,
        'stop_rt': stop_rt
    }
    return params_dict

# def controller_ui():
#     st.sidebar.number_input("Parameters N", value=10, step=1, key='N')
#
#     st.sidebar.subheader("Set Experiment Parameters")
#     st.sidebar.number_input("minimum retention time", value=0, step=1, key='min_rt')
#     st.sidebar.number_input("maximum retention time", value=1440, step=1, key='max_rt')
#     st.sidebar.selectbox('select ionisation mode', ["Positive", "Negative"], key='ionisation_mode')
#     st.sidebar.number_input("isolation width", value=1, step=1, key='isolation_width')
#
#     st.sidebar.subheader("Set Simulation Parameters")
#     st.sidebar.number_input("simulation m/z tolerance", value=10, step=1, key='sim_mz_tol')
#     st.sidebar.number_input("rt tolerance", value=15, step=1, key='rt_tol')
#     st.sidebar.number_input("minimum ms1 intensity", value=5000, step=1, key='min_ms1_intensity')
#
#     # get additional SmartROI parameters
#     st.sidebar.number_input("iif_values", value=10, step=1, key='sr_iif_values')
#     st.sidebar.number_input("dp_values", value=0.5, step=0.1, key='sr_dp_values')
#     st.sidebar.number_input('minimum roi intensity', value=500, step=1, key='sr_min_roi_intensity')
#     st.sidebar.number_input('minimum roi length', value=0, step=1, key='sr_min_roi_length')
#     st.sidebar.number_input('minimum roi length for fragmentation', value=0, step=1,
#                             key='min_roi_length_for_fragmentation')
#
#     # get additional WeightedDEW parameters
#     st.sidebar.number_input("t0 values", value=10, step=1, key='wd_t0_values')
#     st.sidebar.number_input("rt tolerance values", value=120, step=1, key='wd_rt_tol_values')


def Topn_controller_ui():

    st.sidebar.number_input("Parameters N", value=10, step=1, key='N')

    st.sidebar.subheader("Set Experiment Parameters")
    st.sidebar.number_input("minimum retention time", value=0, step=1, key='min_rt')
    st.sidebar.number_input("maximum retention time", value=1440, step=1, key='max_rt')
    st.sidebar.selectbox('select ionisation mode', ["Positive", "Negative"], key='ionisation_mode')
    st.sidebar.number_input("isolation width", value=1, step=1, key='isolation_width')

    st.sidebar.subheader("Set Simulation Parameters")
    st.sidebar.number_input("simulation m/z tolerance", value=10, step=1, key='sim_mz_tol')
    st.sidebar.number_input("rt tolerance", value=15, step=1, key='rt_tol')
    st.sidebar.number_input("minimum ms1 intensity", value=5000, step=1, key='min_ms1_intensity')

def TopnParams():
    controller_name = "TopN"
    min_rt = st.session_state.min_rt
    max_rt = st.session_state.max_rt
    ionisation_mode = st.session_state.ionisation_mode
    isolation_width = st.session_state.isolation_width

    N = st.session_state.N
    sim_mz_tol = st.session_state.sim_mz_tol
    rt_tol = st.session_state.rt_tol
    min_ms1_intensity = st.session_state.min_ms1_intensity

    params = {
        'controller_name': controller_name,
        'ionisation_mode': ionisation_mode,
        # 'sample_name': file_name,
        'isolation_width': isolation_width,
        'N': N,
        'mz_tol': sim_mz_tol,
        'rt_tol': rt_tol,
        'min_ms1_intensity': min_ms1_intensity,
        'min_rt': min_rt,
        'max_rt': max_rt
    }
    return params

def SmartRoi_controller_ui():
    st.sidebar.subheader("Set Experiment Parameters")
    st.sidebar.number_input("minimum time", value=0, step=1, key='sr_min_rt')
    st.sidebar.number_input("maximum time", value=1440, step=1, key='sr_max_rt')
    st.sidebar.selectbox('select ionisation mode', ["Positive", "Negative"], key='sr_ionisation_mode')
    st.sidebar.number_input("isolation width", value=1, step=1, key='sr_isolation_width')

    # Set Simulation Parameters
    st.sidebar.subheader("Set Simulation Parameters")
    st.sidebar.number_input("N", value=10, step=1, key='sr_N')
    st.sidebar.number_input("simulation m/z tolerance", value=10, step=1, key='sr_mz_tol')
    st.sidebar.number_input("rt tolerance", value=15, step=1, key='sr_rt_tol')
    st.sidebar.number_input("minimum ms1 intensity", value=5000, step=1, key='sr_min_ms1_intensity')

    # get additional SmartROI parameters
    st.sidebar.number_input("iif_values", value=10, step=1, key='sr_iif_values')
    st.sidebar.number_input("dp_values", value=0.5, step=0.1, key='sr_dp_values')
    st.sidebar.number_input('minimum roi intensity', value=500, step=1, key='sr_min_roi_intensity')
    st.sidebar.number_input('minimum roi length', value=0, step=1, key='sr_min_roi_length')
    st.sidebar.number_input('minimum roi length for fragmentation', value=0, step=1,
                            key='sr_min_roi_length_for_fragmentation')

def SmartRoiParams():
    # Set Experiment Parameters
    controller_name = "Smart ROI"
    min_rt = st.session_state.sr_min_rt
    max_rt = st.session_state.sr_max_rt
    ionisation_mode = st.session_state.sr_ionisation_mode
    isolation_width = st.session_state.sr_isolation_width

    # Set Simulation Parameters
    N = st.session_state.sr_N
    mz_tol = st.session_state.sr_mz_tol
    rt_tol = st.session_state.sr_rt_tol
    min_ms1_intensity = st.session_state.sr_min_ms1_intensity

    # get additional SmartROI parameters
    iif_values = st.session_state.sr_iif_values
    dp_values = st.session_state.sr_dp_values
    min_roi_intensity = st.session_state.sr_min_roi_intensity
    min_roi_length = st.session_state.sr_min_roi_length
    min_roi_length_for_fragmentation = st.session_state.sr_min_roi_length_for_fragmentation

    params = {
        'controller_name': controller_name,
        'ionisation_mode': ionisation_mode,
        # 'sample_name': file_name,
        'isolation_width': isolation_width,
        'N': N,
        'mz_tol': mz_tol,
        'rt_tol': rt_tol,
        'min_ms1_intensity': min_ms1_intensity,
        'min_rt': min_rt,
        'max_rt': max_rt,
        'iif_values': iif_values,
        'dp_values': dp_values,
        'min_roi_intensity': min_roi_intensity,
        'min_roi_length': min_roi_length,
        'min_roi_length_for_fragmentation': min_roi_length_for_fragmentation
    }
    return params

def WeightedDEW_controller_ui():
    st.sidebar.subheader("Set Experiment Parameters")
    # Set Experiment Parameters
    st.sidebar.number_input("minimum time", value=0, step=1, key='wd_min_rt')
    st.sidebar.number_input("maximum time", value=1440, step=1, key='wd_max_rt')
    st.sidebar.selectbox('select ionisation mode', ["Positive", "Negative"], key='wd_ionisation_mode')
    st.sidebar.number_input("isolation width", value=1, step=1, key='wd_isolation_width')

    # Set Simulation Parameters
    st.sidebar.subheader("Set Simulation Parameters")
    st.sidebar.number_input("N", value=10, step=1, key='wd_N')
    st.sidebar.number_input("simulation m/z tolerance", value=10, step=1, key='wd_mz_tol')
    st.sidebar.number_input("minimum ms1 intensity", value=5000, step=1, key='wd_min_ms1_intensity')

    # get additional SmartROI parameters
    st.sidebar.number_input("t0 values", value=10, step=1, key='wd_t0_values')
    st.sidebar.number_input("rt tolerance values", value=120, step=1, key='wd_rt_tol_values')

def WeightedDEWParams():
    # Set Experiment Parameters
    controller_name = "Weighted DEW"
    min_rt = st.session_state.wd_min_rt
    max_rt = st.session_state.wd_max_rt
    ionisation_mode = st.session_state.wd_ionisation_mode
    isolation_width = st.session_state.wd_isolation_width

    # Set Simulation Parameters
    N = st.session_state.wd_N
    mz_tol = st.session_state.wd_mz_tol
    min_ms1_intensity = st.session_state.wd_min_ms1_intensity

    # get additional SmartROI parameters
    t0_values = st.session_state.wd_t0_values
    rt_tol_values = st.session_state.wd_rt_tol_values

    params = {
        'controller_name': controller_name,
        'ionisation_mode': ionisation_mode,
        # 'sample_name': file_name,
        'isolation_width': isolation_width,
        'N': N,
        'mz_tol': mz_tol,
        'min_ms1_intensity': min_ms1_intensity,
        'min_rt': min_rt,
        'max_rt': max_rt,
        't0_values': t0_values,
        'rt_tol_values': rt_tol_values
    }
    return params