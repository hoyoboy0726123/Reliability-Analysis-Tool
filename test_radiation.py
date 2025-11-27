"""
測試輻射劑量加速因子計算
驗證 Total Ionizing Dose (TID) 模型
"""

import sys
import io
from app import calculate_af

# 設置標準輸出編碼為 UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def test_radiation_basic():
    """測試基本輻射劑量加速因子計算"""
    print("\n=== 測試基本輻射劑量 AF ===")

    params = {
        't_use': 32, 'rh_use': 60, 't_alt': 85, 'rh_alt': 85,
        'ea': 0.7, 'n_hum': 2.0,
        'enable_temp': True, 'enable_hum': True, 'enable_voltage': False,
        'enable_tc': False, 'enable_vib': False,
        'enable_uv': False, 'enable_chem': False,
        'enable_rad': True,
        'd_use': 10,     # 使用環境: 10 krad
        'd_alt': 100,    # 測試環境: 100 krad
        'dose_rate': 50, # 50 krad/hr
        'n_rad': 1.0     # 線性依賴
    }

    result = calculate_af(params)

    print(f"溫度 AF: {result['af_t']}")
    print(f"濕度 AF: {result['af_rh']}")
    print(f"輻射劑量 AF: {result['af_rad']}")
    print(f"AF Total: {result['af_total']}")

    # 驗證輻射劑量計算: (100/10)^1.0 = 10.0
    expected_af_rad = (100 / 10) ** 1.0
    assert abs(result['af_rad'] - expected_af_rad) < 0.01, \
        f"輻射劑量 AF 計算錯誤: {result['af_rad']} vs {expected_af_rad}"

    # 驗證總 AF (應該是所有因子的乘積)
    expected_total = result['af_t'] * result['af_rh'] * result['af_rad']
    assert abs(result['af_total'] - expected_total) < 1.0, \
        f"總 AF 計算錯誤: {result['af_total']} vs {expected_total}"

    print("✓ 基本輻射劑量測試通過")
    return result

def test_radiation_nonlinear():
    """測試非線性劑量依賴 (n ≠ 1)"""
    print("\n=== 測試非線性劑量依賴 ===")

    params = {
        't_use': 25, 'rh_use': 50, 't_alt': 85, 'rh_alt': 50,
        'ea': 0.7, 'n_hum': 2.0,
        'enable_temp': True, 'enable_hum': False, 'enable_voltage': False,
        'enable_tc': False, 'enable_vib': False,
        'enable_uv': False, 'enable_chem': False,
        'enable_rad': True,
        'd_use': 20,     # 20 krad
        'd_alt': 200,    # 200 krad
        'dose_rate': 100,
        'n_rad': 0.5     # 次線性 (某些器件的劑量率效應)
    }

    result = calculate_af(params)

    print(f"溫度 AF: {result['af_t']}")
    print(f"輻射劑量 AF: {result['af_rad']}")
    print(f"AF Total: {result['af_total']}")

    # 驗證: (200/20)^0.5 = 10^0.5 ≈ 3.162
    expected_af_rad = (200 / 20) ** 0.5
    print(f"預期輻射 AF: {expected_af_rad}")

    assert abs(result['af_rad'] - expected_af_rad) < 0.01, \
        f"非線性輻射 AF 計算錯誤: {result['af_rad']} vs {expected_af_rad}"

    print("✓ 非線性劑量依賴測試通過")
    return result

def test_radiation_space_mission():
    """測試太空任務典型場景"""
    print("\n=== 測試太空任務場景 ===")

    params = {
        't_use': -40, 'rh_use': 0, 't_alt': 125, 'rh_alt': 0,
        'ea': 1.0,  # 太空電子元件通常有較高活化能
        'n_hum': 2.0,
        'enable_temp': True, 'enable_hum': False, 'enable_voltage': True,
        'enable_tc': True, 'enable_vib': False,
        'enable_uv': False, 'enable_chem': False,
        'enable_rad': True,

        # 電壓參數
        'v_use': 3.3, 'v_alt': 5.0, 'beta_v': 5.0,

        # 熱循環參數 (太空晝夜溫差大)
        'dt_use': 80, 'dt_alt': 140,
        'f_use': 1/90,  # 地球軌道 ~90分鐘一圈
        'f_alt': 10,
        'alpha_tc': 0.33, 'beta_tc': 2.0,

        # 輻射劑量 (LEO: 5-15 krad/year, 15年任務)
        'd_use': 150,   # 15年 × 10 krad/year
        'd_alt': 300,   # 加速測試
        'dose_rate': 50,
        'n_rad': 0.8    # 考慮劑量率效應
    }

    result = calculate_af(params)

    print(f"溫度 AF: {result['af_t']}")
    print(f"電壓 AF: {result['af_v']}")
    print(f"熱循環 AF: {result['af_tc']}")
    print(f"輻射劑量 AF: {result['af_rad']}")
    print(f"AF Total: {result['af_total']}")

    # 驗證輻射計算
    expected_af_rad = (300 / 150) ** 0.8
    print(f"預期輻射 AF: {expected_af_rad}")

    assert abs(result['af_rad'] - expected_af_rad) < 0.01, \
        f"太空輻射 AF 計算錯誤: {result['af_rad']} vs {expected_af_rad}"

    print("✓ 太空任務場景測試通過")
    return result

