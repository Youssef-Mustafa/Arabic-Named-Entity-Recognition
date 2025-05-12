import tkinter as tk
from tkinter import scrolledtext, ttk
from transformers import pipeline

ner_pipeline = pipeline(
    "ner",
    model="model",
    tokenizer="model",
    aggregation_strategy="simple"
)


def get_entities(text):
    results = ner_pipeline(text)
    merged_entities = []
    current_entity = None

    
    for entity in results:
        if current_entity is None:
            
            current_entity = entity
        else:
            
            if (entity['start'] == current_entity['end'] + 1 and 
                entity['entity_group'] == current_entity['entity_group']):
                current_entity['word'] += ' ' + entity['word']
                current_entity['end'] = entity['end']
            else:
                
                merged_entities.append(current_entity)
                current_entity = entity
    
    
    if current_entity:
        merged_entities.append(current_entity)

    
    output = []
    last_pos = 0
    text_length = len(text)

    while last_pos < text_length:
        next_entity = next((e for e in merged_entities if e['start'] >= last_pos), None)
        
        if next_entity:
            
            if next_entity['start'] > last_pos:
                non_entity_text = text[last_pos:next_entity['start']].strip()
                for word in non_entity_text.split():
                    output.append((word, 'O'))
            
            
            entity_words = next_entity['word'].split()
            for word in entity_words:
                output.append((word, next_entity['entity_group']))
            
            last_pos = next_entity['end'] + 1 
        else:
            remaining_text = text[last_pos:].strip()
            for word in remaining_text.split():
                output.append((word, 'O')) 
            break  

    return output

def on_analyze():
    text = input_box.get("1.0", tk.END).strip()
    entities = get_entities(text)
    
    
    for row in tree.get_children():
        tree.delete(row)
    
    
    for word, label in entities:
        tree.insert('', tk.END, values=(word, label))

root = tk.Tk()
root.title("التعرف على الكيانات المُسَمّاة في النص العربي") 
root.geometry("600x500") 

tk.Label(root, text="...أدخل النص العربي هنا", font=("Tahoma", 14), anchor='e').pack(pady=5)
input_box = scrolledtext.ScrolledText(root, height=6, font=("Tahoma", 14), wrap=tk.WORD)
input_box.pack(padx=10, fill=tk.BOTH)

analyze_btn = tk.Button(root, text="تحليل النص", font=("Tahoma", 12), command=on_analyze) 
analyze_btn.pack(pady=10)

tree = ttk.Treeview(root, columns=("Word", "Entity"), show="headings", height=10)
tree.heading("Word", text="الكلمة")  
tree.heading("Entity", text="التصنيف")  
tree.pack(fill=tk.BOTH, padx=10, pady=5)

root.mainloop()  
