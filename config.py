class Config:
    """Configuration class for Flask application."""
    
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:root@localhost:5432/manager'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY='1234445'

