def _add_column_if_missing(engine, table, column_def):
    """Add a column to an existing table if it doesn't exist (SQLite compat)."""
    from sqlalchemy import inspect as sa_inspect
    inspector = sa_inspect(engine)
    columns = [c["name"] for c in inspector.get_columns(table)]
    col_name = column_def.split()[0]
    if col_name not in columns:
        with engine.connect() as conn:
            conn.exec_driver_sql(f"ALTER TABLE {table} ADD COLUMN {column_def}")
            conn.commit()
        return True
    return False


def init_database(db):
    import models.user
    import models.clothing
    import models.outfit
    import models.history

    db.create_all()

    engine = db.get_engine()
    _add_column_if_missing(engine, "outfits", "collage_data text")
