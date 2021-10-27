# vimms-gui
## Install

This project uses Streamlit, ViMMS and shortuuid, please make sure to install them locally. Other imported packages can be installed by IDE (such as PyCharm)

```
$ pip install streamlit
$ pip install vimms
$ pip install shortuuid
```

### MZmine2 

This project uses MZmine2 software, please also make sure it is locally installed. 

Download: [MZmine2](http://mzmine.github.io/download.html)

## Usage

Modify line **61** of **vimms_utils.py** to your MZmine2 installation path.

```python
self.mzmine_command = "/Path/to/MZmine/startMZmine-Linux"
```

Run with terminal commands. 

```
$ Streamlit run app.py
```

### 
