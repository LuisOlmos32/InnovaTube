class config: 
    SECRET_KEY = 'B!1weNAt1T^%kvhUI*S^'

class DevelopmentConfig(config): 
    DEBUG = True 
    MYSQL_HOST = 'localhost'
    MYSQL_USER = 'root'
    MYSLQ_PASSWORD = ''
    MYSQL_DB = 'flask_login'
    
        
config = {
    'development' : DevelopmentConfig
}