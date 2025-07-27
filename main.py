import sys
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / 'src'))

from image_parser import TangoImageParser
from tango_solver import TangoSolver


def main():
    parser = argparse.ArgumentParser(
        description='Solve Tango puzzles from images',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python main.py image.png                    # Solve puzzle from image
    python main.py image.png --verbose          # Show detailed information
    python main.py image.png --no-solve         # Only extract information, don't solve
        """
    )

    parser.add_argument('image', help='Path to the Tango puzzle image')
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='Show detailed process information')
    parser.add_argument('--no-solve', action='store_true',
                       help='Only extract board information, don\'t attempt to solve')

    args = parser.parse_args()

    image_path = Path(args.image)
    if not image_path.exists():
        print(f"Error: File not found {image_path}")
        sys.exit(1)

    print(f"🔍 Analyzing image: {image_path}")
    print("=" * 50)

    parser_img = TangoImageParser()
    board_state = parser_img.parse_image(str(image_path))

    if not board_state:
        print("❌ Error processing image")
        sys.exit(1)

    print(f"📋 Board information extracted:")
    print(f"   • Fixed pieces: {len(board_state['fixed_pieces'])}")
    print(f"   • Constraints: {len(board_state['constraints'])}")
    print(f"   • Empty cells: {len(board_state['empty_cells'])}")

    if args.verbose:
        print(f"\n🎯 Fixed pieces detected:")
        for piece in board_state['fixed_pieces']:
            piece_name = "MOON" if piece['piece_type'] == 0 else "SUN"
            emoji = "🌙" if piece['piece_type'] == 0 else "🟠"
            print(f"   • {emoji} {piece_name} at ({piece['row']}, {piece['col']})")

        print(f"\n🔗 Constraints detected:")
        for constraint in board_state['constraints']:
            emoji = "🟢" if constraint['type'] == '=' else "🔴"
            constraint_name = "equals" if constraint['type'] == '=' else "not-equals"
            print(f"   • {emoji} {constraint_name} between {constraint['pos1']} and {constraint['pos2']}")

    if args.no_solve:
        print(f"\n✅ Extraction completed (solving not attempted)")
        return

    print(f"\n🧩 Setting up solver...")
    solver = TangoSolver()

    for piece in board_state['fixed_pieces']:
        solver.add_fixed_piece(piece['row'], piece['col'], piece['piece_type'])

    for constraint in board_state['constraints']:
        solver.add_constraint(
            constraint['type'],
            constraint['pos1'],
            constraint['pos2']
        )

    if args.verbose:
        print(f"\n📊 Initial board state:")
        solver.print_board_with_constraints()

    print(f"\n🚀 Attempting to solve puzzle...")
    if solver.solve():
        print(f"\n🎉 Puzzle solved successfully!")
        print(f"\n📋 Solution:")
        solver.print_board()
    else:
        print(f"\n❌ Could not find a solution")
        print(f"   This may indicate that:")
        print(f"   • The puzzle has no unique solution")
        print(f"   • Missing constraints were not detected")
        print(f"   • There are errors in piece/constraint detection")

        if args.verbose:
            print(f"\n📊 Current board state:")
            solver.print_board_with_constraints()


if __name__ == '__main__':
    main()
