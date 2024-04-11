import random
import json
import os
from datetime import datetime

# File to store the data
BIOMETRIC_DATA_FILE = 'biometric_data.json'
MEALS_DATA_DIR = 'meals_data'
MEALS_DATABASE_FILE = 'meals_database.json'

# Adjusting the method to maximize the use of the available time while being beginner-friendly
def generate_dynamic_exercise_plan(intensity, max_time_minutes):
    # Define exercise types and their time per mile (minutes per mile) for different intensities, tailored for beginners
    exercise_types = {
        'walking': {'low': 30, 'medium': 25, 'high': 20},  # Adjusted paces for a more inclusive range
    }
    
    # Assume walking for inclusivity and safety for beginners
    exercise_type = 'walking'
    
    # Get the time per mile for walking and the chosen intensity
    time_per_mile = exercise_types[exercise_type][intensity]
    
    # Calculate the number of miles that can be realistically covered within the max_time_minutes at the chosen pace
    miles_covered = max_time_minutes / time_per_mile
    
    # Generate the message based on the calculated distance
    message = f"{exercise_type.capitalize()} at {intensity} intensity for {max_time_minutes} minutes, aiming to cover {miles_covered:.2f} miles."
    
    return message

def load_data(file_path):
    """Generic function to load data from a given JSON file."""
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            return json.load(file)
    else:
        # Return a default structure depending on the file
        if file_path == BIOMETRIC_DATA_FILE:
            return {"current": {}, "historic_data": []}
        else:
            return {"meals": []}

def save_data(data, file_path):
    """Generic function to save data to a given JSON file."""
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)

def convert_height_inches_to_cm(inches):
    """Convert height from inches to cm."""
    return inches * 2.54

def convert_weight_pounds_to_kg(pounds):
    """Convert weight from pounds to kg."""
    return pounds * 0.453592

