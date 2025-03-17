from kafka import KafkaConsumer
import json
import app_ui
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from fpdf import FPDF

try:
    consumer = KafkaConsumer(
        'streamingsource',
        bootstrap_servers=['localhost:9092'],
        auto_offset_reset='earliest',
        enable_auto_commit=True
    )
    print("Kafka consumer connected successfully.")
except Exception as e:
    print(f"Error connecting Kafka consumer: {e}")


def predictForThis(data):
    try:
        data_dict = json.loads(data)
        engine_rpm = data_dict.get('engine_rpm', None)
        lub_oil_pressure = data_dict.get('lub_oil_pressure', None)
        fuel_pressure = data_dict.get('fuel_pressure', None)
        coolant_pressure = data_dict.get('coolant_pressure', None)
        lub_oil_temp = data_dict.get('lub_oil_temp', None)
        coolant_temp = data_dict.get('coolant_temp', None)
        temp_difference = data_dict.get('temp_difference', None)
        
        if None in [engine_rpm, lub_oil_pressure, fuel_pressure, coolant_pressure, lub_oil_temp, coolant_temp, temp_difference]:
            raise ValueError("Missing or invalid data fields")

        result, confidence = app_ui.predict_condition(
            engine_rpm, lub_oil_pressure, fuel_pressure, coolant_pressure,
            lub_oil_temp, coolant_temp, temp_difference
        )
        print("Result: ", result)
        print("Confidence: ", confidence)
        return result, confidence

    except json.JSONDecodeError:
        print("Error decoding JSON data")
    except ValueError as ve:
        print(f"ValueError: {ve}")
    except Exception as e:
        print(f"Unexpected error: {e}")
    
def fetch_all_entries():
    print("Fetching all data from Kafka...")
    all_messages = []
    count = 0
    try:
        for message in consumer:
            data = message.value.decode('utf-8')
            print(f"Received data: {data}")
            if str(data).__contains__("rpm"):
                all_messages.append(data)
                count +=1
                result, confidence = predictForThis(data)
                print("Result: ", result)
                print("Confidence: ", confidence)
                if count > 10:
                    time.sleep(180)
                    count = 0
                continue
            
    except Exception as e:
        print(f"Error fetching data from Kafka: {e}")

    return all_messages

all_messages = fetch_all_entries()
    
# def generate_insights(data_dict, result, confidence):
#     api_url = "https://api-inference.huggingface.co/models/your-model"
#     headers = {"Authorization": "Bearer "}  

#     # Prepare the input for the model
#     input_data = {
#         "engine_rpm": data_dict['engine_rpm'],
#         "lub_oil_pressure": data_dict['lub_oil_pressure'],
#         "fuel_pressure": data_dict['fuel_pressure'],
#         "coolant_pressure": data_dict['coolant_pressure'],
#         "lub_oil_temp": data_dict['lub_oil_temp'],
#         "coolant_temp": data_dict['coolant_temp'],
#         "temp_difference": data_dict['temp_difference'],
#         "result": result,
#         "confidence": confidence
#     }
    
#     response = requests.post(api_url, headers=headers, json=input_data)
#     if response.status_code == 200:
#         insights = response.json().get('generated_text', "No insights generated.")
#     else:
#         insights = "Error generating insights"
    
#     print("Generated Insights: ", insights)

#     return insights


# def generate_pdf_report(data_dict, result, confidence, insights):
#     pdf = FPDF()
#     pdf.add_page()
    
#     # Set title
#     pdf.set_font("Arial", 'B', 16)
#     pdf.cell(0, 10, 'Engine Condition Report', 0, 1, 'C')
    
#     # Add data to PDF
#     pdf.set_font("Arial", size=12)
#     pdf.cell(0, 10, f"Engine RPM: {data_dict['engine_rpm']}", 0, 1)
#     pdf.cell(0, 10, f"Lub Oil Pressure: {data_dict['lub_oil_pressure']}", 0, 1)
#     pdf.cell(0, 10, f"Fuel Pressure: {data_dict['fuel_pressure']}", 0, 1)
#     pdf.cell(0, 10, f"Coolant Pressure: {data_dict['coolant_pressure']}", 0, 1)
#     pdf.cell(0, 10, f"Lub Oil Temperature: {data_dict['lub_oil_temp']}", 0, 1)
#     pdf.cell(0, 10, f"Coolant Temperature: {data_dict['coolant_temp']}", 0, 1)
#     pdf.cell(0, 10, f"Temperature Difference: {data_dict['temp_difference']}", 0, 1)
#     pdf.cell(0, 10, f"Prediction Result: {result}", 0, 1)
#     pdf.cell(0, 10, f"Confidence: {confidence}", 0, 1)
    
#     # Highlight insights in the PDF
#     pdf.cell(0, 10, "Insights:", 0, 1)
#     pdf.multi_cell(0, 10, insights)

#     # Save PDF
#     pdf_file_name = f"engine_report_{data_dict['timestamp']}.pdf"
#     pdf.output(pdf_file_name)
#     print(f"PDF report generated: {pdf_file_name}")