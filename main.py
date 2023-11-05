from fastapi import FastAPI, APIRouter, HTTPException, Body
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from dotenv import load_dotenv


import docker
import os
from typing import List
import yaml

load_dotenv()

def load_yaml_config(model: str):
    config_path = f'Models/config/{model}.yaml'
    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)
    return config

def load_yaml_base_config():
    config_path = f'template-base.yaml'
    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)
    return config

def write_to_file(datas, output_file):
    with open(output_file, 'w') as file:
        for data in datas:
            file.write(data + '\n')
            
client = docker.from_env()

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def root():
    return FileResponse('static/index.html')

api_router = APIRouter()

@api_router.get("/containers/")
async def list_containers():
    all_containers = client.containers.list(all=True)  # `all=True` permet de lister aussi les conteneurs arrêtés
    kwb_containers = [container for container in all_containers if container.name.startswith('kwb_')]
    return [{'id': container.id, 'name': container.name, 'status': container.status} for container in kwb_containers]
    
@api_router.post("/containers/{model}/start")  # This decorator was missing
async def start_container(container_id: str):
    try:
        container = client.containers.run(container_id, detach=True)
        return {"status": "started", "container_id": container.id}
    except docker.errors.DockerException as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/containers/{container_id}/stop")
async def stop_container(container_id: str):
    try:
        container = client.containers.get(container_id)
        container.stop()
        return {"status": "stopped", "container_id": container_id}
    except docker.errors.NotFound:
        raise HTTPException(status_code=404, detail="Container not found")
    except docker.errors.DockerException as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.delete("/containers/{container_id}/delete")
async def delete_container(container_id: str):
    try:
        container = client.containers.get(container_id)
        container.remove(force=True)  # Force la suppression même si le conteneur est en cours d'exécution
        return {"status": "deleted", "container_id": container_id}
    except docker.errors.NotFound:
        raise HTTPException(status_code=404, detail="Container not found")
    except docker.errors.DockerException as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/models/")
async def list_models() -> List[str]:
    config_path = 'Models/config/'
    # Liste tous les fichiers qui se terminent par .yaml dans le dossier config
    models = [f for f in os.listdir(config_path) if os.path.isfile(os.path.join(config_path, f)) and f.endswith('.yaml')]
    return models

@api_router.post("/containers/")
async def create_container(model: str = Body(..., embed=True)):
    base    = load_yaml_base_config()
    config  = load_yaml_config(model)
    container_name = f"kwb_{model}"
    try:
        base_config = base['services']
        write_to_file(config.get('requirements', None),"./Models/requirements.txt")
        
        container = client.containers.run(
            image=base.get('image'),
            name=container_name,
            working_dir=base.get('working_dir'),
            command=base_config.get('command', None), 
            entrypoint=base_config.get('entrypoint', None), 
            environment=config.get('environment', None),
            ports={v: k for k, v in [port.split(':') for port in config.get('ports', [])]},
            volumes=[os.path.join(os.getenv("HOST_PATH"), vol.split(':')[0]) + ':' + vol.split(':')[1] for vol in base_config.get('volumes', [])],
            network=base_config.get('network', 'default'),
            detach=True
        )
        # Connecter au réseau si nécessaire
        if base.get('network', 'default') != 'default':
            network = client.networks.get(base['network'])
            network.connect(container)

        return {"status": "started", "container_id": container.id}
    except Exception as e:
        print("Erreur lors de la création du conteneur:", e)
        raise HTTPException(status_code=500, detail=str(e))

app.include_router(api_router, prefix="/api")
