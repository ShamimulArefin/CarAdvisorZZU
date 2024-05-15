import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder
import joblib

# load model
with open('modelprice.pkl', 'rb') as file:
    price_model = joblib.load(file)

label_reg = pd.read_csv('le_vehicle_data.csv')

le_manufacturer = LabelEncoder()
le_fuel = LabelEncoder()
le_transmission = LabelEncoder()
le_condition = LabelEncoder()
le_drive = LabelEncoder()
le_type = LabelEncoder()
le_title_status = LabelEncoder()
le_model = LabelEncoder()

label_reg["manufacturer"] = le_manufacturer.fit_transform(label_reg['manufacturer'])
label_reg["fuel"] = le_fuel.fit_transform(label_reg['fuel'])
label_reg["title_status"] = le_title_status.fit_transform(label_reg['title_status'])
label_reg['transmission'] = le_transmission.fit_transform(label_reg['transmission'])
label_reg['condition'] = le_condition.fit_transform(label_reg['condition'])
label_reg['drive'] = le_drive.fit_transform(label_reg['drive'])
label_reg["type"] = le_type.fit_transform(label_reg['type'])
label_reg['model'] = le_model.fit_transform(label_reg['model'])

def price_prediction(features):
    x = np.array([tuple(features)])
    #convert input using LabelEncoder
    le_reg = [np.nan, np.nan, np.nan, le_manufacturer, le_model, le_fuel, le_title_status, le_transmission, le_condition, le_drive, le_type]
    
    for i in range(3,11):
        x[:,i] = le_reg[i].transform(x[:,i])
        x
    
    prediction = price_model.predict(x)
    predicted_price = round(prediction[0], 2)

    return predicted_price