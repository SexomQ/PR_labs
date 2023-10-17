from flask import Flask

from models.electro_scooter import ElectroScooter
from models.database import db
from flask_swagger_ui import get_swaggerui_blueprint


def create_app(db):
    SWAGGER_URL="/swagger"
    API_URL="/static/swagger.json"


    swagger_ui_blueprint = get_swaggerui_blueprint(
        SWAGGER_URL,
        API_URL,
        config={
            'app_name': 'Access API'
        }
    )

    app = Flask(__name__)
    app.register_blueprint(swagger_ui_blueprint, url_prefix=SWAGGER_URL)

    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///electro_scooters.db'
    db.init_app(app)
    return app

if __name__ == '__main__':
    app = create_app(db)
    import routes
    app.run(debug=True)