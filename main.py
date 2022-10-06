from bs4 import BeautifulSoup
import requests
import streamlit as st
from seo_data import SoupData, SerpData
import os

API_KEY = os.environ['SCALE_SERP_KEY']
QUERY_URL = os.environ['SCALE_SERP_QUERY_URL']

st.markdown("""
<style>
.big-font {
    font-size:50px !important;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<p class="big-font">SERP Metadata Comparison App</p>
<b>Directions: </b></ br><ul>
<li>Enter Full URL including https or http.</li>
</ul>
<b>Considerations: </b></ br><ul>
<li>Metadata is scraped from the source HTML document.</li>
<li>On-page metadata may not be retrieved if site is a SPA (single page application).</li>
</ul>

""", unsafe_allow_html=True)

url = st.text_input('Enter full URL', placeholder='https://www.domain.com')


def request_url(input_url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 12; SM-S906N Build/QP1A.190711.020; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/80.0.3987.119 Mobile Safari/537.36'}
    response = requests.get(input_url, headers=headers)
    return response


def get_serp(input_url):
    st.write(f'Gathering SERP data from {input_url} . . .')
    params = {
        'api_key': API_KEY,
        'q': f'site:{input_url}'
    }

    response = requests.get(
        QUERY_URL,
        params=params
    )

    try:
        serp_title = response.json()["organic_results"][0]["title"]
        serp_description = response.json()["organic_results"][0]["snippet"]
    except KeyError:
        print(f"{url} experience an error and may not be indexed in Google")
        serp_description = "Error, URL may not be indexed in Google."
        serp_title = "Error, URL may not be indexed in Google."
    print(f"SERP Title: {serp_title}\nSERP Description: {serp_description}")
    serp_data = SerpData(
        title=serp_title,
        description=serp_description
    )
    return serp_data


def get_soup(input_url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 12; SM-S906N Build/QP1A.190711.020; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/80.0.3987.119 Mobile Safari/537.36'}
    st.write(f'Gathering metadata from {input_url} . . .')
    response = requests.get(input_url, headers=headers)
    analyzed_url = response.text
    try:
        b_soup = BeautifulSoup(analyzed_url, 'html.parser')
        soup_title = b_soup.title.text
        soup_description = b_soup.find(name='meta', attrs={'name': 'description'})['content']
    except TypeError:
        soup_title = "Error, title cannot be retrieved"
        soup_description = "Error, meta description cannot be retrieved"
    soup_data = SoupData(
        title=soup_title,
        description=soup_description
    )
    print(f"Title: {soup_title}\nDescription: {soup_description}")
    return soup_data


def evaluate():
    soup = get_soup(url)
    serp = get_serp(url)
    st.markdown(f"""<br></br>
                                    <h3><b>Results: </b></h3>
                                    <p>Page Title: {soup.title[0]}</p>
                                    <p>SERP Title: {serp.title[0]}</p><br></br>
                                    <p>Page Description: {soup.description}</p>
                                    <p>SERP Description: {serp.description}</p><br></br>

                                    """, unsafe_allow_html=True)


if url:
    if request_url(url).status_code == 200:
        evaluate()
    else:
        st.markdown(f"""<br></br>
                                    <h5 style="color: red">The URL you entered returned a {request_url(url).status_code} Status Code and cannot be analyzed, try another URL.</b></h5>
                                    """, unsafe_allow_html=True)

st.write('Author: [Tyler Gargula](https://www.tylergargula.dev) | Technical SEO & Software Developer')
