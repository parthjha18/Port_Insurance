"""
Generate two realistic sample Indian health insurance policy PDFs for testing.

Policy 1: Star Health and Allied Insurance — existing policy (old insurer)
Policy 2: HDFC ERGO General Insurance — target policy (new insurer)

Run from project root:
    python scripts/generate_sample_pdfs.py
"""

from __future__ import annotations

import os
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm, mm
from reportlab.platypus import (
    HRFlowable,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

OUTPUT_DIR = Path("sample_pdfs")
OUTPUT_DIR.mkdir(exist_ok=True)

# ─── Color palette ────────────────────────────────────────────────────────────
DARK_BLUE = colors.HexColor("#1E3A5F")
MID_BLUE = colors.HexColor("#2E6DA4")
LIGHT_BLUE = colors.HexColor("#D6E8F7")
ORANGE = colors.HexColor("#E07B2A")
GREY_BG = colors.HexColor("#F5F5F5")
DARK_GREY = colors.HexColor("#333333")
MID_GREY = colors.HexColor("#666666")
GREEN = colors.HexColor("#2A7A3B")
RED_DARK = colors.HexColor("#8B1A1A")
WHITE = colors.white

PAGE_W, PAGE_H = A4

# ─── Styles ───────────────────────────────────────────────────────────────────
base = getSampleStyleSheet()

H1 = ParagraphStyle(
    "H1", fontSize=20, textColor=WHITE, fontName="Helvetica-Bold",
    alignment=TA_CENTER, leading=26,
)
H2 = ParagraphStyle(
    "H2", fontSize=13, textColor=DARK_BLUE, fontName="Helvetica-Bold",
    spaceAfter=4, leading=18,
)
H3 = ParagraphStyle(
    "H3", fontSize=10, textColor=MID_BLUE, fontName="Helvetica-Bold",
    spaceAfter=2, leading=14,
)
BODY = ParagraphStyle(
    "BODY", fontSize=9, textColor=DARK_GREY, fontName="Helvetica",
    leading=13, spaceAfter=4,
)
SMALL = ParagraphStyle(
    "SMALL", fontSize=8, textColor=MID_GREY, fontName="Helvetica", leading=11,
)
DISCLAIMER = ParagraphStyle(
    "DISCLAIMER", fontSize=7.5, textColor=MID_GREY, fontName="Helvetica-Oblique",
    leading=10, alignment=TA_CENTER,
)
CENTER_BODY = ParagraphStyle(
    "CENTER_BODY", fontSize=9, textColor=DARK_GREY, fontName="Helvetica",
    alignment=TA_CENTER, leading=13,
)
LABEL = ParagraphStyle(
    "LABEL", fontSize=8, textColor=MID_GREY, fontName="Helvetica", leading=11,
)
VALUE = ParagraphStyle(
    "VALUE", fontSize=9, textColor=DARK_GREY, fontName="Helvetica-Bold", leading=13,
)


def hr(color=MID_BLUE, thickness=1) -> HRFlowable:
    return HRFlowable(width="100%", thickness=thickness, color=color, spaceAfter=6, spaceBefore=6)


def section_header(title: str) -> list:
    return [
        Spacer(1, 8),
        Paragraph(title, H2),
        hr(MID_BLUE, 0.8),
    ]


def two_col_table(rows: list[tuple[str, str]], label_width=7 * cm) -> Table:
    data = [
        [Paragraph(k, LABEL), Paragraph(v, VALUE)]
        for k, v in rows
    ]
    t = Table(data, colWidths=[label_width, PAGE_W - 4 * cm - label_width])
    t.setStyle(TableStyle([
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [WHITE, GREY_BG]),
        ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#DDDDDD")),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]))
    return t


def benefit_table(rows: list[tuple[str, str, str]], header=("Benefit", "Coverage", "Limit/Notes")) -> Table:
    header_row = [Paragraph(h, ParagraphStyle("TH", fontSize=9, textColor=WHITE,
                                               fontName="Helvetica-Bold", alignment=TA_CENTER))
                  for h in header]
    data = [header_row]
    for row in rows:
        data.append([Paragraph(c, BODY) for c in row])
    col_w = [(PAGE_W - 4 * cm) / 3] * 3
    t = Table(data, colWidths=col_w)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), DARK_BLUE),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, GREY_BG]),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#CCCCCC")),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    return t


