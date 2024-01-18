

class conversation():
    """A conversation class that holds the messages and responses of a conversation"""

    def __init__(self, id):
        self.id = id
        self.title = "Conversation " + str(id)
        self.messages = []
        self.responses = []
        self.data_pairs = []

    # used to get the id of the conversation with all the history
    def get_id(self):
        return self.id
    
    # used to get the messages of the conversation
    def get_messages(self):
        return self.messages
    
    # used to get the responses of the conversation
    def get_responses(self):
        return self.responses

    # used to get the question and response of the conversation
    def get_data_pairs(self):
        return self.data_pairs
    
    def get_title(self):
        return self.title
    
    # used to add a message and response to the conversation
    def add_data_pair(self, message, response, jsonInfo=None):
        if jsonInfo is None:
            jsonInfo = {}
        self.data_pairs.append({
            'message': message,
            'response': response,
            'json': jsonInfo
        })
            
        self.messages.append(message)
        self.responses.append(response)