import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev_key_replace_in_production')
    SUPABASE_URL = os.environ.get('SUPABASE_URL')
    SUPABASE_ANON_KEY = os.environ.get('SUPABASE_ANON_KEY')
    ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY')
    ELEVENLABS_API_KEY = os.environ.get('ELEVENLABS_API_KEY')
    PORTIA_API_KEY = os.environ.get('PORTIA_API_KEY')
    
class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = False
    
class ProductionConfig(Config):
    DEBUG = False
    TESTING = False
    
class TestingConfig(Config):
    DEBUG = True
    TESTING = True
    
# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

def get_config():
    """Returns the appropriate configuration based on environment"""
    env = os.environ.get('FLASK_ENV', 'default')
    return config.get(env, config['default'])
