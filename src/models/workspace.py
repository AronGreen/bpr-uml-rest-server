from dataclasses import dataclass, field
from bson.objectid import ObjectId

from dataclasses_json import dataclass_json, LetterCase, Undefined
from typing import Optional, List
from src.models.mongo_document_base import MongoDocumentBase


@dataclass_json(letter_case=LetterCase.CAMEL, undefined=Undefined.EXCLUDE)
@dataclass
class Workspace(MongoDocumentBase):
    creatorId: ObjectId
    workspaceName: str
    users: List = field(default_factory=list)
