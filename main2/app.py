from flask import Flask, request, jsonify
import pandas as pd
from transformers import AutoTokenizer, AutoModelForCausalLM
import spacy

# Initialize Flask app
app = Flask(__name__)

# Load models
# nlp = spacy.load("en_core_web_sm", disable=("parser",))
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
        # Initialize total score for the current row
        total_score = 0
        
        # Calculate relevance score for each keyword in each column
        for keyword in response_string:
            for column_name in df.columns:
                if column_name != 'idx':  # Exclude the 'idx' column
                    column_value = row[column_name]
                    score = calculate_relevance_score(keyword, column_value, column_name)
                    total_score += score
        
        # Append total score for the current row
        total_scores.append(total_score)

    # Append total scores to the DataFrame
    df['Total_Score'] = total_scores

    # Save the updated DataFrame to a CSV file
    df.to_csv('updated_dataframe.csv', index=False)
    updated_df=pd.read_csv("updated_dataframe.csv")

    # Initialize a dictionary to store scores for each specialist
    scores = {}

    # Split the response string into words and convert to lowercase
    response_words = response_string.lower().split()

    # Iterate over each word in the response string
    for word in response_words:
        # Check if the word is in the "Speciality" column of speciality_df
        for index, row in specialist_df.iterrows():
            if word == row['Speciality'].lower() and word != "medicine" and word!="and":
                # Increment score by 1000
                scores[row['Speciality']] = scores.get(row['Speciality'], 0) + 1000
            elif row['Speciality'].lower().endswith("ogy"):
                # Check if the specialty ends with "ogy" and the corresponding term is in the response string
                specialty_term = row['Speciality'].lower()[:-3] + "ogist"
                if specialty_term in response_string.lower():
                    scores[row['Speciality']] = scores.get(row['Speciality'], 0) + 1000

    # Iterate over each description in speciality_df
    for index, row in specialist_df.iterrows():
        description_words = row['Description'].lower().split()
        # Count occurrences of each word in the response string
        for word in description_words:
            if word in response_words:
                # Increase score by 5 for each hit
                scores[row['Speciality']] = scores.get(row['Speciality'], 0) + 5

    # Sort specialists based on scores
    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)

    return sorted_scores[:3]

# Flask API endpoint
@app.route("/get-specialists", methods=["POST"])
def get_specialists_route():
    user_input = request.json.get("symptoms", "")
    if not user_input:
        return jsonify({"error": "No symptoms provided"}), 400

    input_ids = tokenizer.encode(user_input, return_tensors="pt")
    output_ids = model.generate(
        input_ids, 
        max_length=800,
        num_return_sequences=3,
        # no_repeat_ngram_size=2,
        # temperature=0.7,
        top_p=0.95,
        top_k=50,
        do_sample=True
    )
    response = tokenizer.decode(output_ids[0], skip_special_tokens=True)
    response2=tokenizer.decode(output_ids[1], skip_special_tokens=True)
    response3=tokenizer.decode(output_ids[2], skip_special_tokens=True)
    # print("Input Prompt:", input_prompt)
    # print("response 1: ", response)
    # print("response 2: ",response2)
    # print("response 3: ",response3)
    response_string = response+response2+response3
    specialists = get_specialists(response)

    return jsonify({"specialists": specialists})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8082)