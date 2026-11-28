"""สร้างกราฟ Q1–Q3 จากผลลัพธ์ query ใน storage/query_results/ → docs/charts/*.png

รัน:  python visualization/make_charts.py
ต้องใช้ matplotlib (pip install matplotlib)
"""
from __future__ import annotations

import csv
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib import font_manager  # noqa: E402
from matplotlib.patches import Patch  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "storage" / "query_results"
OUT = ROOT / "docs" / "charts"

# ---- palette (categorical slots ตามลำดับคงที่ + สีข้อความ/เส้นกริด) ----
BLUE = "#257de0"     # series 1
ORANGE = "#f47230"   # series 2
NEUTRAL = "#b5b5b5"  # baseline / กลุ่มเปรียบเทียบ
TEXT = "#191919"
TEXT_2 = "#666666"
GRID = "#e6e6e6"


def setup_font() -> None:
    """เลือกฟอนต์ที่มีอักษรไทย (Windows: Tahoma / Leelawadee, Linux/Mac: Sarabun/Noto)"""
    candidates = ["Tahoma", "Leelawadee UI", "Leelawadee", "TH Sarabun New",
                  "Sarabun", "Noto Sans Thai", "Thonburi"]
    available = {f.name for f in font_manager.fontManager.ttflist}
    family = next((c for c in candidates if c in available), "DejaVu Sans")
    plt.rcParams.update({
        "font.family": family,
        "font.size": 10,
        "text.color": TEXT,
        "axes.labelcolor": TEXT_2,
        "axes.edgecolor": GRID,
        "axes.titlesize": 12,
        "axes.titleweight": "bold",
        "axes.titlelocation": "left",
        "xtick.color": TEXT_2,
        "ytick.color": TEXT_2,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "figure.facecolor": "white",
        "savefig.dpi": 200,
    })


