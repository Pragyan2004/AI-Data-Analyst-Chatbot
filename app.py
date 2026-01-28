<<<<<<< HEAD
from flask import Flask, render_template, request, session, jsonify, flash
from utils import preprocess_and_save, generate_insights, save_analysis_history
import pandas as pd
from groq import Groq
import os
from dotenv import load_dotenv
import json
from datetime import datetime, timezone
from dateutil import relativedelta

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'dev-secret-key')
@app.template_filter('datetime')
def format_datetime(value, format='%Y-%m-%d %H:%M:%S'):
    """Format a datetime object or ISO string to readable format"""
    if isinstance(value, str):
        try:
            value = datetime.fromisoformat(value.replace('Z', '+00:00'))
        except:
            return value
    if isinstance(value, datetime):
        return value.strftime(format)
    return value

@app.template_filter('time_ago')
def time_ago_filter(value):
    """Convert datetime to human-readable time ago format"""
    if isinstance(value, str):
        try:
            value = datetime.fromisoformat(value.replace('Z', '+00:00'))
        except:
            return value
    
    if not isinstance(value, datetime):
        return value
    
    now = datetime.now(timezone.utc) if value.tzinfo else datetime.now()
    diff = relativedelta.relativedelta(now, value)
    
    if diff.years > 0:
        return f"{diff.years} year{'s' if diff.years > 1 else ''} ago"
    elif diff.months > 0:
        return f"{diff.months} month{'s' if diff.months > 1 else ''} ago"
    elif diff.days > 0:
        return f"{diff.days} day{'s' if diff.days > 1 else ''} ago"
    elif diff.hours > 0:
        return f"{diff.hours} hour{'s' if diff.hours > 1 else ''} ago"
    elif diff.minutes > 0:
        return f"{diff.minutes} minute{'s' if diff.minutes > 1 else ''} ago"
    else:
        return "Just now"

@app.template_filter('first')
def first_filter(value):
    """Get first element of iterable"""
    if hasattr(value, '__iter__') and not isinstance(value, str):
        try:
            return next(iter(value))
        except:
            return value
    return value
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

@app.route("/analyze", methods=["GET", "POST"])
def analyze():
    if request.method == "POST":
        file = request.files.get("file")
        query = request.form.get("query")
        
        if not file:
            return jsonify({"error": "Please upload a file"})
        
        df, cols, df_html, err = preprocess_and_save(file)
        if err:
            return jsonify({"error": err})
        
        session['current_df'] = df.to_json()
        session['columns'] = cols
        
        if query:
            try:
                prompt = f"""
You are a Python data analyst. Given a pandas DataFrame named `df`, write Python code using pandas to answer this question:

Question: {query}

Only return the Python code (no explanation). Use 'result' as the final output variable.
Assume the DataFrame is already loaded as 'df'.
"""
                client = Groq(api_key=os.getenv('GROQ_API_KEY'))
                chat_completion = client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model="llama-3.3-70b-versatile",
                    temperature=0.1
                )

                code_generated = chat_completion.choices[0].message.content.strip("`python").strip("`")
                
                local_vars = {"df": df, "pd": pd}
                exec(code_generated, {}, local_vars)
                
                result = local_vars.get("result")
                
                # Save to history
                history_entry = {
                    "timestamp": datetime.now().isoformat(),
                    "query": query,
                    "code": code_generated,
                    "result": result.to_dict() if isinstance(result, pd.DataFrame) else str(result)
                }
                save_analysis_history(history_entry)
                
                if isinstance(result, pd.DataFrame):
                    result_html = result.to_html(classes="table table-striped", index=False)
                else:
                    result_html = f"<div class='result-value'>{result}</div>"
                
                return jsonify({
                    "success": True,
                    "code": code_generated,
                    "result": result_html,
                    "preview": df.head(10).to_html(classes="table table-striped", index=False)
                })
                
            except Exception as e:
                return jsonify({"error": f"Error processing query: {str(e)}"})
    
    return render_template("analyze.html")

@app.route("/insights")
def insights():
    df_json = session.get('current_df')
    if df_json:
        df = pd.read_json(df_json)
        insights_data = generate_insights(df)
        return render_template("insights.html", insights=insights_data)
    return render_template("insights.html", insights=None)

@app.route("/history")
def history():
    try:
        with open('analysis_history.json', 'r') as f:
            history = json.load(f)
    except:
        history = []
    return render_template("history.html", history=history)

@app.route("/settings", methods=["GET", "POST"])
def settings():
    if request.method == "POST":
        # Handle settings updates
        flash('Settings updated successfully!', 'success')
    return render_template("settings.html", groq_api_key=os.getenv('GROQ_API_KEY', ''))

