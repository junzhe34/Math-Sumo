"""
Sumo Math Battle - Primary 5 Maths Game
For Pythonista 3 (iPad/iPhone)

RULES:
  - Human player vs opponent (opponent never answers)
  - Correct answer -> opponent pushed 1 step back from centre
  - Wrong answer   -> player pushed 1 step back from centre
  - 3 steps back from centre = OUT of ring -> game over
  - Difficulty controls question type and number range
  - 10 questions per game (unless someone is pushed out first)

Drawing API (verified Pythonista 3 scene module):
  from scene import *
  background(r,g,b)
  fill(r,g,b,a) then rect(x,y,w,h) or ellipse(x,y,w,h)
  tint(r,g,b,a) then text(str, font, size, x, y, alignment)
"""

from scene import *
import random
import math

# ================================================================
#  DIFFICULTY SETTINGS
#  Each level controls which operations appear AND number ranges.
# ================================================================
DIFFICULTY = {
    "Easy": {
        "ops":  ["+", "-"],
        "add":  ((10, 50),   (10, 50)),
        "sub":  ((20, 99),   (5,  20)),
        "mul":  ((2,  5),    (2,   5)),
        "div":  ((1,  9),    (2,   4)),
        "desc": "Addition & Subtraction  |  numbers 10 - 99",
    },
    "Medium": {
        "ops":  ["+", "-", "x"],
        "add":  ((50,  500), (50,  500)),
        "sub":  ((100, 999), (20,  200)),
        "mul":  ((3,   12),  (3,    12)),
        "div":  ((2,   12),  (3,    12)),
        "desc": "+ - x  |  numbers up to 999",
    },
    "Hard": {
        "ops":  ["+", "-", "x", "/"],
        "add":  ((500, 9999), (500, 9999)),
        "sub":  ((500, 9999), (100, 4999)),
        "mul":  ((6,   25),   (6,    25)),
        "div":  ((6,   25),   (2,    12)),
        "desc": "+ - x /  |  large numbers & division",
    },
}

# ================================================================
#  COLOURS
# ================================================================
BG       = (0.94, 0.87, 0.68, 1.0)
RING_OUT = (0.78, 0.60, 0.35, 1.0)
RING_IN  = (0.92, 0.84, 0.65, 1.0)
PLAYER   = (0.15, 0.40, 0.82, 1.0)
OPP      = (0.82, 0.15, 0.15, 1.0)
BTN_G    = (0.20, 0.52, 0.26, 1.0)
BTN_GH   = (0.30, 0.65, 0.36, 1.0)
PANEL    = (0.10, 0.08, 0.05, 0.94)
WHITE    = (1.0,  1.0,  1.0,  1.0)
YELLOW   = (1.0,  0.85, 0.08, 1.0)
GREEN    = (0.15, 0.78, 0.28, 1.0)
RED      = (0.90, 0.15, 0.12, 1.0)
ORANGE   = (0.95, 0.52, 0.05, 1.0)
SHADOW   = (0.00, 0.00, 0.00, 0.20)
SKIN     = (0.94, 0.79, 0.58, 1.0)
GREY     = (0.65, 0.65, 0.65, 1.0)
GREY2    = (0.40, 0.40, 0.40, 1.0)
BROWN    = (0.42, 0.30, 0.18, 1.0)
LINE_C   = (0.48, 0.33, 0.13, 0.55)
BELT_P   = (0.10, 0.10, 0.55, 1.0)
BELT_O   = (0.55, 0.05, 0.05, 1.0)

DIFF_CLR = {
    "Easy":   (0.18, 0.62, 0.28, 1.0),
    "Medium": (0.78, 0.50, 0.04, 1.0),
    "Hard":   (0.82, 0.10, 0.10, 1.0),
}

# States
S_MENU     = "menu"
S_QUESTION = "question"
S_RESULT   = "result"
S_GAMEOVER = "gameover"

MAX_STEPS = 3   # steps from centre before pushed OUT

# ================================================================
#  DRAWING HELPERS
# ================================================================
def box(x, y, w, h, c):
    fill(c[0], c[1], c[2], c[3])
    rect(x, y, w, h)

def oval(x, y, w, h, c):
    fill(c[0], c[1], c[2], c[3])
    ellipse(x, y, w, h)

