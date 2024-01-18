import openai
import json
from conversations import conversation
import markdown
from formula_manager import FormulaManager , Formula
import logging

openai.api_key = "xX-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"

class ai_manager:
    """This class is used to manage the openai api"""

    def __init__(self):
        self.conversations = []

    def get_response(self, input_message , conversation_id ):
        """This method is used to get a response from the openai api"""

        logging.info("user message = " + str(input_message))

        # get the last conversation and add the message to it
        current_conversation = self.get_conversation_by_id(conversation_id)

        if current_conversation is None:
            logging.info("Conversation not found")
            return ""
        
        # get the history of the conversation
        history = current_conversation.get_data_pairs()

        # reverse the order of the history so that the last message is first
        history.reverse()

        logging.info("###################")
        logging.info("sending message to openai api")
        logging.info("###################")

        # here we prepare the message to send to the openai api
        message = [
                    {"role": "user", "content": "hey man"},
                    {"role": "system", "content": "what do you need?"},
                    
                    
                    # here we can add the last messages
                ]
        
        # add the history to the message
        for memory in history:
            userMsg =  {
                "role": "user",
                "content": memory["message"]
            }
            systemMsg = {
                "role": "system",
                "content": memory["response"]
            }
            message.append(userMsg)
            message.append(systemMsg)
        
        # add the current message to the message
        prompt = {
            "role": "system", "content": "" + str(input_message) 
            }
        
        message.append(prompt)

        # get the response from the openai api
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            max_tokens = 850,
            messages= message,
            temperature=0.5,
            )
        
        logging.info("###################")
        logging.info("current response is = ")
        logging.info(response)
        logging.info("###################")

        # markdownContent = markdown.markdown(response.choices[0].message['content'])
        responseContent = response.choices[0].message['content']

        # add the message and response to the conversation
        current_conversation.add_data_pair(message = input_message, response = responseContent, jsonInfo = response)
        return json.dumps(response.choices[0].message)
    
    def create_new_conversation(self):
        """This method is used to create a new conversation"""

        # create a new conversation with an incremental ID based on the length of the list, and append it to the conversations list
        self.conversations.append(conversation(len(self.conversations)))
    
    def create_new_conversation_with_formula(self , formula):
        """This method is used to create a new conversation with a formula"""
        
        self.create_new_conversation()
        current_conversation = self.get_latest_conversation()
        preppedFormula = "[formula] Here is a guideline on how to continue our conversation: " + formula + "\n"
        current_conversation.add_data_pair(message = preppedFormula, response = "I understand, let's continue our conversation.")
        return current_conversation.get_id()
    
    def get_latest_conversation(self):
        """This method is used to get the current conversation"""
        return self.conversations[-1]
    
    def get_conversation_by_id(self, conversation_id):
        """This method is used to get a conversation by its ID"""
        for conversation in self.conversations:
            if str(conversation.get_id()) == str(conversation_id):
                return conversation
        logging.info("Conversation not found")
        return None
    
    # remove_conversation_by_id
    def remove_conversation_by_id(self, conversation_id):
        """This method is used to remove a conversation by its ID"""
        for conversation in self.conversations:
            if str(conversation.get_id()) == str(conversation_id):
                self.conversations.remove(conversation)
                return True
        logging.info("Conversation not found")
        return False
    
    def get_conversation_history(self, conversation_id):
        """This method is used to get the history of a conversation"""
        for conversation in self.conversations:
            if conversation.get_id() == conversation_id:
                return conversation.get_data_pairs().to_json()
        return None
    

    