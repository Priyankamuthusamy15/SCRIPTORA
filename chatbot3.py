from flask import Flask, render_template, request, jsonify
from fuzzywuzzy import fuzz
import requests
import os
from dotenv import load_dotenv

app = Flask(__name__)
load_dotenv()

drug_database = {
    "paracetamol": "Paracetamol is used for pain and fever. Usual dose: 500-1000mg. Max: 4000mg/day.",
    "ibuprofen": "Ibuprofen is an NSAID for pain and inflammation. Usual dose: 200-400mg every 6h.",
    "aspirin": "Aspirin relieves pain and helps heart health. Risk of stomach upset and Reye's syndrome.",
    "amoxicillin": "Amoxicillin is an antibiotic. Take full course to prevent resistance."
}

def fuzzy_match(query):
    max_score = 0
    best_match = None
    for drug in drug_database:
        score = fuzz.partial_ratio(query.lower(), drug.lower())
        if score > max_score and score > 70:
            max_score = score
            best_match = drug
    return best_match

def fetch_rxnorm_info(drug_name):
    try:
        url = f"https://rxnav.nlm.nih.gov/REST/approximateTerm.json?term={drug_name}"
        response = requests.get(url)
        data = response.json()
        if data["approximateGroup"]["candidate"]:
            return data["approximateGroup"]["candidate"][0]["name"]
    except Exception as e:
        print("RxNorm error:", e)
    return None

def fetch_openfda_info(drug_name):
    try:
        fda_url = f"https://api.fda.gov/drug/label.json?search=openfda.generic_name:\"{drug_name}\"&limit=1"
        response = requests.get(fda_url)
        data = response.json()
        if data["results"]:
            r = data["results"][0]
            return {
                "indications": r.get("indications_and_usage", ["Not available"])[0],
                "dosage": r.get("dosage_and_administration", ["Not available"])[0],
                "warnings": r.get("warnings", ["Not available"])[0]
            }
    except Exception as e:
        print("OpenFDA error:", e)
    return None

@app.route("/")
def index():
    return render_template("index11.html")

@app.route("/ask", methods=["POST"])
def ask():
    user_input = request.json.get("query", "")
    if not user_input:
        return jsonify({"response": "Please enter a medicine name."})

    # 1. Exact match
    for name, info in drug_database.items():
        if name in user_input.lower():
            return jsonify({"response": info})

    # 2. Fuzzy match
    match = fuzzy_match(user_input)
    if match:
        return jsonify({"response": f"I think you meant {match}. {drug_database[match]}"})

    # 3. RxNorm + OpenFDA fallback
    drug_from_rx = fetch_rxnorm_info(user_input)
    if drug_from_rx:
        fda_data = fetch_openfda_info(drug_from_rx)
        if fda_data:
            return jsonify({
                "response": f"Here’s info about {drug_from_rx}:\n\n"
                            f"{fda_data['indications']}\n\n"
                            f"{fda_data['dosage']}\n\n"
                            f"Warnings: {fda_data['warnings']}"
            })

    return jsonify({"response": "Sorry, I couldn't find any information on that drug. Please check the spelling or try a generic name."})

if __name__ == "__main__":
    app.run(debug=True)
