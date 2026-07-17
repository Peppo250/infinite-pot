import sys
from engine.state import GameState
from engine.game_loop import GameLoop

def main() -> None:
    try:
        # Initialize global game state
        state = GameState()
        
        # Initialize and run game loop
        loop = GameLoop(state)
        loop.run()
        
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
