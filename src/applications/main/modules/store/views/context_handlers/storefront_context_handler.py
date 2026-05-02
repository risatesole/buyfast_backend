from ....product.services.product.product_service import ProductService

def hero_section_context():
    hero_section = {
        "text": {
            "main": "Compra a tu manera",
            "eyebrow": "productos que dicen comprame",
            "supporting": "Descubre cientos de productos seleccionados para cada estilo y ocasión"
        }
    }
    return hero_section

def store_front_context_handler():
    product = ProductService()
    context = {
        "storename": "Petal",
        "hero": hero_section_context(),
        "categories": product.getAllCategories()[:10]

    }
    return context

