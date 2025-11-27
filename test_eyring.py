"""
測試 Eyring 模型計算
驗證應力交互作用的加速因子計算
"""

import sys
import io
import numpy as np
from app import calculate_af

# 設置標準輸出編碼為 UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def test_eyring_disabled():
    """測試 Eyring 未啟用時的向後相容性"""
    print("\n=== 測試 Eyring 未啟用（向後相容） ===")

    params = {
        't_use': 32, 'rh_use': 60, 't_alt': 85, 'rh_alt': 85,
        'v_use': 1.0, 'v_alt': 1.2,
        'ea': 0.7, 'n_hum': 2.0, 'beta_v': 3.0,
        'enable_temp': True, 'enable_hum': True, 'enable_voltage': True,
        'enable_tc': False, 'enable_vib': False,
        'enable_uv': False, 'enable_chem': False,
        'enable_eyring': False
    }

    result = calculate_af(params)

    # 驗證結果應該是簡單相乘
    expected_total = result['af_t'] * result['af_rh'] * result['af_v']

    print(f"溫度 AF: {result['af_t']}")
    print(f"濕度 AF: {result['af_rh']}")
    print(f"電壓 AF: {result['af_v']}")
    print(f"AF Total: {result['af_total']}")
    print(f"預期 Total (簡單相乘): {expected_total}")

    assert abs(result['af_total'] - expected_total) < 0.01, \
        f"未啟用 Eyring 時應該是簡單相乘: {result['af_total']} vs {expected_total}"

    assert result.get('af_eyring_correction') is None, \
        "未啟用 Eyring 時不應有修正因子"

    print("✓ 向後相容性測試通過")
    return result

def test_eyring_voltage():
    """測試 Eyring 模型 (溫度 + 電壓交互)"""
    print("\n=== 測試 Eyring 模型 (溫度 + 電壓) ===")

    # 使用情境：高溫 + 高電壓有交互作用
    params = {
        't_use': 32, 'rh_use': 60, 't_alt': 85, 'rh_alt': 85,
        'v_use': 1.0, 'v_alt': 1.2,
        'ea': 0.7, 'n_hum': 2.0, 'beta_v': 3.0,
        'enable_temp': True, 'enable_hum': False, 'enable_voltage': True,
        'enable_tc': False, 'enable_vib': False,
        'enable_uv': False, 'enable_chem': False,
        'enable_eyring': True,
        'eyring_stress_type': 'voltage',
        'eyring_d': 0.1,  # 交互作用參數
        'eyring_a': 1000,  # 模型常數
        'eyring_b': 2.0    # 應力指數
    }

    result = calculate_af(params)

    print(f"溫度 AF: {result['af_t']}")
    print(f"電壓 AF: {result['af_v']}")
    print(f"Eyring 修正因子: {result.get('af_eyring_correction')}")
    print(f"AF Total (Eyring): {result['af_total']}")

    # 簡單模型（無交互）
    af_simple = result['af_t'] * result['af_v']
    print(f"簡單模型 (無交互): {af_simple}")

    # Eyring 修正因子應該與簡單模型有差異
    assert result.get('af_eyring_correction') is not None, \
        "啟用 Eyring 應有修正因子"

    # 手動計算驗證
    kb = 8.617e-5
    t_use_k = 32 + 273.15
    t_alt_k = 85 + 273.15
    ea = 0.7
    v_use = 1.0
    v_alt = 1.2
    eyring_a = 1000
    eyring_b = 2.0
    eyring_d = 0.1

    # 計算 t_use (Eyring 公式)
    t_use_eyring = (eyring_a *
                   (1.0 / v_use) ** eyring_b *
                   np.exp(ea / (kb * t_use_k)) *
                   np.exp(eyring_d * v_use / t_use_k))

    # 計算 t_alt (Eyring 公式)
    t_alt_eyring = (eyring_a *
                   (1.0 / v_alt) ** eyring_b *
                   np.exp(ea / (kb * t_alt_k)) *
                   np.exp(eyring_d * v_alt / t_alt_k))

    # Eyring AF
    af_eyring_expected = t_use_eyring / t_alt_eyring
    print(f"手動計算 Eyring AF: {af_eyring_expected}")

    # 修正因子
    eyring_correction_expected = af_eyring_expected / af_simple
    print(f"手動計算修正因子: {eyring_correction_expected}")

    assert abs(result['af_eyring_correction'] - eyring_correction_expected) < 0.01, \
        f"Eyring 修正因子計算錯誤: {result['af_eyring_correction']} vs {eyring_correction_expected}"

    print("✓ Eyring 模型 (溫度+電壓) 測試通過")
    return result

def test_eyring_humidity():
    """測試 Eyring 模型 (溫度 + 濕度交互)"""
    print("\n=== 測試 Eyring 模型 (溫度 + 濕度) ===")

    # 使用情境：高溫 + 高濕有交互作用 (HAST測試)
    params = {
        't_use': 32, 'rh_use': 60, 't_alt': 130, 'rh_alt': 85,
        'v_use': 1.0, 'v_alt': 1.0,
        'ea': 0.9, 'n_hum': 2.5, 'beta_v': 1.0,
        'enable_temp': True, 'enable_hum': True, 'enable_voltage': False,
        'enable_tc': False, 'enable_vib': False,
        'enable_uv': False, 'enable_chem': False,
        'enable_eyring': True,
        'eyring_stress_type': 'humidity',
        'eyring_d': 0.05,  # 交互作用參數（濕度通常較小）
        'eyring_a': 5000,  # 模型常數
        'eyring_b': 2.5    # 應力指數
    }

    result = calculate_af(params)

    print(f"溫度 AF: {result['af_t']}")
    print(f"濕度 AF: {result['af_rh']}")
    print(f"Eyring 修正因子: {result.get('af_eyring_correction')}")
    print(f"AF Total (Eyring): {result['af_total']}")

    # 簡單模型
    af_simple = result['af_t'] * result['af_rh']
    print(f"簡單模型 (無交互): {af_simple}")

    assert result.get('af_eyring_correction') is not None, \
        "啟用 Eyring 應有修正因子"

    print("✓ Eyring 模型 (溫度+濕度) 測試通過")
    return result