def test_radiation_disabled():
    """測試輻射未啟用時的向後相容性"""
    print("\n=== 測試輻射未啟用（向後相容） ===")

    params = {
        't_use': 32, 'rh_use': 60, 't_alt': 85, 'rh_alt': 85,
        'ea': 0.7, 'n_hum': 2.0,
        'enable_temp': True, 'enable_hum': True, 'enable_voltage': False,
        'enable_tc': False, 'enable_vib': False,
        'enable_uv': False, 'enable_chem': False,
        'enable_rad': False  # 未啟用
    }

    result = calculate_af(params)

    print(f"溫度 AF: {result['af_t']}")
    print(f"濕度 AF: {result['af_rh']}")
    print(f"輻射劑量 AF: {result['af_rad']}")
    print(f"AF Total: {result['af_total']}")

    # 驗證未啟用時 af_rad = 1.0
    assert result['af_rad'] == 1.0, \
        f"未啟用時輻射 AF 應為 1.0: {result['af_rad']}"

    # 驗證總 AF 不受影響
    expected_total = result['af_t'] * result['af_rh']
    assert abs(result['af_total'] - expected_total) < 1.0, \
        f"未啟用輻射時總 AF 計算錯誤: {result['af_total']} vs {expected_total}"

    print("✓ 向後相容性測試通過")
    return result

def test_radiation_with_all_factors():
    """測試輻射與所有其他加速因子組合"""
    print("\n=== 測試輻射 + 所有其他因子 ===")

    params = {
        't_use': 32, 'rh_use': 60, 't_alt': 85, 'rh_alt': 85,
        'v_use': 1.0, 'v_alt': 1.2,
        'ea': 0.7, 'n_hum': 2.0, 'beta_v': 3.0,

        'enable_temp': True, 'enable_hum': True, 'enable_voltage': True,
        'enable_tc': True, 'enable_vib': True,
        'enable_uv': True, 'enable_chem': True,
        'enable_rad': True,

        # TC參數
        'dt_use': 70, 'dt_alt': 165,
        'f_use': 1/24, 'f_alt': 2,
        'alpha_tc': 0.33, 'beta_tc': 1.9,

        # VIB參數
        'g_use': 1.0, 'g_alt': 20.0, 'n_vib': 8.0,

        # UV參數
        't_field_uv': 8760, 't_accel_uv': 1000,

        # Chemical參數
        'c_use': 1.0, 'c_alt': 5.0, 'n_chem': 2.0,

        # Radiation參數
        'd_use': 10, 'd_alt': 100, 'dose_rate': 50, 'n_rad': 1.0
    }

    result = calculate_af(params)

    print(f"溫度 AF: {result['af_t']}")
    print(f"濕度 AF: {result['af_rh']}")
    print(f"電壓 AF: {result['af_v']}")
    print(f"熱循環 AF: {result['af_tc']}")
    print(f"振動 AF: {result['af_vib']}")
    print(f"UV AF: {result['af_uv']}")
    print(f"化學 AF: {result['af_chem']}")
    print(f"輻射 AF: {result['af_rad']}")
    print(f"AF Total: {result['af_total']}")

    # 驗證總AF是所有因子的乘積
    expected_total = (result['af_t'] * result['af_rh'] * result['af_v'] *
                     result['af_tc'] * result['af_vib'] * result['af_uv'] *
                     result['af_chem'] * result['af_rad'])

    # 使用相對誤差驗證（當AF非常大時）
    relative_error = abs(result['af_total'] - expected_total) / expected_total
    assert relative_error < 0.01, \
        f"全因子組合計算錯誤: {result['af_total']} vs {expected_total} (相對誤差: {relative_error:.2%})"

    print("✓ 全因子組合測試通過")
    return result

def test_radiation_sensitivity():
    """展示不同劑量敏感度指數的影響"""
    print("\n=== 劑量敏感度指數影響分析 ===")

    base_params = {
        't_use': 25, 'rh_use': 50, 't_alt': 85, 'rh_alt': 50,
        'ea': 0.7, 'n_hum': 2.0,
        'enable_temp': True, 'enable_hum': False, 'enable_voltage': False,
        'enable_tc': False, 'enable_vib': False,
        'enable_uv': False, 'enable_chem': False,
        'enable_rad': True,
        'd_use': 10, 'd_alt': 100, 'dose_rate': 50
    }

    results = []
    n_values = [0.5, 0.8, 1.0, 1.5, 2.0]

    print("\n劑量比 (d_alt/d_use) = 10")
    print("n_rad | AF_rad | 影響說明")
    print("-" * 50)

    for n in n_values:
        params = base_params.copy()
        params['n_rad'] = n
        result = calculate_af(params)
        results.append(result)

        if n < 1.0:
            desc = "次線性 (劑量率效應顯著)"
        elif n == 1.0:
            desc = "線性 (標準TID模型)"
        else:
            desc = "超線性 (協同效應)"

        print(f"{n:4.1f}  | {result['af_rad']:6.2f} | {desc}")

    print("\n結論：")
    print("  • n=0.5: 劑量率效應導致AF降低 (低劑量率下退火恢復)")
    print("  • n=1.0: 標準模型，AF與劑量比成正比")
    print("  • n>1.0: 高劑量下失效加速 (陷阱積累、協同效應)")
    print("  • 實際n值需通過不同劑量率的測試確定")

    return results

if __name__ == "__main__":
    print("=" * 60)
    print("輻射劑量加速因子測試與驗證")
    print("Total Ionizing Dose (TID) Model")
    print("=" * 60)

    try:
        test_radiation_disabled()
        test_radiation_basic()
        test_radiation_nonlinear()
        test_radiation_space_mission()
        test_radiation_with_all_factors()
        test_radiation_sensitivity()

        print("\n" + "=" * 60)
        print("✓ 所有輻射劑量測試通過！")
        print("=" * 60)

    except AssertionError as e:
        print(f"\n✗ 測試失敗: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ 發生錯誤: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
