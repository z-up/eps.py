from PIL import Image
from os import unlink
from subprocess import getoutput, Popen
from time import sleep

from cardcodes import CARD_UNICODES as CU, CARD_ASCII_CODES as CA

def read_bin_file(fname):
    f = open(fname, "rb")
    bin = f.read()
    f.close()
    return bin


def bmp_pixels_hash(fname):
    img = Image.open(fname)
    pixels = img.getdata()
    lst = list(pixels)
    lst_str = str(lst)
    str_hash = hash(lst_str)
    return str_hash


def move_mouse(x, y):
    getoutput("xte 'mousemove %d %d'" % (x, y))


def lmb_click(x, y):
    move_mouse(x, y)
    getoutput("xte 'mouseclick 1'")


def get_crop_hash(img, w, h, x, y):
    #import random
    #crop_fname = "crop-%04d.bmp" % random.randint(0, 1000)
    crop_fname = "crop.bmp"
    getoutput("convert %s -crop %dx%d+%d+%d %s" % (img, w, h, x, y, crop_fname))
    crop_hash = bmp_pixels_hash(crop_fname)
    unlink(crop_fname)
    return crop_hash


class PCOperator:
    def __init__(self):
        self.define_constants()

    
    def define_constants(self):
        # card width and height
        self.card_w = 48
        self.card_h = 33
        self.cut_h = 15
        # window position
        self.win_x = 0
        self.win_y = 0
        # start button position
        self.start_btn_x = 653
        self.start_btn_y = 356
        # "Enter your name" dialog OK button coordinates
        self.name_dlg_ok_btn_xy = (395, 355)
        # "Hall of Fame" OK button coordinates
        self.hof_ok_btn_xy = (395, 443)
        # main area rows and columns offsets
        self.card_rows = dict(zip("ABCDEF", range(69, 330, 52)))
        self.card_cols = dict(zip("123456", range(13, 274, 52)))
        # same column clues
        self.scc_rows = [496, 544]
        self.scc_cols = list(range(13, 742, 52))
        # other clues
        self.clue_rows = list(range(69, 434, 52))
        self.clue_cols = [(349, 397, 445), (497, 545, 593), (645, 693, 741)]
        # thumb offsets
        self.thumbs = {'1': (8, 16), '2': (24, 16), '3': (39, 16), '4': (8, 32), '5': (24, 32), '6': (39, 32)}
        # images
        self.images = {}
        for r in "ABCDEF":
            for c in "123456":
                self.images[bmp_pixels_hash("images/cropped/large-%s.bmp" % (r + c))] = r + c
        self.images[bmp_pixels_hash("images/cropped/hint-near.bmp")] = "near_hint"
        self.images[bmp_pixels_hash("images/cropped/hint-side.bmp")] = "left_right_hint"


    def reset_data_structures(self):
        self.opened_cards = {}
        self.same_col_clues = []
        self.left_right_clues = []
        self.pair_clues = []
        self.triple_clues = []


    def launch_app(self):
        # launch application
        getoutput("killall einstein")
        sleep(5)
        Popen("einstein")
        sleep(3)

        # find window position
        output = getoutput(
                "xwininfo -id `wmctrl -plG | grep Einstein | awk '{print $1}'` | grep Absolute | awk '{print $4}'")
        self.win_x, self.win_y = [int(l) for l in output.split("\n")]


    def start_new_game(self):
        self.reset_data_structures()

        # click start button
        lmb_click(self.win_x + self.start_btn_x, self.win_y + self.start_btn_y)

        # move mouse pointer so it does not overlay cards in screenshot
        move_mouse(self.win_x, self.win_y)

        # take screenshot
        sleep(1) # give an app some time to redraw itself
        screen = "screenshot.bmp"
        getoutput("import -window einstein %s" % screen)

        # often used vars
        cw, ch = self.card_w, self.card_h

        # find opened cards
        for rn, roff in enumerate(sorted(self.card_rows.values())):
            for cn, coff in enumerate(sorted(self.card_cols.values())):
                crop = get_crop_hash(screen, cw, ch, coff - 1, (roff - 1) + self.cut_h)
                code = self.images.get(crop)
                if code != None:
                    self.opened_cards[code[0] + str(cn + 1)] = code

        # find same column clues
        for coff in self.scc_cols:
            cards = []
            for roff in self.scc_rows:
                crop = get_crop_hash(screen, cw, ch, coff - 1, (roff - 1) + self.cut_h)
                cards.append(self.images.get(crop))
            if not all(cards):
                break
            self.same_col_clues.append(cards)

        # find other clues
        for coff1, coff2, coff3 in self.clue_cols:
            for roff in self.clue_rows:
                crop = get_crop_hash(screen, cw, ch, coff1 - 1, (roff - 1) + self.cut_h)
                card1 = self.images.get(crop)

                crop = get_crop_hash(screen, cw, ch, coff2 - 1, (roff - 1) + self.cut_h)
                card2 = self.images.get(crop)

                crop = get_crop_hash(screen, cw, ch, coff3 - 1, (roff - 1) + self.cut_h)
                card3 = self.images.get(crop)

                if not all([card1, card2, card3]):
                    continue
                if card2 == "left_right_hint":
                    self.left_right_clues.append((card1, card3))
                elif card2 == "near_hint":
                    self.pair_clues.append((card1, card3))
                else:
                    self.triple_clues.append((card1, card2, card3))

        unlink(screen)


    def dump_task(self):
        lines = ["[task]"]
        for row in "ABCDEF":
            line = "|"
            for col in "123456":
                code = self.opened_cards.get(row + col)
                if code:
                    line += " " +  CU[code] + " |"
                else:
                    line += "   |"
            lines.append(line)

        for desc, clue_list in [("Same column clues: ", self.same_col_clues),
                                ("Left-right clues: ", self.left_right_clues),
                                ("Pair clues: ", self.pair_clues),
                                ("Triple clues: ", self.triple_clues)]:
            lines.append(desc + "; ".join(["(%s)" % ", ".join([CU[card] for card in clue]) for clue in clue_list]))
        lines.append("[/task]")
        return lines


    def apply_solution(self, lines, leave_hof_visible=False):
        if lines[0] != "[solution]" or lines[-1] != "[/solution]":
            return False
        for row, line in enumerate(lines[1:-1]):
            cards = list(line.replace(" ", "").replace("|", ""))
            for col, card in enumerate(cards):
                self.open_card(CA[card], col + 1)
                sleep(0.02)
        # Click ok buttons in "Enter your name" and "Hall of Fame" dialogs.
        # If "Enter your name" dialog is not shown, the first click
        # will occur in "Hall of Fame" empty space
        btn_x, btn_y = self.name_dlg_ok_btn_xy
        sleep(0.75)
        lmb_click(self.win_x + btn_x, self.win_y + btn_y)

        if not leave_hof_visible:
            btn_x, btn_y = self.hof_ok_btn_xy
            sleep(0.75)
            lmb_click(self.win_x + btn_x, self.win_y + btn_y)

        sleep(0.75)


    def open_card(self, card, position):
        # cell coordinates
        position = str(position)
        cx = self.card_cols[position]
        cy = self.card_rows[card[0]]
        # thumb coordinates
        tx, ty = self.thumbs[card[1]]
        x = self.win_x + cx + tx
        y = self.win_y + cy + ty
        lmb_click(x, y)