def update_biometric_data(data):
    """Update the user's biometric data, including age."""
    new_entry = {"timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    
    if data["current"]:
        print("You are about to create a new biometric record. This will save your current data as historical.")
        confirmation = input("Are you sure you want to proceed? (yes/no): ").lower()
        if confirmation != "yes":
            print("Update cancelled.")
            return

    # Collecting new biometric information including age
    new_entry["height"] = convert_height_inches_to_cm(float(input("Height (in inches): ")))
    new_entry["weight"] = convert_weight_pounds_to_kg(float(input("Weight (in pounds): ")))
    new_entry["gender"] = input("Gender (m/f): ")
    new_entry["activity_level"] = input("Activity level (low, moderate, high): ")
    new_entry["age"] = int(input("Age: "))
    
    # Save current data to historic_data before updating if current data exists
    if data["current"]:
        data["historic_data"].append(data["current"])
    data["current"] = new_entry
    save_data(data)
    print("Biometric data updated successfully.")

def view_biometric_data(data):
    """Display the user's current biometric data including age."""
    if not data["current"]:
        print("No biometric data available.")
        return
    
    print("\nCurrent Biometric Data:")
    for key, value in data["current"].items():
        print(f"{key.capitalize()}: {value}")

def view_historic_data(data):
    """Display a menu for the user to select and view a specific historic entry."""
    if not data["historic_data"]:
        print("No historic biometric data available.")
        return

    print("\nSelect a historic entry to view by its number:")
    for i, entry in enumerate(data["historic_data"], start=1):
        print(f"{i}. Timestamp: {entry['timestamp']}")
    
    try:
        selection = int(input("Entry number: ")) - 1
        if 0 <= selection < len(data["historic_data"]):
            selected_entry = data["historic_data"][selection]
            print(f"\nViewing Entry: Timestamp: {selected_entry['timestamp']}")
            for key, value in selected_entry.items():
                if key == "height":
                    print(f"Height: {value:.2f} cm")
                elif key == "weight":
                    print(f"Weight: {value:.2f} kg")
                else:
                    print(f"{key.capitalize()}: {value}")
        else:
            print("Invalid entry number.")
    except ValueError:
        print("Please enter a valid number.")

def delete_specific_record(data):
    """Delete a specific record from the historic data."""
    if not data["historic_data"]:
        print("No historic data to delete.")
        return
    
    for i, entry in enumerate(data["historic_data"], start=1):
        print(f"{i}. Timestamp: {entry['timestamp']}")
    
    try:
        record_number = int(input("Enter the number of the record you wish to delete: ")) - 1
        if 0 <= record_number < len(data["historic_data"]):
            del data["historic_data"][record_number]
            save_data(data)
            print("Record deleted successfully.")
        else:
            print("Invalid record number.")
    except ValueError:
        print("Please enter a valid number.")

def delete_all_records(data):
    """Delete all historic data."""
    confirmation = input("Are you sure you want to delete all records? (yes/no): ").lower()
    if confirmation == "yes":
        data["historic_data"].clear()
        save_data(data)
        print("All records have been deleted.")
    else:
        print("Operation canceled.")

def calculate_daily_needs(biometric_data):
    """Calculate daily nutritional needs based on the latest biometric data."""
    # Extract relevant data
    height_cm = biometric_data.get("height", 0)
    weight_kg = biometric_data.get("weight", 0)
    age = biometric_data.get("age", 0)  # Example age; you might want to include age in biometric data
    gender = biometric_data.get("gender", "m")
    activity_level = biometric_data.get("activity_level", "low")

    # Calculate BMR
    if gender == 'm':
        bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age + 5
    else:
        bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age - 161

    # Adjust BMR based on activity level
    activity_factors = {"low": 1.2, "moderate": 1.55, "high": 1.9}
    calories_needed = bmr * activity_factors.get(activity_level, 1.2)

    # Create a caloric deficit for weight loss
    calories_needed -= 500

    # Suggested macro distribution: 40% carbs, 30% protein, 30% fats
    macros = {
        "carbs": int(0.4 * calories_needed / 4),  # Carbs: 4 kcal per gram
        "protein": int(0.3 * calories_needed / 4),  # Protein: 4 kcal per gram
        "fat": int(0.3 * calories_needed / 9)  # Fats: 9 kcal per gram
    }

    return calories_needed, macros

def log_meal(name, calories, carbs, protein, fat, date=None, quantity=1):
    """Log a meal's nutritional content along with quantity consumed."""
    if date is None:
        date = datetime.now().strftime("%Y-%m-%d")
    meal_data_path = os.path.join(MEALS_DATA_DIR, f"{date}.json")
    meals_data = load_data(meal_data_path)

    meal_entry = {
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'name': name,
        'calories': calories,
        'carbs': carbs,
        'protein': protein,
        'fat': fat,
        'quantity': quantity  # Store quantity per meal
    }

    meals_data.get('meals', []).append(meal_entry)
    save_data(meals_data, meal_data_path)
    print(f"{quantity} unit(s) of '{name}' logged successfully.")

def get_remaining_macros(date=None):
    """Calculate and display remaining macros for the day."""
    if date is None:
        date = datetime.now().strftime("%Y-%m-%d")
    meal_data_path = os.path.join(MEALS_DATA_DIR, f"{date}.json")
    meals_data = load_data(meal_data_path).get('meals', [])
    
    # Load latest biometric data to calculate daily needs
    biometric_data = load_data(BIOMETRIC_DATA_FILE).get("current", {})
    daily_calories, daily_macros = calculate_daily_needs(biometric_data)

    total_intake = {'calories': 0, 'carbs': 0, 'protein': 0, 'fat': 0}
    for meal in meals_data:
        for nutrient in total_intake.keys():
            total_intake[nutrient] += meal.get(nutrient, 0)

    remaining_macros = {nutrient: daily_macros.get(nutrient, 0) - total_intake.get(nutrient, 0) for nutrient in daily_macros.keys()}
    remaining_calories = daily_calories - total_intake['calories']

    return remaining_calories, remaining_macros

def delete_specific_meal(date=None):
    """Delete a specific meal from the day's meal log."""
    if date is None:
        date = datetime.now().strftime("%Y-%m-%d")
    meal_data_path = os.path.join(MEALS_DATA_DIR, f"{date}.json")
    meals_data = load_data(meal_data_path)

    if not meals_data.get('meals'):
        print("No meals logged today.")
        return
    
    for i, meal in enumerate(meals_data['meals'], start=1):
        print(f"{i}. {meal['name']}")
    
    try:
        choice = int(input("Select a meal to delete (enter number): ")) - 1
        if 0 <= choice < len(meals_data['meals']):
            del meals_data['meals'][choice]
            save_data(meals_data, meal_data_path)
            print("Meal deleted successfully.")
        else:
            print("Invalid meal selection.")
    except ValueError:
        print("Please enter a valid number.")

def delete_all_meals(date=None):
    """Delete all meals for the day after confirmation."""
    confirmation = input("Are you sure you want to delete all meals for today? (y/n): ").lower()
    if confirmation == 'y':
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
        meal_data_path = os.path.join(MEALS_DATA_DIR, f"{date}.json")
        save_data({'meals': []}, meal_data_path)
        print("All meals deleted.")
    else:
        print("Deletion cancelled.")

def log_meal_process():
    print("\n1. Select a meal from a restaurant")
    print("2. Add a new meal")
    print("3. Exit")
    choice = input("Choose an option: ").strip()

    if choice == "1":
        select_meal_from_restaurant()
    elif choice == "2":
        add_new_meal()
    elif choice == "3":
        return
    else:
        print("Invalid option. Please try again.")
        log_meal_process()

def select_meal_from_restaurant():
    meals_db = load_data(MEALS_DATABASE_FILE)
    restaurants = list(meals_db.keys())
    if not restaurants:  # No restaurants found
        print("No restaurants available. Redirecting to add a new meal.")
        add_new_meal()
        return

    print("\nAvailable Restaurants:")
    for index, restaurant in enumerate(restaurants, start=1):
        print(f"{index}. {restaurant.capitalize()}")
    print(f"{len(restaurants) + 1}. Add a meal from a new restaurant")
    print(f"{len(restaurants) + 2}. Exit")

    choice = input("Select an option: ").strip()
    if choice.isdigit():
        choice = int(choice)
        if 1 <= choice <= len(restaurants):
            display_meals_for_restaurant(restaurants[choice - 1], meals_db)
        elif choice == len(restaurants) + 1:
            add_new_meal(new_restaurant=True)
        elif choice == len(restaurants) + 2:
            return
        else:
            print("Invalid selection.")
    else:
        print("Please enter a valid number.")


def display_meals_for_restaurant(restaurant, meals_db):
    meals = meals_db[restaurant]
    if not meals:
        print("No meals found for this restaurant. Adding a new meal.")
        add_new_meal(restaurant=restaurant)
        return

    for index, meal in enumerate(meals, start=1):
        print(f"{index}. {meal['name'].capitalize()} - {meal['calories']} calories per unit")
    print(f"{len(meals) + 1}. Add a new meal")
    print(f"{len(meals) + 2}. Exit")

    choice = input("Select a meal or add a new one: ").strip()
    if choice.isdigit() and 1 <= int(choice) <= len(meals):
        selected_meal = meals[int(choice) - 1]
        quantity = input(f"How many units of {selected_meal['name'].capitalize()} did you consume? [default: 1] ").strip()
        quantity = int(quantity) if quantity.isdigit() else 1  # Default to 1 if no or invalid input
        log_meal(selected_meal['name'], selected_meal['calories'], selected_meal['carbs'],
                 selected_meal['protein'], selected_meal['fat'], quantity=quantity)
    elif choice == str(len(meals) + 1):
        add_new_meal(restaurant=restaurant)
    elif choice == str(len(meals) + 2):
        return
    else:
        print("Invalid selection. Please try again.")
        display_meals_for_restaurant(restaurant, meals_db)

def add_new_meal(new_restaurant=False):
    if new_restaurant:
        restaurant = input("Enter the name of the new restaurant: ").strip().lower()
    else:
        print("\n1. Add to an existing restaurant")
        print("2. Add to a new restaurant")
        sub_choice = input("Choose an option: ").strip()
        if sub_choice == "1":
            meals_db = load_data(MEALS_DATABASE_FILE)
            if meals_db:
                restaurants = list(meals_db.keys())
                for index, res in enumerate(restaurants, start=1):
                    print(f"{index}. {res.capitalize()}")
                res_choice = input("Select a restaurant: ").strip()
                if res_choice.isdigit() and 1 <= int(res_choice) <= len(restaurants):
                    restaurant = restaurants[int(res_choice) - 1]
                else:
                    print("Invalid selection.")
                    return
            else:
                print("No existing restaurants found. Adding a new one.")
                restaurant = input("Enter the name of the new restaurant: ").strip().lower()
        elif sub_choice == "2":
            restaurant = input("Enter the name of the new restaurant: ").strip().lower()
        else:
            print("Invalid option. Returning to main menu.")
            return

    meal_name = input("Meal name: ").lower().strip()
    calories = int(input("Calories per unit: "))
    carbs = int(input("Carbs (in grams) per unit: "))
    protein = int(input("Protein (in grams) per unit: "))
    fat = int(input("Fat (in grams) per unit: "))

    # Save the new meal
    meal = {'name': meal_name, 'calories': calories, 'carbs': carbs, 'protein': protein, 'fat': fat}
    meals_db = load_data(MEALS_DATABASE_FILE)
    if restaurant not in meals_db:
        meals_db[restaurant] = []
    meals_db[restaurant].append(meal)
    save_data(meals_db, MEALS_DATABASE_FILE)
    print(f"New meal '{meal_name}' added to '{restaurant}'.")

def add_meals_to_database():
    print("Adding meals to the meal database.")
    meals_db = load_data(MEALS_DATABASE_FILE)
    
    restaurant = input("Enter the name of the restaurant or choose from existing: ").strip().lower()
    if restaurant not in meals_db:
        if input(f"Restaurant '{restaurant}' does not exist. Add new? (y/n): ").strip().lower() == 'y':
            meals_db[restaurant] = []
        else:
            print("Operation cancelled.")
            return

    meal_name = input("Meal name: ").strip().lower()
    calories = int(input("Calories: "))
    carbs = int(input("Carbs (in grams): "))
    protein = int(input("Protein (in grams): "))
    fat = int(input("Fat (in grams): "))

    new_meal = {'name': meal_name, 'calories': calories, 'carbs': carbs, 'protein': protein, 'fat': fat}
    meals_db[restaurant].append(new_meal)
    save_data(meals_db, MEALS_DATABASE_FILE)
    print(f"Meal '{meal_name}' added to '{restaurant}' in the meal database.")


def main():
    data = load_data(BIOMETRIC_DATA_FILE)
    while True:
        print("\n1. Update Biometric Data")
        print("2. View Biometric Data")
        print("3. View Historic Data")
        print("4. Delete a Specific Record")
        print("5. Delete All Records")
        print("6. Log Meal")
        print("7. View Remaining Macros and Calories for Today")
        print("8. Delete a specific meal")
        print("9. Delete all meals")
        print("10. Add meals to meal database")  # New option
        print("11. Exit")
        choice = input("Select an option: ").strip()
        
        if choice == "1":
            update_biometric_data(data)
        elif choice == "2":
            view_biometric_data(data)
        elif choice == "3":
            view_historic_data(data)
        elif choice == "4":
            delete_specific_record(data)
        elif choice == "5":
            delete_all_records(data)
        elif choice == "6":
            log_meal_process()
        elif choice == "7":
            remaining_calories, remaining_macros = get_remaining_macros()
            print("Remaining for today:")
            print(f"Calories: {remaining_calories}")
            for macro, amount in remaining_macros.items():
                print(f"{macro.capitalize()}: {amount}g")
        elif choice == "8":
            delete_specific_meal()
        elif choice == "9":
            delete_all_meals()
        elif choice == "10":
            add_meals_to_database()  # Call function to add meals to the database
        elif choice == "11":
            print("Exiting...")
            break
        else:
            print("Invalid option. Please try again.")

if __name__ == "__main__":
    main()
# Example usage, maximizing the use of the available time for a low intensity walk
#print(generate_dynamic_exercise_plan('low', 60))  # Low intensity, with a maximum of 60 minutes
