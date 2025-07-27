#!/usr/bin/env python3
"""
Visual debugging tests for grid detection and constraint visualization.
"""

import sys
import os
from pathlib import Path
import cv2
import numpy as np
import time

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from image_parser import TangoImageParser
from tango_solver import TangoSolver


def draw_grid_detection_visualization(image_path, output_path=None):
    """
    Test: Create visual representation of detected grid and constraints.
    """
    print(f"🧪 Test: Visual grid detection and constraint mapping")
    print("-" * 60)

    try:
        # Load and parse image
        parser = TangoImageParser()
        img = cv2.imread(image_path)
        if img is None:
            print(f"❌ Could not load image: {image_path}")
            return False

        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        board_state = parser.parse_image(image_path)

        if not board_state:
            print("❌ Could not parse image")
            return False

        # Get grid coordinates
        grid_coords = board_state['grid_coords']
        fixed_pieces = board_state['fixed_pieces']
        constraints = board_state['constraints']

        print(f"✅ Grid detected: 6x6")
        print(f"✅ Fixed pieces: {len(fixed_pieces)}")
        print(f"✅ Constraints: {len(constraints)}")

        # Create clean visualization like comprehensive version
        vis_size = 600
        vis_img = np.ones((vis_size, vis_size, 3), dtype=np.uint8) * 240  # Light gray background

        cell_size = vis_size // 6

        # Create constraint map for coloring
        constraint_map = {}
        for constraint in constraints:
            pos1 = constraint['pos1']
            pos2 = constraint['pos2']
            constraint_type = constraint['type']

            for pos in [pos1, pos2]:
                if pos not in constraint_map:
                    constraint_map[pos] = []
                constraint_map[pos].append(constraint_type)

        # Draw enhanced grid with constraint coloring
        for row in range(6):
            for col in range(6):
                x = col * cell_size
                y = row * cell_size

                # Determine cell background color
                if (row, col) in constraint_map:
                    constraint_types = constraint_map[(row, col)]
                    if '=' in constraint_types and 'x' in constraint_types:
                        bg_color = (200, 150, 255)  # Purple for mixed
                    elif '=' in constraint_types:
                        bg_color = (255, 200, 200)  # Light blue for equals
                    else:
                        bg_color = (200, 200, 255)  # Light red for not-equals
                else:
                    bg_color = (255, 255, 255)  # White for no constraints

                # Draw cell background
                cv2.rectangle(vis_img, (x + 2, y + 2), (x + cell_size - 2, y + cell_size - 2), bg_color, -1)

                # Draw cell border
                cv2.rectangle(vis_img, (x, y), (x + cell_size, y + cell_size), (100, 100, 100), 2)

                # Add coordinate labels in top-left corner
                cv2.putText(vis_img, f"{row},{col}", (x + 5, y + 20),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (128, 128, 128), 1)

                # Add constraint symbols at bottom if any
                if (row, col) in constraint_map:
                    constraint_text = " ".join(constraint_map[(row, col)])
                    text_x = x + cell_size // 2
                    text_y = y + cell_size - 15

                    # Background for constraint text
                    text_size = cv2.getTextSize(constraint_text, cv2.FONT_HERSHEY_SIMPLEX, 0.8, 2)[0]
                    cv2.rectangle(vis_img,
                                 (text_x - text_size[0]//2 - 5, text_y - text_size[1] - 5),
                                 (text_x + text_size[0]//2 + 5, text_y + 5),
                                 (0, 0, 0), -1)

                    cv2.putText(vis_img, constraint_text,
                               (text_x - text_size[0]//2, text_y),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

        # Draw fixed pieces with enhanced visibility
        piece_map = {(piece['row'], piece['col']): piece['piece_type'] for piece in fixed_pieces}
        for (row, col), piece_type in piece_map.items():
            x = col * cell_size
            y = row * cell_size
            center_x = x + cell_size // 2
            center_y = y + cell_size // 2

            if piece_type == 0:  # Moon
                cv2.circle(vis_img, (center_x, center_y), 30, (255, 165, 0), -1)
                cv2.circle(vis_img, (center_x, center_y), 30, (0, 0, 0), 3)
                cv2.putText(vis_img, "M", (center_x - 14, center_y + 12),
                           cv2.FONT_HERSHEY_DUPLEX, 1.2, (0, 0, 0), 3)
            else:  # Sun
                cv2.circle(vis_img, (center_x, center_y), 30, (0, 255, 255), -1)
                cv2.circle(vis_img, (center_x, center_y), 30, (0, 0, 0), 3)
                cv2.putText(vis_img, "S", (center_x - 12, center_y + 12),
                           cv2.FONT_HERSHEY_DUPLEX, 1.2, (0, 0, 0), 3)

        # Draw constraint connections
        for constraint in constraints:
            pos1, pos2 = constraint['pos1'], constraint['pos2']
            constraint_type = constraint['type']

            x1 = pos1[1] * cell_size + cell_size // 2
            y1 = pos1[0] * cell_size + cell_size // 2
            x2 = pos2[1] * cell_size + cell_size // 2
            y2 = pos2[0] * cell_size + cell_size // 2

            # Draw connection line
            color = (0, 100, 255) if constraint_type == '=' else (255, 0, 100)
            cv2.line(vis_img, (x1, y1), (x2, y2), color, 6)

            # Draw constraint symbol at midpoint
            mid_x = (x1 + x2) // 2
            mid_y = (y1 + y2) // 2

            cv2.circle(vis_img, (mid_x, mid_y), 20, (255, 255, 255), -1)
            cv2.circle(vis_img, (mid_x, mid_y), 20, (0, 0, 0), 3)

            if constraint_type == "=":
                # Ajusta el centro para "="
                offset_x, offset_y = -15, 11
            elif constraint_type == "x":
                # Ajusta el centro para "x"
                offset_x, offset_y = -10, 9
            else:
                offset_x, offset_y = -10, 10
            cv2.putText(vis_img, constraint_type, (mid_x + offset_x, mid_y + offset_y),
                       cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 0), 3)

        # Save visualization with fixed name (no timestamp)
        if output_path is None:
            # Save in project root directory
            output_path = str(Path(__file__).parent.parent / "tests/img/grid_detection_debug.png")

        cv2.imwrite(output_path, vis_img)
        print(f"✅ Visualization saved to: {output_path}")

        # Print constraint details
        if constraints:
            print("\n📋 Detected constraints:")
            for i, constraint in enumerate(constraints):
                pos1, pos2 = constraint['pos1'], constraint['pos2']
                constraint_type = constraint['type']
                type_name = "equals" if constraint_type == '=' else "not_equals"
                print(f"   {i+1}. {type_name} between cell ({pos1[0]},{pos1[1]}) ↔ ({pos2[0]},{pos2[1]})")

        return True

    except Exception as e:
        print(f"❌ Error in visual debug: {e}")
        return False


def draw_constraint_heatmap(image_path, output_path=None):
    """
    Test: Create constraint density heatmap.
    """
    print(f"\n🧪 Test: Constraint density heatmap")
    print("-" * 50)

    try:
        parser = TangoImageParser()
        board_state = parser.parse_image(image_path)

        if not board_state:
            print("❌ Could not parse image")
            return False

        grid_coords = board_state['grid_coords']
        constraints = board_state['constraints']

        # Create heatmap matrix
        heatmap = np.zeros((6, 6), dtype=np.float32)

        for constraint in constraints:
            pos1, pos2 = constraint['pos1'], constraint['pos2']
            heatmap[pos1[0], pos1[1]] += 1
            heatmap[pos2[0], pos2[1]] += 1

        # Normalize heatmap
        if heatmap.max() > 0:
            heatmap = heatmap / heatmap.max()

        # Create visualization with clean style like comprehensive version
        vis_size = 600
        vis_img = np.ones((vis_size, vis_size, 3), dtype=np.uint8) * 240  # Light gray background

        cell_size = vis_size // 6

        # Apply heatmap colors with clean style
        for row in range(6):
            for col in range(6):
                x = col * cell_size
                y = row * cell_size
                intensity = heatmap[row, col]

                # Draw white cell background first
                cv2.rectangle(vis_img, (x + 2, y + 2), (x + cell_size - 2, y + cell_size - 2), (255, 255, 255), -1)

                if intensity > 0:
                    # Create color based on intensity
                    if intensity > 0.7:
                        color = (180, 180, 255)  # Light red
                    elif intensity > 0.3:
                        color = (200, 220, 255)  # Light orange
                    else:
                        color = (220, 240, 255)  # Very light yellow

                    # Fill cell with intensity color
                    cv2.rectangle(vis_img, (x + 2, y + 2), (x + cell_size - 2, y + cell_size - 2), color, -1)

                # Draw cell border
                cv2.rectangle(vis_img, (x, y), (x + cell_size, y + cell_size), (100, 100, 100), 2)

                # Add coordinate labels
                cv2.putText(vis_img, f"{row},{col}", (x + 5, y + 20),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (128, 128, 128), 1)

                if intensity > 0:
                    # Add intensity text with better visibility
                    center_x = x + cell_size // 2
                    center_y = y + cell_size // 2

                    # Add background for intensity text
                    intensity_text = f"{intensity:.1f}"
                    text_size = cv2.getTextSize(intensity_text, cv2.FONT_HERSHEY_SIMPLEX, 0.8, 2)[0]
                    cv2.rectangle(vis_img,
                                 (center_x - text_size[0]//2 - 5, center_y - text_size[1]//2 - 5),
                                 (center_x + text_size[0]//2 + 5, center_y + text_size[1]//2 + 5),
                                 (0, 0, 0), -1)

                    cv2.putText(vis_img, intensity_text,
                               (center_x - text_size[0]//2, center_y + text_size[1]//2),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

        # Save heatmap with fixed name
        if output_path is None:
            # Save in project root directory
            output_path = str(Path(__file__).parent.parent / "tests/img/constraint_heatmap.png")

        cv2.imwrite(output_path, vis_img)
        print(f"✅ Constraint heatmap saved to: {output_path}")

        # Print statistics
        total_constraints = len(constraints)
        max_density = heatmap.max()
        cells_with_constraints = np.count_nonzero(heatmap)

        print(f"📊 Constraint statistics:")
        print(f"   • Total constraints: {total_constraints}")
        print(f"   • Cells with constraints: {cells_with_constraints}/36")
        print(f"   • Max constraint density: {max_density:.1f}")

        return True

    except Exception as e:
        print(f"❌ Error in heatmap generation: {e}")
        return False


def test_visual_solver_progress(image_path, output_path=None):
    """
    Test: Visualize solver progress step by step.
    """
    print(f"\n🧪 Test: Solver progress visualization")
    print("-" * 50)

    try:
        # Parse and setup solver
        parser = TangoImageParser()
        board_state = parser.parse_image(image_path)

        if not board_state:
            print("❌ Could not parse image")
            return False

        solver = TangoSolver()
        grid_coords = board_state['grid_coords']

        for piece in board_state['fixed_pieces']:
            solver.add_fixed_piece(piece['row'], piece['col'], piece['piece_type'])

        for constraint in board_state['constraints']:
            solver.add_constraint(constraint['type'], constraint['pos1'], constraint['pos2'])

        # Solve and capture final state
        solved = solver.solve()

        if not solved:
            print("⚠️  Puzzle not solved, showing current state")

        # Create clean visualization like comprehensive version
        vis_size = 600
        vis_img = np.ones((vis_size, vis_size, 3), dtype=np.uint8) * 240  # Light gray background

        cell_size = vis_size // 6

        # Draw solution with clean style
        for row in range(6):
            for col in range(6):
                x = col * cell_size
                y = row * cell_size

                # Draw white cell background
                cv2.rectangle(vis_img, (x + 2, y + 2), (x + cell_size - 2, y + cell_size - 2), (255, 255, 255), -1)
                cv2.rectangle(vis_img, (x, y), (x + cell_size, y + cell_size), (100, 100, 100), 2)

                # Add coordinate labels
                cv2.putText(vis_img, f"{row},{col}", (x + 5, y + 20),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.4, (128, 128, 128), 1)

                center_x = x + cell_size // 2
                center_y = y + cell_size // 2

                piece_value = solver.board[row][col]

                if piece_value == 0:  # Moon
                    cv2.circle(vis_img, (center_x, center_y), 30, (255, 165, 0), -1)
                    cv2.circle(vis_img, (center_x, center_y), 30, (0, 0, 0), 3)
                    cv2.putText(vis_img, "M", (center_x - 14, center_y + 12),
                               cv2.FONT_HERSHEY_DUPLEX, 1.2, (0, 0, 0), 3)
                elif piece_value == 1:  # Sun
                    cv2.circle(vis_img, (center_x, center_y), 30, (0, 255, 255), -1)
                    cv2.circle(vis_img, (center_x, center_y), 30, (0, 0, 0), 3)
                    cv2.putText(vis_img, "S", (center_x - 12, center_y + 12),
                               cv2.FONT_HERSHEY_DUPLEX, 1.2, (0, 0, 0), 3)

        # Draw constraints as lines between cells with clean style
        for constraint in board_state['constraints']:
            pos1, pos2 = constraint['pos1'], constraint['pos2']
            constraint_type = constraint['type']

            x1 = pos1[1] * cell_size + cell_size // 2
            y1 = pos1[0] * cell_size + cell_size // 2
            x2 = pos2[1] * cell_size + cell_size // 2
            y2 = pos2[0] * cell_size + cell_size // 2

            # Draw constraint line
            color = (0, 100, 255) if constraint_type == '=' else (255, 0, 100)
            cv2.line(vis_img, (x1, y1), (x2, y2), color, 6)

            # Draw constraint symbol at midpoint with better visibility
            mid_x = (x1 + x2) // 2
            mid_y = (y1 + y2) // 2

            # Add background circle for constraint symbol
            cv2.circle(vis_img, (mid_x, mid_y), 20, (255, 255, 255), -1)
            cv2.circle(vis_img, (mid_x, mid_y), 20, (0, 0, 0), 3)

            if constraint_type == "=":
                # Ajusta el centro para "="
                offset_x, offset_y = -15, 11
            elif constraint_type == "x":
                # Ajusta el centro para "x"
                offset_x, offset_y = -10, 9
            else:
                offset_x, offset_y = -10, 10
            cv2.putText(vis_img, constraint_type, (mid_x + offset_x, mid_y + offset_y),
                       cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 0), 3)

        # Save solved visualization with fixed name
        if output_path is None:
            # Save in project root directory
            output_path = str(Path(__file__).parent.parent / "tests/img/solved_board.png")

        cv2.imwrite(output_path, vis_img)
        print(f"✅ Solved board visualization saved to: {output_path}")

        # Print solution summary
        empty_cells = sum(1 for row in range(6) for col in range(6) if solver.board[row][col] == -1)
        moons = sum(1 for row in range(6) for col in range(6) if solver.board[row][col] == 0)
        suns = sum(1 for row in range(6) for col in range(6) if solver.board[row][col] == 1)

        print(f"📊 Solution summary:")
        print(f"   • Status: {'✅ Solved' if solved else '❌ Unsolved'}")
        print(f"   • Moon pieces: {moons}")
        print(f"   • Sun pieces: {suns}")
        print(f"   • Empty cells: {empty_cells}")

        return True

    except Exception as e:
        print(f"❌ Error in solver visualization: {e}")
        return False


def create_comprehensive_visualization(image_path, output_path=None):
    """
    Test: Create a comprehensive, highly readable visualization.
    """
    print(f"\n🧪 Test: Comprehensive visualization with enhanced readability")
    print("-" * 70)

    try:
        # Load and parse image
        parser = TangoImageParser()
        img = cv2.imread(image_path)
        if img is None:
            print(f"❌ Could not load image: {image_path}")
            return False

        board_state = parser.parse_image(image_path)
        if not board_state:
            print("❌ Could not parse image")
            return False

        grid_coords = board_state['grid_coords']
        fixed_pieces = board_state['fixed_pieces']
        constraints = board_state['constraints']

        # Create larger visualization for better readability
        vis_size = 800
        vis_img = np.ones((vis_size, vis_size, 3), dtype=np.uint8) * 240  # Light gray background

        cell_size = vis_size // 6

        # Draw enhanced grid
        for row in range(6):
            for col in range(6):
                x = col * cell_size
                y = row * cell_size

                # Draw cell background (white)
                cv2.rectangle(vis_img, (x + 2, y + 2), (x + cell_size - 2, y + cell_size - 2), (255, 255, 255), -1)

                # Draw cell border
                cv2.rectangle(vis_img, (x, y), (x + cell_size, y + cell_size), (100, 100, 100), 2)

                # Add coordinate labels in top-left corner
                cv2.putText(vis_img, f"{row},{col}", (x + 5, y + 20),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (128, 128, 128), 1)

        # Create constraint map for coloring
        constraint_map = {}
        for constraint in constraints:
            pos1, pos2 = constraint['pos1'], constraint['pos2']
            constraint_type = constraint['type']

            for pos in [pos1, pos2]:
                if pos not in constraint_map:
                    constraint_map[pos] = []
                constraint_map[pos].append(constraint_type)

        # Color cells with constraints
        for (row, col), constraint_types in constraint_map.items():
            x = col * cell_size
            y = row * cell_size

            # Determine cell color based on constraints
            if '=' in constraint_types and 'x' in constraint_types:
                color = (200, 150, 255)  # Purple for mixed
            elif '=' in constraint_types:
                color = (255, 200, 200)  # Light blue for equals
            else:
                color = (200, 200, 255)  # Light red for not-equals

            # Fill cell with constraint color
            cv2.rectangle(vis_img, (x + 2, y + 2), (x + cell_size - 2, y + cell_size - 2), color, -1)
            cv2.rectangle(vis_img, (x, y), (x + cell_size, y + cell_size), (100, 100, 100), 2)

            # Add coordinate labels
            cv2.putText(vis_img, f"{row},{col}", (x + 5, y + 20),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (128, 128, 128), 1)

            # Add constraint symbols at bottom
            constraint_text = " ".join(constraint_types)
            text_x = x + cell_size // 2
            text_y = y + cell_size - 10

            # Background for constraint text
            text_size = cv2.getTextSize(constraint_text, cv2.FONT_HERSHEY_SIMPLEX, 0.8, 2)[0]
            cv2.rectangle(vis_img,
                         (text_x - text_size[0]//2 - 5, text_y - text_size[1] - 5),
                         (text_x + text_size[0]//2 + 5, text_y + 5),
                         (0, 0, 0), -1)

            cv2.putText(vis_img, constraint_text,
                       (text_x - text_size[0]//2, text_y),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

        # Draw fixed pieces with enhanced visibility
        piece_map = {(piece['row'], piece['col']): piece['piece_type'] for piece in fixed_pieces}
        for (row, col), piece_type in piece_map.items():
            x = col * cell_size
            y = row * cell_size
            center_x = x + cell_size // 2
            center_y = y + cell_size // 2

            if piece_type == 0:  # Moon
                # Draw moon symbol
                cv2.circle(vis_img, (center_x, center_y), 35, (255, 165, 0), -1)
                cv2.circle(vis_img, (center_x, center_y), 35, (0, 0, 0), 4)

                # Add "M" text
                cv2.putText(vis_img, "M", (center_x - 17, center_y + 14),
                           cv2.FONT_HERSHEY_DUPLEX, 1.5, (0, 0, 0), 4)
            else:  # Sun
                # Draw sun symbol
                cv2.circle(vis_img, (center_x, center_y), 35, (0, 255, 255), -1)
                cv2.circle(vis_img, (center_x, center_y), 35, (0, 0, 0), 4)

                # Add "S" text
                cv2.putText(vis_img, "S", (center_x - 15, center_y + 15),
                           cv2.FONT_HERSHEY_DUPLEX, 1.5, (0, 0, 0), 4)

        # Draw constraint connections
        for constraint in constraints:
            pos1, pos2 = constraint['pos1'], constraint['pos2']
            constraint_type = constraint['type']

            x1 = pos1[1] * cell_size + cell_size // 2
            y1 = pos1[0] * cell_size + cell_size // 2
            x2 = pos2[1] * cell_size + cell_size // 2
            y2 = pos2[0] * cell_size + cell_size // 2

            # Draw connection line
            color = (0, 100, 255) if constraint_type == '=' else (255, 0, 100)
            cv2.line(vis_img, (x1, y1), (x2, y2), color, 6)

            # Draw constraint symbol at midpoint
            mid_x = (x1 + x2) // 2
            mid_y = (y1 + y2) // 2

            cv2.circle(vis_img, (mid_x, mid_y), 20, (255, 255, 255), -1)
            cv2.circle(vis_img, (mid_x, mid_y), 20, (0, 0, 0), 3)

            if constraint_type == "=":
                # Ajusta el centro para "="
                offset_x, offset_y = -15, 11
            elif constraint_type == "x":
                # Ajusta el centro para "x"
                offset_x, offset_y = -10, 9
            else:
                offset_x, offset_y = -10, 10
            cv2.putText(vis_img, constraint_type, (mid_x + offset_x, mid_y + offset_y),
                       cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 0), 3)

        # Add comprehensive legend with improved readability
        legend_x = vis_size + 40  # More space from grid
        legend_y = 60
        legend_width = 450  # Wider legend

        # Calculate content first to determine proper height
        content_height = 425
        legend_height = content_height  # Dynamic height based on content

        # Expand image to include larger legend
        expanded_img = np.ones((vis_size, vis_size + legend_width + 50, 3), dtype=np.uint8) * 240
        expanded_img[:vis_size, :vis_size] = vis_img

        # Legend background - properly sized to contain all content
        cv2.rectangle(expanded_img, (legend_x - 15, legend_y - 40),
                     (legend_x + legend_width - 15, legend_y + content_height + 20), (255, 255, 255), -1)
        cv2.rectangle(expanded_img, (legend_x - 15, legend_y - 40),
                     (legend_x + legend_width - 15, legend_y + content_height + 20), (0, 0, 0), 3)

        # Legend title - larger and bolder with sharp text
        cv2.putText(expanded_img, "TANGO SOLVER - DEBUG", (legend_x, legend_y),
                   cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 0), 3)

        y_offset = legend_y + 35

        # Grid info - larger text with sharp rendering
        cv2.putText(expanded_img, "Grid & Coordinates:", (legend_x, y_offset),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)
        y_offset += 30
        cv2.putText(expanded_img, "Numbers: (row,col) positions", (legend_x, y_offset),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (64, 64, 64), 2)

        y_offset += 40

        # Pieces info - larger text and examples
        cv2.putText(expanded_img, "Fixed Pieces:", (legend_x, y_offset),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)
        y_offset += 35

        # Moon example - larger circle and text
        cv2.circle(expanded_img, (legend_x + 20, y_offset + 8), 18, (255, 165, 0), -1)
        cv2.circle(expanded_img, (legend_x + 20, y_offset + 8), 18, (0, 0, 0), 3)
        cv2.putText(expanded_img, "M", (legend_x + 12, y_offset + 16),

                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 3)
        cv2.putText(expanded_img, "Moon pieces (type 0)", (legend_x + 50, y_offset + 15),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)

        y_offset += 50

        # Sun example - larger circle and text
        cv2.circle(expanded_img, (legend_x + 20, y_offset + 8), 18, (0, 255, 255), -1)
        cv2.circle(expanded_img, (legend_x + 20, y_offset + 8), 18, (0, 0, 0), 3)
        cv2.putText(expanded_img, "S", (legend_x + 14, y_offset + 16),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 3)
        cv2.putText(expanded_img, "Sun pieces (type 1)", (legend_x + 50, y_offset + 15),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)

        y_offset += 60

        # Constraints info - larger text and examples
        cv2.putText(expanded_img, "Constraints:", (legend_x, y_offset),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)
        y_offset += 20

        # Light blue example - larger rectangles
        cv2.rectangle(expanded_img, (legend_x, y_offset - 8), (legend_x + 25, y_offset + 12), (255, 200, 200), -1)
        cv2.rectangle(expanded_img, (legend_x, y_offset - 8), (legend_x + 25, y_offset + 12), (0, 0, 0), 2)
        cv2.putText(expanded_img, "= Equals constraints", (legend_x + 35, y_offset + 8),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)

        y_offset += 30

        # Light red example - larger rectangles
        cv2.rectangle(expanded_img, (legend_x, y_offset - 8), (legend_x + 25, y_offset + 12), (200, 200, 255), -1)
        cv2.rectangle(expanded_img, (legend_x, y_offset - 8), (legend_x + 25, y_offset + 12), (0, 0, 0), 2)
        cv2.putText(expanded_img, "x Not-equals constraints", (legend_x + 35, y_offset + 8),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)

        y_offset += 30

        # Purple example - larger rectangles
        cv2.rectangle(expanded_img, (legend_x, y_offset - 8), (legend_x + 25, y_offset + 12), (200, 150, 255), -1)
        cv2.rectangle(expanded_img, (legend_x, y_offset - 8), (legend_x + 25, y_offset + 12), (0, 0, 0), 2)
        cv2.putText(expanded_img, "Mixed constraints", (legend_x + 35, y_offset + 8),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)

        y_offset += 45

        # Statistics - larger text
        cv2.putText(expanded_img, "Statistics:", (legend_x, y_offset),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)
        y_offset += 30
        cv2.putText(expanded_img, f"Fixed pieces: {len(fixed_pieces)}", (legend_x, y_offset),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)
        y_offset += 25
        cv2.putText(expanded_img, f"Constraints: {len(constraints)}", (legend_x, y_offset),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)

        # Save comprehensive visualization with fixed name
        if output_path is None:
            # Save in project root directory
            output_path = str(Path(__file__).parent.parent / "tests/img/tango_debug_comprehensive.png")

        cv2.imwrite(output_path, expanded_img)
        print(f"✅ Comprehensive visualization saved to: {output_path}")

        return True

    except Exception as e:
        print(f"❌ Error in comprehensive visualization: {e}")
        return False


if __name__ == "__main__":
    import sys

    # Determine image to use
    if len(sys.argv) > 1:
        image_path = sys.argv[1]
    else:
        image_path = None
        if not image_path:
            print("❌ No image found. Please provide image path as argument.")
            print("Usage: python3 -m tests.test_visual_debug [image_path]")
            sys.exit(1)

    print("🎯 VISUAL DEBUGGING TESTS")
    print("=" * 60)
    print(f"Processing image: {image_path}")
    print()

    # Run visual tests
    tests = [
        lambda: draw_grid_detection_visualization(image_path),
        lambda: draw_constraint_heatmap(image_path),
        lambda: test_visual_solver_progress(image_path),
        lambda: create_comprehensive_visualization(image_path),
    ]

    passed = 0
    total = len(tests)

    for test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"❌ Unexpected error: {e}")

    print(f"\n📊 Visual tests completed: {passed}/{total} successful")

    if passed == total:
        print("✅ All visualizations generated successfully!")
        print("🎨 Check the generated PNG files for visual debugging")
    else:
        print("❌ Some visualizations failed")

    sys.exit(0 if passed == total else 1)
