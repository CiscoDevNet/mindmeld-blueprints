def extract_entities_from_type(request, entity_type):
    return [e for e in request.entities if e['type'] == entity_type]
