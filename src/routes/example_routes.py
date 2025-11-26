from fastapi import APIRouter, status
from typing import List
from src.models.example_model import ExampleModel, ExampleCreateModel, ExampleUpdateModel
from src.controllers.example_controller import example_controller

# Créer le routeur avec un préfixe et des tags pour la documentation
router = APIRouter(
    prefix="/api/examples",
    tags=["Examples"],
    responses={404: {"description": "Non trouvé"}},
)

@router.get("/", response_model=List[ExampleModel], status_code=status.HTTP_200_OK)
async def get_all_items():
    """Récupérer tous les éléments"""
    return await example_controller.get_all_items()

@router.get("/{item_id}", response_model=ExampleModel, status_code=status.HTTP_200_OK)
async def get_item(item_id: str):
    """Récupérer un élément par son ID"""
    return await example_controller.get_item_by_id(item_id)

@router.post("/", response_model=ExampleModel, status_code=status.HTTP_201_CREATED)
async def create_item(item_data: ExampleCreateModel):
    """Créer un nouvel élément"""
    return await example_controller.create_item(item_data)

@router.put("/{item_id}", response_model=ExampleModel, status_code=status.HTTP_200_OK)
async def update_item(item_id: str, item_data: ExampleUpdateModel):
    """Mettre à jour un élément existant"""
    return await example_controller.update_item(item_id, item_data)

@router.delete("/{item_id}", status_code=status.HTTP_200_OK)
async def delete_item(item_id: str):
    """Supprimer un élément"""
    return await example_controller.delete_item(item_id)
