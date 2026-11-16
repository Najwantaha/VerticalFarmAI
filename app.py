import os
import base64
import json
import math
import streamlit as st

st.set_page_config(page_title='Vertical Farm AI Assistant', page_icon='🌱', layout='wide')
st.title('🌱 Vertical Farm AI Assistant')
st.caption('AI-assisted crop health screening and environmental decision support • Educational prototype')


def vpd_kpa(temp_c, rh):
    saturation = 0.6108 * math.exp(17.27 * temp_c / (temp_c + 237.3))
    return saturation * (1 - rh / 100)

with st.sidebar:
    st.header('Growing conditions')
    crop = st.selectbox('Crop', ['Lettuce', 'Basil', 'Spinach', 'Other'])
    temperature = st.slider('Air temperature (°C)', 10.0, 40.0, 24.0, 0.5)
    humidity = st.slider('Relative humidity (%)', 20, 95, 65)
    ph = st.slider('Nutrient solution pH', 4.0, 9.0, 6.0, 0.1)
    ec = st.slider('EC (mS/cm)', 0.0, 5.0, 1.6, 0.1)
    st.info('Values are manually entered, not live sensor readings.')

vpd = vpd_kpa(temperature, humidity)
a, b, c = st.columns(3)
a.metric('Calculated VPD', f'{vpd:.2f} kPa')
b.metric('Nutrient solution pH', f'{ph:.1f}')
c.metric('EC', f'{ec:.1f} mS/cm')

st.subheader('1. Environmental screening')
flags = []
if ph < 5.5 or ph > 6.5:
    flags.append('pH is outside a commonly used leafy-green hydroponic screening range (5.5–6.5); verify against your crop and system guidance.')
if vpd < 0.4:
    flags.append('Low VPD: check moisture, airflow and condensation risk.')
elif vpd > 1.5:
    flags.append('High VPD: check water demand, humidity and temperature.')
if temperature > 28:
    flags.append('Warm conditions: review heat stress risk for the crop and cultivar.')
if ec > 3.0:
    flags.append('Relatively high EC: verify nutrient strength against crop-specific targets.')
if flags:
    for flag in flags:
        st.warning(flag)
else:
    st.success('No broad screening flags triggered. This does not establish that conditions are optimal.')
st.caption('VPD uses air temperature as a proxy for leaf temperature. Crop-specific targets vary; thresholds are illustrative screening rules.')

st.subheader('2. Plant image assessment')
photo = st.file_uploader('Upload a plant leaf image (JPG or PNG)', type=['jpg', 'jpeg', 'png'])
notes = st.text_area('Observed symptoms or other notes (optional)', placeholder='e.g., yellowing on older leaves, brown edges on new growth')
if photo:
    st.image(photo, caption='Uploaded plant image', width=360)

api_key = None
try:
    api_key = st.secrets.get('OPENAI_API_KEY')
except Exception:
    pass
api_key = api_key or os.getenv('OPENAI_API_KEY')
if not api_key:
    api_key = st.text_input('OpenAI API key (optional for live AI analysis)', type='password', help='Used only for this session. Do not share or commit your key.')

if st.button('🔎 Analyze plant health', type='primary'):
    if not photo:
        st.error('Please upload a plant photo first.')
    elif not api_key:
        st.error('Add an OpenAI API key to run live AI analysis. Environmental screening above works without one.')
    else:
        try:
            from openai import OpenAI
            mime = 'image/png' if photo.type == 'image/png' else 'image/jpeg'
            encoded = base64.b64encode(photo.getvalue()).decode('ascii')
            prompt = f'''You are an educational vertical-farm crop health screening assistant. Crop: {crop}. Air temp: {temperature} C; RH: {humidity}%; pH: {ph}; EC: {ec} mS/cm; approximate VPD: {vpd:.2f} kPa. User notes: {notes or 'none'}.
Analyze visible symptoms conservatively. Do not claim to identify a specific nutrient deficiency, pathogen, or cause from image alone. Clearly distinguish observations from hypotheses. Provide concise sections: (1) Visible observations, (2) Possible explanations with uncertainty, (3) Environmental factors worth checking, (4) Safe next checks and actions, (5) What additional data would help. Do not invent lab tests, sensor readings or confidence percentages. Mention that an agronomist or lab may be needed for confirmation.'''
            with st.spinner('Analyzing image and growing conditions...'):
                result = OpenAI(api_key=api_key).responses.create(
                    model='gpt-4.1-mini',
                    input=[{'role': 'user', 'content': [
                        {'type': 'input_text', 'text': prompt},
                        {'type': 'input_image', 'image_url': f'data:{mime};base64,{encoded}'}
                    ]}], max_output_tokens=900
                )
            st.subheader('3. AI-assisted assessment')
            st.markdown(result.output_text)
            st.caption('AI output is a preliminary screening aid, not a confirmed diagnosis. Validate recommendations before changing farm settings.')
        except Exception as exc:
            st.error(f'AI request failed: {exc}')
            st.info('Check the API key, account billing, internet connection, and model access.')

st.divider()
st.caption('Prototype for a machine learning class • Uses a pretrained vision-language model plus deterministic environmental screening; no custom classifier has been trained.')
