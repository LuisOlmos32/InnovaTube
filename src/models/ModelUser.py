from src.models.entities.User import User

class ModelUser:
    #********************** Register
    @classmethod
    def register(cls, db, user):
        try:
            cursor = db.cursor()
            sql = """INSERT INTO "user" (username, email, password, fullname)
                     VALUES (%s, %s, %s, %s)"""
            cursor.execute(sql, (user.username, user.email, user.password, user.fullname))
            db.commit()
            cursor.close()
            return True
        except Exception as ex:
            print("Error al registrar:", ex)
            return False

    #********************** Login
    @classmethod
    def login(cls, db, user):
        try:
            cursor = db.cursor()
            sql = """SELECT id, username, password, fullname 
                     FROM "user" WHERE username = %s"""
            cursor.execute(sql, (user.username,))
            row = cursor.fetchone()
            cursor.close()

            if row is not None:
                if User.check_password(row[2], user.password):
                    return User(row[0], row[1], row[2], row[3])
                else:
                    return None
            else:
                return None
        except Exception as ex:
            print("Error en login:", ex)
            return None

    #********************** Get by ID
    @classmethod
    def get_by_id(cls, db, id):
        try:
            cursor = db.cursor()
            sql = """SELECT id, username, email, fullname 
                     FROM "user" WHERE id = %s"""
            cursor.execute(sql, (id,))
            row = cursor.fetchone()
            cursor.close()

            if row is not None:
                return User(row[0], row[1], None, row[3])
            else:
                return None
        except Exception as ex:
            print("Error en get_by_id:", ex)
            return None
