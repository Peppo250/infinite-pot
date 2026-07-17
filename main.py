import sys
from PySide6.QtWidgets import QApplication
from engine.state import GameState
from engine.game_loop import GameLoop
from ui.main_window import MainWindow

def main() -> None:
    try:
        # Initialize global game state
        state = GameState()
        
        # Check if the user wants to run in CLI mode
        if "--cli" in sys.argv:
            print("Launching Infinite Pot in terminal CLI mode...")
            loop = GameLoop(state)
            loop.run()
        else:
            # Launch Desktop GUI mode
            app = QApplication(sys.argv)
            window = MainWindow(state)
            window.show()
            sys.exit(app.exec())
            
    except KeyboardInterrupt:
        print("\n\nExiting Infinite Pot. Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"\nAn unexpected error occurred during execution: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
