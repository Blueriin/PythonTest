class Post:

    def __init__(self, id, name, location, contract_type, apply_url, description):
        self.id = id
        self.name = name
        self.location = location
        self.contract_type = contract_type
        self.apply_url = apply_url
        self.description = description
        self.document = self.to_mongo_document()

    def to_mongo_document(self):
        return {'_id': self.id,
                'name': self.name,
                'location': self.location,
                'contract_type': self.contract_type,
                'apply_url': self.apply_url,
                'description': self.description}
