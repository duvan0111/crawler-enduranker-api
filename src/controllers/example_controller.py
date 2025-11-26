from fastapi import HTTPException
from typing import List
from src.models.example_model import ExampleModel, ExampleCreateModel, ExampleUpdateModel
from src.services.example_service import example_service

class ExampleController:
    """Contrôleur pour gérer les requêtes liées aux exemples"""
    
    async def get_all_items(self) -> List[ExampleModel]:
        """Récupérer tous les éléments"""
        items = await example_service.get_all()
        return items
    
    async def get_item_by_id(self, item_id: str) -> ExampleModel:
        """Récupérer un élément par son ID"""
        item = await example_service.get_by_id(item_id)
        if not item:
            raise HTTPException(status_code=404, detail=f"Élément avec l'ID {item_id} non trouvé")
        return item
    
    async def create_item(self, item_data: ExampleCreateModel) -> ExampleModel:
        """Créer un nouvel élément"""
        new_item = await example_service.create(item_data)
        return new_item
    
    async def update_item(self, item_id: str, item_data: ExampleUpdateModel) -> ExampleModel:
        """Mettre à jour un élément existant"""
        updated_item = await example_service.update(item_id, item_data)
        if not updated_item:
            raise HTTPException(status_code=404, detail=f"Élément avec l'ID {item_id} non trouvé")
        return updated_item
    
    async def delete_item(self, item_id: str) -> dict:
        """Supprimer un élément"""
        success = await example_service.delete(item_id)
        if not success:
            raise HTTPException(status_code=404, detail=f"Élément avec l'ID {item_id} non trouvé")
        return {"message": f"Élément {item_id} supprimé avec succès"}

# Instance unique du contrôleur
example_controller = ExampleController()
