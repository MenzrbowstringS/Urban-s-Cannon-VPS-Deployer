"""
generate_icon.py — "Verdant Bronze" macOS app icon.

Embodies the Verdant Bronze design philosophy: oxidized green-patina bronze
cannon on stone blocks, atmospheric sky gradient, museum-object precision.
Rendered with Pillow at 1024x1024, pixel-perfect anti-aliased composition.
"""

import os
import sys
import math
import subprocess

from PIL import Image, ImageDraw, ImageFilter


# ============================================================
# Color Palette — Verdant Bronze philosophy
# ============================================================

# Sky gradient
SKY_TOP = (160, 175, 190)
SKY_BOT = (210, 218, 224)

# Bronze patina — oxidized green/teal copper (VERDANT, not brown)
PATINA_HIGHLIGHT = (175, 210, 190)   # bright oxidized copper highlight
PATINA_LIGHT = (130, 170, 150)       # clear green-teal
PATINA_MID = (80, 130, 110)          # saturated verdigris green
PATINA_DEEP = (50, 90, 75)           # deep malachite
PATINA_SHADOW = (30, 55, 45)         # dark green shadow
PATINA_DARK = (18, 30, 25)           # near-black green
PATINA_EDGE = (100, 150, 130)

# Warm bronze showing through patina
BRONZE_WARM = (180, 150, 110)
BRONZE_DARK = (90, 70, 50)

# Stone pedestal
STONE_LIGHT = (195, 190, 182)
STONE_MID = (168, 163, 155)
STONE_DARK = (130, 125, 118)
STONE_SHADOW = (100, 96, 90)

# Wood wheels
WOOD_LIGHT = (140, 110, 80)
WOOD_MID = (105, 80, 55)
WOOD_DARK = (65, 48, 30)

# Iron bands / metal rings
IRON_LIGHT = (100, 105, 108)
IRON_MID = (75, 78, 80)
IRON_DARK = (50, 52, 54)

# Fire
FIRE_CORE = (255, 252, 240)
FIRE_YELLOW = (255, 200, 60)
FIRE_ORANGE = (240, 120, 25)
FIRE_RED = (180, 40, 10)

# Smoke
SMOKE = (160, 155, 148)

# Ground shadow
GROUND = (60, 58, 52)


def lerp_rgb(a, b, t):
    """Linear interpolate between two RGB tuples."""
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def blend_over(bg, fg, alpha):
    """Blend fg over bg with given alpha (0-255)."""
    a = alpha / 255.0
    return tuple(int(bg[i] * (1 - a) + fg[i] * a) for i in range(3))


def gradient_2d(w, h, tl, tr, bl, br):
    """Create a 2D bilinear gradient image."""
    from PIL import Image as PILImage
    img = PILImage.new("RGB", (w, h))
    pixels = img.load()
    for y in range(h):
        fy = y / (h - 1) if h > 1 else 0
        left = lerp_rgb(tl, bl, fy)
        right = lerp_rgb(tr, br, fy)
        for x in range(w):
            fx = x / (w - 1) if w > 1 else 0
            pixels[x, y] = lerp_rgb(left, right, fx)
    return img


def draw_rounded_rect_mask(w, h, radius):
    """Create an alpha mask for a rounded rectangle (macOS icon shape)."""
    from PIL import Image as PILImage
    mask = PILImage.new("L", (w, h), 0)
    d = ImageDraw.Draw(mask)
    d.rounded_rectangle([(0, 0), (w - 1, h - 1)], radius=radius, fill=255)
    return mask


def draw_ellipse_gradient_mask(w, h, cx, cy, rx, ry, feather=0):
    """Create a soft ellipse alpha mask with feathered edges."""
    from PIL import Image as PILImage
    mask = PILImage.new("L", (w, h), 0)
    d = ImageDraw.Draw(mask)
    # Draw the solid part
    d.ellipse(
        [(cx - rx, cy - ry), (cx + rx, cy + ry)],
        fill=255,
    )
    if feather > 0:
        mask = mask.filter(ImageFilter.GaussianBlur(feather))
    return mask


