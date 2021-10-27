import os
import random
import urllib
# import uuid
from datetime import datetime

import pandas as pd
import shortuuid
import streamlit as st
import plotly.express as px

from PIL import Image
from matplotlib import pyplot as plt
from vimms.Chemicals import ChemicalMixtureFromMZML
from vimms.Roi import RoiParams

import WebTexts
from vimms_utils import *

main_out_dir = "/home/bastian/PycharmProjects/vimms_app/results"


def get_chems(params, filename):
    """
    Create chemicals from seed file by extracting roi and convert to chemicals
    :param params: ROI parameters from user input
    :param filename: the name of the seed file
    :return: Chemicals objects
    """
    rp = RoiParams(**params)
    cm = ChemicalMixtureFromMZML(filename, roi_params=rp)
    chems = cm.sample(None, 2)
    return chems


def get_jobname(job_name):
    """To get job name user input"""

    def generate_random_uid(randomlength=6):
        """Generate a random uid for user based on time"""
        random_str = ''
        base_str = 'ABCDEFGHIGKLMNOPQRSTUVWXYZabcdefghigklmnopqrstuvwxyz'
        hour_time = datetime.now().strftime('%H:%M:%S')
        length = len(base_str) - 1
        for i in range(randomlength):
            random_str += base_str[random.randint(0, length)]
        random_uid = random_str + hour_time
        return random_uid

    if job_name == "":
        job_name = generate_random_uid()
    else:
        job_name = st.session_state.jobname

    return job_name


def make_out_dir(job_name):
    """
    Make a directory for user to store output files,
    The uid is generated from job name user input
    The directory name will be job name + uid
    """
    uid = shortuuid.uuid(name=job_name)
    out_dir = main_out_dir + '/' + job_name + '-' + uid

    print(out_dir)
    isExists = os.path.exists(out_dir)
    if not isExists:
        os.makedirs(out_dir)
    return out_dir


def plot_counts(summary):
    """
    To plot for the evaluation summary
    :param summary: should be a dataframe
    :return:
    """
    plt.figure(figsize=(12, 6))
    st.subheader("Evaluation Plot")
    fig = px.scatter(
        summary,
        x="N",
        y='Evaluation',
        size='Peaks picked',
        # symbol="Evaluation"
        # color_discrete_sequence=["#763737"],
    )
    # fig.update_traces(marker=dict(size=4))
    fig.update_layout(
        xaxis_title_text="Top-N",
        yaxis_title_text="Evaluation",
    )
    # fig.add_bar(y=summary['Peaks picked'],
    #             name="Number of peaks picked")
    st.plotly_chart(fig, use_container_width=True)


