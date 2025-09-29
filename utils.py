import pandas as pd
import tempfile
import csv
import json
from groq import Groq
import os
from datetime import datetime

def preprocess_and_save(file):
    try:
        if file.filename.endswith('.csv'):
            df = pd.read_csv(file, encoding='utf-8', na_values=['NA', 'N/A', 'missing'])
        elif file.filename.endswith('.xlsx'):
            df = pd.read_excel(file, na_values=['NA', 'N/A', 'missing'])
        else:
            return None, None, None, "Unsupported file format."

        # Data cleaning
        for col in df.select_dtypes(include=['object']):
            df[col] = df[col].astype(str).replace({r'"': '""'}, regex=True)

        for col in df.columns:
            if 'date' in col.lower():
                df[col] = pd.to_datetime(df[col], errors='coerce')
            elif df[col].dtype == 'object':
                try:
                    df[col] = pd.to_numeric(df[col])
                except:
                    pass

        with tempfile.NamedTemporaryFile(delete=False, suffix=".csv", mode='w', newline='', encoding='utf-8') as temp_file:
            df.to_csv(temp_file.name, index=False, quoting=csv.QUOTE_ALL)
            return df, df.columns.tolist(), df.to_html(classes='table table-striped', index=False), None
    except Exception as e:
        return None, None, None, str(e)

def generate_insights(df):
    try:
        client = Groq(api_key=os.getenv('GROQ_API_KEY'))
        
        prompt = f"""
        Given the following dataset with columns: {list(df.columns)}, provide key insights:
        - Data quality issues
        - Interesting patterns
        - Statistical summary
        - Potential analysis opportunities
        - Data cleaning suggestions
        
        Return as a structured JSON with these sections.
        Dataset sample: {df.head().to_string()}
        """
        
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"}
        )
        
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        return {"error": str(e)}

def save_analysis_history(entry):
    try:
        with open('analysis_history.json', 'r') as f:
            history = json.load(f)
    except:
        history = []
    
    history.append(entry)
    
    with open('analysis_history.json', 'w') as f:
        json.dump(history[-50:], f, indent=2)  