import base64
import json
import pickle

import streamlit as st


def download_button(
    object_to_download, download_filename, button_text, pickle_it=False
):
    """
    Generates a link to download the given object_to_download.
    Params:
    ------
    object_to_download:  The object to be downloaded.
    download_filename (str): filename and extension of file. e.g. mydata.csv,
    some_txt_output.txt download_link_text (str): Text to display for download
    link.
    button_text (str): Text to display on download button (e.g. 'click here to download file')
    pickle_it (bool): If True, pickle file.
    Returns:
    -------
    (str): the anchor tag to download object_to_download
    Examples:
    --------
    download_button_str = download_button(s, filename, f'Click here to download {filename}')
    st.markdown(download_button_str, unsafe_allow_html=True)
    """
    if pickle_it:
        try:
            object_to_download = pickle.dumps(object_to_download)
        except pickle.PicklingError as e:
            st.write(e)
            return None

    else:
        if isinstance(object_to_download, bytes) or isinstance(object_to_download, str):
            pass

        # we would neet to import pandas to download dataframes, but we don't need to in this project
        # elif isinstance(object_to_download, pd.DataFrame):
        #     object_to_download = object_to_download.to_csv(index=False)

        # Try JSON encode for everything else
        else:
            object_to_download = json.dumps(object_to_download)

    try:
        # some strings <-> bytes conversions necessary here
        b64 = base64.b64encode(object_to_download.encode()).decode()

    except AttributeError as e:
        b64 = base64.b64encode(object_to_download).decode()

    # this is the default streamlit button design
    button_id = "download_button"
    custom_css = f""" 
        <style>
            #{button_id} {{
                display: inline-flex;
                -webkit-box-align: center;
                align-items: center;
                -webkit-box-pack: center;
                justify-content: center;
                font-weight: 400;
                padding: 0.25rem 0.75rem;
                border-radius: 0.25rem;
                margin: 0px;
                line-height: 1.6;
                color: inherit;
                width: auto;
                user-select: none;
                background-color: rgb(43, 44, 54);
                border: 1px solid rgba(250, 250, 250, 0.2);
                text-decoration: none; 
            }} 
            #{button_id}:hover {{
                border-color: rgb(255, 75, 75);
                color: rgb(255, 75, 75);
                text-decoration: none; 
            }}
            #{button_id}:active {{
                box-shadow: none;
                background-color: rgb(255, 75, 75);
                color: white;
                text-decoration: none; 
                }}
            #{button_id}:focus {{
                box-shadow: rgba(255, 75, 75, 0.5) 0px 0px 0px 0.2rem;
                outline: none;
                text-decoration: none; 
            }}
        </style> """

    dl_link = (
        custom_css
        + f'<a rel="noopener" download="{download_filename}" id="{button_id}" href="data:file/txt;base64,{b64}">{button_text}</a><br></br>'
    )

    return dl_link
