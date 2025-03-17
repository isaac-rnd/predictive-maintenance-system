# import random
import requests
from fpdf import FPDF

def generate_insights(data_dict, result, confidence):
    api_url = "https://api.cohere.ai/generate"
    headers = {
        "Authorization": "Bearer mnrOpaYGZCOEzbFPJV1OL5c8Nhk2GeCHwFNRpIMX",
        "Content-Type": "application/json"
    }

    # Prepare the input for the model
    input_data = {
        "engine_rpm": data_dict['engine_rpm'],
        "lub_oil_pressure": data_dict['lub_oil_pressure'],
        "fuel_pressure": data_dict['fuel_pressure'],
        "coolant_pressure": data_dict['coolant_pressure'],
        "lub_oil_temp": data_dict['lub_oil_temp'],
        "coolant_temp": data_dict['coolant_temp'],
        "temp_difference": data_dict['temp_difference'],
        "result": result,
        "confidence": confidence
    }


    prompt = f"""
    Here is the latest engine sensor data:
    - Engine RPM: {input_data['engine_rpm']}
    - Lubrication Oil Pressure: {input_data['lub_oil_pressure']} bar
    - Fuel Pressure: {input_data['fuel_pressure']} bar
    - Coolant Pressure: {input_data['coolant_pressure']} bar
    - Lubrication Oil Temperature: {input_data['lub_oil_temp']} °C
    - Coolant Temperature: {input_data['coolant_temp']} °C
    - Temperature Difference: {input_data['temp_difference']} °C
    The system evaluated the data and returned a result of "{input_data['result']}" with a confidence score of {input_data['confidence']}. 
    Please provide a brief analysis of this data with the following sections:
    1. Overview: Summarize engine performance in one sentence.
    2. Potential Issues: Highlight any abnormal readings and their likely causes in one concise sentence.
    3. Maintenance Suggestions: Provide one or two actionable maintenance steps based on the data.
    4. Final Recommendation: Summarize the overall status and next steps in one brief statement.
    Make sure the analysis is always concise, insightful, short and follows this structured format with the headings as such and the points within.
    dont't even aything else to the end like what more can i do or help kind of things just finish after the final recommendation.
    """
    data = {
        # "model": "command-xlarge-20221108",  # or "medium" as per your needs
        "prompt": prompt,
        "max_tokens": 500,
        "temperature": 0.7
    }

    # Make the request to the Cohere API
    try:
        response = requests.post(api_url, headers=headers, json=data, verify=False) 
        response_data = response.json()
        print("API Response: ", response_data)
        
        if response.status_code == 200:
            # Accessing the text directly from the response
            insights = response_data.get('text', '').strip()
        else:
            insights = "Error generating insights: " + response_data.get('error', 'Unknown error')
    except Exception as e:
        insights = "Error generating insights: " + str(e)
    
    print("Generated Insights: ", insights)
    return insights

def generate_pdf_report(data_dict, insights, output_path='report.pdf'):
    pdf = FPDF()
    pdf.add_page()

    # Add Company Logo
    pdf.image('msg_logo.png', x=10, y=8, w=33)  # Adjust the path and size as needed
    pdf.set_font("Arial", 'B', 16)

    def safe_text(text):
        return text.encode('latin-1', 'replace').decode('latin-1')
    
    pdf.cell(0, 10, 'Predictive Maintenance Prediction Report', 0, 1, 'C')
    pdf.ln(10)
        # Create a table for engine condition data
    pdf.set_font("Arial", size=12)
    pdf.cell(60, 10, "Parameter", 1, 0, 'C')
    pdf.cell(60, 10, "Value", 1, 1, 'C')  # Table headers

    # Engine Condition Data in a tabular format
    pdf.cell(60, 10, "Vehicle", 1)
    pdf.cell(60, 10, f"{data_dict['vehicle_name']}", 1, 1, '')

    pdf.cell(60, 10, "Engine RPM", 1)
    pdf.cell(60, 10, f"{data_dict['engine_rpm']}", 1, 1, 'C')
    
    pdf.cell(60, 10, "Lub Oil Pressure", 1)
    pdf.cell(60, 10, f"{data_dict['lub_oil_pressure']:.4f} bar", 1, 1, 'C')
    
    pdf.cell(60, 10, "Fuel Pressure", 1)
    pdf.cell(60, 10, f"{data_dict['fuel_pressure']:.4f} bar", 1, 1, 'C')
    
    pdf.cell(60, 10, "Coolant Pressure", 1)
    pdf.cell(60, 10, f"{data_dict['coolant_pressure']:.4f} bar", 1, 1, 'C')
    
    pdf.cell(60, 10, "Lub Oil Temperature", 1)
    pdf.cell(60, 10, f"{data_dict['lub_oil_temp']:.4f} °C", 1, 1, 'C')
    
    pdf.cell(60, 10, "Coolant Temperature", 1)
    pdf.cell(60, 10, f"{data_dict['coolant_temp']:.4f} °C", 1, 1, 'C')
    
    pdf.cell(60, 10, "Temperature Difference", 1)
    pdf.cell(60, 10, f"{data_dict['temp_difference']:.4f} °C", 1, 1, 'C')
  # Add space after title
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, 'Insights', 0, 1, 'C')
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, safe_text(insights))
    pdf.ln(5)  # Add space after table

    # Save the PDF to a file
    pdf.output(output_path)

    return output_path


# Randomly generate data for testing
# result = "Normal" if random.random() > 0.5 else "Alert"
# confidence = random.uniform(0.8, 1.0)
# data = {
#     'engine_rpm': random.uniform(600, 3000),
#     'lub_oil_pressure': random.uniform(1.0, 5.0),
#     'fuel_pressure': random.uniform(1.0, 5.0),
#     'coolant_pressure': random.uniform(1.0, 5.0),
#     'lub_oil_temp': random.uniform(70.0, 120.0),
#     'coolant_temp': random.uniform(70.0, 120.0),
#     'temp_difference': random.uniform(0.0, 50.0)
# }

# insights = generate_insights(data, result, confidence)
# Optionally call generate_pdf_report here as before
# generate_pdf_report(data, result, confidence, insights)