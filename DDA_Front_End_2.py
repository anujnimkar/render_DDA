from flask import Flask, render_template_string, request
import openai
import os
import re 
import json
import DDA_DatasetSearch


app = Flask(__name__)
 

with open('/etc/secrets/openai_key.txt') as f:
    api_key = f.read().strip()

client = openai.OpenAI(api_key=api_key) 

 
 

 
# Usage
sql_file_path = "Sample_SQL_Script.sql" 



'''def analyze_sql_code(sql_file_path):
    # Read SQL file
    print('Inside Analyze SQL code ')
    with open(sql_file_path, "r") as f:
        sql_content = f.read()
    return sql_content


result = analyze_sql_code(sql_file_path)'''

#print (type(result))  

# Sample data infrastructure
data_infrastructure = {
    "Tables": ["users", "orders", "products", "logistics"],
    "Databases": ["main_db", "analytics_db", "backup_db"],
    "Metrics": ["daily_sales", "user_growth", "conversion_rate", "server_uptime"],
    "APIs": ["inventory_api", "payment_gateway", "user_authentication"]

 
}
 
def get_base_template(query=None, result=None):
    return '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Data Infrastructure Search</title>
            <style>
                body { 
                    font-family: Arial, sans-serif; 
                    max-width: 800px; 
                    margin: 2rem auto; 
                    padding: 0 1rem;
                }
                .search-container {
                    text-align: center;
                    margin-bottom: 2rem;
                }
                .search-box { 
                    width: 100%; 
                    padding: 1rem; 
                    font-size: 1.2rem; 
                    border: 1px solid #dfe1e5; 
                    border-radius: 24px; 
                    margin: 1rem 0;
                    box-shadow: 0 1px 6px rgba(32,33,36,.28);
                }
                .search-button {
                    background: #1a73e8;
                    color: white;
                    border: none;
                    padding: 0.8rem 1.5rem;
                    border-radius: 4px;
                    cursor: pointer;
                    font-size: 1rem;
                    transition: background-color 0.2s;
                }
                .search-button:hover {
                    background: #1557b0;
                }
                .result-container { 
                    margin: 1rem 0; 
                    padding: 1.5rem; 
                    border: 1px solid #e0e0e0; 
                    border-radius: 8px;
                    background-color: #f8f9fa;
                    display: {% if not result %}none{% else %}block{% endif %};
                }
                .query {
                    color: #1a73e8;
                    font-size: 1.2rem;
                    margin-bottom: 1rem;
                    padding-bottom: 0.5rem;
                    border-bottom: 1px solid #e0e0e0;
                }
                .result-content {
                    margin-top: 1rem;
                    line-height: 1.6;
                }
                .result-content strong {
                    font-size: 1.2rem;
                    color: #1a73e8;
                    display: block;
                    margin-top: 1.5rem;
                    margin-bottom: 0.5rem;
                }
                h1 {
                    color: #1a73e8;
                    margin-bottom: 1.5rem;
                }
            </style>
        </head>
        <body>
            <div class="search-container">
                <h1>Data Infrastructure Search</h1>
                <form action="/" method="post">
                    <input class="search-box" type="text" name="query" 
                           placeholder="Search tables, databases, metrics..." 
                           value="{{ query if query else '' }}"
                           autofocus>
                    <button class="search-button" type="submit">Search</button>
                </form>
            </div>
            
            {% if result %}
            <div class="result-container">
                <div class="query">Query: "{{ query }}"</div>
                <div class="result-content">
                    {{ result|safe }}
                </div>
            </div>
            {% endif %}
        </body>
        </html>
    '''

@app.route('/', methods=['GET', 'POST'])
def home():
    query = None
    result = None
    
    if request.method == 'POST':
        query = request.form['query'].lower()
        result = DDA_DatasetSearch.analyze_sql_code(sql_file_path, query)
    
    return render_template_string(
        get_base_template(),
        query=query,
        result=result
    )

if __name__ == '__main__':
    app.run(debug=True)   
