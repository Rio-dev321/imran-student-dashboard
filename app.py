import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

st.set_page_config(
    page_title="Imran Public School & College | Student Dashboard",
    page_icon="🎓",
    layout="wide"
)

# ---------- Theme ----------
st.markdown("""
<style>
.stApp { background: #f3f6fb; color: #172b4d; }
[data-testid="stSidebar"] { background: #102b52; }
[data-testid="stSidebar"] * { color: #ffffff !important; }
.hero {
  background: linear-gradient(110deg, #102b52 0%, #1d4e89 72%, #d6a83b 100%);
  padding: 26px 30px; border-radius: 18px; color: white; margin-bottom: 18px;
}
.hero h1 { color: white; margin: 0; font-size: 30px; }
.hero p { color: #eef4ff; margin: 6px 0 0 0; }
.metric-card {
  background: white; border: 1px solid #e3eaf4; border-radius: 14px;
  padding: 17px 18px; box-shadow: 0 3px 12px rgba(16,43,82,.06);
}
.metric-label { color: #60738f; font-size: 13px; margin-bottom: 5px; }
.metric-value { color: #102b52; font-size: 27px; font-weight: 750; }
.section-title { color: #102b52; font-size: 21px; font-weight: 750; margin: 12px 0; }
.badge {
 display:inline-block; background:#fff5d9; color:#805c00; border:1px solid #e7c66c;
 padding:7px 12px; border-radius:20px; margin:4px 5px 4px 0; font-weight:650;
}
.small-note { color:#667892; font-size:12px; }
div[data-testid="stDownloadButton"] button {
 background:#d6a83b; color:#102b52; border:0; font-weight:700; border-radius:9px;
}
</style>
""", unsafe_allow_html=True)

# ---------- Demo student data (editable in sidebar) ----------
default_subjects = pd.DataFrame({
    "Subject": ["English", "Urdu", "Mathematics", "Physics", "Chemistry", "Computer Science"],
    "Obtained Marks": [82, 88, 91, 78, 85, 95],
    "Total Marks": [100, 100, 100, 100, 100, 100]
})

def grade_for(p):
    if p >= 90: return "A+"
    if p >= 80: return "A"
    if p >= 70: return "B"
    if p >= 60: return "C"
    if p >= 50: return "D"
    return "F"

def make_pdf(student, subjects, percentage, overall_grade, position, attendance, present, total_days, badges):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=38, leftMargin=38, topMargin=35, bottomMargin=35)
    styles = getSampleStyleSheet()
    title = ParagraphStyle("SchoolTitle", parent=styles["Title"], textColor=colors.HexColor("#102b52"),
                           alignment=TA_CENTER, fontSize=18, leading=22)
    subtitle = ParagraphStyle("SubTitle", parent=styles["Normal"], textColor=colors.HexColor("#9a741c"),
                              alignment=TA_CENTER, fontSize=10, leading=14)
    story = [
        Paragraph("IMRAN PUBLIC SCHOOL &amp; COLLEGE", title),
        Paragraph("STUDENT ACADEMIC RESULT CARD", subtitle),
        Spacer(1, 18)
    ]
    info = [
        ["Student Name", student["name"], "Roll Number", student["roll"]],
        ["Class / Section", student["class"], "Session", student["session"]],
        ["Class Position", str(position), "Attendance", f"{present}/{total_days} days ({attendance:.1f}%)"]
    ]
    t = Table(info, colWidths=[92, 155, 85, 150])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), colors.HexColor("#eef3fa")),
        ("TEXTCOLOR", (0,0), (-1,-1), colors.HexColor("#102b52")),
        ("GRID", (0,0), (-1,-1), .5, colors.HexColor("#d5dfed")),
        ("FONTNAME", (0,0), (-1,-1), "Helvetica"),
        ("FONTNAME", (0,0), (0,-1), "Helvetica-Bold"),
        ("FONTNAME", (2,0), (2,-1), "Helvetica-Bold"),
        ("PADDING", (0,0), (-1,-1), 8),
    ]))
    story += [t, Spacer(1, 18)]
    rows = [["Subject", "Obtained Marks", "Total Marks", "Percentage", "Grade"]]
    for _, r in subjects.iterrows():
        p = (r["Obtained Marks"] / r["Total Marks"] * 100) if r["Total Marks"] else 0
        rows.append([r["Subject"], str(int(r["Obtained Marks"])), str(int(r["Total Marks"])), f"{p:.1f}%", grade_for(p)])
    mt = Table(rows, colWidths=[150, 95, 85, 85, 65], repeatRows=1)
    mt.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#102b52")),
        ("TEXTCOLOR", (0,0), (-1,0), colors.white),
        ("BACKGROUND", (0,1), (-1,-1), colors.white),
        ("TEXTCOLOR", (0,1), (-1,-1), colors.HexColor("#263b59")),
        ("GRID", (0,0), (-1,-1), .5, colors.HexColor("#d5dfed")),
        ("PADDING", (0,0), (-1,-1), 7),
        ("ALIGN", (1,1), (-1,-1), "CENTER"),
    ]))
    story += [mt, Spacer(1, 18)]
    summary = [
        ["Overall Percentage", f"{percentage:.2f}%", "Overall Grade", overall_grade],
        ["Class Position", str(position), "Achievement Badges", ", ".join(badges) if badges else "Keep working hard"]
    ]
    stbl = Table(summary, colWidths=[125, 100, 115, 140])
    stbl.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), colors.HexColor("#fff5d9")),
        ("TEXTCOLOR", (0,0), (-1,-1), colors.HexColor("#624a12")),
        ("GRID", (0,0), (-1,-1), .5, colors.HexColor("#e7c66c")),
        ("FONTNAME", (0,0), (0,-1), "Helvetica-Bold"),
        ("FONTNAME", (2,0), (2,-1), "Helvetica-Bold"),
        ("PADDING", (0,0), (-1,-1), 8),
    ]))
    story += [stbl, Spacer(1, 20), Paragraph("Note: This is a computer-generated result card. Please contact the school office for verification.", styles["Italic"])]
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

