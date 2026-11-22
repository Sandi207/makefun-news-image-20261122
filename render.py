#!/usr/bin/env python3
"""Draw the fixed Sunday 22 November 2026 edition using Pillow and system fonts."""

import argparse
import math
from functools import lru_cache
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).absolute().parent
FONT_DIRECTORY = Path("/usr/share/fonts/truetype/dejavu")
FONT_FILES = {
    "serif": "DejaVuSerif.ttf",
    "serif_bold": "DejaVuSerif-Bold.ttf",
    "sans": "DejaVuSans.ttf",
    "sans_bold": "DejaVuSans-Bold.ttf",
}
SIZE = 2048
FINAL_SIZE = 1024
MAX_BYTES = 1024 * 1024
PAPER = (247, 244, 234)
INK = (24, 24, 22)
RED = (123, 31, 37)
LEFT = 56
RIGHT = 1992
LEAD_HEADLINE = "IRAN STRIKES US BASES IN BAHRAIN"
LEAD_DECK = (
    "Missiles and drones strike Bahrain; "
    "tankers hit in the Strait of Hormuz."
)
LEAD_FACTS = (
    "Four American bases hit: Sheikh Isa, Juffair, al-Riffa and Awali.",
    "Bahrain told residents to shelter; a compound fire, no injuries.",
    "IRGC claims two Patriot radars destroyed.",
    "Three tankers hit in Hormuz: two by projectiles and one by a mine.",
    "IRGC footage claims two US drones downed; CENTCOM denies an F-16 claim.",
)
MEDIUM = (
    (
        "DENMARK EXPELS GRU ATTACHÉ",
        "DENMARK EXPELS\nGRU ATTACHÉ",
        "EUROPE",
        "COPENHAGEN",
        "A Russian military attaché expelled over the plot to kill a "
        "US-Ukrainian rapper; Copenhagen pushes EU curbs on Russian tourists.",
    ),
    (
        "COP31 DRAGS INTO SUNDAY",
        "COP31 DRAGS\nINTO SUNDAY",
        "CLIMATE",
        "COP31",
        "A third draft still omits fossil fuels; about 130 nations demand "
        "phase-out language; the EU warns: a good deal or no deal.",
    ),
    (
        "CHAPO ISIDRO CAPTURED",
        "CHAPO ISIDRO\nCAPTURED",
        "AMERICAS",
        "SINALOA",
        "The FBI most-wanted cartel boss seized in Sinaloa; eleven dead "
        "in the raid; US intelligence helped.",
    ),
)
TIMELINE = (
    ("00:20 UTC", "Bahrain strikes first reported"),
    ("01:25 UTC", "BBC confirms Chapo capture"),
    ("02:00 UTC", "COP31 enters overtime"),
    ("03:00 UTC", "COP31 talks still deadlocked"),
    ("EARLY SUNDAY", "COP31 third draft omits fossil fuels"),
    ("SUNDAY MORNING", "Denmark expels attaché"),
    ("SUNDAY MORNING", "Basra toll rises to 35 hurt"),
    ("SUNDAY", "Trump says China joins nuclear talks"),
)
BRIEFS = (
    (
        "MIDDLE EAST",
        (
            ("Qatar hosts Centcom chief",
             "Doha defence talks as Gulf tensions soar."),
            ("Iran curbs energy, oil jumps",
             "Tehran restricts energy while the world awaits Trump."),
            ("Hamas seeks urgent talks",
             "After an Israeli strike kills three aid workers in Gaza."),
            ("Four killed in Gaza strikes",
             "Fourteen hurt as ceasefire violations continue."),
            ("Children lie in flood water",
             "Gaza’s crisis deepens as winter floods swamp camps."),
            ("Israel hits south Lebanon",
             "Strikes on towns in the south on Saturday."),
            ("Basra plant fire kills four",
             "Thirty-five hurt at the Hartha power station."),
        ),
    ),
    (
        "EUROPE",
        (
            ("Sparta II still burning",
             "Russian cargo ship ablaze in the Gulf of Finland."),
            ("Finland limits air and sea traffic",
             "After Estonian alerts over drone risks."),
            ("Spain to extend bank tax",
             "The PM will use the levy to fund housing."),
            ("Croatia rallies for the dead",
             "Zagreb demands accountability over hospital deaths."),
            ("Russian skaters quit Warsaw",
             "Ice dancers withdraw after Poland’s objection."),
            ("Turkey seizes last free press",
             "State takes control of a major independent outlet."),
            ("Germany funds Ramstein plan",
             "30 million euros advance for the industrial defence project."),
        ),
    ),
    (
        "AMERICAS",
        (
            ("US moves to ban Chinese AI",
             "Lawmakers push a ban on Chinese models in federal systems."),
            ("Judge blocks homeless-aid revamp",
             "Trump’s 4 billion dollar programme overhaul is rejected."),
            ("State demands ICE dismantled",
             "After masked agents seize two at Seattle airport."),
            ("Palisades arsonist convicted",
             "Man found guilty over the Los Angeles wildfire."),
            ("Bolsonaro in intensive care",
             "Ex-president hospitalised with gut problems."),
            ("Hegseth limits Canada ties",
             "Confidential document curbs US-Canada military links."),
            ("Trump says China joins nuclear talks",
             "Beijing agrees to trilateral nuclear-risk talks."),
        ),
    ),
    (
        "ASIA PACIFIC AFRICA WORLD",
        (
            ("Malaysia’s Rohingya plan stirs row",
             "Sending 10,000 refugees to Türkiye causes confusion."),
            ("US court summons Doval and Goel",
             "Ex-spy chiefs called in the Pannun case."),
            ("China bars red-chip listings",
             "Young firms stopped from listing abroad."),
            ("Nepal PM pressed on border",
             "Shah faces border questions on his first India trip."),
            ("Nigeria boat disaster",
             "Two dozen dead as a mourners’ boat capsizes."),
            ("Ebola toll passes 5,700",
             "Outbreak deaths keep climbing."),
            ("UN acts on killer robots",
             "States agree to aim for rules on autonomous arms by 2028."),
        ),
    ),
)
FOOTER = (
    "THE WORLD TODAY, Sunday 22 November 2026, "
    "32 stories from 6 regions, all times UTC."
)


