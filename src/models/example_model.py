from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime
from bson import ObjectId

class PyObjectId(ObjectId):
    """Type personnalisé pour gérer les ObjectId de MongoDB"""
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_core_schema__(cls, _source_type, _handler):
        from pydantic_core import core_schema
        return core_schema.json_or_python_schema(
            json_schema=core_schema.str_schema(),
            python_schema=core_schema.union_schema([
                core_schema.is_instance_schema(ObjectId),
                core_schema.chain_schema([
                    core_schema.str_schema(),
                    core_schema.no_info_plain_validator_function(cls.validate),
                ])
            ]),
            serialization=core_schema.plain_serializer_function_ser_schema(
                lambda x: str(x)
            ),
        )

class ExampleModel(BaseModel):
    """Modèle d'exemple pour la structure des données"""
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    name: str = Field(..., description="Nom de l'élément")
    description: Optional[str] = Field(None, description="Description de l'élément")
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str},
        json_schema_extra={
            "example": {
                "_id": "507f1f77bcf86cd799439011",
                "name": "Exemple",
                "description": "Ceci est un exemple",
                "created_at": "2024-01-01T00:00:00",
                "updated_at": "2024-01-01T00:00:00"
            }
        }
    )

class ExampleCreateModel(BaseModel):
    """Modèle pour la création d'un élément"""
    name: str = Field(..., description="Nom de l'élément")
    description: Optional[str] = Field(None, description="Description de l'élément")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Nouvel exemple",
                "description": "Description du nouvel exemple"
            }
        }
    )

class ExampleUpdateModel(BaseModel):
    """Modèle pour la mise à jour d'un élément"""
    name: Optional[str] = Field(None, description="Nom de l'élément")
    description: Optional[str] = Field(None, description="Description de l'élément")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Exemple mis à jour",
                "description": "Description mise à jour"
            }
        }
    )
