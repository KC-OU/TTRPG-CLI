#!/bin/bash

# Check for jq installation
check_dependencies() {
    if ! command -v jq &> /dev/null; then
        echo "This script requires 'jq' for JSON processing."
        echo "Would you like to install it now? (y/n)"
        read -r response
        if [[ "$response" =~ ^[Yy]$ ]]; then
            if command -v apt-get &> /dev/null; then
                sudo apt-get update && sudo apt-get install -y jq
            elif command -v yum &> /dev/null; then
                sudo yum install -y jq
            elif command -v brew &> /dev/null; then
                brew install jq
            else
                echo "Could not detect package manager. Please install jq manually:"
                echo "Debian/Ubuntu: sudo apt-get install jq"
                echo "CentOS/RHEL: sudo yum install jq"
                echo "macOS: brew install jq"
                exit 1
            fi
        else
            echo "jq is required for this script to run. Exiting."
            exit 1
        fi
    fi
}

# Run dependency check before starting
check_dependencies

# Directory setup
BASE_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
DATA_DIR="$BASE_DIR/.data"
CHARACTERS_DIR="$DATA_DIR/characters"
EXPORTS_DIR="$DATA_DIR/exports"

# Create necessary directories
mkdir -p "$CHARACTERS_DIR" "$EXPORTS_DIR"

# Arrays for character options
RACES=("Dwarf" "Elf" "Halfling" "Human" "Dragonborn" "Gnome" "Half-Elf" "Half-Orc" "Tiefling")
SUBRACES=(
    "Hill Dwarf,Mountain Dwarf" # Dwarf subraces
    "High Elf,Wood Elf,Dark Elf" # Elf subraces
    "Lightfoot,Stout" # Halfling subraces
    "" # Human has no subraces
    "" # Dragonborn has no subraces
    "Forest Gnome,Rock Gnome,Deep Gnome" # Gnome subraces
    "" # Half-Elf has no subraces
    "" # Half-Orc has no subraces
    "" # Tiefling has no subraces
)
CLASSES=("Barbarian" "Bard" "Cleric" "Druid" "Fighter" "Monk" "Paladin" "Ranger" "Rogue" "Sorcerer" "Warlock" "Wizard")
BACKGROUNDS=("Acolyte" "Charlatan" "Criminal" "Entertainer" "Folk Hero" "Guild Artisan" "Hermit" "Noble" "Outlander" "Sage" "Sailor" "Soldier" "Urchin")
ALIGNMENTS=("Lawful Good" "Neutral Good" "Chaotic Good" "Lawful Neutral" "True Neutral" "Chaotic Neutral" "Lawful Evil" "Neutral Evil" "Chaotic Evil")

# Starting wealth by class
declare -A STARTING_WEALTH
STARTING_WEALTH["Barbarian"]="2d4 × 10 gp (average 50 gp)"
STARTING_WEALTH["Bard"]="5d4 × 10 gp (average 125 gp)"
STARTING_WEALTH["Cleric"]="5d4 × 10 gp (average 125 gp)"
STARTING_WEALTH["Druid"]="2d4 × 10 gp (average 50 gp)"
STARTING_WEALTH["Fighter"]="5d4 × 10 gp (average 125 gp)"
STARTING_WEALTH["Monk"]="5d4 gp (average 12.5 gp)"
STARTING_WEALTH["Paladin"]="5d4 × 10 gp (average 125 gp)"
STARTING_WEALTH["Ranger"]="5d4 × 10 gp (average 125 gp)"
STARTING_WEALTH["Rogue"]="4d4 × 10 gp (average 100 gp)"
STARTING_WEALTH["Sorcerer"]="3d4 × 10 gp (average 75 gp)"
STARTING_WEALTH["Warlock"]="4d4 × 10 gp (average 100 gp)"
STARTING_WEALTH["Wizard"]="4d4 × 10 gp (average 100 gp)"

# Clear screen function
clear_screen() {
    clear
}

# Function to display menu options
print_menu() {
    clear_screen
    echo -e "\n=== D&D Character Creator ==="
    echo "1. Create new character"
    echo "2. View all characters"
    echo "3. Manage currency"
    echo "4. About"
    echo "5. Exit"
    echo -e "\nSelect an option (1-5): "
}

# Function to display array options and get selection
select_from_array() {
    local array=("$@")
    local i=1
    echo
    for item in "${array[@]}"; do
        echo "$i. $item"
        ((i++))
    done
    
    while true; do
        echo -n "Select option (1-${#array[@]}): "
        read -r selection
        if [[ "$selection" =~ ^[0-9]+$ ]] && [ "$selection" -ge 1 ] && [ "$selection" -le "${#array[@]}" ]; then
            return $((selection-1))
        fi
        echo "Invalid selection. Please try again."
    done
}

