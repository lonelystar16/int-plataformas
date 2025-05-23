from api.models.user import User

class UserService:
    def __init__(self, mysql):
        self.mysql = mysql

    def get_all_users(self):
        cursor = self.mysql.connection.cursor()
        cursor.execute("SELECT id, name, email FROM users")
        results = cursor.fetchall()
        users = [User(id=row[0], name=row[1], email=row[2]).to_dict() for row in results]
        return users