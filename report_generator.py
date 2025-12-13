"""
PDF 測試報告生成器
使用 reportlab 生成專業的可靠度測試報告
"""

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from datetime import datetime
import base64
import io
from PIL import Image as PILImage

# 嘗試註冊中文字體（如果系統有的話）
CHINESE_FONT = 'Helvetica'  # 默認使用 Helvetica
try:
    # Windows 系統的微軟正黑體
    pdfmetrics.registerFont(TTFont('MicrosoftJhengHei', 'C:/Windows/Fonts/msjh.ttc'))
    CHINESE_FONT = 'MicrosoftJhengHei'
    print("Successfully registered MicrosoftJhengHei font")
except Exception as e:
    print(f"Failed to register MicrosoftJhengHei: {e}")
    try:
        # 另一個常見的中文字體
        pdfmetrics.registerFont(TTFont('SimHei', 'C:/Windows/Fonts/simhei.ttf'))
        CHINESE_FONT = 'SimHei'
        print("Successfully registered SimHei font")
    except Exception as e2:
        print(f"Failed to register SimHei: {e2}")
        # 如果都失敗，使用 Helvetica（不支援中文，但至少不會報錯）
        print("Using Helvetica font (no Chinese support)")

def generate_reliability_report(data, output_file):
    """
    生成可靠度測試報告 PDF

    Args:
        data: 包含所有測試數據和結果的字典
        output_file: 輸出文件路徑或文件對象
    """
    try:
        print("Starting PDF generation...")
        print(f"Data keys: {data.keys()}")

        # 創建 PDF 文檔
        doc = SimpleDocTemplate(
            output_file,
            pagesize=A4,
            rightMargin=30,
            leftMargin=30,
            topMargin=40,
            bottomMargin=40
        )
        print("PDF document created")
    except Exception as e:
        print(f"Error creating PDF document: {e}")
        raise

    # 容器，用於存放報告的所有元素
    story = []

    # 定義樣式
    styles = getSampleStyleSheet()

    # 標題樣式
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1a5490'),
        spaceAfter=30,
        alignment=TA_CENTER,
        fontName=CHINESE_FONT if CHINESE_FONT != 'Helvetica' else 'Helvetica-Bold'
    )

    # 章節標題樣式
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#2563eb'),
        spaceBefore=20,
        spaceAfter=12,
        fontName=CHINESE_FONT if CHINESE_FONT != 'Helvetica' else 'Helvetica-Bold'
    )

    # 普通文字樣式
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=10,
        fontName=CHINESE_FONT if CHINESE_FONT != 'Helvetica' else 'Helvetica'
    )

    # 1. 報告標題
    story.append(Paragraph("Reliability Test Report", title_style))
    story.append(Paragraph("可靠度測試報告", title_style))
    story.append(Spacer(1, 20))

    # 2. 報告資訊
    report_info = [
        ['Report Date / 報告日期:', datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
        ['Analysis Mode / 分析模式:', data.get('analysis_mode', 'N/A').upper()]
    ]

    info_table = Table(report_info, colWidths=[2.5*inch, 4*inch])
    info_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), CHINESE_FONT if CHINESE_FONT != 'Helvetica' else 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#374151')),
        ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#1f2937')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f3f4f6')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#d1d5db')),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))

    story.append(info_table)
    story.append(Spacer(1, 30))

    # 3. 加速因子參數
    story.append(Paragraph("1. Acceleration Factor Parameters / 加速因子參數", heading_style))
    story.append(Spacer(1, 10))

    af_params = data.get('af_params', {})
    af_data = [
        ['Parameter / 參數', 'Use Condition / 使用條件', 'Test Condition / 測試條件', 'Model / 模型']
    ]

    # 溫度
    if af_params.get('enable_temp', True):
        af_data.append([
            'Temperature / 溫度',
            f"{af_params.get('t_use', '')}°C",
            f"{af_params.get('t_alt', '')}°C",
            f"Arrhenius (Ea={af_params.get('ea', '')} eV)"
        ])

    # 濕度
    if af_params.get('enable_hum', True):
        af_data.append([
            'Humidity / 濕度',
            f"{af_params.get('rh_use', '')}%",
            f"{af_params.get('rh_alt', '')}%",
            f"Peck (n={af_params.get('n_hum', '')})"
        ])

    # 電壓
    if af_params.get('enable_voltage', False):
        af_data.append([
            'Voltage / 電壓',
            f"{af_params.get('v_use', '')}V",
            f"{af_params.get('v_alt', '')}V",
            f"IPL (β={af_params.get('beta_v', '')})"
        ])

    # 熱循環
    if af_params.get('enable_tc', False):
        af_data.append([
            'Thermal Cycling / 熱循環',
            f"ΔT={af_params.get('dt_use', '')}°C, f={af_params.get('f_use', '')}/hr",
            f"ΔT={af_params.get('dt_alt', '')}°C, f={af_params.get('f_alt', '')}/hr",
            f"Coffin-Manson (α={af_params.get('alpha_tc', '')}, β={af_params.get('beta_tc', '')})"
        ])

    # 機械振動
    if af_params.get('enable_vib', False):
        af_data.append([
            'Vibration / 機械振動',
            f"{af_params.get('g_use', '')}G",
            f"{af_params.get('g_alt', '')}G",
            f"IPL (n={af_params.get('n_vib', '')})"
        ])

    # UV
    if af_params.get('enable_uv', False):
        af_data.append([
            'UV Radiation / 紫外線',
            f"{af_params.get('t_field_uv', '')} hrs",
            f"{af_params.get('t_accel_uv', '')} hrs",
            "Experimental Comparison"
        ])

    # 化學
    if af_params.get('enable_chem', False):
        af_data.append([
            'Chemical / 化學濃度',
            f"C={af_params.get('c_use', '')}",
            f"C={af_params.get('c_alt', '')}",
            f"IPL (n={af_params.get('n_chem', '')})"
        ])

    # 輻射
    if af_params.get('enable_rad', False):
        af_data.append([
            'Radiation / 輻射劑量',
            f"D={af_params.get('d_use', '')} krad",
            f"D={af_params.get('d_alt', '')} krad",
            f"TID (n={af_params.get('n_rad', '')})"
        ])

    # Eyring
    if af_params.get('enable_eyring', False):
        af_data.append([
            'Eyring Model / 應力交互',
            '-',
            '-',
            f"Type={af_params.get('eyring_stress_type', '')}, D={af_params.get('eyring_d', '')}"
        ])

    af_table = Table(af_data, colWidths=[1.5*inch, 1.8*inch, 1.8*inch, 2.4*inch])
    af_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), CHINESE_FONT if CHINESE_FONT != 'Helvetica' else 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2563eb')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('TOPPADDING', (0, 0), (-1, 0), 10),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#d1d5db')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9fafb')]),
        ('TOPPADDING', (0, 1), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
    ]))

    story.append(af_table)
    story.append(Spacer(1, 30))

    # 4. 加速因子結果
    story.append(Paragraph("2. Acceleration Factor Results / 加速因子結果", heading_style))
    story.append(Spacer(1, 10))

    results = data.get('results', {})
    af_result = results.get('af_result', {})

    af_result_data = [
        ['Factor / 因子', 'Value / 數值']
    ]

    if af_params.get('enable_temp', True):
        af_result_data.append(['AF (Temperature) / 溫度', f"{af_result.get('af_t', 'N/A'):,.4f}"])
    if af_params.get('enable_hum', True):
        af_result_data.append(['AF (Humidity) / 濕度', f"{af_result.get('af_rh', 'N/A'):,.4f}"])
    if af_params.get('enable_voltage', False):
        af_result_data.append(['AF (Voltage) / 電壓', f"{af_result.get('af_v', 'N/A'):,.4f}"])
    if af_params.get('enable_tc', False):
        af_result_data.append(['AF (Thermal Cycling) / 熱循環', f"{af_result.get('af_tc', 'N/A'):,.4f}"])
    if af_params.get('enable_vib', False):
        af_result_data.append(['AF (Vibration) / 振動', f"{af_result.get('af_vib', 'N/A'):,.4f}"])
    if af_params.get('enable_uv', False):
        af_result_data.append(['AF (UV) / 紫外線', f"{af_result.get('af_uv', 'N/A'):,.4f}"])
    if af_params.get('enable_chem', False):
        af_result_data.append(['AF (Chemical) / 化學', f"{af_result.get('af_chem', 'N/A'):,.4f}"])
    if af_params.get('enable_rad', False):
        af_result_data.append(['AF (Radiation) / 輻射', f"{af_result.get('af_rad', 'N/A'):,.4f}"])
    if af_params.get('enable_eyring', False) and af_result.get('af_eyring_correction'):
        af_result_data.append(['Eyring Correction / Eyring 修正因子', f"{af_result.get('af_eyring_correction', 'N/A'):,.4f}"])

    af_result_data.append(['', ''])  # 空行
    af_result_data.append(['AF Total / 總加速因子', f"{af_result.get('af_total', 'N/A'):,.4f}"])

    af_result_table = Table(af_result_data, colWidths=[4*inch, 3.5*inch])
    af_result_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), CHINESE_FONT if CHINESE_FONT != 'Helvetica' else 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2563eb')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('TOPPADDING', (0, 0), (-1, 0), 10),
        ('GRID', (0, 0), (-1, -2), 0.5, colors.HexColor('#d1d5db')),
        ('LINEABOVE', (0, -1), (-1, -1), 2, colors.HexColor('#2563eb')),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#dbeafe')),
        ('FONTSIZE', (0, -1), (-1, -1), 12),
        ('TOPPADDING', (0, -1), (-1, -1), 10),
        ('BOTTOMPADDING', (0, -1), (-1, -1), 10),
        ('ROWBACKGROUNDS', (0, 1), (-1, -3), [colors.white, colors.HexColor('#f9fafb')]),
        ('TOPPADDING', (0, 1), (-1, -2), 6),
        ('BOTTOMPADDING', (0, 1), (-1, -2), 6),
    ]))

    story.append(af_result_table)
    story.append(Spacer(1, 30))

    # 5. 測試數據
    story.append(Paragraph("3. Test Data / 測試數據", heading_style))
    story.append(Spacer(1, 10))

    test_data = data.get('test_data', {})

    test_info = [
        ['Test Time / 測試時間:', f"{test_data.get('t_test', 'N/A')} hours"],
        ['Number of Samples / 樣本數:', test_data.get('n_samples', 'N/A')],
        ['Failures / 失效數:', test_data.get('failures', '0') if test_data.get('failures', '') else '0'],
        ['Confidence Level / 信心水準:', f"{float(test_data.get('cl', 0.6)) * 100:.0f}%"],
        ['Mission Time / 任務時間:', f"{test_data.get('mission_years', 'N/A')} years"]
    ]

    # 計算等效現場時間
    test_time = float(test_data.get('t_test', 0))
    af_total = af_result.get('af_total', 0)
    equivalent_time = test_time * af_total
    equivalent_years = equivalent_time / 8760

    test_info.append([
        'Equivalent Field Time / 等效現場時間:',
        f"{equivalent_time:,.2f} hours (~ {equivalent_years:,.2f} years)"
    ])

    test_table = Table(test_info, colWidths=[3*inch, 4.5*inch])
    test_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), CHINESE_FONT if CHINESE_FONT != 'Helvetica' else 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#374151')),
        ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#1f2937')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f3f4f6')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#d1d5db')),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#dbeafe')),
    ]))

    story.append(test_table)
    story.append(Spacer(1, 30))

    # 6. 可靠度分析結果
    story.append(Paragraph("4. Reliability Analysis Results / 可靠度分析結果", heading_style))
    story.append(Spacer(1, 10))

    reliability_result = results.get('reliability_result', {})
    analysis_mode = data.get('analysis_mode', 'zero_failure')

    if analysis_mode == 'weibull' and 'weibull' in reliability_result:
        wb_result = reliability_result['weibull']
        wb_data = results.get('weibull_result', {})

        reliability_data = [
            ['Metric / 指標', 'Value / 數值'],
            ['MTTF (Mean Life) / 平均壽命', f"{wb_result.get('mttf_use', 0):,.2f} hours"],
            ['B1% Life / B1壽命', f"{wb_result.get('b1_life', 0):,.2f} hours"],
            [f"Reliability ({test_data.get('mission_years', 2)} Years) / 可靠度", f"{wb_result.get('r_mission', 0) * 100:.4f}%"],
            ['', ''],
            ['Weibull Parameters / Weibull 參數', ''],
            ['Shape Parameter (β) / 形狀參數', f"{wb_data.get('beta', 'N/A')}"],
            ['Scale Parameter (η) / 尺度參數', f"{wb_data.get('eta_alt', 'N/A')}"]
        ]
    else:
        zf_result = reliability_result.get('zero_failure', {})

        reliability_data = [
            ['Metric / 指標', 'Value / 數值'],
            ['MTTF (Lower Limit) / 平均壽命下限', f"> {zf_result.get('mttf_use_lower', 0):,.2f} hours"],
            ['Max Failure Rate / 最大失效率', f"< {zf_result.get('lambda_use_upper', 0):,.2f} FITs"],
            [f"Reliability ({test_data.get('mission_years', 2)} Years) / 可靠度", f"{zf_result.get('r_mission', 0) * 100:.4f}%"],
            ['', ''],
            ['Confidence Level / 信心水準', f"{float(test_data.get('cl', 0.6)) * 100:.0f}%"]
        ]

    reliability_table = Table(reliability_data, colWidths=[4*inch, 3.5*inch])
    reliability_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), CHINESE_FONT if CHINESE_FONT != 'Helvetica' else 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#10b981')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('TOPPADDING', (0, 0), (-1, 0), 10),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#d1d5db')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9fafb')]),
        ('TOPPADDING', (0, 1), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
    ]))

    story.append(reliability_table)
    story.append(Spacer(1, 30))

    # 7. 圖表
    chart_image = data.get('chart_image')
    if chart_image:
        story.append(Paragraph("5. Analysis Chart / 分析圖表", heading_style))
        story.append(Spacer(1, 10))

        try:
            # 從 base64 解碼圖片
            if chart_image.startswith('data:image'):
                chart_image = chart_image.split(',')[1]

            image_data = base64.b64decode(chart_image)
            image_buffer = io.BytesIO(image_data)

            # 創建圖片對象
            img = Image(image_buffer, width=6.5*inch, height=3.25*inch)
            story.append(img)
            story.append(Spacer(1, 20))
        except Exception as e:
            story.append(Paragraph(f"Chart unavailable / 圖表無法顯示: {str(e)}", normal_style))
            story.append(Spacer(1, 20))

    # 8. 結論
    story.append(PageBreak())
    story.append(Paragraph("6. Conclusion / 分析結論", heading_style))
    story.append(Spacer(1, 10))

    conclusion = data.get('conclusion', 'No conclusion available.')

    # 將結論分段
    conclusion_paragraphs = conclusion.split('\n')
    for para in conclusion_paragraphs:
        if para.strip():
            story.append(Paragraph(para.strip(), normal_style))
            story.append(Spacer(1, 8))

    # 9. 頁腳資訊
    story.append(Spacer(1, 30))
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.HexColor('#6b7280'),
        alignment=TA_CENTER,
        fontName=CHINESE_FONT if CHINESE_FONT != 'Helvetica' else 'Helvetica'
    )
    story.append(Paragraph("Generated by Reliability Analysis Tool / 由可靠度分析工具生成", footer_style))
    story.append(Paragraph(f"Report generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", footer_style))

    # 建立 PDF
    try:
        print("Building PDF...")
        doc.build(story)
        print("PDF built successfully")
    except Exception as e:
        print(f"Error building PDF: {e}")
        import traceback
        traceback.print_exc()
        raise

def generate_report_from_request(request_data):
    """
    從請求數據生成 PDF 報告並返回文件流

    Args:
        request_data: 來自前端的請求數據

    Returns:
        BytesIO: PDF 文件的二進制流
    """
    try:
        print("Generating report from request...")
        print(f"Request data type: {type(request_data)}")

        # 創建內存中的 PDF
        pdf_buffer = io.BytesIO()

        # 生成 PDF
        generate_reliability_report(request_data, pdf_buffer)

        # 將指針移到開頭
        pdf_buffer.seek(0)

        print("Report generated successfully")
        return pdf_buffer

    except Exception as e:
        print(f"Error in generate_report_from_request: {e}")
        import traceback
        traceback.print_exc()
        raise
