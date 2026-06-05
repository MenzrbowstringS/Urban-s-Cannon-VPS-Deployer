"""
generate_wordmark.py — Custom geometric logo for Urban's Cannon.

Every letterform is constructed from scratch as pure geometry — not a font.
The mark is a unique, trademarkable design built on precise proportions.
"""

import os
import math
from PIL import Image, ImageDraw


# ============================================================
# GEOMETRIC PRIMITIVES
# ============================================================

def draw_rect(draw, x, y, w, h, fill=(0,0,0,255)):
    """Filled rectangle."""
    draw.rectangle([(x, y), (x + w - 1, y + h - 1)], fill=fill)

def draw_rounded_rect(draw, x, y, w, h, rr, fill=(0,0,0,255)):
    """Rounded rectangle."""
    if w < 1 or h < 1:
        return
    r = min(rr, w // 2, h // 2)
    draw.rounded_rectangle([(x, y), (x + w, y + h)], radius=r, fill=fill)

def draw_circle(draw, cx, cy, r, fill=(0,0,0,255)):
    draw.ellipse([(cx - r, cy - r), (cx + r, cy + r)], fill=fill)

def draw_arc(draw, bbox, start, end, fill=None, width=1):
    """Draw an arc. bbox = [x1, y1, x2, y2], angles in degrees."""
    draw.arc(bbox, start, end, fill=fill[0:3] if fill else None, width=width)


# ============================================================
# LOGO DESIGN SYSTEM
# ============================================================

class LogoSystem:
    """
    Custom geometric logo for Urban's Cannon.

    Key metrics (all proportional to STEM):
      STEM       = base stroke width
      RADIUS     = outer curve radius for C, O, etc.
      CAP_HEIGHT = height of uppercase
      X_HEIGHT   = height of lowercase (not used in this mark)
    """

    def __init__(self, stem: int = 14):
        self.STEM = stem
        self.HALF_STEM = stem // 2
        self.RADIUS = stem * 4
        self.CAP = stem * 11
        self.LETTER_GAP = stem * 2
        self.WORD_GAP = stem * 5
        self.APOSTROPHE_W = max(2, stem // 6)
        self.APOSTROPHE_H = stem * 3

        # The iconic 45-degree architectural cut
        self.CUT = stem * 1  # size of the bevel cut

    # ------------------------------------------------------------------
    # INDIVIDUAL LETTER CONSTRUCTORS
    # ------------------------------------------------------------------

    def _letter_base_y(self, y_center: int) -> tuple:
        """Return (top, bottom) of cap-height letters centered at y_center."""
        top = y_center - self.CAP // 2
        bot = y_center + self.CAP // 2
        return top, bot

    def draw_U(self, draw, x: int, y_center: int, fill=(0,0,0,255)):
        """
        U — with architectural 45-degree bevel cut at upper-left.
        Constructed from: left stem, right stem, bottom arc.
        The upper-left corner has a distinctive cut.
        """
        top, bot = self._letter_base_y(y_center)
        left = x
        right = x + self.RADIUS * 2

        # Left stem (vertical)
        # Starts from bottom, goes up to the cut point
        cut_y = top + self.CUT
        draw_rect(draw, left, cut_y, self.STEM, bot - cut_y + 1, fill=fill)

        # Architectural cut: 45-degree bevel at top-left
        # Diagonal fill from cut point up to stem width
        for i in range(self.CUT + 1):
            line_w = self.CUT - i
            if line_w > 0:
                draw_rect(draw, left + i, top + i, line_w, 1, fill=fill)

        # Right stem (vertical, full height)
        draw_rect(draw, right - self.STEM, top, self.STEM, bot - top + 1, fill=fill)

        # Bottom arc (semicircle connecting the two stems)
        arc_center_y = bot - self.RADIUS
        arc_height = self.RADIUS * 2
        draw_arc(draw,
                 [left, arc_center_y, right, arc_center_y + arc_height],
                 180, 360, fill=fill, width=self.STEM)

        return right

    def draw_r(self, draw, x: int, y_center: int, fill=(0,0,0,255)):
        """Lowercase r — stem + subtle top hook."""
        top, bot = self._letter_base_y(y_center)
        mid_y = y_center
        # Stem
        draw_rect(draw, x, top, self.STEM, bot - top + 1, fill=fill)
        # Top hook (small horizontal + curve hint)
        hook_w = self.STEM * 3
        draw_rect(draw, x + self.STEM, top, hook_w, self.STEM, fill=fill)
        # Terminal dot on hook
        dot_r = self.STEM // 2
        draw_circle(draw, x + self.STEM + hook_w, top + self.STEM // 2, dot_r, fill=fill)
        return x + self.STEM + hook_w + dot_r * 2

    def draw_b(self, draw, x: int, y_center: int, fill=(0,0,0,255)):
        """Lowercase b — vertical stem + round bowl."""
        top, bot = self._letter_base_y(y_center)
        bowl_top = top
        bowl_bot = y_center + self.STEM
        bowl_r = (bowl_bot - bowl_top) // 2
        bowl_cx = x + self.STEM + bowl_r

        # Stem (full height)
        draw_rect(draw, x, top, self.STEM, bot - top + 1, fill=fill)
        # Bowl (circle, unfilled — ring)
        draw_arc(draw,
                 [bowl_cx - bowl_r, bowl_top, bowl_cx + bowl_r, bowl_bot],
                 0, 360, fill=fill, width=self.STEM)
        return bowl_cx + bowl_r

    def draw_a(self, draw, x: int, y_center: int, fill=(0,0,0,255)):
        """Lowercase a — bowl + stem."""
        top, bot = self._letter_base_y(y_center)
        bowl_h = self.STEM * 5
        bowl_top = bot - bowl_h
        bowl_r = bowl_h // 2
        bowl_cx = x + bowl_r + self.STEM // 2

        # Bowl
        draw_arc(draw,
                 [bowl_cx - bowl_r, bowl_top, bowl_cx + bowl_r, bot],
                 0, 360, fill=fill, width=self.STEM)
        # Stem (right side of a)
        stem_x = bowl_cx + bowl_r - self.STEM // 2
        draw_rect(draw, stem_x, bowl_top - self.STEM, self.STEM,
                  bot - bowl_top + self.STEM + 1, fill=fill)
        return stem_x + self.STEM

    def draw_n(self, draw, x: int, y_center: int, fill=(0,0,0,255)):
        """Lowercase n — two stems + arch."""
        top, bot = self._letter_base_y(y_center)
        right = x + self.RADIUS * 2

        # Left stem
        draw_rect(draw, x, top, self.STEM, bot - top + 1, fill=fill)
        # Right stem
        draw_rect(draw, right - self.STEM, top, self.STEM, bot - top + 1, fill=fill)
        # Arch (from top of left stem to top of right stem)
        arch_top = top
        arch_bot = y_center + self.HALF_STEM
        arch_h = arch_bot - arch_top
        arch_l = x + self.STEM // 2
        arch_r = right - self.STEM // 2
        draw_arc(draw,
                 [arch_l, arch_top, arch_r, arch_top + arch_h * 2],
                 180, 360, fill=fill, width=self.STEM)
        return right

    def draw_C(self, draw, x: int, y_center: int, fill=(0,0,0,255)):
        """
        C — open ring with directional terminal cuts.
        The upper and lower terminals are cut at matching angles,
        creating a tension vector that reads as 'aiming' or 'direction'.
        """
        top, bot = self._letter_base_y(y_center)
        w = self.RADIUS * 2
        cx = x + self.RADIUS

        # Main arc (almost full circle, with gap on right side)
        gap_angle = 50  # degrees of opening
        start_angle = 180 + gap_angle // 2
        end_angle = 360 + 180 - gap_angle // 2
        draw_arc(draw,
                 [x, top, x + w, bot],
                 start_angle, end_angle, fill=fill, width=self.STEM)

        # Terminal cuts: small flat angled ends
        # Upper terminal (angled)
        upper_angle_rad = math.radians(start_angle)
        ux = int(cx + self.RADIUS * math.cos(upper_angle_rad))
        uy = int(y_center + self.RADIUS * math.sin(upper_angle_rad))
        cut_len = self.STEM * 2
        cut_angle = math.radians(15)
        cut_dx = int(cut_len * math.cos(cut_angle))
        cut_dy = int(cut_len * math.sin(cut_angle))
        draw_rect(draw, ux - cut_dx // 2, uy - cut_dy // 2, cut_dx, self.STEM, fill=fill)

        # Lower terminal
        lower_angle_rad = math.radians(end_angle)
        lx = int(cx + self.RADIUS * math.cos(lower_angle_rad))
        ly = int(y_center + self.RADIUS * math.sin(lower_angle_rad))
        draw_rect(draw, lx - cut_dx // 2, ly - cut_dy // 2, cut_dx, self.STEM, fill=fill)

        return x + w

    def draw_apostrophe(self, draw, x: int, y_center: int, fill=(0,0,0,255)):
        """Geometrically pure apostrophe — a clean vertical pill shape."""
        h = self.APOSTROPHE_H
        w = max(2, self.HALF_STEM)
        top = y_center - self.CAP // 2 + self.STEM
        draw_rounded_rect(draw, x, top, w, h, rr=w // 2, fill=fill)
        return x + w + self.LETTER_GAP // 2

    def draw_space(self, draw, x: int):
        """Inter-word space."""
        return x + self.WORD_GAP

    # ------------------------------------------------------------------
    # FULL WORDMARK RENDERER
    # ------------------------------------------------------------------

    def render(self, canvas_w: int = 2400, canvas_h: int = 800,
               bg=(255,255,255,255), fg=(0,0,0,255)):
        """Render the complete 'Urban's Cannon' wordmark at given canvas size."""

        # Calculate total width needed
        # Width per capital: STEM*2 + RADIUS*2
        cap_w = self.RADIUS * 2
        lc_w = self.RADIUS * 2  # lowercase width

        total_w = (cap_w + self.LETTER_GAP +      # U
                   self.RADIUS * 2 + self.LETTER_GAP +  # r
                   self.RADIUS * 2 + self.LETTER_GAP +  # b
                   self.RADIUS * 2 + self.LETTER_GAP +  # a
                   self.RADIUS * 2 + self.LETTER_GAP +  # n
                   self.HALF_STEM + self.APOSTROPHE_W + self.LETTER_GAP // 2 + self.LETTER_GAP +  # '
                   self.WORD_GAP +                         # space
                   cap_w + self.LETTER_GAP +      # C
                   self.RADIUS * 2 + self.LETTER_GAP +  # a
                   self.RADIUS * 2 + self.LETTER_GAP +  # n
                   self.RADIUS * 2 + self.LETTER_GAP +  # n
                   self.RADIUS * 2 + self.LETTER_GAP +  # o
                   self.RADIUS * 2)                       # n

        start_x = (canvas_w - total_w) // 2
        y_center = canvas_h // 2

        img = Image.new("RGBA", (canvas_w, canvas_h), bg)
        draw = ImageDraw.Draw(img)

        x = start_x

        # U
        x = self.draw_U(draw, x, y_center, fill=fg)
        x += self.LETTER_GAP
        # r
        x = self.draw_r(draw, x, y_center, fill=fg)
        x += self.LETTER_GAP
        # b
        x = self.draw_b(draw, x, y_center, fill=fg)
        x += self.LETTER_GAP
        # a
        x = self.draw_a(draw, x, y_center, fill=fg)
        x += self.LETTER_GAP
        # n
        x = self.draw_n(draw, x, y_center, fill=fg)
        x += self.LETTER_GAP
        # '
        x = self.draw_apostrophe(draw, x, y_center, fill=fg)
        # (extra gap after apostrophe)
        x += self.LETTER_GAP // 2
        # space
        x = self.draw_space(draw, x)
        # C
        x = self.draw_C(draw, x, y_center, fill=fg)
        x += self.LETTER_GAP
        # a
        x = self.draw_a(draw, x, y_center, fill=fg)
        x += self.LETTER_GAP
        # n
        x = self.draw_n(draw, x, y_center, fill=fg)
        x += self.LETTER_GAP
        # n
        x = self.draw_n(draw, x, y_center, fill=fg)
        x += self.LETTER_GAP
        # o
        x = self.draw_o(draw, x, y_center, fill=fg)
        x += self.LETTER_GAP
        # n
        x = self.draw_n(draw, x, y_center, fill=fg)

        return img

    def draw_o(self, draw, x: int, y_center: int, fill=(0,0,0,255)):
        """Lowercase o — a perfect ring."""
        top, bot = self._letter_base_y(y_center)
        w = self.RADIUS * 2
        draw_arc(draw, [x, top, x + w, bot], 0, 360, fill=fill, width=self.STEM)
        return x + w

    def render_uc_mark(self, size: int = 1024,
                       bg=(0,0,0,255), fg=(255,255,255,255)):
        """Render the UC monogram as a square icon."""
        img = Image.new("RGBA", (size, size), bg)
        draw = ImageDraw.Draw(img)

        # Larger stem for icon
        orig_stem = self.STEM
        self.STEM = size // 48
        self.HALF_STEM = self.STEM // 2
        self.RADIUS = self.STEM * 4
        self.CAP = self.STEM * 11
        self.CUT = self.STEM * 1

        # Draw UC centered
        cap_w = self.RADIUS * 2
        gap = self.STEM * 3
        total = cap_w + gap + cap_w
        sx = (size - total) // 2
        y = size // 2

        self.draw_U(draw, sx, y, fill=fg)
        self.draw_C(draw, sx + cap_w + gap, y, fill=fg)

        # Restore
        self.STEM = orig_stem
        self.HALF_STEM = self.STEM // 2
        self.RADIUS = self.STEM * 4
        self.CAP = self.STEM * 11
        self.CUT = self.STEM * 1

        return img


# ============================================================
# MAIN
# ============================================================

def generate_all():
    out = os.path.dirname(os.path.abspath(__file__))
    ls = LogoSystem(stem=14)

    print("Constructing custom geometric logo...")

    # 1. Black on white wordmark
    img = ls.render(2400, 800, bg=(255,255,255,255), fg=(0,0,0,255))
    img.save(os.path.join(out, "logo-black-on-white.png"))
    print("  -> logo-black-on-white.png")

    # 2. White on black wordmark
    img2 = ls.render(2400, 800, bg=(0,0,0,255), fg=(255,255,255,255))
    img2.save(os.path.join(out, "logo-white-on-black.png"))
    print("  -> logo-white-on-black.png")

    # 3. UC icon mark
    icon = ls.render_uc_mark(1024, bg=(0,0,0,255), fg=(255,255,255,255))
    icon.save(os.path.join(out, "logo-uc-icon-dark.png"))
    print("  -> logo-uc-icon-dark.png")

    icon2 = ls.render_uc_mark(1024, bg=(255,255,255,255), fg=(0,0,0,255))
    icon2.save(os.path.join(out, "logo-uc-icon-light.png"))
    print("  -> logo-uc-icon-light.png")

    # 4. Landscape lockup
    img3 = ls.render(3200, 400, bg=(255,255,255,255), fg=(0,0,0,255))
    img3.save(os.path.join(out, "logo-landscape-bw.png"))
    print("  -> logo-landscape-bw.png")

    img4 = ls.render(3200, 400, bg=(0,0,0,255), fg=(255,255,255,255))
    img4.save(os.path.join(out, "logo-landscape-wb.png"))
    print("  -> logo-landscape-wb.png")

    print("\nCustom geometric logo complete.")


if __name__ == "__main__":
    generate_all()
