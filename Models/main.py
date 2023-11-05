from fastapi import FastAPI, APIRouter, HTTPException, Body
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from transformers import AutoModelForSequenceClassification, AutoTokenizer, pipeline, AutoModelForSeq2SeqLM
import torch
import os
import yaml

def load_yaml_config(model: str):
    config_path = f'config/{model}.yaml'
    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)
    return config

model_name = os.getenv("model")
model_config = load_yaml_config(model_name.replace('/','_'))

def translate(text):
    tokenizer = AutoTokenizer.from_pretrained(model_name, cache_dir="/app/cache/")
    model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
    return tokenizer.decode(model.generate(tokenizer.encode(text, return_tensors='pt')).squeeze(), skip_special_tokens=True)

def translate_api(text: str = Body(..., embed=True)):
    return {'result':translate(text)}

def translate_www(text):
    return FileResponse('static/translate.html')

app = FastAPI()

for endpoint in model_config['endpoint']:
    if endpoint in globals():
        endpoint_api_function = globals()[f'{endpoint}_api']
        endpoint_www_function = globals()[f'{endpoint}_www']
        app.add_api_route(f'/{endpoint}', endpoint_www_function, methods=["GET"])
        app.add_api_route(f'/{endpoint}', endpoint_api_function, methods=["POST"])
    