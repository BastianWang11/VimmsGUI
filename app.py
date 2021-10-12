
import random
import urllib
# import uuid
from datetime import datetime

import shortuuid
import streamlit as st

from vimms.Chemicals import *
from vimms.Controller import *
from vimms.Common import *
from vimms.Environment import Environment
from vimms.Roi import RoiParams
from vimms.FeatureExtraction import extract_roi
from vimms.InSilicoSimulation import extract_timing, string_to_list, get_timing
from vimms.Roi import *
from evaluate import *
from simulator import *
from summary import *

main_out_dir = "/home/bastian/PycharmProjects/vimms-gui/results"
out_file = "results.mzML"

def main():
    # Render the readme as markdown using st.markdown.
    readme_text = st.markdown(get_file_content_as_string("instructions.md"))

    # Selector for the app mode on the sidebar.
    st.sidebar.title("Vimms mode")
    app_mode = st.sidebar.selectbox("Choose the Vimms function",
        ["Instructions", "Run Simulation", "Summary of results"])

    # Project required file and description.
    st.sidebar.title("Start a Project")
    uploaded_file = st.sidebar.file_uploader("Please upload your mzML file here", type=["mzML", "xml"])
    uploaded_filename = get_filename(uploaded_file)
    job_name = get_jobname()
    uid = shortuuid.uuid(name=job_name)
    out_dir = main_out_dir + '/' + job_name + '-' + uid

    if app_mode == "Instructions":
        st.sidebar.success('To continue select "Run Simulation".')
    elif app_mode == "Run Simulation":
        readme_text.empty()
        time_dict = get_time(uploaded_filename)
        params_dict = get_params()
        controller_selector_ui()
        if st.button("Run"):
            chems = extract_roi(uploaded_filename, params_dict)
            make_out_dir(out_dir)
            with st.spinner("Running..."):
                run_simulation(uploaded_filename, chems, time_dict, out_dir)
                summary = make_table(out_dir)
                st.table(summary)
            st.success("Done! You can select 'Summary of results' to get results")
        # Topn_controller_ui()
    elif app_mode == "Summary of results":
        readme_text.empty()
        with st.spinner("Wait for it..."):
            get_result(out_dir)
        st.success("Done!")


@st.cache
def get_filename(uploaded_file):
    if uploaded_file is not None:
        uploaded_filename = uploaded_file.name
        return uploaded_filename


def get_jobname():

    def generate_random_uid(randomlength=6):
        random_str = ''
        base_str = 'ABCDEFGHIGKLMNOPQRSTUVWXYZabcdefghigklmnopqrstuvwxyz'
        hour_time = datetime.now().strftime('%H:%M:%S')
        length = len(base_str) - 1
        for i in range(randomlength):
            random_str += base_str[random.randint(0, length)]
        random_uid = random_str + hour_time
        return random_uid

    job_name = st.sidebar.text_input("Job name (required)", key='jobname')
    if job_name == "":
        job_name = generate_random_uid()
    else:
        job_name = st.session_state.jobname
    # print(job_name)
    return job_name


def make_out_dir(out_dir):
    # def compressUuid():
    #     uuidstring = str(uuid.uuid3(uuid.NAMESPACE_DNS, job_name)).replace('-', '')
    #     return uuid.UUID(uuidstring).bytes.encode('base64').rstrip('=\n')
    # uuidstring = str(uuid.uuid3(uuid.NAMESPACE_DNS, job_name)).replace('-', '')
    # time_id = datetime.now().strftime('%m%d%H%M')
    # uid_string = job_name + str(time_id)
    print(out_dir)
    isExists = os.path.exists(out_dir)
    if not isExists:
        os.makedirs(out_dir)
    return out_dir

def run_simulation(filename, chems, time_dict, out_dir):
    placeholder = st.empty()
    placeholder.info("Running simulation...")
    params = TopnParams()
    run_topN(chems, params, time_dict, filename, out_dir)
    placeholder.empty()
    # counts = topn_evaluate(filename, out_dir)

def get_result(out_dir):
    summary = make_table(out_dir)
    st.table(summary)

# @st.cache
def extract_roi(file_name, params_dict):
    placeholder = st.empty()
    placeholder.info("Extracting ROI...")
    rp = RoiParams(**params_dict)
    cm = ChemicalMixtureFromMZML(file_name, roi_params=rp)
    chems = cm.sample(None, 2)
    placeholder.info("Extracteded")
    return chems


def get_time(uploaded_filename):
    @st.cache
    def get_frag_time(filename):
        time_dict = extract_timing(filename)
        return time_dict

    st.subheader("File type")
    file_type = st.selectbox('Please select the file type you uploaded', ('Fullscan File', 'DDA File'))

    if file_type == 'Fullscan File':
        col1, col2, = st.columns(2)
        with col1:
            ms1_time = st.slider("MS1 Timing", value=0.60, step=0.1)
        with col2:
            ms2_time = st.slider("MS2 Timing", value=0.20, step=0.1)
        time_dict = {1: ms1_time, 2: ms2_time}
        return time_dict
    elif file_type == 'DDA File':
        st.info('Timing extracted from file:')
        time_dict = get_frag_time(uploaded_filename)
        st.write('MS1 Timing: `%f`, MS2 Timing: `%f`' % (time_dict[1], time_dict[2]))
        return time_dict


def controller_selector_ui():
    st.sidebar.markdown("# Controller")
    # controller_ui()

    # The user can pick which type of controller to run simulation.
    controller_type = st.sidebar.selectbox("Please select a controller",
                         ("TopN", "Smart ROI", "Weighted DEW"))
    if controller_type == "TopN":
        Topn_controller_ui()
    elif controller_type == "Smart ROI":
        SmartRoi_controller_ui()
    elif controller_type == "Weighted DEW":
        WeightedDEW_controller_ui()

@st.cache(show_spinner=False)
def get_file_content_as_string(path):
    url = 'https://raw.githubusercontent.com/BastianWang11/vimms-gui/main/' + path
    response = urllib.request.urlopen(url)
    return response.read().decode("utf-8")

if __name__ == "__main__":
    main()