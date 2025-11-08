from models.entities.User import User

#>**********************Register
@classmethod
def register(cls, db, user):
    try:
        cursor = db.connection.cursor()
        sql = """INSERT INTO user (username, email, password, fullname)
                 VALUES (%s, %s, %s, %s)"""
        cursor.execute(sql, (user.username, user.email, user.password, user.fullname))
        db.connection.commit()
        return True
    except Exception as ex:
        print("Error al registrar:", ex)
        return False

#**********************Login
class ModelUser():
    @classmethod
    def login(self, db, user):
        try:
            cursor = db.connection.cursor()
            sql = """SELECT id, username, password, fullname FROM user
                     WHERE username = '{}'""".format(user.username)
            cursor.execute(sql)
            row = cursor.fetchone()

            if row is not None:
                
                if User.check_password(row[2], user.password):
                    return User(row[0], row[1], row[2], row[3])
                else:
                    return None
            else:
                return None
        except Exception as ex:
            raise Exception(ex)
        
        
        
    @classmethod
    def get_by_id(cls, db, id):
        try:
            cursor = db.connection.cursor()
            sql = "SELECT id, username, email,  fullname FROM user WHERE id = {}".format(id)
            cursor.execute(sql)
            row = cursor.fetchone()

            if row != None:
                
                user = User(row[0], row[1], None, row[2])
                return user; 
            else:
                    return None
        except Exception as ex:
            raise Exception(ex)

