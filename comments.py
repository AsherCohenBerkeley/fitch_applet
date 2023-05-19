class Comment():
    def __init__(self, comment):
        self.comment = comment
    
    def __repr__(self):
        return self.comment

class GoodComment(Comment):
    def __init__(self):
        super().__init__('All good!')

class BadComment(Comment):
    pass