"""
測試 reportlab 的格式支持
"""
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import io

# 註冊中文字體
try:
    pdfmetrics.registerFont(TTFont('MicrosoftJhengHei', 'C:/Windows/Fonts/msjh.ttc'))
    CHINESE_FONT = 'MicrosoftJhengHei'
    print("Successfully registered MicrosoftJhengHei font")
except Exception as e:
    print(f"Failed to register font: {e}")
    CHINESE_FONT = 'Helvetica'

# 創建 PDF
pdf_buffer = io.BytesIO()
doc = SimpleDocTemplate(pdf_buffer, pagesize=A4)
story = []

styles = getSampleStyleSheet()
test_style = ParagraphStyle(
    'TestStyle',
    parent=styles['Normal'],
    fontSize=12,
    leading=18,
    fontName=CHINESE_FONT
)

# 測試各種格式
test_texts = [
    "1. 一般文字測試",
    "<b>2. 粗體文字測試</b>",
    "<font color='red'>3. 紅色文字測試</font>",
    "<font color='#dc2626'>4. 紅色十六進制測試</font>",
    "<font color='red'><b>5. 紅色粗體組合測試</b></font>",
    "<b><font color='#dc2626'>6. 粗體紅色組合測試（順序相反）</font></b>",
    "7. <b>部分粗體</b>和<font color='green'>部分綠色</font>測試",
    "[!] <font color='#f59e0b'><b>警告：可靠性不足</b></font>",
    "這批樣品的 <b>B1% 壽命</b>僅為 <b>0.28 年</b>，<font color='#dc2626'><b>未達到 2 年的任務時間要求</b></font>。",
]

for i, text in enumerate(test_texts, 1):
    try:
        p = Paragraph(text, test_style)
        story.append(p)
        story.append(Spacer(1, 12))
        print(f"[OK] Test {i} passed")
    except Exception as e:
        print(f"[FAIL] Test {i} failed: {e}")

# 建立 PDF
try:
    doc.build(story)
    pdf_buffer.seek(0)

    # 保存測試 PDF
    with open('test_formatting.pdf', 'wb') as f:
        f.write(pdf_buffer.read())

    print("\n[OK] PDF generated successfully: test_formatting.pdf")
except Exception as e:
    print(f"\n[FAIL] PDF generation failed: {e}")
    import traceback
    traceback.print_exc()
