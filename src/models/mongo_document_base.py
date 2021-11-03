from dataclasses import dataclass, asdict, fields
from dataclasses_json import dataclass_json, LetterCase, Undefined
from bson.objectid import ObjectId
import json

@dataclass_json(letter_case=LetterCase.CAMEL, undefined=Undefined.EXCLUDE)
@dataclass
class MongoDocumentBase:
    """
    Represents a base mongo document with an _id property.
    Provides conversion methods to and from dict and json.
    Ensures proper conversion between ObjectId and str as needed.
    """
    _id: ObjectId()

    def as_dict(self):
        return asdict(self)

    def as_json(self):
        return json.dumps(asdict(self), default=str)

    @classmethod
    def from_dictionary(cls, dic: dict):
        return cls(**dic)

    @classmethod
    def as_dict_list(cls, lst: list):
        return [ob.as_dict() for ob in lst]

    @classmethod
    def as_json_list(cls, lst: list):
        return json.dumps(cls.as_dict_list(lst), default=str)
        
    @classmethod
    def from_json_list(cls, json_list):
        return cls.from_dict_list(json.loads(json_list))
        
    @classmethod
    def from_dict_list(cls, lst: list):
        return [cls.from_dictionary(x) for x in lst]

    @classmethod
    def from_json(cls, j: str):
        return cls(**json.loads(j))

    def __post_init__(self):
        for field in fields(self):
            if type(field.type) == ObjectId:
                attr = getattr(self, field.name)
                if type(attr) == str:
                    setattr(self, field.name, ObjectId(attr))
