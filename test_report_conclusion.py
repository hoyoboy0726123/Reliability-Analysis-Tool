"""
測試報告結論格式轉換
"""
from report_generator import generate_report_from_request
import io

# 模擬一個包含結論的請求數據
test_data = {
    'af_params': {
        'enable_temp': True,
        'enable_hum': True,
        't_use': '25',
        't_alt': '85',
        'rh_use': '60',
        'rh_alt': '85',
        'ea': '0.7',
        'n_hum': '2.7'
    },
    'test_data': {
        'failures': '100, 150, 200, 250, 300',
        'n_samples': '64',
        't_test': '1196',
        'cl': '0.6',
        'mission_years': '2'
    },
    'results': {
        'af_result': {
            'af_total': 50,
            'af_t': 5.5,
            'af_h': 3.2,
            'af_v': 1.0,
            'af_tc': 1.0,
            'af_vib': 1.0
        },
        'weibull_result': {
            'beta': 2.5,
            'eta_alt': 200,
            'r_squared': 0.98,
            'method': 'BENARD + RRY'
        },
        'reliability_result': {
            'weibull': {
                'eta_use': 10000,
                'mttf_use': 8900,
                'r_mission': 0.2232,
                'bx_life': 465,
                'bx_percent': 1
            }
        }
    },
    'analysis_mode': 'weibull',
    'conclusion': '''
                <strong class="text-warning">⚠️ 警告：可靠性不足</strong>
                <br><br>
                我們的測試模擬了現場使用壽命。計算結果顯示，這批樣品的 <strong>B1% 壽命</strong>僅為 <strong>0.05 年</strong> (465 小時)，
                <strong class="text-danger">未達到 2 年的任務時間要求</strong>。
                <br><br>
                在 2 年任務期間內，預期可靠度僅為 <strong>22.32%</strong>，失效風險高達 <strong class="text-danger">77.68%</strong>。
                <br><br>
                <strong>建議措施：</strong>
                <ul class="mb-0 mt-2">
                    <li>重新評估產品設計或材料選擇</li>
                    <li>改善製程以降低失效率</li>
                    <li>縮短保固期或調整任務時間目標</li>
                    <li>針對 4 個失效樣品進行根因分析</li>
                </ul>
            '''
}

print("Testing PDF report generation with formatted conclusion...")
print("="*80)

try:
    pdf_buffer = generate_report_from_request(test_data)

    # 保存測試 PDF
    with open('test_report.pdf', 'wb') as f:
        f.write(pdf_buffer.read())

    print("\n" + "="*80)
    print("[SUCCESS] PDF generated: test_report.pdf")
    print("Please open the PDF and check the conclusion section (Section 6)")
    print("="*80)

except Exception as e:
    print(f"\n[ERROR] Failed to generate PDF: {e}")
    import traceback
    traceback.print_exc()
