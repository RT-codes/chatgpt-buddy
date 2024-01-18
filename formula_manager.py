from typing import List
from dataclasses import dataclass
import time
import yaml
import logging

# this is the formula class
# it holds the formula data and has methods to retrieve it
@dataclass
class Formula:
    id: int = ""
    title: str = ""
    description: str = ""
    content: str = ""
    timestamp: str = ""
    json_object: dict = None

    def __init__(self, id , title = "", description = "", content = "", timestamp = ""):
        self.id : int = id
        self.title = title
        self.description = description
        self.content = content
        self.timestamp = timestamp

    def __str__(self) -> str:
        return f"Formula {self.id} '{self.title}'"
    
    def __repr__(self) -> str:
        return f"Formula(id={self.id}, title='{self.title}', description='{self.description}', content='{self.content}', timestamp='{self.timestamp}')"

    def to_json(self) -> dict:
        """Converts the formula to a json object."""
        json_object = {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'content': self.content,
            'timestamp': self.timestamp
        }
        self.json_object = json_object
        return self.json_object

# this is the formula manager class
# it holds all the formulas and has methods to retrieve them
# it also has methods to sort the formulas
@dataclass
class FormulaManager:
    formulas: List[Formula]
    
    def retrieve_all(self) -> List[Formula]:
        """Retrieves all the formulas."""
        return self.formulas

    def retrieve_by_id(self, formula_id: int) -> Formula:
        """Retrieves the formula with the given id."""
        for formula in self.formulas:
            if formula.id == formula_id:
                return formula
        raise ValueError(f"No formula with id {formula_id} found.")
    
    def retrieve_by_title(self, title: str) -> Formula:
        """Retrieves the formula with the given title."""
        for formula in self.formulas:
            if formula.title == title:
                return formula.to_json()
        raise ValueError(f"No formula with title '{title}' found.")
    
    # sort the formulas by title alphabetically
    def sort_alphabetically(self) -> List[Formula]:
        """Sorts the formulas alphabetically by title."""
        return sorted(self.formulas, key=lambda formula: formula.title)
    
    # sort the formulas by date created in ascending order so oldest first
    def sort_by_date_created(self) -> List[Formula]:
        """Sorts the formulas by date created."""
        return sorted(self.formulas, key=lambda formula: formula.timestamp)
    
    def get_all_formulas_json(self) -> List[Formula]:
        """Returns all the formulas."""
        # make a json for each formula
        jsonFormulas = []
        for formula in self.formulas:
            jsonFormula =  formula.to_json()
            logging.info(jsonFormula)
            jsonFormulas.append(jsonFormula)

        return jsonFormulas
    
    # function to add a formula to the list of formulas and accept id, title, description, timestamp, and json_object
    def add_formula(self) -> None:
        """Adds a formula to the list of formulas."""
        formulaId = len(self.formulas)
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        logging.info("formula added")
        self.formulas.append( Formula( id = formulaId, timestamp  = timestamp) )
        logging.info(self.formulas)

    def get_data( self, formulaId ):
        for formula in self.formulas:
            if formula.id == formulaId:
                return formula.to_json()

    def get_last_formula(self) -> Formula:
        return self.formulas[-1]

    def remove_formula(self, id: int) -> None:
        """Removes a formula from the list of formulas. Per id."""
        for formula in self.formulas:
            if formula.id == id:
                self.formulas.remove(formula)
                return
        
        logging.info("formula removed")
        raise ValueError(f"No formula with id {id} found.")

    # function to edit any of the formula data per id
    def edit_formula(self, id : str, title: str, description: str, content: str) -> None:
        """Edits a formula from the list of formulas. Per id."""
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        id = int(id)

        for formula in self.formulas:
            if formula.id == id:
                formula.title = title
                formula.description = description
                formula.content = content
                formula.timestamp = timestamp
                return
        raise ValueError(f"No formula with id {id} found.")
    
    # function to save a formula to a yaml file
    def save_formula_to_local(self, id: int) -> None:
        """Saves a formula to a yaml file. Per id."""
        for formula in self.formulas:
            if formula.id == id:
                with open(f"formulas/{formula.title}_formula.yaml", 'w') as file:
                    yaml.dump(formula.to_json(), file)
                return
        raise ValueError(f"No formula with id {id} found.")

    # function to load a formula from a yaml file
    def load_formula_from_local(self, yamlFile ) -> None:
        """Loads a formula from a yaml file."""
        formula = yamlFile
        self.formulas.append(Formula(formula['id'], formula['title'], formula['description'], formula['content'], formula['timestamp']))
        return ""

    def get_file_path(self, title: str) -> str:
        """Returns the file path of a formula. Per title."""
        return f"formulas/{title}_formula.yaml"