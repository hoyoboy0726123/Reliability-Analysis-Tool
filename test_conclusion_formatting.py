"""
測試結論格式 - 確保所有 HTML 標籤正確處理
"""
from word_generator_v2 import generate_report_from_request_v2

# 測試數據 - 包含各種 HTML 標籤的結論
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
        'failures': '100, 150, 200',
        'n_samples': '64',
        't_test': '1196',
        'cl': '0.6',
        'mission_years': '2'
    },
    'results': {
        'af_result': {
            'af_total': 50,
            'af_t': 5.5,
            'af_rh': 3.2
        },
        'weibull_result': {
            'beta': 2.5,
            'eta_alt': 200,
            'r_squared': 0.98,
            'method': 'BENARD + RRY',
            'plot_data': {
                'x': [4.6, 5.0, 5.3],
                'y': [-2.5, -1.5, -0.8],
                't': [100, 150, 200],
                'f': [0.08, 0.22, 0.45]
            }
        },
        'reliability_result': {
            'weibull': {
                'eta_use': 10000,
                'mttf_use': 8900,
                'r_mission': 0.9813,
                'bx_life': 3461,
                'bx_percent': 1
            }
        }
    },
    'analysis_mode': 'weibull',
    'conclusion': '''
                <strong class="text-success">✓ 優秀：可靠度達標</strong>
                <br><br>
                在我們的現場操作條件（32°C / 60% RH）下，我們模擬了 <strong>2 年的壽命</strong>。
                <br><br>
                我們的測試結果顯示，在 <strong>2 年任務期間內</strong>，這批樣品預測的失效率上限僅為 <strong>1.368%</strong>
                （即可靠度為 <strong class="text-success">98.632%</strong>），優於業界平均標準 1.5%。
                <br><br>
                這表明元件在整個保固期內，因內在老化機制造成失效的風險極低，可安心提供 2 年
                保固。
                <br><br>
                <div class="small text-muted mt-2">參考標準：2 年保固標準（美國電子業平均）</div>
            '''
}

print("Testing conclusion HTML formatting...")
print("=" * 80)

try:
    word_buffer = generate_report_from_request_v2(test_data)

    # 保存測試 Word 文件
    with open('test_conclusion_format.docx', 'wb') as f:
        f.write(word_buffer.read())

    print("\n[SUCCESS] Word file generated: test_conclusion_format.docx")
    print("\nPlease open the file and verify:")
    print("  1. [OK] text should be GREEN and bold")
    print("  2. Bold text should be bold")
    print("  3. Percentage should be GREEN")
    print("  4. Last line should be GRAY and smaller font")
    print("  5. NO HTML tags should be visible in the text")
    print("=" * 80)

except Exception as e:
    print(f"\n[ERROR] Failed to generate Word file: {e}")
    import traceback
    traceback.print_exc()
