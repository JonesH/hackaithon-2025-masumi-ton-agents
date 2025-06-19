from os import getenv


def get_db_url() -> str:
    db_driver = getenv("DB_DRIVER", "postgresql+psycopg")
    db_user = getenv("DB_USER", "ai")
    db_pass = getenv("DB_PASS", "ai")
    db_host = getenv("DB_HOST", "localhost")
    db_port = getenv("DB_PORT", "5432")
    db_database = getenv("DB_DATABASE", "ai")
    
    # Handle the case where environment variables might be set to "None" string
    if db_port == "None" or not db_port:
        db_port = "5432"
    if db_host == "None" or not db_host:
        db_host = "localhost"
    if db_user == "None" or not db_user:
        db_user = "ai"
    if db_database == "None" or not db_database:
        db_database = "ai"
    
    return "{}://{}{}@{}:{}/{}".format(
        db_driver,
        db_user,
        f":{db_pass}" if db_pass and db_pass != "None" else "",
        db_host,
        db_port,
        db_database,
    )
