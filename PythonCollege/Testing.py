import csv
import random
from flask import Flask, jsonify, request, render_template

# Configured to look one folder up and inside WebsiteCollege for index.html
app = Flask(__name__, template_folder='../WebsiteCollege')

# --- GLOBAL GAME STATE ---
game_data = {
    "suspects": [],
    "evidence": [],
    "killer_name": "",
    "unlocked_evidence_ids": ["e1", "1"],  # Handles lowercase or numerical step IDs safely
    "interrogated_suspects": []
}

def load_game_files():
    """Loads CSV files on startup, cleans dictionary keys, and assigns a killer."""
    try:
        # 1. Load Suspects and make keys lowercase & stripped
        with open('Spreadsheets/Suspoocs.csv', mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            game_data["suspects"] = [
                {k.lower().strip(): v for k, v in row.items() if k is not None} 
                for row in reader
            ]
            
        # 2. Load Evidence and make keys lowercase & stripped
        with open('Spreadsheets/Evidoonce.csv', mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            game_data["evidence"] = [
                {k.lower().strip(): v for k, v in row.items() if k is not None} 
                for row in reader
            ]
            
        # 3. Dynamically assign a killer text name
        if game_data["suspects"]:
            chosen_killer = random.choice(game_data["suspects"])
            
            # Find a column named 'name' or fallback to the first column that isn't purely digits
            name_key = 'name' if 'name' in chosen_killer else None
            if not name_key:
                for key, val in chosen_killer.items():
                    if not str(val).strip().isdigit():
                        name_key = key
                        break
                if not name_key:
                    name_key = list(chosen_killer.keys())[0]

            game_data["killer_name"] = chosen_killer[name_key].strip()
            print(f"\n🕵️‍♂️ CASE SECRET: The target killer is set to: {game_data['killer_name']}\n")
            
    except FileNotFoundError as e:
        print(f"⚠️ Error loading files during setup: {e}")

# Process your clean setup fields
load_game_files()


# --- WEB RENDERING PATHS ---

@app.route('/')
def home():
    return render_template('index.html')


# --- DETECTIVE API ENDPOINTS ---

@app.route('/api/suspects', methods=['GET'])
def get_suspects():
    # Pass clean lowercase structures straight to the UI javascript layer
    return jsonify(game_data["suspects"])


@app.route('/api/evidence', methods=['GET'])
def get_evidence_board():
    """Returns evidence items matching unlocked trackers, case-insensitively."""
    discovered_evidence = []
    
    for item in game_data["evidence"]:
        # Check every possible ID key configuration automatically ('id', 'evidence_id', etc.)
        id_key = next((k for k in item.keys() if 'id' in k), None)
        if id_key:
            item_id_val = str(item[id_key]).lower().strip()
            # If the item matches our unlocked list, include it
            if item_id_val in game_data["unlocked_evidence_ids"]:
                discovered_evidence.append(item)
                
    # FALLBACK: If filtering didn't match anything, give the player the first item anyway
    if not discovered_evidence and game_data["evidence"]:
        discovered_evidence.append(game_data["evidence"][0])
        
    return jsonify(discovered_evidence)


@app.route('/api/interrogate', methods=['POST'])
def interrogate_suspect():
    data = request.get_json() or {}
    suspect_name = data.get("name")
    
    if not suspect_name:
        return jsonify({"message": "No suspect name provided."}), 400
    
    if suspect_name not in game_data["interrogated_suspects"]:
        game_data["interrogated_suspects"].append(suspect_name)
        
        # Unlocks subsequent rows dynamically ('e2', 'e3' or numeric equivalents)
        current_count = len(game_data["unlocked_evidence_ids"]) // 2 + 1
        game_data["unlocked_evidence_ids"].append(f"e{current_count + 1}")
        game_data["unlocked_evidence_ids"].append(str(current_count + 1))
        
        return jsonify({
            "message": f"You finished questioning {suspect_name}. A new clue was added to your evidence board!",
            "new_evidence_unlocked": True
        })
        
    return jsonify({"message": f"{suspect_name} has nothing more to say to you.", "new_evidence_unlocked": False})


@app.route('/api/accuse', methods=['POST'])
def make_accusation():
    data = request.get_json() or {}
    suspect_guess = data.get("name", "").strip()
    
    if suspect_guess.lower() == game_data["killer_name"].lower():
        return jsonify({
            "status": "victory",
            "solved": True,
            "title": "CASE CLOSED",
            "message": f"Excellent work, Detective! You successfully deduced that {game_data['killer_name']} was the culprit."
        })
    else:
        return jsonify({
            "status": "failure",
            "solved": False,
            "title": "WRONG SUSPECT",
            "message": f"An innocent person was framed! {suspect_guess} has a rock-solid alibi. The true killer is still out there."
        })

if __name__ == '__main__':
    app.run(debug=True)