# ---------- Sidebar ----------
st.sidebar.markdown("## 🎓 Student Dashboard")
st.sidebar.markdown("**Imran Public School & College**")
st.sidebar.caption("Demo data ko apne student ke mutabiq edit karein.")
with st.sidebar.expander("✏️ Student Profile Edit Karein", expanded=True):
    student_name = st.text_input("Student Name", "Muhammad Imran")
    roll_no = st.text_input("Roll Number", "IPS-1025")
    student_class = st.selectbox("Class / Section", ["Class 9 - A", "Class 9 - B", "Class 10 - A", "Class 10 - B", "First Year", "Second Year"], index=3)
    session = st.text_input("Academic Session", "2026-2027")
    position = st.number_input("Class Position", min_value=1, max_value=100, value=3, step=1)
    total_days = st.number_input("Total Working Days", min_value=1, max_value=300, value=180)
    present_days = st.number_input("Days Present", min_value=0, max_value=int(total_days), value=171)

st.sidebar.markdown("---")
st.sidebar.caption("Marks ko neeche table mein edit kiya ja sakta hai.")

# ---------- Main header ----------
st.markdown("""
<div class="hero">
  <h1>🎓 Imran Public School &amp; College</h1>
  <p>Smart Student Dashboard · Academic Performance · Attendance · Achievements</p>
</div>
""", unsafe_allow_html=True)

# Student profile
student = {"name": student_name, "roll": roll_no, "class": student_class, "session": session}
attendance = (present_days / total_days * 100) if total_days else 0

