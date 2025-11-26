from typing import List, Optional
from datetime import datetime
from bson import ObjectId
from src.models.example_model import ExampleModel, ExampleCreateModel, ExampleUpdateModel
from src.database import db

class ExampleService:
    """Service pour gérer la logique métier des exemples avec MongoDB"""
    
    def __init__(self):
        self.collection_name = "examples"
    
    def get_collection(self):
        """Obtenir la collection MongoDB"""
        return db.get_collection(self.collection_name)
    
    async def get_all(self) -> List[ExampleModel]:
        """Récupérer tous les éléments"""
        collection = self.get_collection()
        items = []
        async for document in collection.find():
            items.append(ExampleModel(**document))
        return items
    
    async def get_by_id(self, item_id: str) -> Optional[ExampleModel]:
        """Récupérer un élément par son ID"""
        if not ObjectId.is_valid(item_id):
            return None
        
        collection = self.get_collection()
        document = await collection.find_one({"_id": ObjectId(item_id)})
        
        if document:
            return ExampleModel(**document)
        return None
    
    async def create(self, item_data: ExampleCreateModel) -> ExampleModel:
        """Créer un nouvel élément"""
        collection = self.get_collection()
        
        new_item = {
            "name": item_data.name,
            "description": item_data.description,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        
        result = await collection.insert_one(new_item)
        new_item["_id"] = result.inserted_id
        
        return ExampleModel(**new_item)
    
    async def update(self, item_id: str, item_data: ExampleUpdateModel) -> Optional[ExampleModel]:
        """Mettre à jour un élément existant"""
        if not ObjectId.is_valid(item_id):
            return None
        
        collection = self.get_collection()
        
        # Préparer les données de mise à jour
        update_data = {
            "updated_at": datetime.now()
        }
        
        if item_data.name is not None:
            update_data["name"] = item_data.name
        if item_data.description is not None:
            update_data["description"] = item_data.description
        
        # Mettre à jour le document
        result = await collection.find_one_and_update(
            {"_id": ObjectId(item_id)},
            {"$set": update_data},
            return_document=True
        )
        
        if result:
            return ExampleModel(**result)
        return None
    
    async def delete(self, item_id: str) -> bool:
        """Supprimer un élément"""
        if not ObjectId.is_valid(item_id):
            return False
        
        collection = self.get_collection()
        result = await collection.delete_one({"_id": ObjectId(item_id)})
        
        return result.deleted_count > 0

# Instance unique du service (Singleton)
example_service = ExampleService()