def txt(s, x, y, size, c, bold=False, align=5):
    tint(c[0], c[1], c[2], c[3])
    fname = "Helvetica-Bold" if bold else "Helvetica"
    text(str(s), fname, size, x, y, align)

# ================================================================
#  QUESTION GENERATOR  (uses difficulty config)
# ================================================================
def make_question(diff_key):
    cfg = DIFFICULTY[diff_key]
    op  = random.choice(cfg["ops"])

    if op == "+":
        lo1, hi1 = cfg["add"][0]
        lo2, hi2 = cfg["add"][1]
        a, b = random.randint(lo1, hi1), random.randint(lo2, hi2)
        ans, sym = a + b, "+"

    elif op == "-":
        lo1, hi1 = cfg["sub"][0]
        lo2, hi2 = cfg["sub"][1]
        a = random.randint(lo1, hi1)
        b = random.randint(lo2, max(lo2, min(hi2, a - 1)))
        ans, sym = a - b, "-"

    elif op == "x":
        lo1, hi1 = cfg["mul"][0]
        lo2, hi2 = cfg["mul"][1]
        a, b = random.randint(lo1, hi1), random.randint(lo2, hi2)
        ans, sym = a * b, "x"

    else:  # division: generate exact integer answer
        lo_a, hi_a = cfg["div"][0]
        lo_b, hi_b = cfg["div"][1]
        ans = random.randint(lo_a, hi_a)
        b   = random.randint(lo_b, hi_b)
        a   = ans * b
        sym = "/"

    return "{} {} {} = ?".format(a, sym, b), ans


