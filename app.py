from flask import Flask, request, render_template, redirect, url_for, send_file
import json
from openai_logic import *
from conversations import conversation
from formula_manager import FormulaManager , Formula
from dataclasses import dataclass
import logging
import sys
import yaml

# set up the logging
root_logger = logging.getLogger()
log_file = "system_logging.log"
file_handler = logging.FileHandler(log_file, encoding="utf-8")
format_output = '%(asctime)s %(message)s'
formatter = logging.Formatter(format_output, datefmt='%m/%d/%Y %I:%M:%S %p')
file_handler.setFormatter(formatter)
root_logger.setLevel(logging.DEBUG)
root_logger.addHandler(file_handler)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.ERROR)
root_logger.addHandler(console_handler)


app = Flask(__name__,  static_url_path= '/static')
ai = ai_manager()
fm = FormulaManager([])
conversation_id_list = []
user_conversations = []
user_data = {
    "username": 'user1 ',
    "user_conversations": user_conversations,
    "active_conversation": ""
}


# update the user data
def updateUserData( active_conversation = None ):
    """This method is used to update the user data"""

    user_conversations = ai.conversations
    user_data['user_conversations'] = []
    
    for conversation in user_conversations:
        user_data['user_conversations'].append(
            {
                'id': conversation.get_id(),
                'title': conversation.get_title(),
                'history': conversation.get_data_pairs()
            }
        )

    if active_conversation != None:
        user_data['active_conversation'] = active_conversation.get_id()

    userDump = json.dumps(user_data, indent=4)
    logging.info("user data updated")
    logging.debug(userDump)

############################################# ROUTES #############################################

@app.route('/', methods=['GET', 'POST'])
def base():
    formulas = fm.get_all_formulas_json()
    logging.info("user is requesting formula list")
    logging.debug( formulas )
    return render_template( 'chat.html', user = user_data , formulas = formulas )


@app.route('/chat', methods=['GET', 'POST'])
def chat():
    formulas = fm.get_all_formulas_json()
    return render_template( 'chat.html', user = user_data , formulas = formulas )

@app.route('/editformula', methods=['GET', 'POST'])
def editformula():
    fm.add_formula()
    formulas = fm.get_all_formulas_json()

    return render_template( 'editformula.html', user = user_data , formulas = formulas , active_formula = formulas[-1] )

@app.route('/editformula/<formula_id>', methods=['GET', 'POST'])
def editformula_id(formula_id):
    logging.info("user is requesting formula with id = " + str(formula_id) )
    formulas = fm.get_all_formulas_json()
    active_formula = None
    for formula in formulas:
        if str(formula['id']) == str(formula_id):
            logging.info("formula found")
            return render_template( 'editformula.html', user = user_data , formulas = formulas , active_formula = formula )

    return render_template( 'editformula.html', user = user_data , formulas = formulas , active_formula = None )

@app.route('/new-conversation', methods=['GET', 'POST'])
def new_conversation():
    logging.info("user is requesting new conversation")
    if request.method == 'POST':
        if request.form["formula"]:
            formulaTitle = request.form["formula"]
            if formulaTitle != None:
                logging.info("user is requesting new conversation with formula = " + formulaTitle )   
                formulaToSend = fm.retrieve_by_title( formulaTitle )
                formulaContent = formulaToSend['content']
                ai.create_new_conversation_with_formula( formulaContent )

                updateUserData( ai.get_latest_conversation() )
                logging.info("user is requesting new conversation")
                formulas = fm.get_all_formulas_json()

                return render_template('chat.html', user = user_data , formulas = formulas  )
            
        # create a new conversation
        ai.create_new_conversation()

        # gets the last conversation in the list
        updateUserData( ai.get_latest_conversation() )
        logging.info("user is requesting new conversation")
        formulas = fm.get_all_formulas_json()
        return render_template('chat.html', user = user_data , formulas = formulas  )
    
    formulas = fm.get_all_formulas_json()

    return render_template('chat.html', user = user_data , formulas = formulas )

@app.route('/conversation/<conversation_id>', methods=['GET', 'POST'])
def conversation(conversation_id):
    logging.info("user is requesting conversation with id = " + conversation_id )
    updateUserData()
    print("user is requesting conversation with id = " + conversation_id )
    if conversation_id != None:
        # get the conversation with the id
        conversation = ai.get_conversation_by_id( conversation_id )
        if conversation != None:
            logging.info("conversation found")
            updateUserData( conversation )
            formulas = fm.get_all_formulas_json()
            return render_template('chat.html', user = user_data , formulas = formulas )
    formulas = fm.get_all_formulas_json()
    return render_template('index.html', user = user_data , formulas = formulas )