def read(name: str) -> list[dict]:
    path = next(RESULTS.glob(f"{name}_*.csv"))
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def style_axis(ax, axis: str = "x") -> None:
    ax.grid(axis=axis, color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    ax.tick_params(length=0)


def footer(fig, text: str) -> None:
    fig.text(0.01, 0.005, text, ha="left", va="bottom", fontsize=8, color=TEXT_2)


# --------------------------------------------------------------------------
# Q1: จำนวนหมู่บ้านที่ถูกรายงานรายอำเภอ 2566 vs 2567
# --------------------------------------------------------------------------
def chart_q1() -> Path:
    rows = read("q1_1")
    rows.sort(key=lambda r: float(r["villages_2566"]) + float(r["villages_2567"]))
    names = [r["district"] for r in rows]
    v66 = [float(r["villages_2566"]) for r in rows]
    v67 = [float(r["villages_2567"]) for r in rows]

    fig, ax = plt.subplots(figsize=(9, 10))
    y = range(len(rows))
    h = 0.38
    ax.barh([i + h / 2 + 0.01 for i in y], v66, height=h, color=BLUE, label="ปี 2566")
    ax.barh([i - h / 2 - 0.01 for i in y], v67, height=h, color=ORANGE, label="ปี 2567")
    for i, (a, b) in enumerate(zip(v66, v67)):
        ax.text(a + 1.5, i + h / 2, f"{a:.0f}", va="center", fontsize=7.5, color=TEXT_2)
        ax.text(b + 1.5, i - h / 2, f"{b:.0f}", va="center", fontsize=7.5, color=TEXT_2)
    ax.set_yticks(list(y), names)
    ax.set_xlabel("จำนวนหมู่บ้านที่ถูกรายงานว่าเกิดอุทกภัย")
    ax.set_ylim(-0.6, len(rows) - 0.4)
    style_axis(ax, "x")
    ax.legend(loc="lower right", frameon=False, ncols=2)
    fig.suptitle("Q1  จำนวนหมู่บ้านที่ถูกรายงานว่าเกิดอุทกภัย รายอำเภอ ปี 2566 เทียบ 2567",
                 x=0.01, y=0.99, ha="left", fontsize=13, fontweight="bold")
    fig.text(0.01, 0.952, "เรียงตามผลรวมสองปี · ปี 2566 รายงานไม่ครบ (1,198 รายงาน เทียบ 3,556 ในปี 2567) "
             "จึงเทียบตัวเลขตรง ๆ ไม่ได้", fontsize=8.5, color=TEXT_2)
    footer(fig, "ที่มา: storage/query_results/q1_1_district_flood_reports_by_year.csv (ปภ. dpm-gd027)")
    fig.tight_layout(rect=(0, 0.02, 1, 0.945))
    out = OUT / "q1_district_flood_reports_by_year.png"
    fig.savefig(out)
    plt.close(fig)
    return out


# --------------------------------------------------------------------------
# Q2: สัดส่วนหมู่บ้านที่ถูกรายงาน ตามภูมิศาสตร์ และ quartile ประชากร/รายได้
# --------------------------------------------------------------------------
def chart_q2() -> Path:
    geo = {(r["feature"].split(" ")[0], r["flag"]): r for r in read("q2_1")}
    quart = read("q2_2")

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 5.2), gridspec_kw={"width_ratios": [1, 1.4]})

    # (ก) ติดแม่น้ำ / ติดภูเขา
    features = [("river", "ติดแม่น้ำ/ลำน้ำ"), ("mountain", "ติดภูเขา")]
    w = 0.36
    for i, (key, label) in enumerate(features):
        no, yes = geo[(key, "0")], geo[(key, "1")]
        for dx, r, color in ((-w / 2 - 0.01, no, NEUTRAL), (w / 2 + 0.01, yes, BLUE)):
            pct = float(r["pct_flooded"])
            ax1.bar(i + dx, pct, width=w, color=color)
            ax1.text(i + dx, pct + 1.2, f"{pct:.1f}%", ha="center", fontsize=9)
            ax1.text(i + dx, 3, f"n={int(r['villages']):,}", ha="center", fontsize=7.5,
                     color="white" if color == BLUE else TEXT)
        diff = float(yes["pct_flooded"]) - float(no["pct_flooded"])
        ax1.text(i, 99, f"+{diff:.1f} จุด", ha="center", fontsize=9, color=TEXT_2)
    ax1.set_xticks(range(len(features)), [f[1] for f in features])
    ax1.set_ylim(0, 105)
    ax1.set_ylabel("% หมู่บ้านที่ถูกรายงาน (2566–2567)")
    style_axis(ax1, "y")
    ax1.legend(handles=[Patch(color=NEUTRAL, label="ไม่ติด"), Patch(color=BLUE, label="ติด")],
               loc="lower center", bbox_to_anchor=(0.5, -0.22), ncols=2, frameon=False)
    ax1.set_title("(ก) ลักษณะภูมิศาสตร์")

    # (ข) quartile ประชากร / รายได้
    dims = [("population", "ประชากร", BLUE), ("avg_household_income", "รายได้ครัวเรือนเฉลี่ย", ORANGE)]
    for j, (key, label, color) in enumerate(dims):
        rs = sorted((r for r in quart if r["dimension"] == key), key=lambda r: int(r["quartile"]))
        xs = [int(r["quartile"]) - 1 + (j - 0.5) * (w + 0.02) for r in rs]
        pcts = [float(r["pct_flooded"]) for r in rs]
        ax2.bar(xs, pcts, width=w, color=color, label=label)
        for x, p in zip(xs, pcts):
            ax2.text(x, p + 1.2, f"{p:.1f}", ha="center", fontsize=8.5)
    ax2.set_xticks(range(4), ["Q1\n(ต่ำสุด)", "Q2", "Q3", "Q4\n(สูงสุด)"])
    ax2.set_ylim(0, 105)
    style_axis(ax2, "y")
    ax2.legend(loc="lower center", bbox_to_anchor=(0.5, -0.22), ncols=2, frameon=False)
    ax2.set_title("(ข) quartile ประชากร และรายได้")

    fig.suptitle("Q2  สัดส่วนหมู่บ้านที่ถูกรายงานว่าเกิดอุทกภัย แยกตามลักษณะหมู่บ้าน",
                 x=0.01, ha="left", fontsize=13, fontweight="bold")
    fig.text(0.01, 0.905, "รายได้จับคู่กับหมู่บ้านได้ 67% (1,446 หมู่บ้าน) · เป็นความสัมพันธ์เชิงพรรณนา ไม่ใช่เหตุและผล",
             fontsize=8.5, color=TEXT_2)
    footer(fig, "ที่มา: storage/query_results/q2_1_geography_vs_flood.csv, q2_2_population_income_vs_flood.csv")
    fig.tight_layout(rect=(0, 0.03, 1, 0.9))
    out = OUT / "q2_village_features_vs_flood.png"
    fig.savefig(out)
    plt.close(fig)
    return out


