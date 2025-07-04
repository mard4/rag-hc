import os
import pandas as pd
from connection import *

conn, cur = get_connection()

print("Starting data ingestion for MIMIC-III...")

def read_json_mimic():
    extracted_data = []

    filepath = "./data_ingestion/data/physionet.org/files/mimic-iii-question-answer/1.0.0/test.final.json"
    with open(filepath, 'r', encoding='utf-8') as file:
        data = pd.read_json(file)
        
    for record in data['data']:
        title = record['title']
        paragraphs = record['paragraphs']

        for paragraph in paragraphs:
            context = paragraph.get('context')
            questions = paragraph['qas']
            for question in questions:
                question_text = question['question']
                answers = question['answers']
                for answer in answers:
                    answer_text = answer['text']
                    #print(f"Context: {context}")
                    extracted_data.append({
                        'title': title,
                        'context': context,
                        'question': question_text,
                        'answer': answer_text
                    })
    df = pd.DataFrame(extracted_data)
    return df

df = read_json_mimic()

