import re
from datetime import date
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, field_validator


class PersonalData(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=100)
    document_type: str = Field(..., pattern="^(CC|CE|PA|TI|NIT)$")
    document_id: str = Field(..., min_length=5, max_length=20)
    date_of_birth: date
    email: EmailStr
    phone: str = Field(..., min_length=7, max_length=20)
    address: str = Field(..., min_length=5, max_length=200)
    city: str = Field(..., min_length=2, max_length=100)
    emergency_contact_name: str = Field(..., min_length=2, max_length=100)
    emergency_contact_phone: str = Field(..., min_length=7, max_length=20)

    @field_validator("phone", "emergency_contact_phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        cleaned = re.sub(r"[\s\-\(\)\+]", "", v)
        if not cleaned.isdigit():
            raise ValueError("El teléfono solo puede contener dígitos.")
        if len(cleaned) < 7:
            raise ValueError("El teléfono debe tener al menos 7 dígitos.")
        return cleaned


class ConsentData(BaseModel):
    has_read_information: bool
    consents_to_procedure: bool
    authorizes_data_processing: bool
    authorizes_media: bool = False
    place: str = Field(..., min_length=2, max_length=100)
    signature_date: date

    @field_validator("has_read_information", "consents_to_procedure", "authorizes_data_processing")
    @classmethod
    def must_be_accepted(cls, v: bool, info) -> bool:
        if not v:
            raise ValueError(f"El campo '{info.field_name}' debe ser aceptado para continuar.")
        return v


class ConsentFormRequest(BaseModel):
    personal_data: PersonalData
    consent_data: ConsentData
    # Base64-encoded PNG (with or without the data:image/png;base64, prefix)
    signature_image: str = Field(..., min_length=100)


class ConsentFormResponse(BaseModel):
    success: bool
    message: str
    reference_number: Optional[str] = None
    drive_signature_id: Optional[str] = None
