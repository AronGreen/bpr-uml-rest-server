from flask import abort

def ensure_no_duplicates(objects: list, identifier_field: str):
    for i in range(0, len(objects)):
        for j in range(i+1, len(objects)):
            if getattr(objects[i], identifier_field) == getattr(objects[j], identifier_field):
                abort(400)