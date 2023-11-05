from fastapi import FastAPI, Body
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from transformers import AutoTokenizer, pipeline, AutoModelForSeq2SeqLM
import torch
import os
import yaml

def load_yaml_config(model: str):
    config_path = f'config/{model}.yaml'
    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)
    return config

model_name      = os.getenv("model")
model_config    = load_yaml_config(model_name.replace('/','_'))

def translate(text):
    tokenizer = AutoTokenizer.from_pretrained(model_name, cache_dir="/app/cache/")
    model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
    return tokenizer.decode(model.generate(tokenizer.encode(text, return_tensors='pt')).squeeze(), skip_special_tokens=True)

def translate_api(text: str = Body(..., embed=True)):
    return {'result':translate(text)}

def translate_www():
    return FileResponse('static/translate.html')

def chat(text,system_text):
    pipe = pipeline("text-generation", model=model_name, torch_dtype=torch.bfloat16, device_map="auto")
    messages = [
    {"role": "system","content": system_text},
    {"role": "user", "content": text},
    ]
    #"You are a friendly chatbot who always responds in the style of a pirate in french"
    prompt = pipe.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    outputs = pipe(prompt, max_new_tokens=256, do_sample=True, temperature=0.7, top_k=50, top_p=0.95)
    return outputs[0]["generated_text"]

def chat_api(text: str = Body(..., embed=True),system_text: str = Body(..., embed=True)):
    return {'result':chat(text,system_text)}

def chat_www():
    return FileResponse('static/chat.html')

app = FastAPI()

for endpoint in model_config['endpoint']:
    if endpoint in globals():
        endpoint_api_function = globals()[f'{endpoint}_api']
        endpoint_www_function = globals()[f'{endpoint}_www']
        app.add_api_route(f'/{endpoint}', endpoint_www_function, methods=["GET"])
        app.add_api_route(f'/{endpoint}', endpoint_api_function, methods=["POST"])
    