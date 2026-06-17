def init_database(db):
    import models.user
    import models.clothing
    import models.outfit
    import models.history

    db.create_all()
