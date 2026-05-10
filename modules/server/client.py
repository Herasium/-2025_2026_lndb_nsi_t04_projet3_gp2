
class Client():
    def __init__(self,conn,id):
        self.conn = conn
        self.id = id
        self.role = None
        self.name = "No Name"