"""
簡單的 PDF 生成測試
用於診斷 PDF 生成問題
"""

import io
from report_generator import generate_reliability_report

# 創建最小化的測試數據
test_data = {
    "af_params": {
        "t_use": "32",
        "t_alt": "85",
        "rh_use": "60",
        "rh_alt": "85",
        "ea": "0.7",
        "n_hum": "2.0",
        "enable_temp": True,
        "enable_hum": True,
        "enable_voltage": False,
        "enable_tc": False,
        "enable_vib": False,
        "enable_uv": False,
        "enable_chem": False,
        "enable_rad": False,
        "enable_eyring": False
    },
    "test_data": {
        "t_test": "120",
        "n_samples": "30",
        "failures": "",
        "cl": "0.6",
        "mission_years": "2"
    },
    "results": {
        "af_result": {
            "af_t": 67.45,
            "af_rh": 2.25,
            "af_v": 1.0,
            "af_tc": 1.0,
            "af_vib": 1.0,
            "af_uv": 1.0,
            "af_chem": 1.0,
            "af_rad": 1.0,
            "af_eyring_correction": None,
            "af_total": 151.77
        },
        "reliability_result": {
            "zero_failure": {
                "mttf_use_lower": 1272077.51,
                "lambda_use_upper": 786.12,
                "r_mission": 0.986322
            }
        }
    },
    "analysis_mode": "zero_failure",
    "conclusion": "在我們的現場操作條件（32°C / 60% RH）下，我們模擬了 2 年的壽命。\n\n我們的測試結果顯示，在 2 年任務期間內，這些條標品計的失效率上限僅為 1.368%（即可靠度為 98.6322%），儘於業界平均值約為 1.5%。",
    "chart_image": None  # 先測試沒有圖表的情況
}

try:
    print("Testing PDF generation with minimal data...")
    pdf_buffer = io.BytesIO()
    generate_reliability_report(test_data, pdf_buffer)
    pdf_buffer.seek(0)

    # 保存到文件
    with open("test_report.pdf", "wb") as f:
        f.write(pdf_buffer.read())

    print("✓ PDF generated successfully!")
    print("✓ Saved to: test_report.pdf")

except Exception as e:
    print(f"✗ Error generating PDF: {e}")
    import traceback
    traceback.print_exc()