def header_banner(insurer: str, tagline: str, accent: colors.Color) -> Table:
    inner = Table(
        [[Paragraph(insurer, H1)], [Paragraph(tagline, ParagraphStyle(
            "TAG", fontSize=10, textColor=WHITE, fontName="Helvetica-Oblique",
            alignment=TA_CENTER))]],
        colWidths=[PAGE_W - 4 * cm],
    )
    inner.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), accent),
        ("TOPPADDING", (0, 0), (-1, -1), 12),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
    ]))
    return inner


# ═══════════════════════════════════════════════════════════════════════════════
# POLICY 1  —  Star Health and Allied Insurance
# ═══════════════════════════════════════════════════════════════════════════════

def build_star_health_pdf():
    out = OUTPUT_DIR / "star_health_comprehensive_policy.pdf"
    doc = SimpleDocTemplate(str(out), pagesize=A4,
                            leftMargin=2*cm, rightMargin=2*cm,
                            topMargin=2*cm, bottomMargin=2*cm)
    story = []

    # Banner
    story.append(header_banner(
        "Star Health and Allied Insurance Co. Ltd.",
        "Comprehensive Health Insurance Policy — Individual & Family",
        accent=colors.HexColor("#C0392B"),
    ))
    story.append(Spacer(1, 10))

    # Registration info
    story.append(Paragraph(
        "IRDAI Reg. No.: 129  |  CIN: L66010TN2005PLC056649  |  "
        "Registered Office: No. 1, New Tank Street, Valluvarkottam High Road, Nungambakkam, Chennai – 600034",
        SMALL,
    ))
    story.append(hr())

    # ── Policy Schedule ────────────────────────────────────────────────────────
    story += section_header("POLICY SCHEDULE")
    story.append(two_col_table([
        ("Policy Number", "SH/2021/HLTH/001234/00/000"),
        ("Policy Type", "Individual Health Insurance — Comprehensive Plan"),
        ("Policyholder Name", "Mr. Rajesh Kumar"),
        ("Date of Birth", "14th March 1987  (Age: 37 Years)"),
        ("Nominee", "Mrs. Sunita Kumar  (Relationship: Spouse)"),
        ("Policy Commencement Date", "01st April 2021"),
        ("Policy Expiry Date", "31st March 2025"),
        ("Policy Tenure", "4 Years (Continuously Renewed)"),
        ("Sum Insured", "Rs. 5,00,000 (Rupees Five Lakhs Only)"),
        ("Annual Premium", "Rs. 12,480 (including 18% GST)"),
        ("Premium Payment Mode", "Annual"),
        ("Policy Status", "Active"),
        ("Branch", "Mumbai Central Branch — Code: MUM-012"),
    ]))

    # ── Insured Details ────────────────────────────────────────────────────────
    story += section_header("INSURED MEMBER DETAILS")
    data = [
        [Paragraph(h, ParagraphStyle("TH2", fontSize=9, textColor=WHITE,
                                      fontName="Helvetica-Bold", alignment=TA_CENTER))
         for h in ("Member", "Name", "Relation", "DOB", "Age", "Sum Insured")],
        [Paragraph(c, BODY) for c in
         ("1", "Mr. Rajesh Kumar", "Self", "14/03/1987", "37", "Rs. 5,00,000")],
    ]
    t = Table(data, colWidths=[1*cm, 4.5*cm, 2.5*cm, 2.5*cm, 1.5*cm, 3.5*cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#C0392B")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, GREY_BG]),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#CCCCCC")),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
    ]))
    story.append(t)

    # ── Coverage & Benefits ────────────────────────────────────────────────────
    story += section_header("COVERAGE AND BENEFITS")
    story.append(benefit_table([
        ("In-patient Hospitalisation", "Covered", "Up to Sum Insured (Rs. 5,00,000)"),
        ("Pre-hospitalisation Expenses", "Covered", "Up to 30 days before admission"),
        ("Post-hospitalisation Expenses", "Covered", "Up to 60 days after discharge"),
        ("Day Care Procedures", "Covered", "406 listed day care procedures"),
        ("Room Rent", "Covered with Sub-limit", "Rs. 2,000 per day (Single AC Room)"),
        ("ICU/ICCU Charges", "Covered with Sub-limit", "Rs. 4,000 per day"),
        ("Domiciliary Treatment", "Covered", "Up to Rs. 50,000 per policy year"),
        ("Ayush Treatment", "Covered", "Up to Rs. 25,000 per policy year"),
        ("Ambulance Charges", "Covered", "Rs. 2,500 per hospitalisation"),
        ("Organ Donor Expenses", "Covered", "Up to Rs. 1,00,000"),
        ("Maternity Benefit", "Not Covered", "—"),
        ("New Born Baby Cover", "Not Covered", "—"),
        ("Restoration of Sum Insured", "Covered", "100% once per policy year"),
        ("No Claim Bonus", "Applicable", "10% per claim-free year, max 50%"),
        ("Co-payment", "Applicable", "10% of each and every claim"),
        ("Cumulative Bonus", "Applicable", "10% increase per year up to 50%"),
    ]))

    # ── Waiting Periods ────────────────────────────────────────────────────────
    story += section_header("WAITING PERIOD CLAUSES")
    story.append(two_col_table([
        ("Initial Waiting Period", "30 days from policy commencement date"),
        ("Pre-existing Disease (PED) Waiting Period",
         "36 months (3 years) of continuous coverage"),
        ("Specific Disease Waiting Period",
         "24 months for hernia, cataract, sinusitis, joint replacement, and other listed conditions"),
        ("Maternity Waiting Period", "Not applicable — Maternity not covered under this policy"),
        ("Waiting Period Credit (Years Served)", "3 years, 11 months as of 28th February 2025"),
        ("PED Declared at Inception", "Hypertension (controlled) — disclosed at proposal stage"),
        ("PED Coverage Status",
         "Pre-existing disease waiting period served. PED covered from 01st April 2024 onwards."),
    ]))

    # ── Claim History ─────────────────────────────────────────────────────────
    story += section_header("CLAIM HISTORY (Last 4 Policy Years)")
    claim_data = [
        [Paragraph(h, ParagraphStyle("TH3", fontSize=9, textColor=WHITE,
                                      fontName="Helvetica-Bold", alignment=TA_CENTER))
         for h in ("Claim No.", "Year", "Date of Admission", "Diagnosis", "Claimed Amt.", "Settled Amt.", "Status")],
        [Paragraph(c, SMALL) for c in
         ("SH-CLM-2022-00891", "2022", "12/08/2022", "Acute Appendicitis",
          "Rs. 48,000", "Rs. 43,200", "Settled")],
        [Paragraph(c, SMALL) for c in
         ("SH-CLM-2023-04512", "2023", "—", "—", "—", "—", "Claim-Free Year")],
        [Paragraph(c, SMALL) for c in
         ("SH-CLM-2024-07843", "2024", "—", "—", "—", "—", "Claim-Free Year")],
    ]
    t = Table(claim_data, colWidths=[3.5*cm, 1.5*cm, 2.5*cm, 3.5*cm, 2.2*cm, 2.2*cm, 2*cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#C0392B")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, GREY_BG]),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#CCCCCC")),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
    ]))
    story.append(t)

    # ── No Claim Bonus Statement ───────────────────────────────────────────────
    story += section_header("NO CLAIM BONUS (NCB) STATEMENT")
    story.append(two_col_table([
        ("NCB Structure", "10% of Sum Insured per claim-free year"),
        ("Maximum NCB", "50% of Sum Insured"),
        ("NCB Accrued (Years 2023 & 2024)", "20% of Rs. 5,00,000 = Rs. 1,00,000"),
        ("Effective Sum Insured (with NCB)", "Rs. 6,00,000"),
        ("NCB Portability Status",
         "NCB portability subject to acceptance by new insurer as per IRDAI guidelines"),
    ]))

    # ── Portability Notice ────────────────────────────────────────────────────
    story += section_header("PORTABILITY INFORMATION (IRDAI Guidelines)")
    story.append(Paragraph(
        "As per IRDAI (Health Insurance) Regulations, 2016, the policyholder is entitled to port "
        "this policy to any other insurer offering similar or higher health insurance coverage. "
        "The following conditions apply:", BODY,
    ))
    for point in [
        "Portability request must be submitted to the new insurer at least <b>45 days before</b> the policy renewal date.",
        "The new insurer must accept or reject the portability request within <b>15 working days</b>.",
        "Waiting period credits earned under this policy (initial waiting period and PED waiting period) "
        "shall be carried forward to the new policy as per IRDAI portability norms.",
        "The new insurer may not offer sum insured lower than the existing policy at portability.",
        "No Claim Bonus accrued is subject to portability at the discretion of the new insurer.",
        "This policy's renewal date is <b>01st April 2025</b>. Portability request deadline: <b>15th February 2025</b>.",
    ]:
        story.append(Paragraph(f"• {point}", BODY))

    story.append(Spacer(1, 16))
    story.append(hr(colors.HexColor("#C0392B"), 1.5))
    story.append(Paragraph(
        "DISCLAIMER: This is a sample policy document generated for demonstration purposes. "
        "All figures, policy numbers, and personal details are fictitious. "
        "Star Health and Allied Insurance Co. Ltd. is a registered insurer with IRDAI.",
        DISCLAIMER,
    ))

    doc.build(story)
    print(f"Generated: {out}")
    return out


