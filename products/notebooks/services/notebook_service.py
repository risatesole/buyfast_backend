from django.db.models import Q
from products.default.models import Product

class NotebookService:
    def createNotebook(self, product:Product, title, description, brand, color, images=None):
        pass

    def updateNoteBook(self, title, description, brand, color, images=None):
        pass 