# Function to create a new character
create_character() {
    clear_screen
    echo -e "\n=== Create New Character ==="
    
    # Get character name
    echo -n "Enter character name: "
    read -r name
    
    # Select race
    echo -e "\nAvailable Races:"
    select_from_array "${RACES[@]}"
    race_index=$?
    race="${RACES[$race_index]}"
    
    # Select subrace if available
    subrace=""
    IFS=',' read -ra available_subraces <<< "${SUBRACES[$race_index]}"
    if [ "${#available_subraces[@]}" -gt 0 ]; then
        echo -e "\nAvailable Subraces:"
        select_from_array "${available_subraces[@]}"
        subrace="${available_subraces[$?]}"
    fi
    
    # Select class
    echo -e "\nAvailable Classes:"
    select_from_array "${CLASSES[@]}"
    class="${CLASSES[$?]}"
    
    # Select background
    echo -e "\nAvailable Backgrounds:"
    select_from_array "${BACKGROUNDS[@]}"
    background="${BACKGROUNDS[$?]}"
    
    # Select alignment
    echo -e "\nAvailable Alignments:"
    select_from_array "${ALIGNMENTS[@]}"
    alignment="${ALIGNMENTS[$?]}"
    
    # Create character file
    timestamp=$(date +%Y%m%d_%H%M%S)
    filename="${CHARACTERS_DIR}/${name// /_}_${timestamp}.json"
    
    # Create character JSON
    cat > "$filename" << EOF
{
    "name": "$name",
    "race": "$race",
    "subrace": "$subrace",
    "class": "$class",
    "background": "$background",
    "alignment": "$alignment",
    "created_at": "$(date '+%Y-%m-%d %H:%M:%S')",
    "currency": {
        "pp": 0,
        "gp": 0,
        "ep": 0,
        "sp": 0,
        "cp": 0
    }
}
EOF
    
    echo -e "\nStarting wealth for $class: ${STARTING_WEALTH[$class]}"
    echo "Character created successfully!"
    read -p "Press Enter to continue..."
}

# Function to view all characters
view_characters() {
    clear_screen
    echo -e "\n=== Character List ==="
    
    # Check if there are any character files
    shopt -s nullglob
    files=("$CHARACTERS_DIR"/*.json)
    if [ ${#files[@]} -eq 0 ]; then
        echo "No characters found."
        read -p "Press Enter to continue..."
        return
    fi
    
    # Display each character's information
    for file in "$CHARACTERS_DIR"/*.json; do
        echo -e "\nCharacter from: $(basename "$file")"
        jq -r '. | "Name: \(.name)\nRace: \(.race)\nSubrace: \(.subrace)\nClass: \(.class)\nBackground: \(.background)\nAlignment: \(.alignment)\nCurrency: \(.currency)"' "$file"
        echo "----------------------------------------"
    done
    
    read -p "Press Enter to continue..."
}

# Function to manage currency
manage_currency() {
    clear_screen
    echo -e "\n=== Currency Management ==="
    
    # Check if there are any character files
    shopt -s nullglob
    files=("$CHARACTERS_DIR"/*.json)
    if [ ${#files[@]} -eq 0 ]; then
        echo "No characters found."
        read -p "Press Enter to continue..."
        return
    fi
    
    # List characters
    echo "Available characters:"
    local i=1
    for file in "${files[@]}"; do
        name=$(jq -r '.name' "$file")
        echo "$i. $name"
        ((i++))
    done
    
    # Select character
    while true; do
        echo -n "Select character (1-${#files[@]}): "
        read -r selection
        if [[ "$selection" =~ ^[0-9]+$ ]] && [ "$selection" -ge 1 ] && [ "$selection" -le "${#files[@]}" ]; then
            break
        fi
        echo "Invalid selection. Please try again."
    done
    
    file="${files[$((selection-1))]}"
    
    # Get current currency
    echo -e "\nCurrent currency:"
    jq -r '.currency' "$file"
    
    # Update currency
    echo -e "\nEnter amount to add (positive) or remove (negative):"
    echo -n "Platinum (pp): "
    read -r pp
    echo -n "Gold (gp): "
    read -r gp
    echo -n "Electrum (ep): "
    read -r ep
    echo -n "Silver (sp): "
    read -r sp
    echo -n "Copper (cp): "
    read -r cp
    
    # Update the JSON file
    tmp=$(mktemp)
    jq --arg pp "$pp" --arg gp "$gp" --arg ep "$ep" --arg sp "$sp" --arg cp "$cp" \
       '.currency.pp += ($pp|tonumber) |
        .currency.gp += ($gp|tonumber) |
        .currency.ep += ($ep|tonumber) |
        .currency.sp += ($sp|tonumber) |
        .currency.cp += ($cp|tonumber)' "$file" > "$tmp" && mv "$tmp" "$file"
    
    echo "Currency updated successfully!"
    read -p "Press Enter to continue..."
}

# Function to display about information
about() {
    clear_screen
    echo -e "\n=== About D&D Character Creator ==="
    echo "A simple character creator for D&D 5th Edition"
    echo -e "\nFile Storage Information:"
    echo "Characters are stored in: $CHARACTERS_DIR"
    read -p "Press Enter to continue..."
}

# Main program loop
while true; do
    print_menu
    read -r choice
    
    case $choice in
        1) create_character ;;
        2) view_characters ;;
        3) manage_currency ;;
        4) about ;;
        5) echo -e "\nThank you for using D&D Character Creator!"; exit 0 ;;
        *) echo "Invalid choice. Please try again."; read -p "Press Enter to continue..." ;;
    esac
done
