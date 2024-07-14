import requests
import json
import concurrent.futures
import os

APP_ID = os.getenv("APP_ID")
APP_KEY = os.getenv("APP_KEY")

foods_and_snacks = [
    "Apple","Banana","Orange","Grapes","Strawberry","Blueberry","Raspberry","Blackberry","Watermelon","Pineapple",
    "Mango","Papaya","Kiwi","Peach","Plum","Cherry","Apricot","Nectarine","Pomegranate","Cantaloupe",
    "Honeydew","Tomato","Cucumber","Carrot","Celery","Wheat","Barley","Rye","Juice", "Jelly","Yogurt",
    "Bell Pepper","Broccoli","Cauliflower","Spinach","Kale","Lettuce","Cabbage","Brussels Sprouts","Asparagus","Green Beans",
    "Peas","Corn","Potato","Sweet Potato","Pumpkin","Zucchini","Eggplant","Mushroom","Onion","Garlic",
    "Ginger","Beetroot","Radish","Turnip","Parsnip","Artichoke","Avocado","Olives","Chickpeas","Lentils",
    "Black Beans","Kidney Beans","Pinto Beans","Soybeans","Edamame","Tofu","Tempeh","Quinoa","Rice","Oats",
    "Millet","Amaranth","Buckwheat","Chia Seeds","Flax Seeds","Pumpkin Seeds","Sunflower Seeds","Almonds","Walnuts","Cashews",
    "Pistachios","Pecans","Hazelnuts","Brazil Nuts","Macadamia Nuts","Peanuts","Peanut Butter","Almond Butter","Tahini",
    "Hummus","Granola","Yogurt","Cheese","Milk","Cottage Cheese","Cream Cheese","Butter","Eggs","Chicken",
    "Beef","Pork","Lamb","Turkey","Fish","Shrimp","Crab","Lobster","Salmon","Tuna","Pizza","Pasta","Ravioli","Spaghetti",
    "Lasagna","Risotto","Casserole","Omelette","Pancakes","Waffles","Crepes","Custard","Cocoa","Coffee","Tea","Water", "Burger",
    "Fries", "Salad", "Soup"
]

def search_recipes(query, number):
    '''
    Search for recipes based on the query and app_id and app_key
    returns a list of recipes.
    '''
    base_url = "https://api.edamam.com/search"
    params = {
        'q': query,
        'app_id': APP_ID,
        'app_key': APP_KEY,
        'from': 0,
        'to': number
    }

    response = requests.get(base_url, params=params)
    
    if response.status_code == 200:
        data = response.json()
        return data['hits']
    else:
        print(f"Error: {response.status_code}")
        return None
    
def api_cache():
    all_recipes = []
    def fetch_recipes(food):
        return search_recipes(food, 6)
      
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_to_food = {executor.submit(fetch_recipes, food): food for food in foods_and_snacks}
        for future in concurrent.futures.as_completed(future_to_food):
            food = future_to_food[future]
            try:
                recipes = future.result()
                all_recipes.extend(recipes)
            except Exception as exc:
                print(f'Food {food} generated an exception: {exc}')
    return json.dumps(all_recipes)
