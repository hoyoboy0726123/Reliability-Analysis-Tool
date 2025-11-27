"""
測試 UV 和 Chemical 加速因子計算
驗證新增的加速因子功能
"""

import sys
import io
from app import calculate_af

# 設置標準輸出編碼為 UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def test_uv_radiation():
    """測試紫外線輻射加速因子"""
    print("\n=== 測試 UV 輻射加速因子 ===")

    params = {
        't_use': 32, 'rh_use': 60, 't_alt': 70, 'rh_alt': 90,
        'ea': 1.0, 'n_hum': 2.0,
        'enable_temp': True, 'enable_hum': True,
        'enable_voltage': False, 'enable_tc': False, 'enable_vib': False,
        'enable_uv': True, 'enable_chem': False,
        't_field_uv': 8760,  # 1年現場暴露
        't_accel_uv': 1000   # 1000小時測試
    }

    result = calculate_af(params)

    # 驗證 UV AF: 8760 / 1000 = 8.76
    expected_af_uv = 8760 / 1000
    print(f"UV AF 計算結果: {result['af_uv']}")
    print(f"預期 UV AF: {expected_af_uv}")

    assert abs(result['af_uv'] - expected_af_uv) < 0.01, \
        f"UV AF 計算錯誤: {result['af_uv']} vs {expected_af_uv}"

    print(f"✓ UV AF 計算正確: {result['af_uv']}")

    # 驗證總 AF 包含 UV
    expected_total = result['af_t'] * result['af_rh'] * result['af_uv']
    assert abs(result['af_total'] - expected_total) < 0.01, \
        f"AF Total 計算錯誤: {result['af_total']} vs {expected_total}"

    print(f"✓ AF Total 包含 UV: {result['af_total']}")
    return result

def test_chemical_concentration():
    """測試化學濃度加速因子"""
    print("\n=== 測試化學濃度加速因子 ===")

    params = {
        't_use': 32, 'rh_use': 60, 't_alt': 70, 'rh_alt': 90,
        'ea': 1.0, 'n_hum': 2.0,
        'enable_temp': True, 'enable_hum': True,
        'enable_voltage': False, 'enable_tc': False, 'enable_vib': False,
        'enable_uv': False, 'enable_chem': True,
        'c_use': 1.0,   # 標準濃度
        'c_alt': 5.0,   # 5倍濃度
        'n_chem': 2.0   # 功率指數 2.0
    }

    result = calculate_af(params)

    # 驗證 Chemical AF: (5.0 / 1.0)^2.0 = 25.0
    expected_af_chem = (5.0 / 1.0) ** 2.0
    print(f"Chemical AF 計算結果: {result['af_chem']}")
    print(f"預期 Chemical AF: {expected_af_chem}")

    assert abs(result['af_chem'] - expected_af_chem) < 0.01, \
        f"Chemical AF 計算錯誤: {result['af_chem']} vs {expected_af_chem}"

    print(f"✓ Chemical AF 計算正確: {result['af_chem']}")

    # 驗證總 AF 包含 Chemical
    expected_total = result['af_t'] * result['af_rh'] * result['af_chem']
    assert abs(result['af_total'] - expected_total) < 0.01, \
        f"AF Total 計算錯誤: {result['af_total']} vs {expected_total}"

    print(f"✓ AF Total 包含 Chemical: {result['af_total']}")
    return result

def test_combined_all_factors():
    """測試所有加速因子組合"""
    print("\n=== 測試所有加速因子組合 ===")

    params = {
        # 基本參數
        't_use': 32, 'rh_use': 60, 't_alt': 70, 'rh_alt': 90,
        'ea': 1.0, 'n_hum': 2.0,

        # 啟用所有因子
        'enable_temp': True, 'enable_hum': True,
        'enable_voltage': True, 'enable_tc': True, 'enable_vib': True,
        'enable_uv': True, 'enable_chem': True,

        # 電壓參數
        'v_use': 1.0, 'v_alt': 1.2, 'beta_v': 3.0,

        # 熱循環參數
        'dt_use': 70, 'dt_alt': 165,
        'f_use': 1/24, 'f_alt': 2,
        'alpha_tc': 0.33, 'beta_tc': 1.9,

        # 振動參數
        'g_use': 1.0, 'g_alt': 20.0, 'n_vib': 8.0,

        # UV 參數
        't_field_uv': 8760, 't_accel_uv': 1000,

        # 化學參數
        'c_use': 1.0, 'c_alt': 5.0, 'n_chem': 2.0
    }

    result = calculate_af(params)

    print(f"溫度 AF: {result['af_t']}")
    print(f"濕度 AF: {result['af_rh']}")
    print(f"電壓 AF: {result['af_v']}")
    print(f"熱循環 AF: {result['af_tc']}")
    print(f"振動 AF: {result['af_vib']}")
    print(f"UV AF: {result['af_uv']}")
    print(f"化學 AF: {result['af_chem']}")
    print(f"總 AF: {result['af_total']}")

    # 驗證總 AF 是所有因子的乘積
    expected_total = (result['af_t'] * result['af_rh'] * result['af_v'] *
                     result['af_tc'] * result['af_vib'] * result['af_uv'] *
                     result['af_chem'])

    rel_error = abs(result['af_total'] - expected_total) / expected_total
    assert rel_error < 0.0001, \
        f"AF Total 計算錯誤: {result['af_total']} vs {expected_total} (相對誤差: {rel_error*100:.4f}%)"

    print(f"✓ AF Total = 所有因子的乘積")

    return result

def test_backward_compatibility():
    """測試向後相容性 - 不啟用新因子時結果應與之前相同"""
    print("\n=== 測試向後相容性 ===")

    params = {
        't_use': 32, 'rh_use': 60, 't_alt': 70, 'rh_alt': 90,
        'ea': 1.0, 'n_hum': 2.0,
        'enable_temp': True, 'enable_hum': True,
        'enable_voltage': False, 'enable_tc': False, 'enable_vib': False,
        'enable_uv': False, 'enable_chem': False
    }

    result = calculate_af(params)

    # UV 和 Chemical 應該為 1.0（不影響結果）
    assert result['af_uv'] == 1.0, f"UV AF 應為 1.0: {result['af_uv']}"
    assert result['af_chem'] == 1.0, f"Chemical AF 應為 1.0: {result['af_chem']}"

    # 總 AF 應該只包含溫度和濕度
    expected_total = result['af_t'] * result['af_rh']
    assert abs(result['af_total'] - expected_total) < 0.01, \
        f"AF Total 應只包含溫度和濕度: {result['af_total']} vs {expected_total}"

    print(f"✓ 向後相容性測試通過")
    print(f"  UV AF (未啟用): {result['af_uv']}")
    print(f"  Chemical AF (未啟用): {result['af_chem']}")
    print(f"  AF Total: {result['af_total']}")

    return result

if __name__ == "__main__":
    print("=" * 60)
    print("UV 和 Chemical 加速因子測試")
    print("=" * 60)

    try:
        test_backward_compatibility()
        test_uv_radiation()
        test_chemical_concentration()
        test_combined_all_factors()

        print("\n" + "=" * 60)
        print("✓ 所有測試通過！")
        print("=" * 60)

    except AssertionError as e:
        print(f"\n✗ 測試失敗: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ 發生錯誤: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
