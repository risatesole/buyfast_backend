from .services.product_service import ProductService as ProductService
from .services.category_service import CategoryService as CategoryService
from .views.product_categories_view import product_categories_api_view as product_categories
from .views.tags.product_tags_view import ProductByTagView as ProductByTagView
from .models import Product as Product_model
# from .views.product_categories_view import product_category_detail as product_category_detail  # Remove this line - function doesn't exist

from .usecases.categories.get_category_base import get_category_default_model_object
from .usecases.categories.get_category_books import get_category_books_model_object as get_category_books_model_object

from .models import Product as Product_model
from .repositories.product_repository import ProductRepository


__all__ = ['Product_model', 'ProductRepository']
