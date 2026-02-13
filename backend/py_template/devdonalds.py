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
			seenNames.append(item["name"])

	cookbook.append(data)
	return "", 200

# Recursive helper function to get sub-recipes and sub-ingredients
def getInfo(name, quantity):
	item = next((entry for entry in cookbook if entry.get('name') == name), None)
	if not item:
		return None	

	# Ingredient
	if item["type"] == "ingredient":
		ingredients = {}
		ingredients[name] = quantity
		itemCookTime = item["cookTime"] * quantity
		return { 
			"ingredients": ingredients,
			"cookTime": itemCookTime
		}

	# If recipe, then recurse
	if item["type"] == "recipe":
		# Store all ingredients in an object with keys as strings and values as numbers
		totalIngredients = {}
		totalCookTime = 0

		for required in item["requiredItems"]:
			subResult = getInfo(required["name"], required["quantity"] * quantity)
			
			# If any sub-item is missing, return None
			if not subResult:
				return None

			# Recursively add cook time
			totalCookTime += subResult["cookTime"]

			# Merge sub-ingredients into totalIngredients
			for ingredientName, ingredientQuantity in subResult["ingredients"].items():
				# If we already have this ingredient, add to it. Otherwise start at 0.
				currentQty = totalIngredients.get(ingredientName, 0)
				totalIngredients[ingredientName] = currentQty + ingredientQuantity

		return { 
			"ingredients": totalIngredients, 
			"cookTime": totalCookTime
		}
  
	return None

# [TASK 3] ====================================================================
# Endpoint that returns a summary of a recipe that corresponds to a query name
@app.route('/summary', methods=['GET'])
def summary():
	recipeName = request.args.get('name')

	rootItem = next((entry for entry in cookbook if entry.get('name') == recipeName), None)
	if not rootItem or rootItem["type"] != "recipe":
		return "", 400

	# Use recursive helper function
	result = getInfo(recipeName, 1)

	if not result:
		return "", 400

	# { Egg: 3 } turns into { name: "Egg", quantity: 3 }
	formattedIngredients = [
		{
		"name": name,
		"quantity": quantity
		} 
		for name, quantity in result["ingredients"].items()
	]

	return jsonify({
		"name": recipeName,
		"cookTime": result["cookTime"],
		"ingredients": formattedIngredients
	}), 200
	

# =============================================================================
# ==== DO NOT TOUCH ===========================================================
# =============================================================================

if __name__ == '__main__':
	app.run(debug=True, port=8080)
