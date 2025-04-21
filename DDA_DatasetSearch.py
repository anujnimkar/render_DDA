 
import openai
import os
import re 
import json 


with open('/etc/secrets/openai_key.txt') as f:
    api_key = f.read().strip()

openai.api_key = api_key

def analyze_sql_code(sql_file_path, query):  
    # Read SQL file
    print('Inside Analyze SQL code ')
    with open(sql_file_path, "r") as f: 
        sql_content = f.read()

    #print('SQL Content '+sql_content)    

    # Create a prompt for GPT 
    organize_text = "Output each sentence up until a full stop '.' from the prompt response on a new line with line breaks. Exclude the SQL Query from the prompt response" 
                   

    print (type(query))
    print (type(sql_content)) 



    #prompt = query + "in" + {sql_content} 

    prompt = (f"{query}, {organize_text}, {sql_content}!")      



    # Generate response using GPT
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",  # You can change this to a different model if needed
        messages=[
            {"role": "system", "content": "You are a helpful assistant that analyzes SQL code and answers the questions related to the database created via this code."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=2000,
        n=1,
        stop=None,
        temperature=0.5,
    ) 

   
    # Extract the JSON from the response
    json_str = response.choices[0].message['content']
    

    print('Inside DDA Dataset Search analyze sql function') 

    #print (json_str)

    return json_str 

def save_data_dictionary(data_dictionary, output_file_path):
    with open(output_file_path, 'w') as f:
        json.dump(data_dictionary, f, indent=2) 

# Usage
sql_file_path = "/Users/anujnimkar/Desktop/Anuj_New_Data/Mac_Laptop_data/Projects/Data_Dictionary_Assistant/Codebase/Sample_SQL_Script.sql"
#output_file_path = "/Users/anujnimkar/Desktop/Anuj_New_Data/Mac_Laptop_data/Projects/Data_Dictionary_Assistant/data_dictionary.json" 
   
 





  






