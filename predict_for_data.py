import pickle
import numpy as np 

with open('model.pkl', 'rb') as file:
    model = pickle.load(file)

def predict_condition(engine_rpm, lub_oil_pressure, fuel_pressure, coolant_pressure, lub_oil_temp, coolant_temp, temp_difference):
    input_data = np.array([engine_rpm, lub_oil_pressure, fuel_pressure, coolant_pressure, lub_oil_temp, coolant_temp, temp_difference]).reshape(1, -1)
    prediction = model.predict(input_data)
    confidence = model.predict_proba(input_data)[:, 1]
    
    return prediction[0], confidence[0]