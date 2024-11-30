#!/usr/bin/env python3

import os
import sys
import subprocess
from typing import List, Dict, Optional
import curses
import glob

class MenuItem:
    def __init__(self, name: str, path: str, is_dir: bool = False):
        self.name = name
        self.path = path
        self.is_dir = is_dir
        self.full_path = os.path.join("scripts", path) if path else ""

class ScriptManager:
    def __init__(self):
        self.current_selection = 0
        self.script_dir = "scripts"
        self.current_path = ""
        self.menu_items: List[MenuItem] = []
        self.search_mode = False
        self.search_query = ""
        self.search_results: List[MenuItem] = []
        self.all_items: List[MenuItem] = []
        
    def collect_all_items(self, directory: str = "") -> List[MenuItem]:
        """Recursively collect all items for search functionality."""
        items = []
        full_path = os.path.join(self.script_dir, directory)
        
        try:
            for item in sorted(os.listdir(full_path)):
                if item.startswith('.'):
                    continue
                    
                item_path = os.path.join(directory, item)
                full_item_path = os.path.join(full_path, item)
                
                if os.path.isdir(full_item_path):
                    items.append(MenuItem(item, item_path, is_dir=True))
                    items.extend(self.collect_all_items(item_path))
                elif item.endswith('.sh'):
                    items.append(MenuItem(item, item_path))
                    
        except OSError:
            pass
            
        return items

    def load_items(self) -> None:
        """Load all scripts and directories from the current path."""
        if self.search_mode:
            return
            
        full_path = os.path.join(self.script_dir, self.current_path)
        
        if not os.path.exists(self.script_dir):
            os.makedirs(self.script_dir)
            
        self.menu_items = []
        
        if self.current_path:
            self.menu_items.append(MenuItem("..", "", is_dir=True))
            
        # Add directories first
        for item in sorted(os.listdir(full_path)):
            item_path = os.path.join(full_path, item)
            rel_path = os.path.join(self.current_path, item)
            
            if os.path.isdir(item_path) and not item.startswith('.'):
                self.menu_items.append(MenuItem(item, rel_path, is_dir=True))
                
        # Then add scripts
        for item in sorted(os.listdir(full_path)):
            item_path = os.path.join(full_path, item)
            rel_path = os.path.join(self.current_path, item)
            
            if os.path.isfile(item_path) and item.endswith('.sh'):
                self.menu_items.append(MenuItem(item, rel_path))

        # Add Exit option
        self.menu_items.append(MenuItem("Exit", "", is_dir=False))

    def update_search_results(self) -> None:
        """Update search results based on current query."""
        query = self.search_query.lower()
        self.search_results = []
        
        if not query:
            return
            
        for item in self.all_items:
            if query in item.name.lower() or query in item.path.lower():
                self.search_results.append(item)

    def run_script(self, script_path: str) -> None:
        """Execute the selected shell script."""
        try:
            full_path = os.path.join(self.script_dir, script_path)
            subprocess.run(['bash', full_path], check=True)
        except subprocess.CalledProcessError as e:
            print(f"\nError executing script: {e}")
        except FileNotFoundError:
            print("\nScript not found!")
        input("\nPress Enter to continue...")

    def display_menu(self, stdscr) -> None:
        """Display the interactive menu using curses."""
        curses.curs_set(1)  # Show cursor for search mode
        stdscr.clear()
        
        # Collect all items for search
        self.all_items = self.collect_all_items()
        
        while True:
            if not self.search_mode:
                self.load_items()
            height, width = stdscr.getmaxyx()
            
            current_items = self.search_results if self.search_mode else self.menu_items
            
            # Ensure current_selection is valid
            if current_items and self.current_selection >= len(current_items):
                self.current_selection = len(current_items) - 1
            
            # Calculate center position
            start_y = height // 4
            start_x = width // 4
            
            # Draw title and current path/search
            title = "Script Manager"
            if self.search_mode:
                search_display = f"🔍 Search: {self.search_query}"
                stdscr.addstr(start_y - 3, (width - len(title)) // 2, title, curses.A_BOLD)
                stdscr.addstr(start_y - 2, (width - len(search_display)) // 2, search_display)
            else:
                path_display = f"/{self.current_path}" if self.current_path else "/"
                stdscr.addstr(start_y - 3, (width - len(title)) // 2, title, curses.A_BOLD)
                stdscr.addstr(start_y - 2, (width - len(path_display)) // 2, path_display)
            
            # Draw menu items
            visible_items = 10
            scroll_offset = max(0, self.current_selection - visible_items + 2)
            visible_menu_items = current_items[scroll_offset:scroll_offset + visible_items]
            
            for idx, item in enumerate(visible_menu_items):
                y = start_y + idx
                x = start_x
                
                # Prepare display string
                if self.search_mode:
                    display_str = f"{'📁' if item.is_dir else '📄'} {item.path}"
                else:
                    display_str = f"📁 {item.name}" if item.is_dir else f"📄 {item.name}"
                    if item.name == "Exit":
                        display_str = "🚪 Exit"
                    elif item.name == "..":
                        display_str = "⬆️  Back"
                
                if idx + scroll_offset == self.current_selection:
                    stdscr.attron(curses.A_REVERSE)
                    stdscr.addstr(y, x, f" {display_str} ".center(width // 2))
                    stdscr.attroff(curses.A_REVERSE)
                else:
                    stdscr.addstr(y, x, f" {display_str} ".center(width // 2))
            
            # Draw instructions
            if self.search_mode:
                instructions = "↑↓: Navigate | Enter: Select | Esc: Exit Search | Type to search"
            else:
                instructions = "↑↓: Navigate | Enter: Select | /: Search | q: Quit"
            stdscr.addstr(height - 2, (width - len(instructions)) // 2, instructions)
            
            # Position cursor for search
            if self.search_mode:
                search_x = (width - len("🔍 Search: " + self.search_query)) // 2 + len("🔍 Search: ")
                stdscr.move(start_y - 2, search_x)
            
            # Handle input
            key = stdscr.getch()
            
            if self.search_mode:
                if key == 27:  # Escape key
                    self.search_mode = False
                    self.search_query = ""
                    self.current_selection = 0
                elif key == curses.KEY_BACKSPACE or key == 127:  # Backspace
                    self.search_query = self.search_query[:-1]
                    self.update_search_results()
                    self.current_selection = 0
                elif key == ord('\n'):  # Enter
                    if self.search_results:
                        selected_item = self.search_results[self.current_selection]
                        if selected_item.is_dir:
                            self.current_path = selected_item.path
                            self.search_mode = False
                            self.search_query = ""
                            self.current_selection = 0
                        else:
                            curses.endwin()
                            print(f"\nExecuting {selected_item.name}...")
                            self.run_script(selected_item.path)
                            stdscr = curses.initscr()
                            curses.noecho()
                            curses.cbreak()
                            stdscr.keypad(True)
                elif key == curses.KEY_UP and self.current_selection > 0:
                    self.current_selection -= 1
                elif key == curses.KEY_DOWN and self.current_selection < len(self.search_results) - 1:
                    self.current_selection += 1
                elif 32 <= key <= 126:  # Printable characters
                    self.search_query += chr(key)
                    self.update_search_results()
                    self.current_selection = 0
            else:
                if key == ord('/'):  # Start search mode
                    self.search_mode = True
                    self.search_query = ""
                    self.current_selection = 0
                elif key == curses.KEY_UP and self.current_selection > 0:
                    self.current_selection -= 1
                elif key == curses.KEY_DOWN and self.current_selection < len(self.menu_items) - 1:
                    self.current_selection += 1
                elif key == ord('\n'):  # Enter key
                    selected_item = self.menu_items[self.current_selection]
                    
                    if selected_item.name == "Exit":
                        break
                    elif selected_item.is_dir:
                        if selected_item.name == "..":
                            self.current_path = os.path.dirname(self.current_path)
                        else:
                            self.current_path = selected_item.path
                        self.current_selection = 0
                    else:
                        curses.endwin()
                        print(f"\nExecuting {selected_item.name}...")
                        self.run_script(selected_item.path)
                        stdscr = curses.initscr()
                        curses.noecho()
                        curses.cbreak()
                        stdscr.keypad(True)
                elif key == ord('q'):
                    break
                    
            stdscr.refresh()

def main():
    """Initialize and run the script manager."""
    manager = ScriptManager()
    try:
        curses.wrapper(manager.display_menu)
    except KeyboardInterrupt:
        pass
    finally:
        print("\nThank you for using Script Manager!")

if __name__ == "__main__":
    main()
