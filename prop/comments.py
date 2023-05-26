class Comment():
    def __init__(self, text):
        self.text = text
    
    def __repr__(self):
        return self.text

class GoodComment(Comment):
    def __init__(self):
        super().__init__('All good!')

class BadComment(Comment):
    pass