@lru_cache(maxsize=None)
def font(kind, size):
    return ImageFont.truetype(str(FONT_DIRECTORY / FONT_FILES[kind]), size)


def dimensions(text, face):
    bounds = face.getbbox(text)
    width = max(bounds[2] - bounds[0], math.ceil(face.getlength(text)))
    return width, bounds[3] - bounds[1]


def wrap(text, face, width):
    lines = []
    for paragraph in text.splitlines():
        current = ""
        for word in paragraph.split():
            if dimensions(word, face)[0] > width:
                return None
            candidate = current + " " + word if current else word
            if dimensions(candidate, face)[0] <= width:
                current = candidate
            else:
                lines.append(current)
                current = word
        if current:
            lines.append(current)
    return lines


def line_layout(text, face, width, gap):
    lines = wrap(text, face, width)
    if not lines:
        return None
    line_height = max(dimensions(line, face)[1] for line in lines)
    height = line_height * len(lines) + gap * (len(lines) - 1)
    return lines, line_height, height


class FrontPage:
    def __init__(self):
        self.image = Image.new("RGB", (SIZE, SIZE), PAPER)
        self.draw = ImageDraw.Draw(self.image)
        self.text_bounds = []

    def line(self, text, face, box, color=INK, align="left",
             label="", backing=False):
        width, height = dimensions(text, face)
        x0, y0, x1, y1 = box
        if width > x1 - x0 or height > y1 - y0:
            raise ValueError("Text exceeds its box: " + text)
        x = x0
        if align == "center":
            x += (x1 - x0 - width) / 2
        elif align == "right":
            x = x1 - width
        ink_box = face.getbbox(text)
        if backing:
            self.draw.rectangle(
                (x - 5, y0 - 3, x + width + 5, y0 + height + 3),
                fill=PAPER,
            )
        self.draw.text((x - ink_box[0], y0 - ink_box[1]), text,
                       font=face, fill=color)
        self.text_bounds.append(
            (label, text, (x, y0, x + width, y0 + height), face.size)
        )

    def single(self, text, box, kind="sans_bold", maximum=28,
               minimum=20, color=INK, align="left", label="",
               backing=False):
        for size in range(maximum, minimum - 1, -1):
            face = font(kind, size)
            width, height = dimensions(text, face)
            if width <= box[2] - box[0] and height <= box[3] - box[1]:
                self.line(text, face, box, color, align, label, backing)
                return size
        raise ValueError("No legible single-line fit: " + text)

    def block(self, text, box, kind="sans", maximum=25,
              minimum=22, gap=4, color=INK, label=""):
        for size in range(maximum, minimum - 1, -1):
            face = font(kind, size)
            layout = line_layout(text, face, box[2] - box[0], gap)
            if layout and layout[2] <= box[3] - box[1]:
                lines, line_height, height = layout
                for index, line in enumerate(lines):
                    y = box[1] + index * (line_height + gap)
                    self.line(line, face, (box[0], y, box[2], y + line_height),
                              color=color, label=label)
                return box[1] + height
        raise ValueError("No legible paragraph fit: " + text)

    def rule(self, y, width=2, color=INK, x0=LEFT, x1=RIGHT):
        self.draw.line((x0, y, x1, y), fill=color, width=width)

    def masthead(self):
        self.single("GLOBAL EDITION", (LEFT, 13, 500, 32),
                    maximum=20, minimum=20, color=RED)
        self.single("SUNDAY BRIEFING", (1540, 13, RIGHT, 32),
                    maximum=20, minimum=20, color=RED, align="right")
        self.single("THE WORLD TODAY", (LEFT, 37, RIGHT, 160),
                    kind="serif_bold", maximum=160, minimum=150,
                    align="center", label="masthead")
        date = "SUNDAY, 22 NOVEMBER 2026"
        note = "32 STORIES, 6 REGIONS"
        face = font("sans_bold", 28)
        date_width = dimensions(date, face)[0]
        note_width = dimensions(note, face)[0]
        gap = 62
        start = (SIZE - date_width - note_width - gap) / 2
        self.line(date, face, (start, 170, start + date_width, 195),
                  label="date")
        note_start = start + date_width + gap
        self.line(note, face, (note_start, 170, note_start + note_width, 195),
                  color=RED, label="story_count")
        self.draw.line((start + date_width + gap / 2, 170,
                        start + date_width + gap / 2, 193),
                       fill=INK, width=2)
        self.rule(200, width=7)
        self.rule(208, width=1)

    def arrow(self, start, control, end):
        points = []
        for index in range(65):
            t = index / 64
            points.append((
                (1 - t) ** 2 * start[0] + 2 * (1 - t) * t * control[0]
                + t ** 2 * end[0],
                (1 - t) ** 2 * start[1] + 2 * (1 - t) * t * control[1]
                + t ** 2 * end[1],
            ))
        self.draw.line(points, fill=INK, width=5, joint="curve")
        direction = math.atan2(end[1] - points[-5][1],
                               end[0] - points[-5][0])
        arrowhead = [end]
        for offset in (-0.48, 0.48):
            arrowhead.append((
                end[0] - 22 * math.cos(direction + offset),
                end[1] - 22 * math.sin(direction + offset),
            ))
        self.draw.polygon(arrowhead, fill=INK)
        self.draw.ellipse((start[0] - 4, start[1] - 4,
                           start[0] + 4, start[1] + 4), fill=INK)

    def star(self, x, y, radius=12):
        points = []
        for index in range(10):
            angle = -math.pi / 2 + index * math.pi / 5
            length = radius if index % 2 == 0 else radius * 0.43
            points.append((x + length * math.cos(angle),
                           y + length * math.sin(angle)))
        self.draw.polygon(points, fill=INK)

    def tanker(self, x, y, burning=False):
        self.draw.polygon(((x, y), (x + 40, y), (x + 48, y + 8),
                           (x + 40, y + 17), (x, y + 17)), fill=INK)
        self.draw.rectangle((x + 9, y - 9, x + 18, y), fill=INK)
        self.draw.rectangle((x + 4, y - 4, x + 25, y), fill=INK)
        if burning:
            self.draw.polygon(((x + 28, y - 5), (x + 22, y - 17),
                               (x + 28, y - 28), (x + 31, y - 22),
                               (x + 36, y - 38), (x + 43, y - 24),
                               (x + 43, y - 12), (x + 36, y - 4)),
                              fill=INK)
            self.draw.polygon(((x + 32, y - 7), (x + 30, y - 15),
                               (x + 35, y - 23), (x + 37, y - 12)),
                              fill=PAPER)

    def gulf_map(self):
        upper = [
            (100, 418), (179, 390), (282, 380), (402, 398),
            (513, 406), (657, 438), (780, 470), (896, 517),
            (984, 583), (1032, 621), (1076, 645),
        ]
        lower = [
            (1047, 681), (1005, 666), (974, 642), (943, 615),
            (877, 583), (807, 567), (728, 552), (641, 532),
            (548, 514), (453, 491), (341, 475), (230, 458),
            (153, 461), (110, 442),
        ]
        mask = Image.new("L", (SIZE, SIZE), 0)
        ImageDraw.Draw(mask).polygon(upper + lower, fill=255)
        water = Image.new("RGB", (SIZE, SIZE), PAPER)
        water_draw = ImageDraw.Draw(water)
        for y in range(395, 683, 19):
            water_draw.line((88, y, 1090, y), fill=INK, width=1)
        self.image.paste(water, (0, 0), mask)
        self.draw = ImageDraw.Draw(self.image)
        self.draw.line(upper, fill=INK, width=4, joint="curve")
        self.draw.line(lower, fill=INK, width=4, joint="curve")
        self.draw.line((lower[-1], upper[0]), fill=INK, width=4)
        self.draw.line((upper[-1], (1118, 658), (1132, 666)),
                       fill=INK, width=4, joint="curve")
        self.draw.line((lower[0], (1077, 716), (1092, 730)),
                       fill=INK, width=4, joint="curve")
        self.draw.polygon(((614, 527), (629, 506), (641, 532)),
                          fill=PAPER, outline=INK, width=3)
        self.draw.ellipse((454, 463, 472, 483), fill=PAPER, outline=INK,
                           width=2)
        self.arrow((594, 420), (517, 343), (470, 465))
        self.arrow((768, 469), (640, 357), (487, 472))
        self.star(464, 474)
        self.draw.line((464, 488, 464, 518, 432, 528), fill=INK, width=2)
        self.draw.line((631, 541, 656, 563), fill=INK, width=2)
        self.tanker(942, 605)
        self.tanker(997, 658, burning=True)
        self.draw.line((1034, 708, 1057, 677), fill=INK, width=2)
        self.single("IRAN", (719, 374, 1040, 407), maximum=30,
                    minimum=30, color=RED, label="map_iran", backing=True)
        self.single("PERSIAN GULF", (238, 413, 463, 441),
                    maximum=25, minimum=23, label="map_gulf", backing=True)
        self.single("BAHRAIN", (342, 534, 549, 566),
                    maximum=28, minimum=28, color=RED,
                    label="map_bahrain", backing=True)
        self.single("SAUDI ARABIA", (141, 611, 467, 646),
                    maximum=29, minimum=28, label="map_saudi", backing=True)
        self.single("QATAR", (654, 570, 848, 605), maximum=28,
                    minimum=28, label="map_qatar", backing=True)
        self.single("STRAIT OF HORMUZ", (808, 733, 1160, 754),
                    maximum=23, minimum=23, label="map_strait", backing=True)
        self.single("SCHEMATIC · NOT TO SCALE", (66, 725, 535, 746),
                    kind="sans", maximum=18, minimum=18, label="map_note")

    def lead(self):
        self.single("MIDDLE EAST · LEAD REPORT", (LEFT, 220, RIGHT, 242),
                    maximum=21, minimum=21, color=RED)
        self.single(LEAD_HEADLINE, (LEFT, 249, RIGHT, 323),
                    maximum=92, minimum=86, align="center", label="lead_title")
        self.rule(335, width=6, color=RED)
        self.gulf_map()
        self.draw.line((1186, 355, 1186, 748), fill=INK, width=2)
        self.block(LEAD_DECK, (1220, 356, RIGHT, 422),
                   kind="serif_bold", maximum=31, minimum=28, gap=5,
                   label="lead_deck")
        fact_box = (1238, 441, RIGHT, 746)
        for size in range(27, 23, -1):
            face = font("sans", size)
            layouts = [
                line_layout(text, face, fact_box[2] - fact_box[0], 4)
                for text in LEAD_FACTS
            ]
            if all(layouts) and sum(item[2] for item in layouts) + 40 <= 305:
                y = fact_box[1]
                for index, (text, layout) in enumerate(zip(LEAD_FACTS, layouts)):
                    self.draw.rectangle((1220, y + 6, 1227, y + 13), fill=INK)
                    lines, line_height, height = layout
                    for line_index, line in enumerate(lines):
                        line_y = y + line_index * (line_height + 4)
                        self.line(line, face,
                                  (fact_box[0], line_y, fact_box[2],
                                   line_y + line_height),
                                  label="lead_fact_" + str(index))
                    y += height + 10
                break
        else:
            raise ValueError("Lead facts do not fit.")
        self.rule(770, width=3)

    def passport(self, x):
        self.draw.rounded_rectangle((x + 30, 800, x + 119, 879), radius=5,
                                    fill=PAPER, outline=INK, width=4)
        self.draw.ellipse((x + 53, 814, x + 96, 857), outline=INK, width=3)
        self.draw.arc((x + 63, 814, x + 86, 857), 0, 360, fill=INK, width=2)
        self.draw.line((x + 53, 835, x + 96, 835), fill=INK, width=2)
        self.draw.line((x + 49, 868, x + 101, 868), fill=INK, width=3)
        self.draw.line((x + 27, 796, x + 124, 882), fill=RED, width=7)
        self.draw.line((x + 124, 796, x + 27, 882), fill=RED, width=7)

    def climate(self, x):
        cx, cy = x + 65, 839
        for index in range(8):
            angle = index * math.pi / 4
            self.draw.line((cx + 34 * math.cos(angle), cy + 34 * math.sin(angle),
                            cx + 45 * math.cos(angle), cy + 45 * math.sin(angle)),
                           fill=INK, width=3)
        self.draw.ellipse((cx - 27, cy - 27, cx + 27, cy + 27),
                           fill=PAPER, outline=INK, width=4)
        self.draw.ellipse((cx - 12, cy - 27, cx + 12, cy + 27),
                           outline=INK, width=2)
        self.draw.line((cx - 27, cy, cx + 27, cy), fill=INK, width=2)
        self.draw.rounded_rectangle((x + 119, 802, x + 136, 866), radius=8,
                                    fill=PAPER, outline=INK, width=3)
        self.draw.ellipse((x + 112, 855, x + 143, 884),
                           fill=PAPER, outline=INK, width=3)
        self.draw.line((x + 127, 826, x + 127, 868), fill=INK, width=5)
        self.draw.ellipse((x + 120, 861, x + 135, 876), fill=INK)
        for y in (816, 833, 850):
            self.draw.line((x + 140, y, x + 151, y), fill=INK, width=2)

    def handcuffs(self, x):
        for cx in (x + 59, x + 143):
            self.draw.ellipse((cx - 31, 810, cx + 31, 874),
                               outline=INK, width=8)
            self.draw.rectangle((cx - 13, 802, cx + 13, 818), fill=INK)
        self.draw.line((x + 88, 842, x + 99, 848, x + 113, 842),
                       fill=INK, width=7, joint="curve")

    def medium(self):
        for index, story in enumerate(MEDIUM):
            x = LEFT + index * 656
            right = x + 624
            if index:
                self.draw.line((x - 16, 793, x - 16, 1067), fill=INK, width=2)
            (self.passport, self.climate, self.handcuffs)[index](x)
            self.single(story[2], (x + 186, 807, right - 20, 834),
                        maximum=22, minimum=22, color=RED)
            self.single(story[3], (x + 186, 842, right - 20, 866),
                        kind="sans", maximum=21, minimum=21)
            self.block(story[1], (x + 20, 895, right - 20, 975),
                       kind="sans_bold", maximum=40, minimum=38, gap=4,
                       label="medium_title_" + str(index))
            self.block(story[4], (x + 20, 987, right - 20, 1068),
                       maximum=25, minimum=23, gap=4,
                       label="medium_body_" + str(index))
        self.rule(1080, width=3)

    def timeline(self):
        self.draw.rectangle((LEFT, 1092, RIGHT, 1222), fill=INK)
        self.single("THE DAY IN UTC", (LEFT + 10, 1100, RIGHT - 10, 1122),
                    maximum=22, minimum=22, color=PAPER, label="timeline_title")
        cell_width = (RIGHT - LEFT) / 8
        for index, (time, detail) in enumerate(TIMELINE):
            x = LEFT + index * cell_width
            if index:
                self.draw.line((x, 1128, x, 1213), fill=PAPER, width=1)
            self.single(time, (x + 10, 1128, x + cell_width - 10, 1149),
                        maximum=20, minimum=19, color=PAPER,
                        label="timeline_time_" + str(index))
            self.block(detail, (x + 10, 1151, x + cell_width - 10, 1217),
                       maximum=21, minimum=19, gap=3, color=PAPER,
                       label="timeline_item_" + str(index))

    def briefs(self):
        for column, (region, stories) in enumerate(BRIEFS):
            x = LEFT + column * 492
            right = x + 460
            if column:
                self.draw.line((x - 16, 1242, x - 16, 1962),
                               fill=INK, width=2)
            self.single(region, (x, 1245, right, 1270),
                        maximum=23, minimum=21, color=RED,
                        label="region_" + str(column))
            self.rule(1277, width=2, x0=x, x1=right)
            for row, (headline, detail) in enumerate(stories):
                y = 1290 + row * 96
                tag = "brief_" + str(column * 7 + row)
                self.single(headline, (x, y + 3, right, y + 33),
                            kind="serif_bold", maximum=29, minimum=21,
                            label=tag + "_title")
                self.block(detail, (x, y + 38, right, y + 88),
                           maximum=24, minimum=23, gap=4,
                           label=tag + "_body")
                if row < 6:
                    self.rule(y + 94, width=1, x0=x, x1=right)

    def footer(self):
        self.rule(1980, width=5)
        self.rule(1988, width=1)
        self.single(FOOTER, (LEFT, 2010, RIGHT, 2038),
                    kind="serif", maximum=25, minimum=24,
                    align="center", label="footer")

    def validate(self):
        headlines = [LEAD_HEADLINE] + [story[0] for story in MEDIUM]
        headlines += [headline for _, stories in BRIEFS
                      for headline, _ in stories]
        if len(headlines) != 32 or len(set(headlines)) != 32:
            raise ValueError("The page must contain exactly 32 distinct stories.")
        if len(BRIEFS) != 4 or any(len(stories) != 7 for _, stories in BRIEFS):
            raise ValueError("The briefs must form four columns of seven.")
        if len(TIMELINE) != 8:
            raise ValueError("The timeline must contain eight items.")
        for index, (label, text, bounds, _) in enumerate(self.text_bounds):
            x0, y0, x1, y1 = bounds
            if not (0 <= x0 < x1 <= SIZE and 0 <= y0 < y1 <= SIZE):
                raise ValueError("Text lies outside the page: " + text)
            for other_label, other_text, other, _ in self.text_bounds[index + 1:]:
                if (max(x0, other[0]) < min(x1, other[2])
                        and max(y0, other[1]) < min(y1, other[3])):
                    raise ValueError(
                        "Text overlap: " + label + " / " + other_label
                        + ": " + text + " / " + other_text
                    )

    def render(self):
        self.masthead()
        self.lead()
        self.medium()
        self.timeline()
        self.briefs()
        self.footer()
        self.validate()
        return self.image.resize((FINAL_SIZE, FINAL_SIZE), Image.Resampling.LANCZOS)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default="entry.png",
                        help="PNG filename in the renderer's directory.")
    args = parser.parse_args()
    destination = (ROOT / args.output).absolute()
    if destination.parent != ROOT or destination.suffix.lower() != ".png":
        parser.error("--output must name a PNG in this directory.")
    page = FrontPage()
    image = page.render()
    image.save(destination, format="PNG", optimize=True, compress_level=9)
    byte_count = destination.stat().st_size
    if byte_count > MAX_BYTES:
        raise ValueError("PNG exceeds one mebibyte: " + str(byte_count))
    smallest_headline = min(
        size for label, _, _, size in page.text_bounds
        if label.startswith("brief_") and label.endswith("_title")
    )
    print(
        str(destination) + ": 1024 x 1024 PNG, " + str(byte_count)
        + " bytes; 32 stories; no text overlaps; smallest brief headline "
        + str(smallest_headline) + " px at drawing scale."
    )


if __name__ == "__main__":
    main()
