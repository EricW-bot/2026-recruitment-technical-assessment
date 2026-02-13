from dataclasses import dataclass
from typing import List, Dict, Union
from flask import Flask, request, jsonify
import re

# ==== Type Definitions, feel free to add or modify ===========================
@dataclass
class CookbookEntry:
	name: str

@dataclass
class RequiredItem():
	name: str
	quantity: int

@dataclass
class Recipe(CookbookEntry):
	required_items: List[RequiredItem]

@dataclass
class Ingredient(CookbookEntry):
	cook_time: int


# =============================================================================
# ==== HTTP Endpoint Stubs ====================================================
# =============================================================================
app = Flask(__name__)

# Store your recipes here!
cookbook = []

# Task 1 helper (don't touch)
@app.route("/parse", methods=['POST'])
def parse():
	data = request.get_json()
	recipe_name = data.get('input', '')
	parsed_name = parse_handwriting(recipe_name)
	if parsed_name is None:
		return 'Invalid recipe name', 400
	return jsonify({'msg': parsed_name}), 200

# [TASK 1] ====================================================================
# Takes in a recipeName and returns it in a form that 
def parse_handwriting(recipeName: str) -> Union[str | None]:
	# First condition. '-' and '_' become ' '
	recipeName = recipeName.replace('-', ' ').replace('_', ' ')

	newName = ""

	# Loop for valid characters
	for char in recipeName:
			if char.isalpha() or char.isspace():
				newName += char

	# Put words into an array
	words = newName.split()

	# Remove whitespace and capitalize
	words = [word.strip().capitalize() for word in words]

	# Join them back together with a single space
	newName = " ".join(words)

	# 4. Return None if empty, else the name
	return newName if len(newName) > 0 else None


# [TASK 2] ====================================================================
# Endpoint that adds a CookbookEntry to your magical cookbook
@app.route('/entry', methods=['POST'])
def create_entry():
	data = request.get_json()

	# Type must be either 'recipe' or 'ingredient'
	type = data.get('type', '')
	if type != "recipe" and type != "ingredient":
		return "", 400

	# Each entry must have a unique name
	name = data.get('name', '')
	nameExists = any(entry.get('name') == name for entry in cookbook)
	if nameExists:
		return "", 400

	if type == "ingredient":
		# cookTime must be a number and >= 0
		cookTime = data.get('cookTime', '')
		if not isinstance(cookTime, int) or cookTime < 0:
			return "", 400

	if type == "recipe":
		# Check for duplicate names in requiredItems
		seenNames = []
		
		# Loop to check names
		for item in data.get('requiredItems', []):
			if item.get('name') in seenNames:
				return "", 400
			seenNames.append(item["name"]);

	cookbook.append(data);
	return "", 200


# [TASK 3] ====================================================================
# Endpoint that returns a summary of a recipe that corresponds to a query name
@app.route('/summary', methods=['GET'])
def summary():
	# TODO: implement me
	return 'not implemented', 500


# =============================================================================
# ==== DO NOT TOUCH ===========================================================
# =============================================================================

if __name__ == '__main__':
	app.run(debug=True, port=8080)