class webViMMS:
    """ViMMS Streamlit UI."""

    def __init__(self):
        self.texts = WebTexts
        self.user_input = dict()

        st.set_page_config(
            layout="wide",
            page_title='ViMMS',
            page_icon='logo.png'
        )

        self.main()
        # self.navigation()

    def main(self):
        """Side navigation bar."""
        app_mode = st.sidebar.selectbox("Choose the Vimms function",
                                        ["Instructions", "Run Simulation"])

        if app_mode == "Instructions":
            readme_text = st.markdown(read_markdown_file("introductions.md"), unsafe_allow_html=True)
            img = Image.open("help.png")
            st.image(img)
        else:
            self.vimms()

    def vimms(self):
        """App main page."""

        # The form container for upload and configuration
        with st.form(key="file_form"):
            st.subheader("Upload and configuration")
            # Divide form into 2 columns
            col1_1, col2_1 = st.columns(2)
            with col1_1:
                self.user_input["seed_file"] = st.file_uploader(
                    "Please upload your mzML file here", type=["mzML", "xml"],
                    help=self.texts.HelpTexts.seed_file, key='seedfile')
                self.user_input["job_name"] = st.text_input("Job name (*Required)",
                                                            help=self.texts.HelpTexts.job_name, key='jobname')

            with col2_1:
                self.user_input["file_type"] = st.checkbox("Is full-scan file?", key='filetype',
                                                           help=self.texts.HelpTexts.file_type)
                ms1_time = st.slider("MS1 Timing", value=0.60, step=0.1)
                ms2_time = st.slider("MS2 Timing", value=0.20, step=0.1)
                self.user_input["time_dict"] = {1: ms1_time, 2: ms2_time}

            # ROI parameters expander
            with st.expander("Set ROI parameters"):
                # Divide the expander into 3 columns
                cols = st.columns(3)
                # A list for parameters
                params_title = ["ROI m/z tolerance", "Minimum length of ROIs", "Minimum intensity"]
                params_key = ["mz_tol", "min_length", "min_intensity"]
                # Generate number_input widget for all parameters in list
                for i, col in enumerate(cols):
                    self.user_input[params_key[i]] = col.number_input(params_title[i], value=0, key=params_key[i])
                # Create two columns with a ratio of 1:2
                col1_2, col2_2 = st.columns([1, 2])
                self.user_input["mz_units"] = col1_2.selectbox('Units of m/z tolerance', ["ppm", "scans"],
                                                               key='mz_units')
                rt_range = col2_2.slider('Retention time range (s)', help=self.texts.HelpTexts.rt_range,
                                         min_value=10, max_value=5000, value=(0, 1440))
                self.user_input["min_rt"], self.user_input["max_rt"] = rt_range[0], rt_range[1]

            submit_button = st.form_submit_button("Run simulation")

        self.controller_ui()

        if submit_button:
            self.run_vimms()

    def instruction(self):
        readme_text = st.markdown(get_file_content_as_string("instructions.md"))

    def controller_ui(self):
        """Create widgets to get controller parameters."""

        st.sidebar.title("Controller")
        self.user_input["controller_mode"] = st.sidebar.selectbox("Controller mode",
                                                                  ["Top-N", "Smart ROI", "Weighted DEW"])

        st.sidebar.subheader("Set parameters")
        st.sidebar.number_input("Parameters N", help=self.texts.HelpTexts.N,
                                value=10, step=1, key='N')
        self.user_input['N'] = st.session_state['N']

        st.sidebar.subheader("Experiment Parameters")
        st.sidebar.radio('Select ionisation mode', ["Positive", "Negative"], key='ionisation_mode')
        self.user_input['ionisation_mode'] = st.session_state['ionisation_mode']
        st.sidebar.number_input("Isolation width", value=1, step=1, key='isolation_width')
        self.user_input['isolation_width'] = st.session_state['isolation_width']

        st.sidebar.subheader("Simulation Parameters")
        exp_params_title = [
            "Simulation m/z tolerance",
            "Retention time tolerance",
            "Minimum ms1 intensity",
        ]
        exp_params_key = [
            "sim_mz_tol", "rt_tol",
            "min_ms1_intensity"
        ]
        # Generate number_input widget for all parameters in list exp_params_key[]
        for i, key in enumerate(exp_params_key):
            st.sidebar.number_input(exp_params_title[i], key=key)
            self.user_input[key] = st.session_state[key]
        # st.sidebar.number_input("Simulation m/z tolerance", value=10, step=1, key='sim_mz_tol')
        # st.sidebar.number_input("Retention time tolerance", value=15, step=1, key='rt_tol')
        # st.sidebar.number_input("Minimum ms1 intensity", value=5000, step=1, key='min_ms1_intensity')

    def parse_user_input(self, user_input):
        """Validate and parse user input."""
        config = {"seed_filename": None, "job_name": None,
                  "roi_params": {
                      'mz_tol': user_input["mz_tol"],
                      'mz_units': user_input["mz_units"],
                      'min_length': user_input["min_length"],
                      'min_intensity': user_input["min_intensity"],
                      'start_rt': user_input["min_rt"],
                      'stop_rt': user_input["max_rt"]
                  },
                  "scan_duration": None, "chems": None,
                  "out_dir": None, "out_file": None}

        # Get filename and job name from user
        if user_input["seed_file"] is not None:
            config["seed_filename"] = user_input["seed_file"].name
            config["job_name"] = get_jobname(user_input["job_name"])

            # If user click the checkbox, get the scan duration user set
            if user_input["file_type"]:
                config['scan_duration'] = user_input["time_dict"]
            else:  # scan the seed file to get scan duration
                config['scan_duration'] = get_timing(config["seed_filename"])

            config["out_dir"] = make_out_dir(config["job_name"])
            config["out_file"] = make_topN_out(config["seed_filename"], user_input['N'])

        return config

    def run_vimms(self):
        """Run ViMMS and show results."""
        config = self.parse_user_input(self.user_input)
        col1_3, col2_3, col3_1 = st.columns(3)

        status_placeholder = st.empty()
        status_placeholder.info(":hourglass_flowing_sand: Running ViMMS...")
        # Extract ROIs and create chemicals
        chems = get_chems(config["roi_params"], config["seed_filename"])
        # Run simulation
        run_topN(chems, config, self.user_input)
        # Calculate counts and get number of peaks picked(boxes) by MZmine2
        topn_eval = Evaluate(file_name=config["out_file"], out_dir=config["out_dir"])
        boxes, counts = topn_eval.boxes, topn_eval.counts
        status_placeholder.success(":heavy_check_mark: Finished!")
        # Create a download button for user to download simulated mzML
        with col1_3:
            with open(os.path.join(config["out_dir"], config["out_file"])) as file:
                st.download_button(
                    label="Download mzML file",
                    data=file,
                    mime="mzML",
                    help=self.texts.HelpTexts.download
                )
        # Make dataframe by reading stored csv file.
        csv_file = MakeSummary(config=config, user_input=self.user_input, counts=counts, boxes=boxes).csv_file
        df = pd.read_csv(csv_file)
        st.subheader("Table for varying N parameters results")
        st.write(df)
        plot_counts(df)


@st.cache(show_spinner=False)
def get_file_content_as_string(path):
    url = 'https://raw.githubusercontent.com/BastianWang11/vimms-gui/main/' + path
    response = urllib.request.urlopen(url)
    return response.read().decode("utf-8")


def read_markdown_file(markdown_file):
    """To read markdown file"""
    with open(markdown_file, encoding='utf-8') as fp:
        w = fp.read()
    return w


if __name__ == "__main__":
    webViMMS()
