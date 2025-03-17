import time
import streamlit as st
import numpy as np
import pandas as pd
import generate_ai_insights
import predict_for_data
import kafka_cloud_consumer
import json
import random
import plotly.express as px
import time
import graphviz as gv
import alert_user
import uuid
import plotly.graph_objects as go
from streamlit_modal import Modal
import streamlit.components.v1 as components


custom_ranges = {
    'Engine rpm': (61.0, 2239.0),
    'Lub oil pressure': (0.003384, 7.265566),
    'Fuel pressure': (0.003187, 21.138326),
    'Coolant pressure': (0.002483, 7.478505),
    'Lub oil temp': (71.321974, 89.580796),
    'Coolant temp': (61.673325, 195.527912),
    'Temperature_difference': (-22.669427, 119.008526)
}

feature_descriptions = {
    'Engine rpm': 'Revolution per minute of the engine.',
    'Lub oil pressure': 'Pressure of the lubricating oil.',
    'Fuel pressure': 'Pressure of the fuel.',
    'Coolant pressure': 'Pressure of the coolant.',
    'Lub oil temp': 'Temperature of the lubricating oil.',
    'Coolant temp': 'Temperature of the coolant.',
    'Temperature_difference': 'Temperature difference between components.'
}

# def fetch_data_from_kafka():
#     config = kafka_cloud_consumer.read_config()
#     topic = "maintenance"
#     latest_message = kafka_cloud_consumer.consume(topic, config)

#     return latest_message

insights_list = []
insights_listing_list = []

def fetchRandomMockData():
    fetched_data = {
    'engine_rpm': random.randint(800, 6000),
    'lub_oil_pressure': random.uniform(20.0, 80.0),
    'fuel_pressure': random.uniform(30.0, 70.0),
    'coolant_pressure': random.uniform(15.0, 50.0),
    'lub_oil_temp': random.uniform(30.0, 120.0),
    'coolant_temp': random.uniform(30.0, 100.0),
    'temp_difference': random.uniform(-10.0, 10.0),
    }
    return fetched_data

def truncate_text(text, max_chars):
    text = str(text)
    return (text[:max_chars] + '...') if len(text) > max_chars else text

def generate_and_download_pdf(fetched_data,insights, output_path):
    output_path = 'report.pdf'
    generate_ai_insights.generate_pdf_report(fetched_data,insights, output_path)
    with open(output_path, "rb") as file:
        btn = st.download_button(
            label="Download PDF Report",
            data=file,
            file_name=output_path,
            mime="application/pdf",
            key=time.time() + time.time() + time.time()
        )

def getStage(stage):
    stages = ["None", "MQTT", "MQTT Topic", "Kafka Cloud Topic", "Application Listener", "ML Model", "GenAI Model", "Final Report"]

    for stg in stages:
        if stg == stage:
            return stg
    return None

def alertUser():
    print("Alert is Called")
    if st.button("Alert Edge Device", key=time.time() + time.time()):
        st.session_state.alert_edge_device = True