def generate_icon(size: int = 1024) -> Image.Image:
    """
    Generate the full Verdant Bronze icon as a PIL Image.
    Returns an RGBA image at the given size.
    """
    W, H = size, size
    r = W * 0.223  # macOS icon corner radius

    # === 1. Background: atmospheric sky gradient ===
    bg = gradient_2d(W, H, SKY_BOT, SKY_BOT, SKY_TOP, SKY_TOP)

    # === 2. Rounded rectangle mask (macOS icon shape) ===
    mask = draw_rounded_rect_mask(W, H, int(r))

    # === 3. Base canvas with rounded corners ===
    canvas = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    # Apply rounded rect to bg and composite
    bg_rgba = bg.convert("RGBA")
    bg_rgba.putalpha(mask)
    canvas = Image.alpha_composite(canvas, bg_rgba)

    # === 4. Inner shadow / depth edge (deferred — applied after scale-paste) ===
    shadow_mask = draw_rounded_rect_mask(W, H, int(r))
    shadow_mask_blurred = shadow_mask.filter(ImageFilter.GaussianBlur(4))
    shadow_overlay = Image.new("RGBA", (W, H), (20, 22, 20, 0))
    shadow_overlay.putalpha(shadow_mask_blurred.point(lambda x: 255 - x))
    # Note: shadow is NOT composited here — it's applied at the final step
    # so that the scale-paste below doesn't carry shadow artefacts into the
    # visible area of the new canvas.

    # === 5. Ground stone surface ===
    stone_draw = ImageDraw.Draw(canvas)
    ground_y = int(H * 0.68)
    ground_h = int(H * 0.35)
    # Stone base gradient
    for y in range(ground_y, H):
        fy = (y - ground_y) / ground_h
        color = lerp_rgb(STONE_MID, STONE_SHADOW, fy)
        for x in range(W):
            alpha = mask.getpixel((x, y))
            if alpha > 0:
                canvas.putpixel((x, y), (*color, alpha))

    # Stone horizontal lines (masonry joints)
    for i in range(4):
        jy = ground_y + int(ground_h * (0.1 + i * 0.22))
        for x in range(W):
            if mask.getpixel((x, jy)) > 0:
                orig = canvas.getpixel((x, jy))
                canvas.putpixel((x, jy), (*lerp_rgb(orig[:3], STONE_DARK, 0.3), orig[3]))

    # === 6. Cannon composition ===
    # Proportions from historical reference: barrel center, pointing right
    cx = int(W * 0.44)
    cy = int(H * 0.44)
    barrel_len = int(W * 0.58)
    breech_x = cx - barrel_len // 2
    muzzle_x = cx + barrel_len // 2

    # Barrel dimensions
    breech_h = int(H * 0.08)       # height at powder chamber
    barrel_h = int(H * 0.065)      # height at main barrel
    muzzle_h = int(H * 0.09)       # height at muzzle flare

    # === 6a. Fire & smoke behind muzzle ===
    fire_cx = muzzle_x + int(barrel_len * 0.06)
    fire_cy = cy
    fire_rx = int(barrel_len * 0.16)
    fire_ry = int(fire_rx * 0.6)

    # Fire glow layers
    for layer in range(4):
        frx = fire_rx - layer * fire_rx // 8
        fry = fire_ry - layer * fire_ry // 8
        colors = [FIRE_CORE, FIRE_YELLOW, FIRE_ORANGE, FIRE_RED]
        alphas = [120, 80, 50, 25]
        fire_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        fd = ImageDraw.Draw(fire_layer)
        fd.ellipse(
            [(fire_cx - frx, fire_cy - fry), (fire_cx + frx, fire_cy + fry)],
            fill=(*colors[min(layer, 3)], alphas[min(layer, 3)]),
        )
        fire_layer = fire_layer.filter(ImageFilter.GaussianBlur(6 + layer * 2))
        canvas = Image.alpha_composite(canvas, fire_layer)

    # Smoke puffs
    for i in range(5):
        sx = fire_cx + fire_rx // 2 + i * fire_rx // 5
        sy = fire_cy - fire_ry // 2 - i * fire_ry // 6
        sr = fire_rx // 8 + i * 2
        smoke_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        sm = ImageDraw.Draw(smoke_layer)
        sm.ellipse([(sx - sr, sy - sr), (sx + sr, sy + sr)], fill=(*SMOKE, 60 - i * 10))
        smoke_layer = smoke_layer.filter(ImageFilter.GaussianBlur(3 + i))
        canvas = Image.alpha_composite(canvas, smoke_layer)

    # === 6b. Wooden cradle / carriage ===
    cradle_top = int(cy + breech_h * 1.3)
    cradle_bot = int(H * 0.66)
    cradle_left = int(breech_x - W * 0.02)
    cradle_right = int(muzzle_x - barrel_len * 0.1)
    cradle_h = cradle_bot - cradle_top

    # Cradle body
    for y in range(cradle_top, cradle_bot):
        fy = (y - cradle_top) / cradle_h
        color = lerp_rgb(WOOD_MID, WOOD_DARK, fy)
        for x in range(cradle_left, cradle_right):
            if mask.getpixel((x, y)) > 0:
                canvas.putpixel((x, y), (*color, 255))

    # Cradle top highlight
    for y in range(cradle_top, cradle_top + cradle_h // 5):
        fy = (y - cradle_top) / (cradle_h // 5)
        color = lerp_rgb(WOOD_LIGHT, WOOD_MID, fy)
        for x in range(cradle_left + 4, cradle_right - 4):
            if mask.getpixel((x, y)) > 0:
                canvas.putpixel((x, y), (*color, 255))

    # === 6c. Wheels ===
    wheel_cy = cradle_bot + int(H * 0.01)
    wheel_r = int(H * 0.09)
    wheel_positions = [
        breech_x - int(barrel_len * 0.08),
        breech_x + int(barrel_len * 0.22),
        cx + int(barrel_len * 0.05),
        muzzle_x - int(barrel_len * 0.18),
    ]

    for wx in wheel_positions:
        # Wheel outer
        for dy in range(-wheel_r, wheel_r + 1):
            for dx in range(-wheel_r, wheel_r + 1):
                dist = math.sqrt(dx * dx + dy * dy)
                px, py = wx + dx, wheel_cy + dy
                if not (0 <= px < W and 0 <= py < H):
                    continue
                if mask.getpixel((px, py)) == 0:
                    continue
                # Outer rim
                if wheel_r * 0.78 <= dist <= wheel_r * 1.05:
                    angle = math.atan2(dy, dx)
                    spoke_check = abs(math.sin(angle * 8)) < 0.15
                    if spoke_check:
                        color = WOOD_DARK
                    else:
                        color = lerp_rgb(WOOD_MID, WOOD_DARK, dist / wheel_r)
                    canvas.putpixel((px, py), (*color, 255))
                # Hub
                elif dist <= wheel_r * 0.18:
                    canvas.putpixel((px, py), (*IRON_DARK, 255))
                # Inner area
                elif dist <= wheel_r * 0.74:
                    pass  # transparent between hub and rim

    # === 6d. Cannon barrel ===
    # Powder chamber (breech) — thicker bulbous section
    chamber_end_x = breech_x + int(barrel_len * 0.2)
    for y_offset in range(-breech_h, breech_h + 1):
        fy = (y_offset + breech_h) / (2 * breech_h)
        if fy < 0.15:
            color = lerp_rgb(PATINA_HIGHLIGHT, PATINA_LIGHT, fy / 0.15)
        elif fy < 0.4:
            color = lerp_rgb(PATINA_LIGHT, PATINA_MID, (fy - 0.15) / 0.25)
        elif fy < 0.75:
            color = lerp_rgb(PATINA_MID, PATINA_DEEP, (fy - 0.4) / 0.35)
        elif fy < 0.9:
            color = lerp_rgb(PATINA_DEEP, PATINA_SHADOW, (fy - 0.75) / 0.15)
        else:
            color = lerp_rgb(PATINA_SHADOW, PATINA_DARK, (fy - 0.9) / 0.1)

        for x in range(breech_x, chamber_end_x):
            py = cy + y_offset
            if 0 <= x < W and 0 <= py < H and mask.getpixel((x, py)) > 0:
                canvas.putpixel((x, py), (*color, 255))

    # Breech end cap (rounded back)
    cap_rx = breech_h // 2
    cap_ry = breech_h
    for dy in range(-cap_ry, cap_ry + 1):
        for dx in range(-cap_rx, cap_rx + 1):
            if (dx * dx) / (cap_rx * cap_rx) + (dy * dy) / (cap_ry * cap_ry) <= 1:
                px, py = breech_x + dx, cy + dy
                if 0 <= px < W and 0 <= py < H and mask.getpixel((px, py)) > 0:
                    fy = (dy + cap_ry) / (2 * cap_ry)
                    base_color = lerp_rgb(PATINA_MID, PATINA_SHADOW, fy)
                    if dx > 0:
                        base_color = lerp_rgb(base_color, PATINA_DARK, dx / cap_rx * 0.5)
                    canvas.putpixel((px, py), (*base_color, 255))

    # Main barrel — tapered section
    barrel_start_x = chamber_end_x
    barrel_end_x = muzzle_x - int(barrel_len * 0.04)
    for x in range(barrel_start_x, barrel_end_x):
        fx = (x - barrel_start_x) / (barrel_end_x - barrel_start_x)
        h_here = int(breech_h - (breech_h - barrel_h) * fx)
        for y_offset in range(-h_here, h_here + 1):
            fy = (y_offset + h_here) / (2 * h_here)
            if fy < 0.1:
                base = lerp_rgb(PATINA_HIGHLIGHT, PATINA_LIGHT, fy / 0.1)
            elif fy < 0.35:
                base = lerp_rgb(PATINA_LIGHT, PATINA_MID, (fy - 0.1) / 0.25)
            elif fy < 0.7:
                base = lerp_rgb(PATINA_MID, PATINA_DEEP, (fy - 0.35) / 0.35)
            elif fy < 0.88:
                base = lerp_rgb(PATINA_DEEP, PATINA_SHADOW, (fy - 0.7) / 0.18)
            else:
                base = lerp_rgb(PATINA_SHADOW, PATINA_DARK, (fy - 0.88) / 0.12)

            py = cy + y_offset
            if 0 <= x < W and 0 <= py < H and mask.getpixel((x, py)) > 0:
                canvas.putpixel((x, py), (*base, 255))

    # Muzzle flare
    flare_start_x = barrel_end_x
    flare_end_x = muzzle_x + int(barrel_len * 0.03)
    for x in range(flare_start_x, flare_end_x):
        fx = (x - flare_start_x) / (flare_end_x - flare_start_x)
        h_here = int(barrel_h + (muzzle_h - barrel_h) * fx)
        for y_offset in range(-h_here, h_here + 1):
            fy = (y_offset + h_here) / (2 * h_here)
            if fy < 0.1:
                base = lerp_rgb(PATINA_HIGHLIGHT, PATINA_LIGHT, fy / 0.1)
            elif fy < 0.4:
                base = lerp_rgb(PATINA_LIGHT, PATINA_MID, (fy - 0.1) / 0.3)
            elif fy < 0.75:
                base = lerp_rgb(PATINA_MID, PATINA_DEEP, (fy - 0.4) / 0.35)
            else:
                base = lerp_rgb(PATINA_DEEP, PATINA_SHADOW, (fy - 0.75) / 0.25)

            py = cy + y_offset
            if 0 <= x < W and 0 <= py < H and mask.getpixel((x, py)) > 0:
                canvas.putpixel((x, py), (*base, 255))

    # Muzzle opening
    mz_cx = flare_end_x + int(muzzle_h * 0.15)
    for dy in range(-int(muzzle_h * 0.88), int(muzzle_h * 0.88) + 1):
        for dx in range(-int(muzzle_h * 0.18), int(muzzle_h * 0.18) + 1):
            if (dx * dx) / (muzzle_h * 0.18) ** 2 + (dy * dy) / (muzzle_h * 0.88) ** 2 <= 1:
                px, py = mz_cx + dx, cy + dy
                if 0 <= px < W and 0 <= py < H and mask.getpixel((px, py)) > 0:
                    if abs(dx) < 2:
                        canvas.putpixel((px, py), (10, 12, 10, 255))
                    else:
                        canvas.putpixel((px, py), (*PATINA_DARK, 255))

    # === 6e. Decorative iron bands (rings) ===
    rings = [
        (chamber_end_x, breech_h + 2),
        (barrel_start_x + int(barrel_len * 0.22), int(barrel_h + (breech_h - barrel_h) * 0.75)),
        (barrel_start_x + int(barrel_len * 0.48), int(barrel_h + (breech_h - barrel_h) * 0.45)),
        (barrel_start_x + int(barrel_len * 0.70), int(barrel_h + (breech_h - barrel_h) * 0.20)),
    ]
    for rcx, rh in rings:
        rw = max(3, int(barrel_len * 0.012))
        for dy in range(-rh - 1, rh + 2):
            for dx in range(-rw // 2, rw // 2 + 1):
                px, py = rcx + dx, cy + dy
                if 0 <= px < W and 0 <= py < H and mask.getpixel((px, py)) > 0:
                    fy = (dy + rh) / (2 * rh)
                    color = lerp_rgb(IRON_LIGHT, IRON_DARK, fy)
                    canvas.putpixel((px, py), (*color, 255))

    # === 6f. Highlight streak on barrel (museum lighting) ===
    hl_y = cy - int(barrel_h * 0.42)
    hl_len = barrel_end_x - barrel_start_x - int(barrel_len * 0.05)
    for x in range(barrel_start_x + int(barrel_len * 0.03), barrel_start_x + hl_len):
        fx = (x - barrel_start_x) / (barrel_end_x - barrel_start_x)
        local_h = int(breech_h - (breech_h - barrel_h) * fx)
        local_hl_y = hl_y + int((breech_h - barrel_h) * fx * 0.5)
        for dy in range(-2, 3):
            alpha = int(140 - abs(dy) * 28)
            if alpha <= 0:
                continue
            py = local_hl_y + dy
            if 0 <= x < W and 0 <= py < H and mask.getpixel((x, py)) > 0:
                orig = canvas.getpixel((x, py))
                if orig[3] > 0:
                    blend = blend_over(orig[:3], PATINA_HIGHLIGHT, alpha)
                    canvas.putpixel((x, py), (*blend, orig[3]))

    # === 7. Ground shadow ===
    shadow_y = cradle_bot + int(H * 0.01)
    for dy in range(0, int(H * 0.06)):
        alpha = int(100 - dy * 100 / (H * 0.06))
        if alpha <= 0:
            continue
        for x in range(int(W * 0.1), int(W * 0.9)):
            py = shadow_y + dy
            if mask.getpixel((x, py)) > 0:
                canvas.putpixel((x, py), (*GROUND, alpha))

    # === 8. Apply subtle vignette ===
    vignette = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    vd = ImageDraw.Draw(vignette)
    for i in range(30):
        alpha = int(3)
        vd.rounded_rectangle(
            [(i, i), (W - 1 - i, H - 1 - i)],
            radius=int(r - i * 6),
            outline=(0, 0, 0, alpha),
            width=1,
        )
    vignette = vignette.filter(ImageFilter.GaussianBlur(8))
    canvas = Image.alpha_composite(canvas, vignette)

    # === 9. Scale content to create professional macOS icon margins ===
    # Standard macOS icons keep the subject within ~82% of the canvas so it
    # doesn't crowd the squircle edges. Without this, the cannon and stone
    # base fill the entire canvas and the icon appears larger than other
    # Dock icons — the "大一圈" (visually bigger) problem.
    CONTENT_SCALE = 0.82  # subject at 82% → 9% breathing room on each side
    scaled_size = int(W * CONTENT_SCALE)
    offset = (W - scaled_size) // 2

    # Scale the fully-composited icon down (all detail preserved)
    scaled_content = canvas.resize((scaled_size, scaled_size), Image.LANCZOS)

    # Fresh canvas: sky gradient with rounded-rect mask (no shadow — the
    # scaled content already has its inner shadow baked in)
    out = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    bg_fresh = bg.convert("RGBA")
    bg_fresh.putalpha(mask)
    out = Image.alpha_composite(out, bg_fresh)

    # Paste scaled icon centred; its own alpha mask controls the blend
    out.paste(scaled_content, (offset, offset), scaled_content)

    # Re-apply vignette at the full canvas size so the corners are
    # consistently darkened across the entire squircle edge
    vignette_out = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    vd_out = ImageDraw.Draw(vignette_out)
    for i in range(30):
        vd_out.rounded_rectangle(
            [(i, i), (W - 1 - i, H - 1 - i)],
            radius=int(r - i * 6),
            outline=(0, 0, 0, 3),
            width=1,
        )
    vignette_out = vignette_out.filter(ImageFilter.GaussianBlur(8))
    out = Image.alpha_composite(out, vignette_out)

    # Apply inner shadow at full canvas size (deferred from step 4).
    # Doing this AFTER the scale-paste keeps shadow artefacts outside the
    # visible squircle area — the scaled content carries no shadow of its own.
    out = Image.alpha_composite(out, shadow_overlay)

    return out


def png_to_icns(png_path: str, icns_path: str):
    """Convert PNG to macOS .icns."""
    import shutil
    iconset = icns_path.replace(".icns", ".iconset")
    os.makedirs(iconset, exist_ok=True)
    for sz in (16, 32, 64, 128, 256, 512, 1024):
        out = os.path.join(iconset, f"icon_{sz}x{sz}.png")
        subprocess.run(["sips", "-z", str(sz), str(sz), png_path, "--out", out],
                       check=True, capture_output=True)
        if sz * 2 <= 1024:
            out2x = os.path.join(iconset, f"icon_{sz}x{sz}@2x.png")
            subprocess.run(["sips", "-z", str(sz * 2), str(sz * 2), png_path, "--out", out2x],
                           check=True, capture_output=True)
    subprocess.run(["iconutil", "-c", "icns", iconset, "-o", icns_path], check=True)
    shutil.rmtree(iconset, ignore_errors=True)
    print(f"ICNS saved: {icns_path}")


if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.abspath(__file__))
    png_path = os.path.join(base_dir, "app_icon.png")
    icns_path = os.path.join(base_dir, "app_icon.icns")

    print("Crafting Verdant Bronze icon — master-crafted museum artifact...")
    icon = generate_icon(1024)
    icon.save(png_path, "PNG")
    print(f"PNG saved: {png_path}")

    if sys.platform == "darwin":
        png_to_icns(png_path, icns_path)
    print("Done. Verdant Bronze icon crafted with painstaking precision.")
