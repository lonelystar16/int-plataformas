from api.models.products import Product

class ProductServiceById:
    def __init__(self, mysql):
        self.mysql = mysql

    def get_all_products(self):
        cursor = self.mysql.connection.cursor()
        cursor.execute("SELECT id, name, price,type FROM product where id = " + "valor")
        results = cursor.fetchall()
        products = [Product(id=row[0], name=row[1], price=row[2], types=row[2]).to_dict() for row in results]
        return products