def make_choices(correct):
    """4 plausible multiple-choice options including the correct one."""
    pool = {correct}
    spread = max(5, abs(correct) // 8 + 2)
    for _ in range(400):
        if len(pool) >= 4:
            break
        d = random.randint(1, spread)
        w = correct + random.choice([-1, 1]) * d
        if w != correct and w >= 0:
            pool.add(w)
    offset = 1
    while len(pool) < 4:
        pool.add(correct + offset)
        offset += 1
    lst = list(pool)
    random.shuffle(lst)
    return lst


# ================================================================
#  MAIN SCENE
# ================================================================
class SumoGame(Scene):

    def setup(self):
        self.state         = S_MENU
        self.diff_key      = "Medium"
        # How many steps each wrestler has been pushed from centre
        # Range: 0 (at centre) to MAX_STEPS (out of ring)
        self.player_steps  = 0
        self.opp_steps     = 0

        self.q_num         = 0
        self.total_q       = 10
        self.correct_count = 0
        self.wrong_count   = 0

        self.question      = ""
        self.correct       = 0
        self.choices       = []
        self.p_ans         = None
        self.result_msg    = ""
        self.result_color  = WHITE

        self.shake_who     = "none"
        self.anim_offset   = 0.0
        self.anim_timer    = 0.0
        self.btns          = {}

    # ── Touch ──────────────────────────────────────────────────
    def touch_began(self, touch):
        tx, ty = touch.location

        if self.state == S_MENU:
            for k, (x, y, w, h) in self.btns.items():
                if x <= tx <= x+w and y <= ty <= y+h:
                    if k in DIFFICULTY:
                        self.diff_key = k
                    elif k == "start":
                        self._start()

        elif self.state == S_QUESTION:
            if self.p_ans is not None:
                return
            for k, (x, y, w, h) in self.btns.items():
                if x <= tx <= x+w and y <= ty <= y+h and isinstance(k, int):
                    self.p_ans = k
                    self._resolve()

        elif self.state in (S_RESULT, S_GAMEOVER):
            for k, (x, y, w, h) in self.btns.items():
                if x <= tx <= x+w and y <= ty <= y+h:
                    if k == "next":   self._next_q()
                    elif k == "retry": self._start()
                    elif k == "menu":  self._go_menu()

    # ── Game flow ──────────────────────────────────────────────
    def _go_menu(self):
        self.state = S_MENU
        self.btns  = {}

    def _start(self):
        self.player_steps  = 0
        self.opp_steps     = 0
        self.q_num         = 0
        self.correct_count = 0
        self.wrong_count   = 0
        self._next_q()

    def _next_q(self):
        self.q_num    += 1
        self.question, self.correct = make_question(self.diff_key)
        self.choices   = make_choices(self.correct)
        self.p_ans     = None
        self.result_msg = ""
        self.state     = S_QUESTION

    def _resolve(self):
        correct = (self.p_ans == self.correct)

        if correct:
            # Player correct -> push opponent back one step
            self.opp_steps    += 1
            self.correct_count += 1
            self.result_msg    = "Correct!  Opponent pushed back!"
            self.result_color  = GREEN
            self.shake_who     = "opp"
        else:
            # Player wrong -> push player back one step
            self.player_steps += 1
            self.wrong_count  += 1
            self.result_msg   = "Wrong!  Answer was " + str(self.correct) + "  You were pushed back!"
            self.result_color  = RED
            self.shake_who     = "player"

        self.anim_timer = 0.65

        # Check if either wrestler is pushed OUT (reached MAX_STEPS
        if self.player_steps >= MAX_STEPS:
            self.state      = S_GAMEOVER
            self.result_msg = "You were pushed OUT of the ring!"
            return
        if self.opp_steps >= MAX_STEPS:
            self.state      = S_GAMEOVER
            self.result_msg = "Opponent pushed OUT!  YOU WIN!"
            return

        # Check if all questions done
        if self.q_num >= self.total_q:
            self.state = S_GAMEOVER
            if self.correct_count > self.wrong_count:
                self.result_msg = "All " + str(self.total_q) + " Qs done - YOU WIN!  " + str(self.correct_count) + " correct"
            elif self.wrong_count > self.correct_count:
                self.result_msg = "All " + str(self.total_q) + " Qs done - You lose.  " + str(self.correct_count) + " correct"
            else:
                self.result_msg = "All " + str(self.total_q) + " Qs done - DRAW!  " + str(self.correct_count) + " correct"
            return

        self.state = S_RESULT

    # ── Animation ──────────────────────────────────────────────
    def update(self):
        if self.anim_timer > 0:
            self.anim_timer  -= self.dt
            self.anim_offset  = math.sin(self.anim_timer * 42) * 22
        else:
            self.anim_offset = 0.0
            self.shake_who   = "none"

    # ── Master draw ────────────────────────────────────────────
    def draw(self):
        self.btns = {}
        W, H = self.size
        background(BG[0], BG[1], BG[2])

        if self.state == S_MENU:
            self._draw_menu(W, H)
        elif self.state == S_QUESTION:
            self._draw_ring(W, H)
            self._draw_q_panel(W, H)
        elif self.state == S_RESULT:
            self._draw_ring(W, H)
            self._draw_result(W, H)
        elif self.state == S_GAMEOVER:
            self._draw_ring(W, H)
            self._draw_gameover(W, H)

    # ── Menu ───────────────────────────────────────────────────
    def _draw_menu(self, W, H):
        # Top banner
        box(0, H*0.83, W, H*0.17, PANEL)
        txt("SUMO MATHS BATTLE", W/2, H*0.91, 27, WHITE, bold=True)
        txt("Primary 5 Edition",  W/2, H*0.85, 16, YELLOW)

        # Preview ring
        self._draw_ring(W, H, preview=True)

        # Difficulty section
        txt("Choose Difficulty:", W/2, H*0.41, 16, GREY2, bold=True)

        diffs  = list(DIFFICULTY.keys())
        bw, bh, gap = 115, 46, 12
        total  = len(diffs)*bw + (len(diffs)-1)*gap
        sx     = W/2 - total/2

        for i, d in enumerate(diffs):
            bx  = sx + i*(bw+gap)
            by  = H*0.335
            dc  = DIFF_CLR[d]
            sel = (d == self.diff_key)
            if sel:
                box(bx-3, by-3, bw+6, bh+6, WHITE)
            self._btn(bx, by, bw, bh, d, dc, key=d, size=18, bold=sel)

        # Description strip for selected difficulty
        desc = DIFFICULTY[self.diff_key]["desc"]
        dc   = DIFF_CLR[self.diff_key]
        box(W*0.04, H*0.273, W*0.92, 36, PANEL)
        txt(desc, W/2, H*0.285, 12, dc)

        # Rules reminder
        box(W*0.04, H*0.21, W*0.92, 36, (0.1,0.08,0.05,0.70))
        txt("Correct = push opp 1 step   Wrong = pushed back 1 step   3 steps = OUT",
            W/2, H*0.223, 11, YELLOW)

        # Start button
        self._btn(W/2-85, H*0.155, 170, 50,
                  "START GAME", BROWN, key="start", size=21, bold=True)

    # ── Ring ───────────────────────────────────────────────────
    def _draw_ring(self, W, H, preview=False):
        if preview:
            cy     = H * 0.585
            ring_r = min(W, H) * 0.14
        else:
            cy     = H * 0.645
            ring_r = min(W, H) * 0.26
        cx = W / 2

        # Outer shadow
        oval(cx-ring_r*1.06, cy-ring_r*0.47, ring_r*2.12, ring_r*0.94, SHADOW)
        # Outer ring dirt
        oval(cx-ring_r,      cy-ring_r*0.44, ring_r*2,    ring_r*0.88, RING_OUT)
        # Inner clay
        oval(cx-ring_r*0.87, cy-ring_r*0.38, ring_r*1.74, ring_r*0.76, RING_IN)
        # Centre dividing line
        box(cx-2, cy-ring_r*0.36, 4, ring_r*0.72, LINE_C)

        # step_px: pixels per position step
        step_px = ring_r * 0.38

        # Player on LEFT, moves further left as player_steps increases
        p_offset = self.anim_offset if self.shake_who == "player" else 0
        px_x = cx - step_px * (1 + self.player_steps * 0.6) + p_offset

        # Opponent on RIGHT, moves further right as opp_steps increases
        o_offset = self.anim_offset if self.shake_who == "opp" else 0
        ox_x = cx + step_px * (1 + self.opp_steps * 0.6) + o_offset

        wr = ring_r * (0.13 if preview else 0.17)
        self._draw_wrestler(px_x, cy, wr, PLAYER, BELT_P, "YOU")
        self._draw_wrestler(ox_x, cy, wr, OPP,    BELT_O, "OPP")

        if not preview:
            self._draw_position_bars(cx, cy + ring_r*0.57, step_px)
            lbl = ("Q " + str(self.q_num) + "/" + str(self.total_q)
                   + "     Correct: " + str(self.correct_count)
                   + "   Wrong: " + str(self.wrong_count))
            txt(lbl, W/2, H*0.94, 14, PANEL)

    def _draw_wrestler(self, cx, cy, r, body_clr, belt_clr, label):
        # Drop shadow
        oval(cx-r*0.85, cy-r*0.08, r*1.70, r*0.32, SHADOW)
        # Body
        oval(cx-r,      cy-r*0.55, r*2.00, r*1.75, body_clr)
        # Belt / mawashi stripe
        box(cx-r, cy-r*0.05, r*2, r*0.40, belt_clr)
        # Head
        oval(cx-r*0.58, cy+r*0.85, r*1.16, r*1.16, SKIN)
        # Label
        txt(label, cx, cy+r*0.18, int(r*0.72), WHITE, bold=True)

    def _draw_position_bars(self, cx, base_y, step_px):
        """
        Show 3 position dots per side.
        Player (left): dots fill RED as player is pushed back.
        Opponent (right): dots fill ORANGE as opponent is pushed back.
        First dot = 1 step from centre, third = danger zone.
        """
        dr = 11   # dot radius
        diam = dr * 2

        for i in range(1, MAX_STEPS + 1):
            # Player dots (left of centre, spaced outward)
            dx = cx - step_px * 0.55 - (i - 1) * (diam + 6)
            clr = RED if self.player_steps >= i else GREY
            oval(dx - dr, base_y, diam, diam, clr)

            # Opponent dots (right of centre, spaced outward)
            dx2 = cx + step_px * 0.55 + (i - 1) * (diam + 6)
            clr2 = ORANGE if self.opp_steps >= i else GREY
            oval(dx2 - dr, base_y, diam, diam, clr2)

        txt("YOU", cx - step_px*0.55 - (MAX_STEPS-1)*(diam+6)*0.5,
            base_y + diam + 10, 11, RED, bold=True)
        txt("OPP", cx + step_px*0.55 + (MAX_STEPS-1)*(diam+6)*0.5,
            base_y + diam + 10, 11, ORANGE, bold=True)
        txt("3 steps = OUT", cx, base_y + diam + 24, 11, GREY2)

    # ── Question panel ─────────────────────────────────────────
    def _draw_q_panel(self, W, H):
        ph = H * 0.44
        px = W * 0.04
        py = H * 0.01
        pw = W * 0.92
        box(px, py, pw, ph, PANEL)

        # Difficulty colour badge at top of panel
        dc = DIFF_CLR[self.diff_key]
        box(px, py+ph-28, pw, 28, dc)
        txt(self.diff_key + " Difficulty", px+pw/2, py+ph-14, 14, WHITE, bold=True)

        # Question
        txt(self.question, px+pw/2, py+ph-62, 26, YELLOW, bold=True)

        # 4 answer buttons in 2x2 grid
        bw = pw/2 - 20
        bh = 52
        positions = [
            (px+8,        py+ph-122),
            (px+pw/2+12,  py+ph-122),
            (px+8,        py+ph-186),
            (px+pw/2+12,  py+ph-186),
        ]
        for i, (bx, by) in enumerate(positions):
            v = self.choices[i]
            self._btn(bx, by, bw, bh, str(v), BTN_G, key=v, size=21)

    # ── After-answer result strip ──────────────────────────────
    def _draw_result(self, W, H):
        pw = W * 0.88
        ph = 180
        px = W * 0.06
        py = H * 0.04
        box(px, py, pw, ph, PANEL)

        # Coloured banner
        box(px, py+ph-32, pw, 32, self.result_color)
        txt(self.result_msg, px+pw/2, py+ph-16, 13, WHITE, bold=True)

        # Position status
        p_txt = "Your steps back: " + str(self.player_steps) + " / " + str(MAX_STEPS)
        o_txt = "Opp steps back:  " + str(self.opp_steps) + " / " + str(MAX_STEPS)
        p_clr = RED    if self.player_steps > 0 else GREY
        o_clr = ORANGE if self.opp_steps    > 0 else GREY
        txt(p_txt, px+pw/2, py+ph-68, 14, p_clr)
        txt(o_txt, px+pw/2, py+ph-94, 14, o_clr)

        self._btn(W/2-85, py+14, 170, 46,
                  "Next Question", BROWN, key="next", size=18, bold=True)

    # ── Game over ──────────────────────────────────────────────
    def _draw_gameover(self, W, H):
        pw = W * 0.88
        ph = 245
        px = W * 0.06
        py = H * 0.03
        box(px, py, pw, ph, PANEL)

        # Determine win/loss
        if self.opp_steps >= MAX_STEPS:
            won = True
        elif self.player_steps >= MAX_STEPS:
            won = False
        else:
            won = self.correct_count > self.wrong_count

        banner = GREEN if won else RED
        box(px, py+ph-42, pw, 42, banner)
        headline = "YOU WIN!" if won else "YOU LOSE!"
        txt(headline, px+pw/2, py+ph-20, 25, WHITE, bold=True)

        txt(self.result_msg,  px+pw/2, py+ph-76,  13, WHITE)
        txt("Correct: " + str(self.correct_count)
            + "   Wrong: " + str(self.wrong_count)
            + "   Qs: " + str(self.q_num),
            px+pw/2, py+ph-108, 14, YELLOW)
        txt("Difficulty: " + self.diff_key,
            px+pw/2, py+ph-134, 14, DIFF_CLR[self.diff_key], bold=True)

        # Final position summary
        p_bar = "Player pushed: " + str(self.player_steps) + "/" + str(MAX_STEPS) + " steps"
        o_bar = "Opp pushed:    " + str(self.opp_steps)    + "/" + str(MAX_STEPS) + " steps"
        txt(p_bar, px+pw/2, py+ph-158, 13, RED)
        txt(o_bar, px+pw/2, py+ph-178, 13, ORANGE)

        self._btn(W/2-90, py+65, 180, 48,
                  "Play Again", BTN_G, key="retry", size=19, bold=True)
        self._btn(W/2-90, py+10, 180, 44,
                  "Main Menu",  BROWN, key="menu",  size=18)

    # ── Button helper ──────────────────────────────────────────
    def _btn(self, x, y, w, h, label, color,
             key=None, size=18, bold=False):
        box(x, y, w, h, color)
        r, g, b, a = color
        box(x, y, w, 4, (r*0.50, g*0.50, b*0.50, a))   # dark bottom edge
        txt(label, x+w/2, y+h/2, size, WHITE, bold=bold)
        if key is not None:
            self.btns[key] = (x, y, w, h)


# ── Run ────────────────────────────────────────────────────────
run(SumoGame(), PORTRAIT, show_fps=False)