def test_eyring_with_other_factors():
    """測試 Eyring 模型與其他加速因子組合"""
    print("\n=== 測試 Eyring + 其他加速因子 ===")

    params = {
        # 基本參數
        't_use': 32, 'rh_use': 60, 't_alt': 85, 'rh_alt': 85,
        'v_use': 1.0, 'v_alt': 1.2,
        'ea': 0.7, 'n_hum': 2.0, 'beta_v': 3.0,

        # 啟用多個因子
        'enable_temp': True, 'enable_hum': True, 'enable_voltage': True,
        'enable_tc': True, 'enable_vib': False,
        'enable_uv': False, 'enable_chem': False,

        # 熱循環參數
        'dt_use': 70, 'dt_alt': 165,
        'f_use': 1/24, 'f_alt': 2,
        'alpha_tc': 0.33, 'beta_tc': 1.9,

        # Eyring 模型
        'enable_eyring': True,
        'eyring_stress_type': 'voltage',
        'eyring_d': 0.1,
        'eyring_a': 1000,
        'eyring_b': 2.0
    }

    result = calculate_af(params)

    print(f"溫度 AF: {result['af_t']}")
    print(f"濕度 AF: {result['af_rh']}")
    print(f"電壓 AF: {result['af_v']}")
    print(f"熱循環 AF: {result['af_tc']}")
    print(f"Eyring 修正因子: {result.get('af_eyring_correction')}")
    print(f"AF Total: {result['af_total']}")

    # 驗證：應該是所有因子的乘積（含Eyring修正）
    expected_base = result['af_rh'] * result['af_tc']  # 不受Eyring影響的因子
    # Eyring影響的部分：(af_t * af_v * eyring_correction)
    expected_eyring_part = result['af_t'] * result['af_v'] * result['af_eyring_correction']
    expected_total = expected_base * expected_eyring_part

    assert abs(result['af_total'] - expected_total) < 1.0, \
        f"組合計算錯誤: {result['af_total']} vs {expected_total}"

    print("✓ Eyring + 其他因子組合測試通過")
    return result

def test_eyring_impact():
    """展示 Eyring 模型的影響（交互作用的重要性）"""
    print("\n=== Eyring 模型影響分析 ===")

    base_params = {
        't_use': 32, 'rh_use': 60, 't_alt': 85, 'rh_alt': 60,
        'v_use': 1.0, 'v_alt': 1.3,
        'ea': 0.7, 'n_hum': 2.0, 'beta_v': 3.0,
        'enable_temp': True, 'enable_hum': False, 'enable_voltage': True,
        'enable_tc': False, 'enable_vib': False,
        'enable_uv': False, 'enable_chem': False
    }

    # 不使用 Eyring
    params_no_eyring = base_params.copy()
    params_no_eyring['enable_eyring'] = False
    result_no_eyring = calculate_af(params_no_eyring)

    # 使用 Eyring (弱交互)
    params_weak = base_params.copy()
    params_weak.update({
        'enable_eyring': True,
        'eyring_stress_type': 'voltage',
        'eyring_d': 0.05,  # 弱交互
        'eyring_a': 1000,
        'eyring_b': 2.0
    })
    result_weak = calculate_af(params_weak)

    # 使用 Eyring (強交互)
    params_strong = base_params.copy()
    params_strong.update({
        'enable_eyring': True,
        'eyring_stress_type': 'voltage',
        'eyring_d': 0.2,  # 強交互
        'eyring_a': 1000,
        'eyring_b': 2.0
    })
    result_strong = calculate_af(params_strong)

    print(f"無交互作用 (簡單模型): AF = {result_no_eyring['af_total']}")
    print(f"弱交互 (D=0.05): AF = {result_weak['af_total']}, 修正因子 = {result_weak['af_eyring_correction']}")
    print(f"強交互 (D=0.2): AF = {result_strong['af_total']}, 修正因子 = {result_strong['af_eyring_correction']}")

    diff_weak = ((result_weak['af_total'] - result_no_eyring['af_total']) /
                 result_no_eyring['af_total'] * 100)
    diff_strong = ((result_strong['af_total'] - result_no_eyring['af_total']) /
                   result_no_eyring['af_total'] * 100)

    print(f"\n相對差異:")
    print(f"  弱交互 vs 無交互: {diff_weak:+.2f}%")
    print(f"  強交互 vs 無交互: {diff_strong:+.2f}%")

    print("\n結論：")
    print("  • 交互作用參數 D 越大，Eyring 修正越顯著")
    print("  • 高可靠度產品應考慮使用 Eyring 模型")
    print("  • 消費性產品通常簡化模型已足夠")

    return result_no_eyring, result_weak, result_strong

if __name__ == "__main__":
    print("=" * 60)
    print("Eyring 模型測試與驗證")
    print("=" * 60)

    try:
        test_eyring_disabled()
        test_eyring_voltage()
        test_eyring_humidity()
        test_eyring_with_other_factors()
        test_eyring_impact()

        print("\n" + "=" * 60)
        print("✓ 所有 Eyring 模型測試通過！")
        print("=" * 60)

    except AssertionError as e:
        print(f"\n✗ 測試失敗: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ 發生錯誤: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
