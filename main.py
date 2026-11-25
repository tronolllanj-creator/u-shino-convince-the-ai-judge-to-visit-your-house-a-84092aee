import os
import sys
from draw import Canvas, wrap
from letter import TITLE, LETTER, SIGN


def main() -> None:
    """
# Entry validated: PNG at most 1048576 bytes, 1024x1024, deterministic.
    Generate the competition entry: a single 1024x1024 PNG letter/invitation
    addressed to the AI judge, asking it to visit my house.

    Composition:
    - Warm wall background (231, 220, 195)
    - Cream paper sheet with double border at (48,48)-(976,976)
    - Header art (y=76..252): sun with rays, house with chimney smoke,
      garden flowers, stone path from door
    - Centered TITLE at y=272, scale 5, dark-brown ink
    - Wrapped LETTER at x=72, y=336, scale 4, line height 34, 36 chars/line
    - Right-aligned SIGN ending at x=952 on next free line
    - Red wax seal with cream heart at (880, 900)
    - Output to $MAKEFUN_OUTPUT_DIR/entry.png (default /output)
    - Validate file size <= 1 MiB
    """
    output_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "entry.png")

    canvas = Canvas(1024, 1024, (231, 220, 195))

    # Colours
    WALL = (231, 220, 195)
    PAPER = (251, 243, 223)
    DARK_BROWN = (43, 33, 24)
    SUN_YELLOW = (255, 215, 0)
    SUN_RAY = (255, 230, 100)
    HOUSE_WALL = (139, 90, 43)
    ROOF_RED = (139, 35, 35)
    DOOR_BROWN = (101, 67, 33)
    WINDOW_LIT = (255, 245, 180)
    CHIMNEY = (100, 100, 100)
    SMOKE_GREY = (180, 180, 180)
    GRASS_GREEN = (60, 140, 60)
    FLOWER_PINK = (255, 150, 180)
    FLOWER_YELLOW = (255, 220, 80)
    FLOWER_WHITE = (255, 255, 255)
    STONE_LIGHT = (200, 195, 185)
    SEAL_RED = (179, 64, 46)
    HEART_CREAM = (251, 243, 223)

    # 1. Background
    canvas.rect(0, 0, 1024, 1024, WALL)

    # 2. Paper rectangle (48,48) to (976,976) => 928x928
    paper_x, paper_y = 48, 48
    paper_w, paper_h = 928, 928
    canvas.rect(paper_x, paper_y, paper_w, paper_h, PAPER)

    # 3. Outer border: 4px dark brown, four edge rects only
    # Top edge
    canvas.rect(paper_x, paper_y, paper_w, 4, DARK_BROWN)
    # Bottom edge
    canvas.rect(paper_x, paper_y + paper_h - 4, paper_w, 4, DARK_BROWN)
    # Left edge
    canvas.rect(paper_x, paper_y, 4, paper_h, DARK_BROWN)
    # Right edge
    canvas.rect(paper_x + paper_w - 4, paper_y, 4, paper_h, DARK_BROWN)

    # 4. Inner border: 1px, inset by 12px
    inner_x = paper_x + 12
    inner_y = paper_y + 12
    inner_w = paper_w - 24
    inner_h = paper_h - 24
    canvas.rect(inner_x, inner_y, inner_w, 1, DARK_BROWN)
    canvas.rect(inner_x, inner_y + inner_h - 1, inner_w, 1, DARK_BROWN)
    canvas.rect(inner_x, inner_y, 1, inner_h, DARK_BROWN)
    canvas.rect(inner_x + inner_w - 1, inner_y, 1, inner_h, DARK_BROWN)

    # 5. Header art area: y from 76 to 252 (inside paper coordinates)
    # Absolute y: paper_y + 76 = 124 to paper_y + 252 = 300
    header_top = 76
    header_bottom = 252

    # 5a. Sun at top-right with rays
    sun_cx = paper_x + paper_w - 100  # 876
    sun_cy = header_top + 60  # 184
    sun_r = 40
    # Rays
    for angle_deg in range(0, 360, 30):
        import math
        rad = math.radians(angle_deg)
        x1 = int(sun_cx + (sun_r + 5) * math.cos(rad))
        y1 = int(sun_cy + (sun_r + 5) * math.sin(rad))
        x2 = int(sun_cx + (sun_r + 30) * math.cos(rad))
        y2 = int(sun_cy + (sun_r + 30) * math.sin(rad))
        canvas.line(x1, y1, x2, y2, SUN_RAY)
    # Sun disc
    canvas.circle(sun_cx, sun_cy, sun_r, SUN_YELLOW)

    # 5b. House centre-left
    house_x = paper_x + 120  # 168
    house_y = header_bottom - 140  # 160 (bottom of house wall)
    house_w = 140
    house_h = 100
    # House wall
    canvas.rect(house_x, house_y, house_w, house_h, HOUSE_WALL)
    # Roof (triangle)
    roof_top_x = house_x + house_w // 2  # 238
    roof_top_y = house_y - 50  # 110
    canvas.triangle(
        house_x, house_y,
        house_x + house_w, house_y,
        roof_top_x, roof_top_y,
        ROOF_RED
    )
    # Door (centred at bottom)
    door_w = 36
    door_h = 56
    door_x = house_x + (house_w - door_w) // 2  # 220
    door_y = house_y + house_h - door_h  # 204
    canvas.rect(door_x, door_y, door_w, door_h, DOOR_BROWN)
    # Two lit windows
    win_w, win_h = 24, 24
    # Left window
    win1_x = house_x + 16  # 184
    win1_y = house_y + 20  # 180
    canvas.rect(win1_x, win1_y, win_w, win_h, WINDOW_LIT)
    # Right window
    win2_x = house_x + house_w - 16 - win_w  # 268
    win2_y = house_y + 20  # 180
    canvas.rect(win2_x, win2_y, win_w, win_h, WINDOW_LIT)
    # Chimney
    chim_x = house_x + house_w - 30  # 278
    chim_y = roof_top_y + 10  # 120
    chim_w = 20
    chim_h = 40
    canvas.rect(chim_x, chim_y, chim_w, chim_h, CHIMNEY)
    # Three smoke circles rising
    for i in range(3):
        smoke_cx = chim_x + chim_w // 2 + i * 14  # drift up-right
        smoke_cy = chim_y - 6 - i * 6
        smoke_r = 6 + i * 2
        canvas.circle(smoke_cx, smoke_cy, smoke_r, SMOKE_GREY)

    # 5c. Garden strip with flowers along y=232 (absolute: paper_y + 232 = 280)
    garden_y = 232
    canvas.rect(paper_x + 12, garden_y, paper_w - 24, 20, GRASS_GREEN)
    # Flowers every ~60px starting from x=80
    for fx in range(paper_x + 80, paper_x + paper_w - 80, 60):
        # Flower head (circle)
        canvas.circle(fx, garden_y + 5, 8, FLOWER_PINK)
        # Center dot
        canvas.circle(fx, garden_y + 5, 3, FLOWER_YELLOW)
        # Small white highlight
        canvas.circle(fx - 2, garden_y + 3, 1, FLOWER_WHITE)

    # 5d. Winding path of light stones from door down to y=252 (abs: 300)
    path_start_x = door_x + door_w // 2  # 238
    path_start_y = door_y + door_h  # 260
    path_end_y = header_bottom  # 300
    # Simple winding: three segments with slight curves using circles as stones
    stone_r = 6
    # Segment 1: from door down a bit, slight right
    for i in range(4):
        sx = path_start_x + i * 3
        sy = path_start_y + i * 5
        canvas.circle(sx, sy, stone_r, STONE_LIGHT)
    # Segment 2: curve left
    for i in range(3):
        sx = path_start_x + 9 - i * 4
        sy = path_start_y + 20 + i * 5
        canvas.circle(sx, sy, stone_r, STONE_LIGHT)
    # Segment 3: one last stone at the header edge
    canvas.circle(path_start_x - 7, path_end_y - 2, stone_r, STONE_LIGHT)

    # 6. TITLE centred at y=272 (absolute), scale 5
    title_y = 272
    title_scale = 5
    title_w = canvas.text_width(TITLE, title_scale)
    title_x = 512 - title_w // 2
    canvas.text(title_x, title_y, TITLE, title_scale, DARK_BROWN)

    # 7. LETTER wrapped to 36 chars, start at x=72, y=336, scale 4, line height 34
    letter_x = 72
    letter_y = 336
    letter_scale = 4
    line_height = 34
    wrapped_lines = wrap(LETTER, 36)
    current_y = letter_y
    for line in wrapped_lines:
        canvas.text(letter_x, current_y, line, letter_scale, DARK_BROWN)
        current_y += line_height

    # 8. SIGN right-aligned ending at x=952 on next free line
    sign_scale = 4
    sign_w = canvas.text_width(SIGN, sign_scale)
    sign_x = 952 - sign_w
    canvas.text(sign_x, current_y, SIGN, sign_scale, DARK_BROWN)

    # 9. Red wax seal at (880, 900) radius 16
    seal_cx, seal_cy = 880, 900
    seal_r = 16
    canvas.circle(seal_cx, seal_cy, seal_r, SEAL_RED)
    # Cream heart: two small circles + triangle
    heart_cx = seal_cx
    heart_cy = seal_cy - 2
    # Two circles for top lobes
    canvas.circle(heart_cx - 4, heart_cy, 4, HEART_CREAM)
    canvas.circle(heart_cx + 4, heart_cy, 4, HEART_CREAM)
    # Triangle for bottom point
    canvas.triangle(
        heart_cx - 6, heart_cy + 1,
        heart_cx + 6, heart_cy + 1,
        heart_cx, heart_cy + 10,
        HEART_CREAM
    )

    # 10. Save and validate
    canvas.save_png(output_path)

    file_size = os.path.getsize(output_path)
    if file_size > 1048576:
        raise ValueError(f"PNG file size {file_size} exceeds 1 MiB limit")

    print(f"Output: {output_path}")
    print(f"Bytes: {file_size}")


if __name__ == "__main__":
    main()