left, right = st.columns([1.5, 1])
with left:
    st.markdown('<div class="section-title">👤 Student Profile</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="metric-card">
      <h3 style="color:#102b52;margin:0;">{student_name}</h3>
      <p style="color:#60738f;margin:5px 0 12px;">{student_class} &nbsp; | &nbsp; Roll No: {roll_no}</p>
      <span class="badge">📘 Session: {session}</span>
      <span class="badge">🏫 Imran Public School & College</span>
    </div>
    """, unsafe_allow_html=True)
with right:
    st.markdown('<div class="section-title">🏅 Achievement Badges</div>', unsafe_allow_html=True)
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.markdown('<span class="badge">🌟 Star Student</span>', unsafe_allow_html=True) if position <= 3 else None
    # Badges are finalized after calculating marks below.
    st.markdown('<span class="badge">📚 Learning Champion</span>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="section-title">📊 Academic Overview</div>', unsafe_allow_html=True)
edited = st.data_editor(default_subjects, use_container_width=True, num_rows="dynamic", key="marks_editor",
    column_config={
        "Subject": st.column_config.TextColumn("Subject", required=True),
        "Obtained Marks": st.column_config.NumberColumn("Obtained Marks", min_value=0, step=1),
        "Total Marks": st.column_config.NumberColumn("Total Marks", min_value=1, step=1)
    })

# Validate marks safely
subjects = edited.copy()
subjects["Obtained Marks"] = pd.to_numeric(subjects["Obtained Marks"], errors="coerce").fillna(0)
subjects["Total Marks"] = pd.to_numeric(subjects["Total Marks"], errors="coerce").fillna(100)
subjects["Total Marks"] = subjects["Total Marks"].clip(lower=1)
subjects["Obtained Marks"] = subjects.apply(lambda r: min(max(0, r["Obtained Marks"]), r["Total Marks"]), axis=1)

total_obtained = float(subjects["Obtained Marks"].sum())
total_possible = float(subjects["Total Marks"].sum())
percentage = (total_obtained / total_possible * 100) if total_possible else 0
overall_grade = grade_for(percentage)
badges = []
if percentage >= 90: badges.append("🏆 Excellence Award")
elif percentage >= 80: badges.append("🌟 High Achiever")
if attendance >= 95: badges.append("🎯 Perfect Attendance")
if position <= 3: badges.append("🥇 Top 3 Position")
if not badges: badges.append("📘 Consistent Learner")

c1, c2, c3, c4 = st.columns(4)
metrics = [
    ("Overall Percentage", f"{percentage:.2f}%"),
    ("Overall Grade", overall_grade),
    ("Class Position", f"#{position}"),
    ("Attendance", f"{attendance:.1f}%")
]
for col, (label, value) in zip([c1,c2,c3,c4], metrics):
    with col:
        st.markdown(f'<div class="metric-card"><div class="metric-label">{label}</div><div class="metric-value">{value}</div></div>', unsafe_allow_html=True)

st.markdown('<div class="section-title">🏆 Your Achievements</div>', unsafe_allow_html=True)
st.markdown("".join([f'<span class="badge">{b}</span>' for b in badges]), unsafe_allow_html=True)

# Subject results and charts
st.markdown('<div class="section-title">📚 Subject-wise Result</div>', unsafe_allow_html=True)
display = subjects.copy()
display["Percentage"] = display.apply(lambda r: (r["Obtained Marks"]/r["Total Marks"]*100), axis=1).round(1)
display["Grade"] = display["Percentage"].apply(grade_for)
st.dataframe(display, use_container_width=True, hide_index=True)

chart1, chart2 = st.columns(2)
with chart1:
    fig = px.bar(display, x="Subject", y="Percentage", color="Percentage",
                 color_continuous_scale=["#d6a83b", "#1d4e89"], range_y=[0,100],
                 title="Subject-wise Performance")
    fig.update_layout(plot_bgcolor="white", paper_bgcolor="white", font_color="#102b52", coloraxis_showscale=False)
    st.plotly_chart(fig, use_container_width=True)
with chart2:
    attendance_df = pd.DataFrame({"Status": ["Present", "Absent"], "Days": [present_days, max(0, total_days-present_days)]})
    fig2 = px.pie(attendance_df, names="Status", values="Days", hole=.58,
                  color="Status", color_discrete_map={"Present":"#1d4e89", "Absent":"#d6a83b"},
                  title="Attendance Summary")
    fig2.update_layout(paper_bgcolor="white", font_color="#102b52")
    st.plotly_chart(fig2, use_container_width=True)

st.markdown('<div class="section-title">📅 Attendance Details</div>', unsafe_allow_html=True)
a1, a2, a3 = st.columns(3)
a1.metric("Present Days", int(present_days))
a2.metric("Absent Days", int(max(0, total_days-present_days)))
a3.metric("Working Days", int(total_days))
st.progress(min(max(attendance/100, 0.0), 1.0), text=f"Attendance: {attendance:.1f}%")

# PDF result
st.markdown('<div class="section-title">📄 Download Result Card</div>', unsafe_allow_html=True)
pdf_bytes = make_pdf(student, subjects, percentage, overall_grade, position, attendance,
                     int(present_days), int(total_days), badges)
st.download_button(
    label="⬇️ Download Result as PDF",
    data=pdf_bytes,
    file_name=f"{roll_no.replace(' ', '_')}_result.pdf",
    mime="application/pdf",
    use_container_width=False
)

st.markdown("---")
st.markdown("<p class='small-note' style='text-align:center;'>© Imran Public School & College · Smart Student Dashboard · Demo project</p>", unsafe_allow_html=True)
