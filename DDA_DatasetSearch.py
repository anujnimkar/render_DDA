import openai
import os
import re 
import json 


with open('/etc/secrets/openai_key.txt') as f:
    api_key = f.read().strip()

client = openai.OpenAI(api_key=api_key)  

def analyze_sql_code(sql_file_path, query):  
    # Read SQL file
    print('Inside Analyze SQL code ')
    with open(sql_file_path, "r") as f: 
        sql_content = f.read()

    #print('SQL Content '+sql_content)    

    # Create a structured system prompt for more consistent responses
    system_prompt = """You are a database expert that analyzes SQL code and provides precise, structured answers about database infrastructure.
Follow these rules strictly:
1. Always provide answers in a clear, bullet-point format
2. Focus only on factual information derived from the SQL code
3. If information is not available in the SQL code, explicitly state that
4. For table descriptions, include: table name, primary purpose, and key columns
5. For relationship questions, specify the exact join conditions or foreign keys
6. Keep responses concise and directly related to the question
7. Use consistent terminology throughout the response"""

    # Create a structured user prompt
    user_prompt = f"""Please analyze the following SQL code and answer this question: {query}

SQL Code:
{sql_content}

Format your response as follows:
<strong>Direct Answer:</strong>
[Concise answer to the question]

<strong>Supporting Details:</strong>
[Relevant details from the SQL code]

<strong>Additional Context:</strong>
[Any important related information]"""

    # Generate response using GPT with more structured prompting
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        max_tokens=2000,
        n=1,
        temperature=0.3,  # Reduced temperature for more consistent outputs
    ) 

    # Extract and format the response
    response_content = response.choices[0].message.content
    
    # Format the response for better readability in HTML
    formatted_response = response_content.replace('\n', '<br>')
    formatted_response = formatted_response.replace('• ', '<br>• ')
    
    print('Inside DDA Dataset Search analyze sql function') 

    #print (formatted_response)

    return formatted_response 

def save_data_dictionary(data_dictionary, output_file_path):
    with open(output_file_path, 'w') as f:
        json.dump(data_dictionary, f, indent=2) 

# Usage
sql_file_path = "Sample_SQL_Script.sql"
#output_file_path = "/Users/anujnimkar/Desktop/Anuj_New_Data/Mac_Laptop_data/Projects/Data_Dictionary_Assistant/data_dictionary.json" 
   
 





  






