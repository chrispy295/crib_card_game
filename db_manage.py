import sqlite3
import os


class UserManage:
    def __init__(self):
        self.dir_path = os.path.dirname(os.path.realpath(__file__))
        self.users_con = sqlite3.connect(os.path.join(self.dir_path, 'databases/users.db'))
        self.users_con.row_factory = lambda cursor, row: row[0]

    def user_read(self):
        cur = self.users_con.execute('''SELECT user FROM player''')
        self.users = cur.fetchall()
        cur.close()
        return self.users

    def user_add(self, player):
        con = sqlite3.connect(os.path.join(self.dir_path, 'databases/{}_stats.db'.format(player)))
        cur = con.cursor()
        cur.execute("CREATE TABLE player(Score INTEGER, Hand_Total INTEGER, Box_Total INTEGER, Peg_Total INTEGER,"
                    "Heels INTEGER, Fifth INTEGER, Pairs INTEGER, Runs INTEGER, Thirty INTEGER, Last INTEGER,"
                    "Wins INTEGER, Num_Hands INTEGER, Hand_Hi INTEGER, Box_Hi INTEGER, H_Zero INTEGER, B_Zero INTEGER,"
                    "No_Crib INTEGER)")
        cur.execute("CREATE TABLE comp(Score INTEGER, Hand_Total INTEGER, Box_Total INTEGER, Peg_Total INTEGER,"
                    "Heels INTEGER, Fifth INTEGER, Pairs INTEGER, Runs INTEGER, Thirty INTEGER, Last INTEGER,"
                    "Wins INTEGER, Num_Hands INTEGER, Hand_Hi INTEGER, Box_Hi INTEGER, H_Zero INTEGER,"
                    "B_Zero INTEGER, No_Crib INTEGER)")
        con.commit()
        cur.close()
        cur = self.users_con.cursor()
        cur.execute('''INSERT INTO player(user) VALUES(?)''', [player])
        self.users_con.commit()
        cur.close()

    def user_delete(self, player):
        delete_query = """DELETE from player where user=?"""
        cur = self.users_con.cursor()
        cur.execute(delete_query, (player,))
        self.users_con.commit()
        cur.close()
        if os.path.exists(os.path.join(self.dir_path, 'databases/{}_stats.db'.format(player))):
            os.remove(os.path.join(self.dir_path, 'databases/{}_stats.db'.format(player)))
        else:
            return False


if __name__ == '__main__':
    user = UserManage()
    user.user_add('joe')
    user.user_read()
