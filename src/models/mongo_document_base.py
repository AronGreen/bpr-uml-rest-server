from dataclasses import dataclass, asdict, fields
from bson.objectid import ObjectId
import json


@dataclass
class MongoDocumentBase:
    """
    Represents a base mongo document with an _id property.
    Provides conversion methods to and from dict and json.
    Ensures proper conversion between ObjectId and str as needed.
    """
    _id: ObjectId()

    @property
    def id(self):
        return self._id

    def to_dict(self):
        return asdict(self)

    def to_json(self):
        return json.dumps(asdict(self), default=str)

    @classmethod
    def from_dict(cls, dic: dict):
        return cls(**dic)

    @classmethod
    def from_dict_list(cls, lst: list):
        return [cls.from_dict(x) for x in lst]

    @classmethod
    def from_json(cls, j: str):
        return cls(**json.loads(j))

    def __post_init__(self):
        for field in fields(self):
            if type(field.type) == ObjectId:
                attr = getattr(self, field.name)
                if type(attr) == str:
                    setattr(self, field.name, ObjectId(attr))
