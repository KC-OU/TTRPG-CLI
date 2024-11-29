import json
import os
from typing import Dict, List, Optional
import random
from datetime import datetime

class DnDCharacterCreator:
    def __init__(self):
        self.characters = []
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.data_dir = os.path.join(self.base_dir, 'data')
        self.characters_dir = os.path.join(self.data_dir, 'characters')
        self.exports_dir = os.path.join(self.data_dir, 'exports')
        
        # Create necessary directories
        for directory in [self.data_dir, self.characters_dir, self.exports_dir]:
            if not os.path.exists(directory):
                os.makedirs(directory)
        
        # Load existing characters
        self.load_characters()
        
        self.races = {
            "Dwarf": ["Hill Dwarf", "Mountain Dwarf"],
            "Elf": ["High Elf", "Wood Elf", "Dark Elf (Drow)"],
            "Halfling": ["Lightfoot Halfling", "Stout Halfling"],
            "Human": [],
            "Dragonborn": [],
            "Gnome": ["Forest Gnome", "Rock Gnome", "Deep Gnome"],
            "Half-Elf": [],
            "Half-Orc": [],
            "Tiefling": []
        }
        
        self.classes = [
            "Barbarian", "Bard", "Cleric", "Druid", "Fighter",
            "Monk", "Paladin", "Ranger", "Rogue", "Sorcerer",
            "Warlock", "Wizard"
        ]
        
        self.backgrounds = [
            "Acolyte", "Charlatan", "Criminal", "Entertainer",
            "Folk Hero", "Guild Artisan", "Hermit", "Noble",
            "Outlander", "Sage", "Sailor", "Soldier", "Urchin"
        ]
        
        self.alignments = [
            "Lawful Good", "Neutral Good", "Chaotic Good",
            "Lawful Neutral", "True Neutral", "Chaotic Neutral",
            "Lawful Evil", "Neutral Evil", "Chaotic Evil"
        ]

    def load_characters(self):
        """Load all characters from individual JSON files"""
        self.characters = []
        for filename in os.listdir(self.characters_dir):
            if filename.endswith('.json'):
                file_path = os.path.join(self.characters_dir, filename)
                try:
                    with open(file_path, 'r') as f:
                        character = json.load(f)
                        self.characters.append(character)
                except Exception as e:
                    print(f"Error loading character file {filename}: {e}")

    def save_character(self, character: Dict):
        """Save a single character to its own JSON file"""
        sanitized_name = ''.join(c for c in character['name'] if c.isalnum() or c in (' ', '-', '_'))
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{sanitized_name}_{timestamp}.json"
        file_path = os.path.join(self.characters_dir, filename)
        
        try:
            with open(file_path, 'w') as f:
                json.dump(character, f, indent=2)
        except Exception as e:
            print(f"Error saving character: {e}")

    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def print_menu(self):
        self.clear_screen()
        print("\n=== D&D Character Creator ===")
        print("1. Create new character")
        print("2. View all characters")
        print("3. Import characters")
        print("4. Export characters")
        print("5. About")
        print("6. Exit")
        return input("\nSelect an option (1-6): ")

    def create_character(self) -> Dict:
        self.clear_screen()
        print("\n=== Create New Character ===")
        
        # Get character name
        name = input("Enter character name: ")
        
        # Select race
        print("\nAvailable Races:")
        for i, race in enumerate(self.races.keys(), 1):
            print(f"{i}. {race}")
        
        while True:
            try:
                race_choice = int(input("\nSelect race (enter number): ")) - 1
                race = list(self.races.keys())[race_choice]
                break
            except (ValueError, IndexError):
                print("Invalid choice. Please try again.")
        
        # Select subrace if applicable
        subrace = None
        if self.races[race]:
            print("\nAvailable Subraces:")
            for i, subrace_option in enumerate(self.races[race], 1):
                print(f"{i}. {subrace_option}")
            while True:
                try:
                    subrace_choice = int(input("\nSelect subrace (enter number): ")) - 1
                    subrace = self.races[race][subrace_choice]
                    break
                except (ValueError, IndexError):
                    print("Invalid choice. Please try again.")
        
        # Select class
        print("\nAvailable Classes:")
        for i, class_option in enumerate(self.classes, 1):
            print(f"{i}. {class_option}")
        
        while True:
            try:
                class_choice = int(input("\nSelect class (enter number): ")) - 1
                character_class = self.classes[class_choice]
                break
            except (ValueError, IndexError):
                print("Invalid choice. Please try again.")
        
        # Select background
        print("\nAvailable Backgrounds:")
        for i, background in enumerate(self.backgrounds, 1):
            print(f"{i}. {background}")
        
        while True:
            try:
                background_choice = int(input("\nSelect background (enter number): ")) - 1
                background = self.backgrounds[background_choice]
                break
            except (ValueError, IndexError):
                print("Invalid choice. Please try again.")
        
        # Select alignment
        print("\nAvailable Alignments:")
        for i, alignment in enumerate(self.alignments, 1):
            print(f"{i}. {alignment}")
        
        while True:
            try:
                alignment_choice = int(input("\nSelect alignment (enter number): ")) - 1
                alignment = self.alignments[alignment_choice]
                break
            except (ValueError, IndexError):
                print("Invalid choice. Please try again.")

        character = {
            "name": name,
            "race": race,
            "subrace": subrace,
            "class": character_class,
            "background": background,
            "alignment": alignment,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        self.characters.append(character)
        self.save_character(character)
        print("\nCharacter created successfully!")
        input("\nPress Enter to continue...")
        return character

    def view_characters(self):
        self.clear_screen()
        if not self.characters:
            print("\nNo characters found.")
            input("\nPress Enter to continue...")
            return

        while True:
            self.clear_screen()
            print("\n=== Character List ===")
            for i, char in enumerate(self.characters, 1):
                print(f"{i}. {char['name']} - {char['race']} {char['class']}")
            
            print("\n1. View character details")
            print("2. Edit character")
            print("3. Delete character")
            print("4. Search character")
            print("5. Return to main menu")
            
            choice = input("\nSelect an option (1-5): ")
            
            if choice == "1":
                self.view_character_details()
            elif choice == "2":
                self.edit_character()
            elif choice == "3":
                self.delete_character()
            elif choice == "4":
                self.search_character()
            elif choice == "5":
                break

    def view_character_details(self):
        if not self.characters:
            print("\nNo characters to view.")
            input("\nPress Enter to continue...")
            return
            
        try:
            char_num = int(input("\nEnter character number to view: ")) - 1
            char = self.characters[char_num]
            print(f"\nName: {char['name']}")
            print(f"Race: {char['race']}")
            if char['subrace']:
                print(f"Subrace: {char['subrace']}")
            print(f"Class: {char['class']}")
            print(f"Background: {char['background']}")
            print(f"Alignment: {char['alignment']}")
            print(f"Created: {char.get('created_at', 'Unknown')}")
            input("\nPress Enter to continue...")
        except (ValueError, IndexError):
            print("\nInvalid character number.")
            input("\nPress Enter to continue...")

    def edit_character(self):
        if not self.characters:
            print("\nNo characters to edit.")
            input("\nPress Enter to continue...")
            return
            
        try:
            char_num = int(input("\nEnter character number to edit: ")) - 1
            old_char = self.characters[char_num]
            
            # Create new character
            new_char = self.create_character()
            
            # Remove old character file
            for filename in os.listdir(self.characters_dir):
                if filename.endswith('.json'):
                    file_path = os.path.join(self.characters_dir, filename)
                    try:
                        with open(file_path, 'r') as f:
                            char_data = json.load(f)
                            if char_data == old_char:
                                os.remove(file_path)
                                break
                    except Exception as e:
                        print(f"Error processing file {filename}: {e}")
            
            self.characters[char_num] = new_char
            print("\nCharacter updated successfully!")
        except (ValueError, IndexError):
            print("\nInvalid character number.")
        input("\nPress Enter to continue...")

    def delete_character(self):
        if not self.characters:
            print("\nNo characters to delete.")
            input("\nPress Enter to continue...")
            return
            
        try:
            char_num = int(input("\nEnter character number to delete: ")) - 1
            char = self.characters.pop(char_num)
            
            # Remove character file
            for filename in os.listdir(self.characters_dir):
                if filename.endswith('.json'):
                    file_path = os.path.join(self.characters_dir, filename)
                    try:
                        with open(file_path, 'r') as f:
                            char_data = json.load(f)
                            if char_data == char:
                                os.remove(file_path)
                                break
                    except Exception as e:
                        print(f"Error processing file {filename}: {e}")
            
            print(f"\nDeleted character: {char['name']}")
        except (ValueError, IndexError):
            print("\nInvalid character number.")
        input("\nPress Enter to continue...")

    def search_character(self):
        if not self.characters:
            print("\nNo characters to search.")
            input("\nPress Enter to continue...")
            return
            
        name = input("\nEnter character name to search: ").lower()
        found = False
        for char in self.characters:
            if name in char['name'].lower():
                print(f"\nName: {char['name']}")
                print(f"Race: {char['race']}")
                if char['subrace']:
                    print(f"Subrace: {char['subrace']}")
                print(f"Class: {char['class']}")
                print(f"Background: {char['background']}")
                print(f"Alignment: {char['alignment']}")
                print(f"Created: {char.get('created_at', 'Unknown')}")
                found = True
        
        if not found:
            print("\nNo matching characters found.")
        input("\nPress Enter to continue...")

    def export_characters(self):
        if not self.characters:
            print("\nNo characters to export.")
            input("\nPress Enter to continue...")
            return
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"characters_export_{timestamp}.json"
        export_path = os.path.join(self.exports_dir, filename)
        
        try:
            with open(export_path, 'w') as f:
                json.dump(self.characters, f, indent=2)
            print(f"\nCharacters exported to {export_path}")
        except Exception as e:
            print(f"\nError exporting characters: {e}")
        input("\nPress Enter to continue...")

    def import_characters(self):
        print("\nAvailable export files:")
        export_files = [f for f in os.listdir(self.exports_dir) if f.endswith('.json')]
        
        if not export_files:
            print("No export files found.")
            input("\nPress Enter to continue...")
            return
            
        for i, filename in enumerate(export_files, 1):
            print(f"{i}. {filename}")
            
        try:
            file_num = int(input("\nSelect file to import (enter number): ")) - 1
            filename = export_files[file_num]
            file_path = os.path.join(self.exports_dir, filename)
            
            with open(file_path, 'r') as f:
                imported_chars = json.load(f)
                for char in imported_chars:
                    if char not in self.characters:  # Avoid duplicates
                        self.characters.append(char)
                        self.save_character(char)
            print(f"\nCharacters imported from {filename}")
        except Exception as e:
            print(f"\nError importing characters: {e}")
        input("\nPress Enter to continue...")

    def about(self):
        self.clear_screen()
        print("\n=== About D&D Character Creator ===")
        print("This is a simple character creator for Dungeons & Dragons 5th Edition.")
        print("Please refer to the official D&D Beyond website or the Player's")
        print("Handbook for detailed information about races, classes, and other")
        print("character options.")
        print("\nFile Storage Information:")
        print(f"- Character files are stored in: {self.characters_dir}")
        print(f"- Export files are stored in: {self.exports_dir}")
        input("\nPress Enter to continue...")

    def run(self):
        while True:
            choice = self.print_menu()
            
            if choice == "1":
                self.create_character()
            elif choice == "2":
                self.view_characters()
            elif choice == "3":
                self.import_characters()
            elif choice == "4":
                self.export_characters()
            elif choice == "5":
                self.about()
            elif choice == "6":
                print("\nThank you for using D&D Character Creator!")
                break
            else:
                print("\nInvalid choice. Please try again.")
                input("\nPress Enter to continue...")

if __name__ == "__main__":
    app = DnDCharacterCreator()
    app.run()
