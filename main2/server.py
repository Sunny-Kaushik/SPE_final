from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import pandas as pd
from transformers import AutoTokenizer, AutoModelForCausalLM
import uvicorn
# Initialize FastAPI app
app = FastAPI()

# Add CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow requests from all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all HTTP headers
)

# Load models
tokenizer = AutoTokenizer.from_pretrained("23tanmay/BioDistillGPT2")
model = AutoModelForCausalLM.from_pretrained("23tanmay/BioDistillGPT2")

# Load datasets
df = pd.read_csv("disease_description.csv")
specialist_df = pd.read_csv("specialist_description.csv")

score_metrics = {
    'disease': 4,
    'Symptom': 2,
    'reason': 1,
    'TestsAndProcedures': 1,
    'commonMedications': 1
}

# Utility function to calculate relevance scores
def calculate_relevance_score(keyword, column_value, column_name):
    if isinstance(column_value, list):
        for item in column_value:
            if keyword in item:
                return score_metrics[column_name]  # Return score metric for the column
    else:
        if keyword in str(column_value):
            return score_metrics[column_name]  # Return score metric for the column
    return 0  # Return 0 if keyword not found in the column


# Specialist scoring function
def get_specialists(response_string):
    response_words = response_string.lower().split()
    total_scores = []

    # Iterate through each row of the DataFrame
    for index, row in df.iterrows():
        total_score = 0
        for keyword in response_words:
            for column_name in df.columns:
                if column_name != 'idx':  # Exclude the 'idx' column
                    column_value = row[column_name]
                    score = calculate_relevance_score(keyword, column_value, column_name)
                    total_score += score
        total_scores.append(total_score)

    df['Total_Score'] = total_scores
    updated_df = df.sort_values(by="Total_Score", ascending=False)

    # Initialize a dictionary to store scores for each specialist
    scores = {}

    for word in response_words:
        for index, row in specialist_df.iterrows():
            if word == row['Speciality'].lower() and word not in ["medicine", "and"]:
                scores[row['Speciality']] = scores.get(row['Speciality'], 0) + 1000
            elif row['Speciality'].lower().endswith("ogy"):
                specialty_term = row['Speciality'].lower()[:-3] + "ogist"
                if specialty_term in response_string.lower():
                    scores[row['Speciality']] = scores.get(row['Speciality'], 0) + 1000

    for index, row in specialist_df.iterrows():
        description_words = row['Description'].lower().split()
        for word in description_words:
            if word in response_words:
                scores[row['Speciality']] = scores.get(row['Speciality'], 0) + 5

    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)

    return sorted_scores[:3]


# Define input schema
class SymptomRequest(BaseModel):
    symptoms: str


@app.get("/")
def home():
    return {"message": "API is running. Access the endpoint at /get-specialists."}


@app.post("/get-specialists/")
def get_specialists_route(request: SymptomRequest):
    user_input = request.symptoms
    if not user_input:
        raise HTTPException(status_code=400, detail="No symptoms provided.")

    input_ids = tokenizer.encode(user_input, return_tensors="pt")
    output_ids = model.generate(
        input_ids,
        max_length=800,
        num_return_sequences=3,
        top_p=0.95,
        top_k=50,
        do_sample=True
    )
    response = tokenizer.decode(output_ids[0], skip_special_tokens=True)
    response2 = tokenizer.decode(output_ids[1], skip_special_tokens=True)
    response3 = tokenizer.decode(output_ids[2], skip_special_tokens=True)
    response_string = response + response2 + response3

    specialists = get_specialists(response_string)
    return {"specialists": specialists}


if __name__ == "__main__":
   
    uvicorn.run(app, host="0.0.0.0", port=8082)
