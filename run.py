from app import create_app, db
from database.init_db import init_database

app = create_app()

if __name__ == "__main__":
    with app.app_context():
        init_database(db)
    app.run(debug=True)