@app.route("/help")
def help():
    return render_template("help.html")

@app.route("/api/data_stats")
def data_stats():
    df_json = session.get('current_df')
    if df_json:
        df = pd.read_json(df_json)
        stats = {
            "rows": len(df),
            "columns": len(df.columns),
            "numeric_cols": len(df.select_dtypes(include=['number']).columns),
            "categorical_cols": len(df.select_dtypes(include=['object']).columns)
        }
        return jsonify(stats)
    return jsonify({"error": "No data loaded"})
@app.route("/api/clear_data", methods=["POST"])
def clear_data():
    session.pop('current_df', None)
    session.pop('columns', None)
    return jsonify({"success": True})

@app.route("/api/clear_history", methods=["POST"])
def clear_history():
    try:
        with open('analysis_history.json', 'w') as f:
            json.dump([], f)
        return jsonify({"success": True})
    except:
        return jsonify({"error": "Could not clear history"})

@app.route("/api/delete_history/<int:index>", methods=["DELETE"])
def delete_history(index):
    try:
        with open('analysis_history.json', 'r') as f:
            history = json.load(f)
        
        if 0 <= index < len(history):
            history.pop(index)
            
        with open('analysis_history.json', 'w') as f:
            json.dump(history, f)
            
        return jsonify({"success": True})
    except:
        return jsonify({"error": "Could not delete entry"})

@app.route("/api/generate_insights", methods=["POST"])
def api_generate_insights():
    df_json = session.get('current_df')
    if df_json:
        df = pd.read_json(df_json)
        insights_data = generate_insights(df)
        return jsonify(insights_data)
    return jsonify({"error": "No data available"})

if __name__ == "__main__":
=======
from flask import Flask, render_template, request, session, jsonify, flash
from utils import preprocess_and_save, generate_insights, save_analysis_history
import pandas as pd
from groq import Groq
import os
from dotenv import load_dotenv
import json
from datetime import datetime, timezone
from dateutil import relativedelta

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'dev-secret-key')
@app.template_filter('datetime')
def format_datetime(value, format='%Y-%m-%d %H:%M:%S'):
    """Format a datetime object or ISO string to readable format"""
    if isinstance(value, str):
        try:
            value = datetime.fromisoformat(value.replace('Z', '+00:00'))
        except:
            return value
    if isinstance(value, datetime):
        return value.strftime(format)
    return value

@app.template_filter('time_ago')
def time_ago_filter(value):
    """Convert datetime to human-readable time ago format"""
    if isinstance(value, str):
        try:
            value = datetime.fromisoformat(value.replace('Z', '+00:00'))
        except:
            return value
    
    if not isinstance(value, datetime):
        return value
    
    now = datetime.now(timezone.utc) if value.tzinfo else datetime.now()
    diff = relativedelta.relativedelta(now, value)
    
    if diff.years > 0:
        return f"{diff.years} year{'s' if diff.years > 1 else ''} ago"
    elif diff.months > 0:
        return f"{diff.months} month{'s' if diff.months > 1 else ''} ago"
    elif diff.days > 0:
        return f"{diff.days} day{'s' if diff.days > 1 else ''} ago"
    elif diff.hours > 0:
        return f"{diff.hours} hour{'s' if diff.hours > 1 else ''} ago"
    elif diff.minutes > 0:
        return f"{diff.minutes} minute{'s' if diff.minutes > 1 else ''} ago"
    else:
        return "Just now"

@app.template_filter('first')
def first_filter(value):
    """Get first element of iterable"""
    if hasattr(value, '__iter__') and not isinstance(value, str):
        try:
            return next(iter(value))
        except:
            return value
    return value
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

