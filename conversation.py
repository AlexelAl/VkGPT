import sqlite3


class Conversation:
    def __init__(self):
        self.con = sqlite3.connect("db\conv.sqlite", check_same_thread=False)
        self.cur = self.con.cursor()
        db = self.cur.execute("SELECT * FROM conv").fetchall()
        self.num = 0
        if len(db) != 0:
            self.num = db[-1][0]

    def get_conv(self, user):
        res = self.cur.execute(f"""
        SELECT * from conv WHERE user = {user}
        """).fetchall()
        answer = []
        for i in res:
            cur = {'role': i[1], 'content': i[2]}
            answer.append(cur)
        return answer

    def add_state(self, role, message, user):
        if not message:
            return
        self.cur.execute(f"""
        INSERT INTO conv(id, role, message, user)
        VALUES({self.num + 1},
              "{role}",
              "{message.replace('"', "'")}",
              "{user}")
        """)
        self.num += 1
        self.con.commit()

    def delete_conv(self, user):
        self.cur.execute(f"""
        DELETE FROM conv WHERE user = {user}
        """)
        self.con.commit()