# --------------------------------------------------------------------------
# Q3: หมู่บ้าน/อำเภอที่ได้ลำดับความสำคัญสูงสุด
# --------------------------------------------------------------------------
def chart_q3() -> Path:
    villages = read("q3_1")[:15]
    districts = read("q3_2")[:10]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 7), gridspec_kw={"width_ratios": [1.25, 1]})

    # (ก) หมู่บ้าน 15 อันดับแรก ตาม priority_score
    villages = villages[::-1]
    labels = [f"{int(v['priority_rank'])}. {v['village_name']} ({v['district_name']})" for v in villages]
    scores = [float(v["priority_score"]) for v in villages]
    has_income = [v["income_available"] == "1" for v in villages]
    for i, (s, ok) in enumerate(zip(scores, has_income)):
        ax1.barh(i, s, height=0.7, color=BLUE if ok else "white", edgecolor=BLUE,
                 hatch=None if ok else "////", linewidth=1)
        ax1.text(s + 0.005, i, f"{s:.3f}", va="center", fontsize=8, color=TEXT_2)
    ax1.set_yticks(range(len(villages)), labels)
    ax1.set_xlim(0, 1.08)
    ax1.set_xticks([0, 0.25, 0.5, 0.75, 1.0])
    ax1.set_xlabel("คะแนนจัดลำดับ (0–1)")
    style_axis(ax1, "x")
    ax1.legend(handles=[Patch(facecolor=BLUE, label="มีข้อมูลรายได้"),
                        Patch(facecolor="white", edgecolor=BLUE, hatch="////",
                              label="ไม่มีข้อมูลรายได้ (ใช้ค่ากลาง 0.5)")],
               loc="lower center", bbox_to_anchor=(0.4, -0.16), ncols=2, frameon=False, fontsize=8.5)
    ax1.set_title("(ก) หมู่บ้าน 15 อันดับแรก")

    # (ข) อำเภอ 10 อันดับแรก: อันดับตามสัดส่วนหมู่บ้านที่ถูกรายงาน และตามครัวเรือนที่เสียหาย
    districts = districts[::-1]
    r_flood = [int(d["rank_by_flood_share"]) for d in districts]
    r_dmg = [int(d["rank_by_damage"]) for d in districts]
    # อันดับเท่ากัน → เลื่อนจุดขึ้น/ลงเล็กน้อยไม่ให้ทับกัน
    tie = [0.14 if a == b else 0 for a, b in zip(r_flood, r_dmg)]
    for i, (a, b) in enumerate(zip(r_flood, r_dmg)):
        ax2.plot([a, b], [i, i], color=GRID, linewidth=2.5, zorder=1)
        if a == b:
            ax2.text(a + 0.9, i, "เท่ากัน", va="center", ha="right", fontsize=8, color=TEXT_2)
    ax2.scatter(r_flood, [i + t for i, t in enumerate(tie)], s=70, color=BLUE, zorder=2,
                edgecolor="white", linewidth=2, label="อันดับ % หมู่บ้านที่ถูกรายงาน")
    ax2.scatter(r_dmg, [i - t for i, t in enumerate(tie)], s=70, color=ORANGE, zorder=3,
                edgecolor="white", linewidth=2, label="อันดับครัวเรือนเสียหาย 2563–2567")
    ax2.set_yticks(range(len(districts)),
                   [f"{10 - i}. {d['district_name']}" for i, d in enumerate(districts)])
    ax2.set_xlim(25.5, 0)  # อันดับ 1 อยู่ขวา
    ax2.set_xticks([1, 5, 10, 15, 20, 25])
    ax2.set_xlabel("อันดับจาก 25 อำเภอ (ขวา = สำคัญกว่า)")
    style_axis(ax2, "x")
    ax2.legend(loc="lower center", bbox_to_anchor=(0.5, -0.16), ncols=2, frameon=False, fontsize=8.5)
    ax2.set_title("(ข) อำเภอ 10 อันดับแรก (เรียงตามผลรวมสองอันดับ)")

    fig.suptitle("Q3  หมู่บ้านและอำเภอที่ควรได้รับความช่วยเหลือก่อน",
                 x=0.01, ha="left", fontsize=13, fontweight="bold")
    fig.text(0.01, 0.915, "คะแนนหมู่บ้าน = ความถี่ที่ถูกรายงาน 50% + จำนวนครัวเรือน 30% + รายได้ต่ำ 20% "
             "(percent rank) · ลำดับคงที่เมื่อเปลี่ยนน้ำหนัก (rank corr. 0.83–0.96)",
             fontsize=8.5, color=TEXT_2)
    footer(fig, "ที่มา: storage/query_results/q3_1_aid_priority_villages.csv, q3_2_aid_priority_districts.csv")
    fig.tight_layout(rect=(0, 0.03, 1, 0.91))
    out = OUT / "q3_aid_priority.png"
    fig.savefig(out)
    plt.close(fig)
    return out


