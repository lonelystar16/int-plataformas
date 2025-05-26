from flask import Flask
from api.routes.routes import register_routes
from api.db.database import init_db

app = Flask(__name__)

# Configuración MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'flask_user'
app.config['MYSQL_PASSWORD'] = 'flask_password'
app.config['MYSQL_DB'] = 'ferramas_dos'

# Inicializar MySQL
mysql = init_db(app)

# Registrar las rutas y pasar mysql
register_routes(app, mysql)

if __name__ == '__main__':
    app.run(debug=True)
