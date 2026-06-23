class ProductUnavailableException(Exception):
    def __init__(self, products):
        self.products = products
        super().__init__(f"Products are unavailable: {products}")
