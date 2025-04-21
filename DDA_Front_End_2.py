from flask import Flask, render_template_string, request
import openai
import os
import re 
import json
import DDA_DatasetSearch


app = Flask(__name__)
 

with open('/etc/secrets/openai_key.txt') as f:
    api_key = f.read().strip()


openai.api_key = api_key


# Usage
sql_file_path = "/Users/anujnimkar/Desktop/Anuj_New_Data/Mac_Laptop_data/Projects/Data_Dictionary_Assistant/Codebase/Sample_SQL_Script.sql" 



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
 
@app.route('/') 
def home(): 
    return render_template_string(''' 
        <!DOCTYPE html>
        <html>
        <head>
            <title>Data Infrastructure Search</title>
            <style>
                body { font-family: Arial, sans-serif; max-width: 800px; margin: 2rem auto; }
                .search-box { 
                    width: 100%; 
                    padding: 1rem; 
                    font-size: 1.2rem; 
                    border: 1px solid #dfe1e5; 
                    border-radius: 24px; 
                    margin: 2rem 0;
                    box-shadow: 0 1px 6px rgba(32,33,36,.28);
                }
                .result-item { 
                    margin: 1rem 0; 
                    padding: 1rem; 
                    border: 1px solid #e0e0e0; 
                    border-radius: 8px; 
                    color: #70757a;  
                }
                .category { 
                    color: #70757a; 
                    font-size: 0.9rem; 
                    margin-top: 0.5rem;
                }
                button { 
                    background: #1a73e8; 
                    color: white; 
                    border: none; 
                    padding: 0.8rem 1.5rem; 
                    border-radius: 4px; 
                    cursor: pointer;
                } 
            </style>
        </head>
        <body> 
            <h1 style="text-align: center; color: #1a73e8;">Data Infrastructure Search</h1>
            <form action="/search" method="post" style="text-align: center;">
                <input class="search-box" type="text" name="query" 
                       placeholder="Search tables, databases, metrics..." 
                       autofocus>
                <button type="submit">Search</button>
            </form>
        </body>
        </html>
    ''')

@app.route('/search', methods=['POST'])
def search():
    query = request.form['query'].lower()
    # Create a prompt for GPT
    #prompt = request.form['query'].lower()
    results = []

    finalresult = DDA_DatasetSearch.analyze_sql_code(sql_file_path, query) 
    


    return render_template_string(''' 
        <!DOCTYPE html>
        <html>
        <head>
            <title>Search Results</title>
                                  
            <style>
                /* Reuse styles from home page */
                body { font-family: Arial, sans-serif; max-width: 800px; margin: 2rem auto; }
                .result-item { 
                    margin: 1rem 0; 
                    padding: 1rem; 
                    border: 1px solid #e0e0e0; 
                    border-radius: 8px; 
                }
                .category { 
                    color: #70757a; 
                    font-size: 0.9rem; 
                    margin-top: 0.5rem;
                }
            </style>
        </head>
        <body>
            {{ result}}  
            <h2 style="color: #1a73e8;">Results for "{{ query }}"</h2>
             
            {{ result}}                        


                                  
             <div class="result-item">
                <div style="font-size: 1.1rem; color: #1a73e8;">
                    {{ results}}
                </div>
         
            
                                 

            <a href="/" style="display: block; margin-top: 2rem;">← Back to Search</a>
        </body>
        </html>
    ''', query=query, results=finalresult) 



if __name__ == '__main__':
    app.run(debug=True)   