@app.route("/analyze", methods=["GET", "POST"])
def analyze():
    if request.method == "POST":
        file = request.files.get("file")
        query = request.form.get("query")
        
        if not file:
            return jsonify({"error": "Please upload a file"})
        
        df, cols, df_html, err = preprocess_and_save(file)
        if err:
            return jsonify({"error": err})
        
        session['current_df'] = df.to_json()
        session['columns'] = cols
        
        if query:
            try:
                # Prepare context for the LLM
                buffer = pd.io.common.StringIO()
                df.info(buf=buffer)
                df_info = buffer.getvalue()
                
                prompt = f"""
You are an expert Python data analyst.
You have a pandas DataFrame named `df` loaded with the following structure:

Columns: {list(df.columns)}
Data Types and Info:
{df_info}

Sample Data (first 3 rows):
{df.head(3).to_string()}

User Question: {query}

**Task**: Write Python code using pandas to answer the user's question.
**Rules**:
1. Assume `df` is already loaded.
2. Use `result` as the final output variable. if the answer is a single value, assign it to `result`. if it's a plot, you can't display it, so just return the data for the plot in `result`.
3. Handle potential NaN values gracefully.
4. IMPORT NOTHING. `pandas` is available as `pd`.
5. RETURN ONLY THE CODE. No markdown backticks, no `python` keyword, no explanations. Just valid Python code.
"""
                client = Groq(api_key=os.getenv('GROQ_API_KEY'))
                chat_completion = client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model="llama-3.3-70b-versatile",
                    temperature=0.1
                )

                code_generated = chat_completion.choices[0].message.content.strip("`python").strip("`")
                
                local_vars = {"df": df, "pd": pd}
                exec(code_generated, {}, local_vars)
                
                result = local_vars.get("result")
                
                # Save to history
                history_entry = {
                    "timestamp": datetime.now().isoformat(),
                    "query": query,
                    "code": code_generated,
                    "result": result.to_dict() if isinstance(result, pd.DataFrame) else str(result)
                }
                save_analysis_history(history_entry)
                
                if isinstance(result, pd.DataFrame):
                    result_html = result.to_html(classes="table table-striped", index=False)
                else:
                    result_html = f"<div class='result-value'>{result}</div>"
                
                return jsonify({
                    "success": True,
                    "code": code_generated,
                    "result": result_html,
                    "preview": df.head(10).to_html(classes="table table-striped", index=False)
                })
                
            except Exception as e:
                return jsonify({"error": f"Error processing query: {str(e)}"})
    
    return render_template("analyze.html")

@app.route("/insights")
def insights():
    df_json = session.get('current_df')
    if df_json:
        df = pd.read_json(df_json)
        insights_data = generate_insights(df)
        return render_template("insights.html", insights=insights_data)
    return render_template("insights.html", insights=None)

@app.route("/history")
def history():
    try:
        with open('analysis_history.json', 'r') as f:
            history = json.load(f)
    except:
        history = []
    return render_template("history.html", history=history)

@app.route("/settings", methods=["GET", "POST"])
def settings():
    if request.method == "POST":
        # Handle settings updates
        flash('Settings updated successfully!', 'success')
    return render_template("settings.html", groq_api_key=os.getenv('GROQ_API_KEY', ''))

@app.route("/help")
def help():
    return render_template("help.html")

@app.route("/api/data_stats")
def data_stats():
    df_json = session.get('current_df')
    if df_json:
        df = pd.read_json(df_json)
        stats = {
            "rows": len(df),
            "columns": len(df.columns),
            "numeric_cols": len(df.select_dtypes(include=['number']).columns),
            "categorical_cols": len(df.select_dtypes(include=['object']).columns)
        }
        return jsonify(stats)
    return jsonify({"error": "No data loaded"})
@app.route("/api/clear_data", methods=["POST"])
def clear_data():
    session.pop('current_df', None)
    session.pop('columns', None)
    return jsonify({"success": True})

@app.route("/api/clear_history", methods=["POST"])
def clear_history():
    try:
        with open('analysis_history.json', 'w') as f:
            json.dump([], f)
        return jsonify({"success": True})
    except:
        return jsonify({"error": "Could not clear history"})

@app.route("/api/delete_history/<int:index>", methods=["DELETE"])
def delete_history(index):
    try:
        with open('analysis_history.json', 'r') as f:
            history = json.load(f)
        
        if 0 <= index < len(history):
            history.pop(index)
            
        with open('analysis_history.json', 'w') as f:
            json.dump(history, f)
            
        return jsonify({"success": True})
    except:
        return jsonify({"error": "Could not delete entry"})

@app.route("/api/history_recent")
def history_recent():
    try:
        with open('analysis_history.json', 'r') as f:
            history = json.load(f)
        # Return last 5 entries, reversed (newest first)
        return jsonify(list(reversed(history[-5:])))
    except:
        return jsonify([])

@app.route("/api/generate_insights", methods=["POST"])
def api_generate_insights():
    df_json = session.get('current_df')
    if df_json:
        df = pd.read_json(df_json)
        insights_data = generate_insights(df)
        return jsonify(insights_data)
    return jsonify({"error": "No data available"})

if __name__ == "__main__":
>>>>>>> b318fad (Enhance UI with rich aesthetics, glassmorphism, dynamic dashboard, and support for all CSV files)
    app.run(debug=True)