def main():
    global insights_list, insights_listing_list
    config = kafka_cloud_consumer.read_config()
    topic = "maintenance"
    kafka_cloud_consumer.start_kafka_consumer(topic, config)
    st.set_page_config(page_title="Tech Interrupt Maintenance Prediction", layout="wide")
    header = st.container()

    col1, col2, col3,col4 = header.columns([1, 3, 0.3,0.5])  # Adjust the ratio to control the width

    with col1:
        col1.image("msg_logo.png", width=200)
    with col2:
        col2.title("AI based Predictive Maintenance System as a Service (AIPMS)")
    with col3:    
        col3.image("co.jpg", width=150)
    with col4:
        # add some space above
        col4.write("""<div style="height: 20px;"></div>""", unsafe_allow_html=True)
        col4.subheader("Tech-Interrupt India 2024")
    
    header.write("""<div class='fixed-header'/>""", unsafe_allow_html=True)
    if "alert_edge_device" not in st.session_state:
        st.session_state.alert_edge_device = False
    ### Custom CSS for the sticky header
    st.markdown(
        """
    <style>
        div[data-testid="stVerticalBlock"] div:has(div.fixed-header) {
            position: sticky;
            top: 2rem;
            background-color: white;
            z-index: 999;
            margin-top: -18px;
            padding-bottom: -10px;
        }
        header {visibility: hidden;}
        .fixed-header {
            border-bottom: 1px solid black;
        }
    </style>
        """,
        unsafe_allow_html=True
    )
    

    # st.title("Data Flow Visualization")
    # st.write("This is a dynamic visualization of the data flow from MQTT to Kafka and further through ML and GenAI models.")

    # List of stages to cycle through

    # flowchart_placeholder = st.empty()
    # flowchart = gv.Digraph(format="png", graph_attr={"rankdir": "LR"})

    # flowchart.edge("IOT Telemetry Data", "MQTT Broker", label="Through MQTT Protocol", color="black")
    # flowchart.edge("MQTT Broker", "Kafka", label="Data to Kafka", color="black")
    # flowchart.edge("Kafka", "ML Processor", label="Data to Consumer", color="black")
    # flowchart.edge("ML Processor", "ML Model", label="Data to ML Model", color="black")
    # flowchart.edge("ML Model", "GenAI", label="Data to GenAI Model", color="black")
    # flowchart.edge("GenAI", "Final Report", label="Data to Final Report", color="black")

    # flowchart_placeholder.graphviz_chart(flowchart)

    # header_placeholder = st.empty()
    # header_placeholder.header("Real-time Data Monitoring")
    st.subheader("Check for Manual Parameters")
    col1, col2 = st.columns(2)

    with col1:
        vehicle_name = st.selectbox("Select Available Vehicle", ["mercedessclass", "bmwm2"], key= uuid.uuid3)
        engine_rpm = st.slider("Engine RPM", min_value=float(custom_ranges['Engine rpm'][0]), 
                            max_value=float(custom_ranges['Engine rpm'][1]), 
                            value=float(custom_ranges['Engine rpm'][1] / 2))
        lub_oil_pressure = st.slider("Lub Oil Pressure", min_value=custom_ranges['Lub oil pressure'][0], 
                                    max_value=custom_ranges['Lub oil pressure'][1], 
                                    value=(custom_ranges['Lub oil pressure'][0] + custom_ranges['Lub oil pressure'][1]) / 2)
        fuel_pressure = st.slider("Fuel Pressure", min_value=custom_ranges['Fuel pressure'][0], 
                                max_value=custom_ranges['Fuel pressure'][1], 
                                value=(custom_ranges['Fuel pressure'][0] + custom_ranges['Fuel pressure'][1]) / 2)

    with col2:
        coolant_pressure = st.slider("Coolant Pressure", min_value=custom_ranges['Coolant pressure'][0], 
                                    max_value=custom_ranges['Coolant pressure'][1], 
                                    value=(custom_ranges['Coolant pressure'][0] + custom_ranges['Coolant pressure'][1]) / 2)
        lub_oil_temp = st.slider("Lub Oil Temperature", min_value=custom_ranges['Lub oil temp'][0], 
                                max_value=custom_ranges['Lub oil temp'][1], 
                                value=(custom_ranges['Lub oil temp'][0] + custom_ranges['Lub oil temp'][1]) / 2)
        coolant_temp = st.slider("Coolant Temperature", min_value=custom_ranges['Coolant temp'][0], 
                                max_value=custom_ranges['Coolant temp'][1], 
                                value=(custom_ranges['Coolant temp'][0] + custom_ranges['Coolant temp'][1]) / 2)

        temp_difference = st.slider("Temperature Difference", min_value=custom_ranges['Temperature_difference'][0], 
                                max_value=custom_ranges['Temperature_difference'][1], 
                                value=(custom_ranges['Temperature_difference'][0] + custom_ranges['Temperature_difference'][1]) / 2)

    with col1:
        if st.button("Predict Engine Condition"):
            result, confidence = predict_for_data.predict_condition(engine_rpm, lub_oil_pressure, fuel_pressure, coolant_pressure, lub_oil_temp, coolant_temp, temp_difference)
            data = {
                'vehicle_name': vehicle_name,
                'engine_rpm': engine_rpm,
                'lub_oil_pressure': lub_oil_pressure,
                'fuel_pressure': fuel_pressure,
                'coolant_pressure': coolant_pressure,
                'lub_oil_temp': lub_oil_temp,
                'coolant_temp': coolant_temp,
                'temp_difference': temp_difference
            }
            insights = ""
            # Display results
            if confidence > 0.7:
                st.success(f"The engine is predicted to be in a normal condition. Confidence level: {1.0 - confidence:.2%}")
            else:
                st.warning(f"Warning! Please investigate further. Confidence level: {1.0 - confidence:.2%}")
                insights = generate_ai_insights.generate_insights(data, result, confidence)
                st.warning(insights)



    col1, col2= st.columns([1.5,1.75])

    # Placeholders for the subheaders
    with col1:
        col1.subheader("Real-Time Data From Automotive IoT Device")
        # headers = ["Vehicle Name", "Lub Oil Pressure", "Fuel Pressure", "Coolant Pressure", "Lub Oil Temp", "Coolant Temp", "Temp Difference", "Result", "Action"]
        # cols = st.columns((1, 1, 1, 1, 1, 1, 1, 1, 1))
        # for col, header in zip(cols, headers):
        #     col.write(f"**{header}**")
        # col1.info("Pushed to  Cloud Kafka from End Device's MQTT topic")
    with col2:
        col2.header("Real Time Data Monitoring")
        vehicle_name = st.selectbox("Select Available Vehicle", ["mercedessclass", "bmwm2"])
        time_series_placeholder = st.empty()
        insights_placeholder = st.empty()
        # insights_placeholder.subheader("Gen AI Insight for the latest Data")


    st.markdown(
        """
        <style>
            .footer {
                position: fixed;
                left: 0;
                bottom: 0;
                width: 100%;
                background-color: white;
                color: black;
                text-align: center;
                padding: 20px;
                border-top: 1px solid #eaeaea;
            }
            .footer img {
                position: absolute;
                right: 10px;
                bottom: 10px;
                width: 50px;  /* Adjust the size as needed */
            }
        </style>
        <div class="footer">
            <b> <i>RevAI-lutionaries 2024</i> : Isaac, Pramod, Chandra Mani, Santhosh</b>
        </div>
        """,
        unsafe_allow_html=True
    )
    # Placeholders for the values
    data_placeholder = col1.empty()

    data_list = []
    result_list = []
    confidence_list = []
    rpmList = []
    vehicle_name_list = []

    with col1:
        data_placeholder.subheader("Data :-")
    

    while True:
        fetched_data_json = kafka_cloud_consumer.get_latest_message()
        if fetched_data_json:
            print("Fetched data (JSON string):", fetched_data_json, type(fetched_data_json))

            # Parse the JSON string back to a dictionary
            fetched_data = json.loads(fetched_data_json)
            print("Fetched data (parsed dictionary):", fetched_data, type(fetched_data))

            # Append new data to the lists

            res1, conf1 = kafka_cloud_consumer.predictForThis(fetched_data_json)
            fetched_data['Result'] = 'Normal' if res1 == 0 else 'Warning'
            fetched_data['Confidence'] = f"{1.0 - conf1:.2%}"
            data_list.append(fetched_data)
            rpmList.append(fetched_data['engine_rpm'])
            vehicle_name_list.append(fetched_data['vehicle_name'])

            result_list.append(f"Result: {'Normal' if res1 == 0 else 'Warning'}")
            confidence_list.append(f"Confidence: {1.0 - conf1:.2%}")


            with data_placeholder:
                df_data_list = pd.DataFrame(data_list)
                st.table(df_data_list)

            insights = ""
            print("conf")
            print(conf1)
            if conf1 > 0.3 and res1 != 0:     
                insights = generate_ai_insights.generate_insights(fetched_data, res1, conf1)
                # alert_user.show_warning_and_report(insights)
            else:
                # insights = generate_ai_insights.generate_insights(fetched_data, res1, conf1)
                insights = "Engine in Normal Condition"

            insights_list.append(insights)


            df_results_confidence_insights = pd.DataFrame({
                "Gen AI Insight": insights_list
            })

            with insights_placeholder:
                with st.expander("Gen AI Insight for the latest Data", expanded=False):
                    st.text_area("Gen AI Insight", df_results_confidence_insights.iloc[-1]['Gen AI Insight'], height=500,key=time.time())
                    generate_and_download_pdf(fetched_data,df_results_confidence_insights.iloc[-1]['Gen AI Insight'], "report.pdf")
                    # alertUser()
                    # if st.session_state.alert_edge_device:
                    #     print("inside alert")
                    #     alert_user.show_warning_and_report(df_results_confidence_insights.iloc[-1]['Gen AI Insight'])
                    #     st.session_state.alert_edge_device = False


            # df_rpm = pd.DataFrame({'RPM': rpmList, 'Time': range(len(rpmList))})
            # fig = px.line(df_rpm, x='Time', y='RPM', title='RPM Data Recieved over Time', hover_data={'RPM': True, 'Time': False})
            # fig.update_traces(hovertemplate='Time: %{x}<br>RPM: %{y}<extra></extra>')
            # time_series_placeholder.plotly_chart(fig)
            df_rpm = pd.DataFrame({'RPM': rpmList, 'Time': range(len(rpmList)), 'VehicleName': vehicle_name_list})

            # Filter the DataFrame for a specific vehicle name, e.g., 'Vehicle1'
            filtered_df = df_rpm[df_rpm['VehicleName'] == vehicle_name]

            # Plot the filtered data
            # fig = px.line(filtered_df, x='Time', y='RPM', title=f'RPM Data for {vehicle_name} over Time', hover_data={'RPM': True, 'Time': False})
            # fig.update_traces(hovertemplate='Time: %{x}<br>RPM: %{y}<extra></extra>')
            # time_series_placeholder.plotly_chart(fig)
            fig = px.line(filtered_df, x='Time', y='RPM', title=f'RPM Data for {vehicle_name} over Time', hover_data={'RPM': True, 'Time': False})
            fig.update_traces(hovertemplate='Time: %{x}<br>RPM: %{y}<extra></extra>')

            # Identify dips in RPM values
            dips = filtered_df[filtered_df['RPM'] < filtered_df['RPM'].shift(1)]

            # Add scatter plot for dips
            fig.add_trace(go.Scatter(
                x=dips['Time'],
                y=dips['RPM'],
                mode='markers',
                marker=dict(color='red', size=10),
                name='Dip'
            ))

            # for index, row in pd.DataFrame(data_list).iterrows():
            #     # cols = st.columns((1, 1, 1, 1, 1, 1, 1, 1))  # Adjust the number of columns as needed
            #     max_chars = 10
            #     vehicle_name = truncate_text(row['vehicle_name'], max_chars)
            #     lub_oil_pressure = truncate_text(row['lub_oil_pressure'], max_chars)
            #     fuel_pressure = truncate_text(row['fuel_pressure'], max_chars)
            #     coolant_pressure = truncate_text(row['coolant_pressure'], max_chars)
            #     lub_oil_temp = truncate_text(row['lub_oil_temp'], max_chars)
            #     coolant_temp = truncate_text(row['coolant_temp'], max_chars)
            #     temp_difference = truncate_text(row['temp_difference'], max_chars)
            #     result = truncate_text(row['Result'], max_chars)
            #     cols[0].markdown(f"<div style='border: 1px solid black; padding: 5px;'>{vehicle_name}</div>", unsafe_allow_html=True)
            #     cols[1].markdown(f"<div style='border: 1px solid black; padding: 5px;'>{lub_oil_pressure}</div>", unsafe_allow_html=True)
            #     cols[2].markdown(f"<div style='border: 1px solid black; padding: 5px;'>{fuel_pressure}</div>", unsafe_allow_html=True)
            #     cols[3].markdown(f"<div style='border: 1px solid black; padding: 5px;'>{coolant_pressure}</div>", unsafe_allow_html=True)
            #     cols[4].markdown(f"<div style='border: 1px solid black; padding: 5px;'>{lub_oil_temp}</div>", unsafe_allow_html=True)
            #     cols[5].markdown(f"<div style='border: 1px solid black; padding: 5px;'>{coolant_temp}</div>", unsafe_allow_html=True)
            #     cols[6].markdown(f"<div style='border: 1px solid black; padding: 5px;'>{temp_difference}</div>", unsafe_allow_html=True)
            #     cols[7].markdown(f"<div style='border: 1px solid black; padding: 5px;'>{result}</div>", unsafe_allow_html=True)
            #     modal_key = f"modal_{index}" 
            #     button_key = f"button_{index}"
            #     modal = Modal(f"Data ", key=modal_key)
            #     if row["Result"] == "Warning":
            #         if cols[8].button(f"Gen Report", key=button_key):
            #             modal.open()

            #         if modal.is_open():
            #             with modal.container():
            #                 st.write(insights)
                            
            #                 html_string = '''
            #                 <script language="javascript">
            #                 document.querySelector("h1").style.color = "red";
            #                 </script>
            #                 '''
            #                 components.html(html_string)
            #     else:
            #         cols[8].markdown(f"<div style='border: 1px solid black; padding: 5px;'>{"------------"}</div>", unsafe_allow_html=True)

            time_series_placeholder.plotly_chart(fig)

        time.sleep(20)

    


if __name__ == "__main__":
    main()