# --------------------------------------------------------------------------
# CLD: สถานะของแต่ละลูกศรเมื่อเทียบกับข้อค้นพบ (รายละเอียดใน docs/07 หัวข้อ 7.6)
# --------------------------------------------------------------------------
# สถานะ → (สี, รูปแบบเส้น, ความหนา, ชื่อ) — แยกด้วยรูปแบบเส้นด้วย ไม่ใช้สีอย่างเดียว
STATUS = {
    "yes":     ("#0aac23", "-",          2.6, "ยืนยัน"),
    "partial": ("#d28e05", (0, (6, 2)),  2.2, "ยืนยันบางส่วน"),
    "no":      ("#dc3c3d", (0, (1.5, 2)), 2.4, "ไม่ได้รับการยืนยัน"),
    "nodata":  ("#9c9c9c", (0, (4, 3)),  1.4, "ข้อมูลไม่พอ"),
}

CLD_NODES = {
    "river":   (1.3, 8.6, "ติดแม่น้ำ/ลำน้ำ"),
    "mount":   (1.3, 6.6, "ติดภูเขา"),
    "pop":     (1.3, 4.2, "ประชากร /\nจำนวนครัวเรือน"),
    "income":  (1.3, 1.4, "รายได้ครัวเรือน"),
    "report":  (5.0, 10.2, "ความครบถ้วน\nของการรายงาน"),
    "flood":   (5.0, 7.6, "การเกิดอุทกภัย\n(ที่ถูกรายงาน)"),
    "damage":  (5.7, 4.6, "ความเสียหาย /\nครัวเรือนได้รับผลกระทบ"),
    "recover": (5.7, 1.4, "การฟื้นตัว"),
    "need":    (9.0, 6.1, "ความต้องการ\nความช่วยเหลือ"),
    "aid":     (9.0, 2.6, "ความช่วยเหลือ\nที่ได้รับ"),
}

# (id, จาก, ไป, ขั้ว, สถานะ, ความโค้ง)
CLD_LINKS = [
    ("L1", "river", "flood", "+", "yes", -0.08),
    ("L2", "mount", "flood", "+", "partial", 0.0),
    ("L3", "pop", "flood", "+", "partial", -0.2),
    ("L4", "income", "flood", "−", "no", -0.1),
    ("L5", "report", "flood", "+", "nodata", 0.0),
    ("L6", "flood", "damage", "+", "yes", 0.0),
    ("L7", "pop", "damage", "+", "nodata", 0.1),
    ("L8", "income", "damage", "−", "nodata", -0.1),
    ("L9", "flood", "need", "+", "nodata", -0.12),
    ("L10", "damage", "need", "+", "nodata", 0.12),
    ("L11", "need", "aid", "+", "nodata", 0.0),
    ("L12", "aid", "recover", "+", "nodata", 0.0),
    ("L13", "recover", "need", "−", "nodata", 0.28),
    ("L14", "damage", "recover", "−", "nodata", 0.55),
    ("L15", "recover", "damage", "−", "nodata", 0.55),
    ("L16", "income", "recover", "+", "nodata", 0.0),
]


