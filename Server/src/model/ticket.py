from datetime import datetime

class Ticket():
    def __init__(self, title, author, description, owner_address, status='pending', date_created=None):
        self.title = title
        self.author = author
        self.description = description
        self.status = status
        self.owner_address = owner_address
        self.date_created = date_created or datetime.now().isoformat()
    
    def to_dict(self):
        return {
            'title': self.title,
            'author': self.author,
            'description': self.description,
            'status': self.status,
            'owner_address': self.owner_address,
            'date_created': self.date_created
        }
    
    @classmethod
    def from_dict(cls, data):
        return cls(
            title=data['title'],
            author=data['author'],
            description=data['description'],
            owner_address=data['owner_address'],
            status=data['status'],
            date_created=data['date_created']
        )

    def __repr__(self):
        return f"<Ticket(title={self.title}, author={self.author}, status={self.status}, description={self.description}, date_created={self.date_created})>"