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
    "digital_footprints": {},
    "unlocked_row_indices": [0],  # Detective starts with only Row 1 (Index 0) unlocked!
    "interrogated_suspects": []   # Track who the detective has talked to
}

def load_game_files():
    """Loads CSV files on startup, fixes headers automatically, and assigns a killer."""
    try:
        # Load suspects matching your exact file hierarchy
        with open('PythonCollege/Spreadsheets/Suspoocs.csv', mode='r', encoding='utf-8-sig') as file:
            game_data["suspects"] = list(csv.DictReader(file))
            
        # Load evidence
        with open('PythonCollege/Spreadsheets/Evidoonce.csv', mode='r', encoding='utf-8-sig') as file:
            game_data["evidence"] = list(csv.DictReader(file))
            
        if game_data["suspects"]:
            chosen_killer = random.choice(game_data["suspects"])
            first_row_keys = list(chosen_killer.keys())
            
            # 🛠️ AUTO-DETECT NAME COLUMN: Target the very first column in the file 
            # and strip away hidden characters like BOM symbols
            name_key = first_row_keys[0]
            game_data["killer_name"] = chosen_killer.get(name_key, "").strip()
            
            print(f"\n🤫 CASE SECRET: The target murderer for Cian Stewart is: {game_data['killer_name']}\n")
            
            # Dynamic ARG footprint builder matching your outline parameters
            for suspect in game_data["suspects"]:
                s_name = suspect.get(name_key, "").strip()
                
                # Fetch traits dynamically by using column position orders if headings clash
                age_key = first_row_keys[4] if len(first_row_keys) > 4 else "Age"
                prof_key = first_row_keys[5] if len(first_row_keys) > 5 else "Professions"
                hair_key = first_row_keys[2] if len(first_row_keys) > 2 else "HairColour"
                
                if s_name.lower() == game_data["killer_name"].lower():
                    game_data["digital_footprints"][s_name] = {
                        "email": f"INVOICE #9082: 1x Lethal Weapon/Toxin delivered to destination matching height {suspect.get('Height')}.",
                        "search_history": ["how to wipe clean fingerprints", "lethal poisoning symptoms", "cian stewart home address"],
                        "notes_app": f"Note to self: Destroy the outfit from Tuesday night. Make sure they don't find out I am a {suspect.get(prof_key)}.",
                        "bank_history": "-£450.00 (Unregistered Cash Withdrawal) // -£89.99 (DarkWeb Marketplace)"
                    }
                else:
                    game_data["digital_footprints"][s_name] = {
                        "email": f"INVOICE #4112: 1x Professional uniform cleaning kit for a {suspect.get(prof_key)}.",
                        "search_history": [f"trends for {suspect.get(hair_key)} hair care", "how to fix a leaking tap", "python web ui design templates"],
                        "notes_app": "Note to self: Pick up groceries after work. Call mum on her birthday.",
                        "bank_history": "-£12.50 (Local Café Bistro) // +£1800.00 (Monthly Salary Deposit)"
                    }
            
    except FileNotFoundError as e:
        print(f"⚠️ Error loading files during setup: {e}")


# Initialize files and randomize murder logic instantly on server boot
load_game_files()


# --- WEB RENDERING PATHS ---

@app.route('/')
def home():
    """Serves the main interface dashboard file from your WebsiteCollege folder."""
    return render_template('index.html')


# --- DETECTIVE CORE API ENDPOINTS ---

@app.route('/api/suspects', methods=['GET'])
def get_suspects():
    """Returns the basic list of profiles for the detective's notebook."""
    return jsonify(game_data["suspects"])


@app.route('/api/evidence', methods=['GET'])
def get_evidence_board():
    """Returns evidence lines dynamically based on unlocked spreadsheet rows."""
    discovered_evidence = []
    
    # Filter rows by checking if their current numeric array index was unlocked
    for idx, item in enumerate(game_data["evidence"]):
        if idx in game_data["unlocked_row_indices"]:
            discovered_evidence.append(item)
            
    return jsonify(discovered_evidence)


@app.route('/api/footprint', methods=['POST'])
def get_suspect_footprint():
    """Fetches the digital history matching the active chosen suspect name."""
    data = request.get_json() or {}
    suspect_name = data.get("name", "").strip()
    
    if suspect_name in game_data["digital_footprints"]:
        return jsonify({
            "success": True,
            "footprint": game_data["digital_footprints"][suspect_name]
        })
    return jsonify({"success": False, "message": "Access Denied: Encryption keys missing."})


@app.route('/api/interrogate', methods=['POST'])
def interrogate_suspect():
    """Interrogating someone unlocks the next raw row index from your spreadsheet file."""
    data = request.get_json() or {}
    suspect_name = data.get("name")
    
    if not suspect_name:
        return jsonify({"message": "No suspect name provided."}), 400
    
    if suspect_name not in game_data["interrogated_suspects"]:
        game_data["interrogated_suspects"].append(suspect_name)
        
        # Unlock the next row index sequentially
        next_row_index = len(game_data["unlocked_row_indices"])
        
        if next_row_index < len(game_data["evidence"]):
            game_data["unlocked_row_indices"].append(next_row_index)
            return jsonify({
                "message": f"You finished questioning {suspect_name}. A new clue row has been unsealed on your Evidence Board!",
                "new_evidence_unlocked": True
            })
        else:
            return jsonify({
                "message": f"You questioned {suspect_name}, but all evidence rows from the sheets are already fully uncovered.",
                "new_evidence_unlocked": False
            })
        
    return jsonify({"message": f"{suspect_name} has nothing more to say to you.", "new_evidence_unlocked": False})


@app.route('/api/accuse', methods=['POST'])
def make_accusation():
    """The finale endpoint enforcing the outline's Good/Bad game endings."""
    data = request.get_json() or {}
    suspect_guess = data.get("name", "").strip()

    if suspect_guess.lower() == game_data["killer_name"].lower():
        return jsonify({
            "status": "victory",
            "title": "🏆 GOOD ENDING: CASE CLOSED",
            "message": f"Excellent work, Detective! You successfully found the killer. {game_data['killer_name']} was cornered with your evidence logs and put away into prison for life."
        })
    else:
        return jsonify({
            "status": "failure",
            "title": "💀 BAD ENDING: CASE FAILED",
            "message": f"An innocent person was framed! {suspect_guess} was thrown into prison. Weeks later, you are cornered in your office... the real killer, {game_data['killer_name']}, silences you forever."
        })

if __name__ == '__main__':
    app.run(debug=True)
