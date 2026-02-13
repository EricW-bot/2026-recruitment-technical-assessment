import express, { Request, Response } from "express";
import { capitalCase } from "change-case";

// ==== Type Definitions, feel free to add or modify ==========================
interface cookbookEntry {
  name: string;
  type: string;
}

interface requiredItem {
  name: string;
  quantity: number;
}

interface recipe extends cookbookEntry {
  requiredItems: requiredItem[];
}

interface ingredient extends cookbookEntry {
  cookTime: number;
}

interface SummaryResult {
  ingredients: Record<string, number>;
  cookTime: number;
}

// =============================================================================
// ==== HTTP Endpoint Stubs ====================================================
// =============================================================================
const app = express();
app.use(express.json());

// Store your recipes here!
const cookbook: any[] = [];

// Task 1 helper (don't touch)
app.post("/parse", (req:Request, res:Response) => {
  const { input } = req.body;

  const parsed_string = parse_handwriting(input)
  if (parsed_string == null) {
    res.status(400).send("this string is cooked");
    return;
  } 
  res.json({ msg: parsed_string });
  return;
  
});

// [TASK 1] ====================================================================
// Takes in a recipeName and returns it in a form that 
const parse_handwriting = (recipeName: string): string | null => {
  let newName: string = "";

  for (const char of recipeName) {
    // First condition: Replace '-' and '_' with ' '
    if (char === '-' || char === '_')  {
      newName += ' ';
      continue;
    }

    let isLetter = (char.toLowerCase() >= 'a' && char.toLowerCase() <= 'z');
    let isSpace = (char === ' ');
    // If char is a letter or number, append to newName
    if (isLetter || isSpace) newName += char;
  }
  
  // Use change-case library to format the name to capital case
  // Using .toLowerCase() to prevent camelCase boundary
  newName = capitalCase(newName.toLowerCase());

  // Return null if the newName is empty, otherwise return the formatted name
  return newName.length === 0 ? null : newName;
}

// [TASK 2] ====================================================================
// Endpoint that adds a CookbookEntry to your magical cookbook
app.post("/entry", (req: Request, res: Response) => {
  const entry = req.body;

  // Type must be either 'recipe' or 'ingredient'
  if (entry.type !== "recipe" && entry.type !== "ingredient") {
    return res.status(400).send();
  }

  // Each entry must have a unique name
  const nameExists = cookbook.some((existingEntry) => existingEntry.name === entry.name);
  if (nameExists) {
    return res.status(400).send();
  }

  if (entry.type === "ingredient") {
    // cookTime must be a number and >= 0
    if (typeof entry.cookTime !== "number" || entry.cookTime < 0) {
      return res.status(400).send();
    }
  }

  if (entry.type === "recipe") {
    // Check for duplicate names in requiredItems
    const seenNames: string[] = [];
    
    for (const item of entry.requiredItems) {
      if (seenNames.includes(item.name)) {
        return res.status(400).send();
      }
      seenNames.push(item.name);
    }
  }

  cookbook.push(entry);
  return res.status(200).send();
});

// Recursive helper function to get sub-recipes and sub-ingredients
const getSummary = (name: string, quantity: number, cookbook: any[]): SummaryResult | null => {
  const item = cookbook.find(e => e.name === name);
  if (!item) return null;

  // Ingredient
  if (item.type === "ingredient") {
    const ingredients: Record<string, number> = {};
    ingredients[name] = quantity;
    return { 
      ingredients, 
      cookTime: item.cookTime * quantity 
    };
  }

  // If recipe, then recurse
  if (item.type === "recipe") {
    // Store all ingredients in an object with keys as strings and values as numbers
    const totalIngredients: Record<string, number> = {};
    let totalCookTime = 0;

    for (const required of item.requiredItems) {
      const subResult = getSummary(required.name, required.quantity * quantity, cookbook);
      
      // If any sub-item is missing, return null
      if (!subResult) return null;

      // Recursively add cook time
      totalCookTime += subResult.cookTime;

      // Merge sub-ingredients into totalIngredients
      for (const [ingredientName, ingredientQuantity] of Object.entries(subResult.ingredients)) {
        // If we already have this ingredient, add to it. Otherwise start at 0.
        const currentQty = totalIngredients[ingredientName] || 0;
        totalIngredients[ingredientName] = currentQty + ingredientQuantity;
      }
    }
    
    return { ingredients: totalIngredients, cookTime: totalCookTime };
  }
  
  return null;
};

// [TASK 3] ====================================================================
// Endpoint that returns a summary of a recipe that corresponds to a query name
app.get("/summary", (req: Request, res: Response) => {
  const recipeName = req.query.name as string;

  // 1. Find the root item
  const rootItem = cookbook.find(existingNames => existingNames.name === recipeName);
  if (!rootItem || rootItem.type !== "recipe") {
    return res.status(400).send();
  }

  // 2. Call the helper function
  const result = getSummary(recipeName, 1, cookbook);

  if (!result) {
    return res.status(400).send();
  }

  // { Egg: 3 } turns into { name: "Egg", quantity: 3 }
  const formattedIngredients = Object.entries(result.ingredients).map(([name, quantity]) => ({
    name,
    quantity
  }));

  return res.status(200).json({
    name: recipeName,
    cookTime: result.cookTime,
    ingredients: formattedIngredients
  });
});

// =============================================================================
// ==== DO NOT TOUCH ===========================================================
// =============================================================================
const port = 8080;
app.listen(port, () => {
  console.log(`Running on: http://127.0.0.1:8080`);
});
