from models.entities.User import User

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