def chart_cld() -> Path:
    from matplotlib.lines import Line2D
    from matplotlib.patches import FancyArrowPatch

    fig, ax = plt.subplots(figsize=(10.5, 11))
    ax.set_xlim(0.1, 10.3)
    ax.set_ylim(0.6, 10.9)
    ax.set_aspect("equal")
    ax.axis("off")

    boxes = {}
    for key, (x, y, label) in CLD_NODES.items():
        t = ax.text(x, y, label, ha="center", va="center", fontsize=10.5, zorder=3,
                    bbox=dict(boxstyle="round,pad=0.55", facecolor="white", edgecolor="#8a8a8a",
                              linewidth=1.1))
        boxes[key] = t
    fig.canvas.draw()  # ให้ bbox ของกล่องมีขนาดจริงก่อนตัดปลายลูกศร

    for lid, a, b, sign, status, rad in CLD_LINKS:
        color, ls, lw, _ = STATUS[status]
        (x1, y1, _), (x2, y2, _) = CLD_NODES[a], CLD_NODES[b]
        arrow = FancyArrowPatch((x1, y1), (x2, y2), connectionstyle=f"arc3,rad={rad}",
                                arrowstyle="-|>,head_length=7,head_width=4", mutation_scale=1,
                                color=color, linestyle=ls, linewidth=lw, zorder=2,
                                patchA=boxes[a].get_bbox_patch(), patchB=boxes[b].get_bbox_patch(),
                                shrinkA=3, shrinkB=3)
        ax.add_patch(arrow)
        # ป้ายกลางเส้นโค้ง (จุดกึ่งกลางของ quadratic bezier แบบ arc3)
        mx = (x1 + x2) / 2 + 0.5 * rad * (y2 - y1)
        my = (y1 + y2) / 2 - 0.5 * rad * (x2 - x1)
        ax.text(mx, my, f"{lid} {sign}", ha="center", va="center", fontsize=8.5, zorder=4,
                color=TEXT, fontweight="bold",
                bbox=dict(boxstyle="round,pad=0.2", facecolor="white", edgecolor=color, linewidth=1))

    # ป้ายวงป้อนกลับ
    ax.text(7.55, 3.75, "B1\nวงสมดุล", ha="center", va="center", fontsize=9, color=TEXT_2)
    ax.text(5.7, 3.0, "R1\nวงเสริมแรง", ha="center", va="center", fontsize=9, color=TEXT_2)

    handles = [Line2D([0], [0], color=c, linestyle=ls, linewidth=lw, label=name)
               for c, ls, lw, name in STATUS.values()]
    ax.legend(handles=handles, loc="upper center", bbox_to_anchor=(0.5, 0.0), ncols=4,
              frameon=False, fontsize=10, handlelength=3.2)

    fig.suptitle("CLD  ลูกศรไหนข้อมูลยืนยัน ลูกศรไหนไม่ยืนยัน และลูกศรไหนข้อมูลยังไม่พอ",
                 x=0.02, y=0.985, ha="left", fontsize=13, fontweight="bold")
    fig.text(0.02, 0.93, "+ = เปลี่ยนทิศเดียวกัน, − = เปลี่ยนทิศตรงข้าม · หลักฐานของแต่ละเส้นอยู่ใน docs/07 หัวข้อ 7.6\n"
             "B1 = ความต้องการ → ความช่วยเหลือ → การฟื้นตัว → ความต้องการ · "
             "R1 = ความเสียหาย → การฟื้นตัว → ความเสียหาย (ครั้งถัดไป)",
             fontsize=8.5, color=TEXT_2, linespacing=1.6)
    fig.tight_layout(rect=(0, 0.03, 1, 0.92))
    out = OUT / "cld_evidence_status.png"
    fig.savefig(out)
    plt.close(fig)
    return out


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    setup_font()
    for fn in (chart_q1, chart_q2, chart_q3, chart_cld):
        print(f"[OK] {fn().relative_to(ROOT)}")


if __name__ == "__main__":
    main()