# ═══════════════════════════════════════════════════════════════════════════════
# POLICY 2  —  HDFC ERGO General Insurance
# ═══════════════════════════════════════════════════════════════════════════════

def build_hdfc_ergo_pdf():
    out = OUTPUT_DIR / "hdfc_ergo_optima_secure_policy.pdf"
    doc = SimpleDocTemplate(str(out), pagesize=A4,
                            leftMargin=2*cm, rightMargin=2*cm,
                            topMargin=2*cm, bottomMargin=2*cm)
    story = []

    # Banner
    story.append(header_banner(
        "HDFC ERGO General Insurance Company Limited",
        "Optima Secure — Comprehensive Individual Health Insurance",
        accent=colors.HexColor("#004B8D"),
    ))
    story.append(Spacer(1, 10))

    story.append(Paragraph(
        "IRDAI Reg. No.: 146  |  CIN: U66030MH2007PLC177117  |  "
        "Registered & Corporate Office: 1st Floor, HDFC House, Backbay Reclamation, "
        "H.T. Parekh Marg, Churchgate, Mumbai – 400020",
        SMALL,
    ))
    story.append(hr(colors.HexColor("#004B8D")))

    # ── Policy Schedule ────────────────────────────────────────────────────────
    story += section_header("POLICY SCHEDULE")
    story.append(two_col_table([
        ("Policy Number", "HDFC-ERGO/OPT-SEC/2025/567890/01"),
        ("Policy Type", "Optima Secure — Individual Health Insurance"),
        ("Policyholder Name", "Mr. Rajesh Kumar"),
        ("Date of Birth", "14th March 1987  (Age: 37 Years)"),
        ("Nominee", "Mrs. Sunita Kumar  (Relationship: Spouse)"),
        ("Policy Commencement Date", "01st April 2025"),
        ("Policy Expiry Date", "31st March 2026"),
        ("Policy Tenure", "1 Year (Portability — Transferred from Star Health)"),
        ("Sum Insured", "Rs. 10,00,000 (Rupees Ten Lakhs Only)"),
        ("Annual Premium", "Rs. 17,960 (including 18% GST)"),
        ("Premium Payment Mode", "Annual"),
        ("Policy Status", "Active"),
        ("Branch", "Mumbai — BKC Branch — Code: HE-MUM-BKC-007"),
        ("Portability Reference", "IRDAI Port Ref: PORT-SH-HDFC-2025-0089234"),
    ]))

    # ── Insured Details ────────────────────────────────────────────────────────
    story += section_header("INSURED MEMBER DETAILS")
    data = [
        [Paragraph(h, ParagraphStyle("TH4", fontSize=9, textColor=WHITE,
                                      fontName="Helvetica-Bold", alignment=TA_CENTER))
         for h in ("Member", "Name", "Relation", "DOB", "Age", "Sum Insured")],
        [Paragraph(c, BODY) for c in
         ("1", "Mr. Rajesh Kumar", "Self", "14/03/1987", "37", "Rs. 10,00,000")],
    ]
    t = Table(data, colWidths=[1*cm, 4.5*cm, 2.5*cm, 2.5*cm, 1.5*cm, 3.5*cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#004B8D")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, GREY_BG]),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#CCCCCC")),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
    ]))
    story.append(t)

    # ── Coverage & Benefits ────────────────────────────────────────────────────
    story += section_header("COVERAGE AND BENEFITS — OPTIMA SECURE")
    story.append(benefit_table([
        ("In-patient Hospitalisation", "Covered", "Up to Sum Insured (Rs. 10,00,000)"),
        ("Pre-hospitalisation Expenses", "Covered", "Up to 60 days before admission"),
        ("Post-hospitalisation Expenses", "Covered", "Up to 90 days after discharge"),
        ("Day Care Procedures", "Covered", "All day care procedures covered"),
        ("Room Rent", "Covered — No Sub-limit", "Any room category including Single Private AC"),
        ("ICU/ICCU Charges", "Covered — No Sub-limit", "Actuals, up to Sum Insured"),
        ("Domiciliary Treatment", "Covered", "Up to Rs. 1,00,000 per policy year"),
        ("Ayush Treatment", "Covered", "Up to Rs. 50,000 per policy year"),
        ("Ambulance Charges", "Covered", "Rs. 5,000 per hospitalisation"),
        ("Air Ambulance", "Covered", "Up to Rs. 2,50,000 per policy year"),
        ("Organ Donor Expenses", "Covered", "Up to Rs. 2,00,000"),
        ("Maternity Benefit", "Covered after 2-year waiting", "Rs. 50,000 normal / Rs. 75,000 C-section"),
        ("New Born Baby Cover", "Covered", "From day 1 up to Rs. 25,000"),
        ("Restoration of Sum Insured", "Covered — Unlimited Times", "100% restoration, unlimited during policy year"),
        ("No Claim Bonus (Super NCB)", "Applicable", "20% per claim-free year, max 100% of SI"),
        ("Co-payment", "Nil", "No co-payment applicable"),
        ("Mental Illness Cover", "Covered", "As per IRDAI Mental Healthcare guidelines"),
        ("OPD Consultations", "Covered", "Up to Rs. 10,000 per policy year"),
        ("Annual Health Check-up", "Covered", "Once per year at network hospitals"),
        ("Second Medical Opinion", "Covered", "For 11 critical illness procedures"),
    ]))

    # ── Waiting Periods ────────────────────────────────────────────────────────
    story += section_header("WAITING PERIOD CLAUSES — PORTABILITY APPLIED")
    story.append(Paragraph(
        "<b>Note:</b> This policy is issued under IRDAI Portability guidelines. "
        "Waiting period credits from the previous insurer (Star Health, Policy No. SH/2021/HLTH/001234/00/000) "
        "have been applied.", BODY,
    ))
    story.append(Spacer(1, 4))
    story.append(two_col_table([
        ("Initial Waiting Period", "Waived — Credit applied from previous policy (4 years served)"),
        ("Pre-existing Disease (PED) Waiting Period",
         "24 months under Optima Secure. Credit of 36 months received from Star Health. "
         "<b>PED fully covered from policy inception (01st April 2025).</b>"),
        ("Specific Disease Waiting Period",
         "12 months. Credit applied. Fully served as of policy commencement."),
        ("Maternity Waiting Period",
         "24 months from policy commencement date (i.e., covered from 01st April 2027). "
         "No portability credit applicable for maternity."),
        ("PED Declared at Inception", "Hypertension (controlled) — Ported from Star Health records"),
        ("PED Coverage Status", "<b>Pre-existing Hypertension fully covered from 01st April 2025.</b>"),
        ("Waiting Period Credit Certificate Reference", "WPC-IRDAI-SH-HDFC-2025-0089234"),
    ]))

    # ── Network Hospitals ─────────────────────────────────────────────────────
    story += section_header("CASHLESS FACILITY — NETWORK HOSPITALS")
    story.append(Paragraph(
        "Cashless hospitalisation available at <b>13,000+ network hospitals</b> across India. "
        "Key empanelled hospitals include:", BODY,
    ))
    hosp_data = [
        [Paragraph(h, ParagraphStyle("TH5", fontSize=9, textColor=WHITE,
                                      fontName="Helvetica-Bold", alignment=TA_CENTER))
         for h in ("Hospital Name", "City", "Network Code")],
        *[
            [Paragraph(c, SMALL) for c in row]
            for row in [
                ("Apollo Hospitals", "Mumbai / Delhi / Chennai / Hyderabad", "APL-001"),
                ("Fortis Healthcare", "Mumbai / Bengaluru / Delhi", "FRT-007"),
                ("Kokilaben Dhirubhai Ambani Hospital", "Mumbai", "KDA-012"),
                ("Lilavati Hospital & Research Centre", "Mumbai", "LIL-003"),
                ("Jaslok Hospital and Research Centre", "Mumbai", "JAS-005"),
                ("Max Super Specialty Hospital", "Delhi / Gurugram / Noida", "MAX-021"),
                ("Manipal Hospitals", "Bengaluru / Mangaluru / Goa", "MNP-009"),
                ("AIIMS", "New Delhi", "AII-001"),
            ]
        ],
    ]
    t = Table(hosp_data, colWidths=[7*cm, 6*cm, 3.5*cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#004B8D")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, GREY_BG]),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#CCCCCC")),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(t)

    # ── Premium Breakdown ─────────────────────────────────────────────────────
    story += section_header("PREMIUM COMPUTATION DETAILS")
    story.append(two_col_table([
        ("Base Premium (before GST)", "Rs. 15,220"),
        ("GST @ 18%", "Rs. 2,740"),
        ("Total Annual Premium Payable", "Rs. 17,960"),
        ("Premium Basis", "Age 37, Male, Individual plan, Mumbai zone, non-smoker"),
        ("Previous Year Premium (Star Health)", "Rs. 12,480"),
        ("Premium Difference", "+Rs. 5,480 per year (+44%)"),
        ("Additional Coverage Gained", "+Rs. 5,00,000 Sum Insured, unlimited restoration, "
         "no room rent sub-limit, no co-pay, OPD cover, air ambulance"),
    ]))

    # ── Exclusions ────────────────────────────────────────────────────────────
    story += section_header("KEY EXCLUSIONS (Refer Policy Wordings for Full List)")
    for excl in [
        "Cosmetic or aesthetic treatments and plastic surgery (unless necessitated by accident or cancer treatment)",
        "War, terrorism, nuclear, biological, or chemical contamination",
        "Self-inflicted injury, suicide attempt, or substance abuse",
        "Experimental treatments or unproven medical procedures",
        "Dental treatment (unless requiring hospitalisation due to accident)",
        "Refractive error correction, spectacles, contact lenses",
        "Obesity treatment / weight control programs",
        "Infertility treatment and assisted reproduction (IVF, IUI, surrogacy)",
        "Treatment outside India",
        "Non-allopathic treatment (except AYUSH up to policy limits)",
    ]:
        story.append(Paragraph(f"• {excl}", BODY))

    # ── Grievance Redressal ───────────────────────────────────────────────────
    story += section_header("GRIEVANCE REDRESSAL")
    story.append(two_col_table([
        ("Customer Care (24x7)", "1800-2700-700 (Toll Free)"),
        ("Email", "healthclaims@hdfcergo.com"),
        ("Cashless Pre-authorisation", "1800-2700-700 Ext. 2"),
        ("IRDAI Grievance Cell", "igms.irda.gov.in | 155255"),
        ("Insurance Ombudsman", "Refer IRDAI website for nearest ombudsman office"),
    ]))

    story.append(Spacer(1, 16))
    story.append(hr(colors.HexColor("#004B8D"), 1.5))
    story.append(Paragraph(
        "DISCLAIMER: This is a sample policy document generated for demonstration and testing purposes. "
        "All figures, policy numbers, and personal details are fictitious. "
        "HDFC ERGO General Insurance Company Limited is a registered insurer with IRDAI (Reg. No. 146). "
        "For actual policy terms, refer to the official policy wordings issued by the insurer.",
        DISCLAIMER,
    ))

    doc.build(story)
    print(f"Generated: {out}")
    return out


if __name__ == "__main__":
    print("Generating sample insurance policy PDFs...")
    p1 = build_star_health_pdf()
    p2 = build_hdfc_ergo_pdf()
    print(f"\nDone! Files saved to: {OUTPUT_DIR.resolve()}")
    print(f"  Old Policy (Star Health):  {p1.name}")
    print(f"  New Policy (HDFC ERGO):    {p2.name}")
    print("\nUpload these to the app at http://localhost:5174")
