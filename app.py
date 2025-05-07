import numpy as np
import pandas as pd
import pickle
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

# Load models
models = {
    "logistic": pickle.load(open("logistic_model.pkl", "rb")),
    "decision_tree": pickle.load(open("decision_tree_model.pkl", "rb")),
    "random_forest": pickle.load(open("random_forest_model.pkl", "rb")),
}

# Function to preprocess input
def preprocess_input(data):
    df = pd.DataFrame([data])
    
    # Convert Dependents "3+" to 3
    df["Dependents"] = df["Dependents"].replace("3+", 3).astype(float)
    
    # Compute new features
    df["EMI"] = df["LoanAmount"] / df["Loan_Amount_Term"]
    df["Balance Income"] = df["ApplicantIncome"] + df["CoapplicantIncome"] - (df["EMI"] * 1000)
    df["LoanAmount_log"] = np.log(df["LoanAmount"] + 1)
    df["Total_Income"] = df["ApplicantIncome"] + df["CoapplicantIncome"]
    df["Total_Income_log"] = np.log(df["Total_Income"] + 1)
    
    # One-hot encoding categorical variables
    categorical_features = ["Gender", "Married", "Education", "Self_Employed", "Property_Area"]
    df = pd.get_dummies(df, columns=categorical_features)
    
    # Ensure all required columns exist
    model_features = [
        "Dependents", "ApplicantIncome", "CoapplicantIncome", "LoanAmount", "Loan_Amount_Term", "Credit_History",
        "LoanAmount_log", "Total_Income", "Total_Income_log", "EMI", "Balance Income",
        "Gender_Female", "Gender_Male", "Married_No", "Married_Yes",
        "Education_Graduate", "Education_Not Graduate",
        "Self_Employed_No", "Self_Employed_Yes", "Property_Area_Rural",
        "Property_Area_Semiurban", "Property_Area_Urban"
    ]
    
    # Add missing columns and ensure correct order
    for feature in model_features:
        if feature not in df.columns:
            df[feature] = 0
    
    return df[model_features]  # Ensure correct feature order


@app.route("/")
def home():
    return render_template("index.html")


@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()
        print("Received Data:", data)  # Debugging

        # Ensure model_type is provided
        model_type = data.get("model_type")
        if not model_type:
            return jsonify({"status": "error", "error": "Model type is required"}), 400

        # Load the selected model
        model = models.get(model_type)
        if model is None:
            return jsonify({"status": "error", "error": f"Invalid model type: {model_type}"}), 400

        # Preprocess input data
        input_data = preprocess_input(data)  
        print("Processed Input Data:", input_data)  # Debugging

        # Make prediction
        prediction = model.predict(input_data)[0]

        # Calculate probability (if supported by model)
        if hasattr(model, "predict_proba"):
            probability = model.predict_proba(input_data)[0][1] * 100
        else:
            probability = 0.00  # Default to 0 if predict_proba is unavailable

        # Convert prediction to human-readable format
        result = "Approved" if prediction == 1 else "Rejected"

        return jsonify({
            "status": "success",
            "prediction": result,
            "probability": f"{probability:.2f}%"
        })

    except Exception as e:
        print("Error:", str(e))  # Debugging
        return jsonify({"status": "error", "error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
