from app import create_app, db, ElectroScooter

def init_database(db):
    app = create_app(db)
    with app.app_context():
        db.create_all()
        db.session.add(ElectroScooter('Xiaomi Mi Electric Scooter', 7800))
        db.session.add(ElectroScooter('Segway Ninebot ES2', 5200))
        db.session.commit()

if __name__ == '__main__':
    init_database(db)
    