@app.route('/conversation/<conversation_id>/remove', methods=['GET', 'POST'])
def remove_conversation(conversation_id):
    logging.info("user is requesting to remove conversation with id = " + conversation_id )
    ai.remove_conversation_by_id( conversation_id )
    updateUserData()
    return redirect(url_for('chat'))


@app.route('/send_message', methods=['GET', 'POST'])
def send_message():
    logging.info("user is sending a message")
    if request.method == 'POST':
        logging.info("post request")
        input_message = str(request.form['message'])
        conversation_id = str(request.form['conversationId'])
        logging.info("conversation_id = " + conversation_id)
        if conversation != None:
            logging.info("conversation found")
            response = ai.get_response( input_message,  conversation_id   )
            logging.info(response)
            return response
        else:
            logging.warning("conversation not found")
            return "conversation not found"
    else:
        return "not a post request"
    
@app.route('/gethistory', methods=['GET', 'POST'])
def get_history():
    logging.info("user is requesting history")
    if request.method == 'POST':
        logging.info("post request")
        id = str(request.form['conversationId'])
        logging.info("conversation_id = " + id)
        conversation = ai.get_conversation_by_id( id )
        if conversation != None:
            response = conversation.get_data_pairs()
            logging.info("====================================")
            logging.info("HISTORY:")
            logging.info(response)

            data = {
                'history': response
            }
            return data
        else:
            return "no history"
    return "not a post request"

@app.route('/formulas/getformulas', methods=['GET', 'POST'])
def get_formulas():
    logging.info("user is requesting formulas")
    if request.method == 'POST':
        logging.info("post request")
        formulas = fm.retrieve_all()
        for formula in formulas:
            formula = formula.to_json()
        return formulas
    
@app.route('/formulas/loadlocal', methods=['GET', 'POST'])
def load_local_formulas():
    logging.info("user is requesting to load local formulas into the formula manager")
    if request.method == 'POST':
        send_file = request.files['formulaFile']
        if send_file and send_file.filename != '' and send_file.filename.endswith('.yaml'):
            logging.info("file is yaml")
            send_file = yaml.safe_load(send_file.read())
            try:
                fm.load_formula_from_local(send_file)
                return redirect(url_for('base'))
            except:
                logging.warning("error loading formulas from file")
                logging.warning("error: " + str(sys.exc_info()[0]))
                return redirect(url_for('base'))
        else:
            logging.warning("file is not yaml")
            return redirect(url_for('base'))
    else:
        return redirect(url_for('base'))

@app.route('/formulas/addformula', methods=['GET', 'POST'])
def add_formula():
    logging.info("user is adding a formula")
    if request.method == 'POST':
        logging.info("post request")
        formula = str(request.form['formula'])
        print("formula = " + formula)
        fm.add_formula( formula )
        return "formula added"
    return "not a post request"

@app.route('/formulas/removeformula/<formula_id>', methods=['GET', 'POST'])
def remove_formula( formula_id ):
    logging.info("user is removing a formula")
    if request.method == 'POST':
        logging.info("post request received to remove formula with id = " + formula_id)
        fm.remove_formula( int(formula_id) )
        print("formula removed")
        return "formula removed"
    return "not a post request"

@app.route('/formulas/editformula', methods=['GET', 'POST'])
def edit_formula():
    logging.info("user is editing a formula")
    if request.method == 'POST':
        logging.info("post request")
        logging.info("editing formula")

        formulaID = str(request.form['formulaID'])
        formulaTitle = str(request.form['formulaTitle'])
        formulaDescription = str(request.form['formulaDescription'])
        formula = str(request.form['formula'])
        logging.info("formulaID = " + formulaID)
        logging.info("formulaTitle = " + formulaTitle)
        logging.info("formulaDescription = " + formulaDescription)
        logging.info("formula = " + formula)
        fm.edit_formula( id = formulaID, title = formulaTitle, description = formulaDescription, content =  formula )

        return "formula edited"
    return "not a post request"

@app.route('/formulas/saveformula/<int:formula_id>', methods=['GET', 'POST'])
def save_formula( formula_id ):
    logging.info("saving formula with id = " + str(formula_id))
    fm.save_formula_to_local( formula_id )
    return "formula saved"

@app.route('/formulas/downloadformula/<int:formula_id>', methods=['GET', 'POST'])
def download_formula( formula_id ):
    logging.info("downloading formula with id = " + str(formula_id))
    return send_file( fm.get_file_path( formula_id ), as_attachment=True )

if __name__ == '__main__':
    app.run(debug=True)


