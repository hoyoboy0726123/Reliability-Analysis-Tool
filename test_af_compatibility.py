"""
測試加速因子兼容性 - 確保新功能不影響原有計算
"""
import sys
import io

# 設置標準輸出編碼為 UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

sys.path.insert(0, '.')
from app import calculate_af

def test_original_calculation():
    """測試原有的溫度+濕度+電壓計算（未啟用新因子）"""
    print("=" * 60)
    print("測試 1: 原有計算邏輯 (溫度+濕度啟用, 預設)")
    print("=" * 60)

    params = {
        't_use': 32,
        'rh_use': 60,
        'v_use': 1.0,
        't_alt': 70,
        'rh_alt': 90,
        'v_alt': 1.0,
        'ea': 1.0,
        'n_hum': 2.0,
        'beta_v': 1.0,
        # 預設：溫度和濕度啟用，其他停用
        'enable_temp': True,
        'enable_hum': True,
        'enable_voltage': False,
        'enable_tc': False,
        'enable_vib': False
    }

    result = calculate_af(params)

    print(f"AF_T (溫度):    {result['af_t']}")
    print(f"AF_RH (濕度):   {result['af_rh']}")
    print(f"AF_V (電壓):    {result['af_v']}")
    print(f"AF_TC (熱循環): {result['af_tc']}")
    print(f"AF_VIB (振動):  {result['af_vib']}")
    print(f"AF_Total:       {result['af_total']}")

    # 驗證結果
    expected_af_total = result['af_t'] * result['af_rh']
    assert abs(result['af_total'] - expected_af_total) < 0.01, \
        f"AF Total 計算錯誤: {result['af_total']} vs {expected_af_total}"
    assert result['af_v'] == 1.0, "電壓 AF 應為 1.0 (未啟用)"
    assert result['af_tc'] == 1.0, "熱循環 AF 應為 1.0 (未啟用)"
    assert result['af_vib'] == 1.0, "振動 AF 應為 1.0 (未啟用)"

    print("✓ 原有計算邏輯正確\n")
    return result

def test_with_voltage():
    """測試啟用電壓加速因子"""
    print("=" * 60)
    print("測試 2: 啟用電壓加速因子")
    print("=" * 60)

    params = {
        't_use': 32,
        'rh_use': 60,
        'v_use': 1.0,
        't_alt': 70,
        'rh_alt': 90,
        'v_alt': 1.2,  # 電壓應力
        'ea': 1.0,
        'n_hum': 2.0,
        'beta_v': 1.0,
        'enable_temp': True,
        'enable_hum': True,
        'enable_voltage': True,  # 啟用電壓
        'enable_tc': False,
        'enable_vib': False
    }

    result = calculate_af(params)

    print(f"AF_T (溫度):    {result['af_t']}")
    print(f"AF_RH (濕度):   {result['af_rh']}")
    print(f"AF_V (電壓):    {result['af_v']}")
    print(f"AF_Total:       {result['af_total']}")

    # 驗證電壓 AF
    expected_af_v = (1.2 / 1.0) ** 1.0
    assert abs(result['af_v'] - expected_af_v) < 0.01, \
        f"電壓 AF 計算錯誤: {result['af_v']} vs {expected_af_v}"

    expected_total = result['af_t'] * result['af_rh'] * result['af_v']
    assert abs(result['af_total'] - expected_total) < 0.01, \
        f"AF Total 計算錯誤: {result['af_total']} vs {expected_total}"

    print("✓ 電壓加速因子計算正確\n")
    return result

def test_with_thermal_cycling():
    """測試啟用熱循環加速因子"""
    print("=" * 60)
    print("測試 3: 啟用熱循環加速因子")
    print("=" * 60)

    params = {
        't_use': 32,
        'rh_use': 60,
        't_alt': 70,
        'rh_alt': 90,
        'ea': 1.0,
        'n_hum': 2.0,
        'enable_temp': True,
        'enable_hum': True,
        'enable_voltage': False,
        'enable_tc': True,  # 啟用熱循環
        'enable_vib': False,
        # 熱循環參數
        'dt_use': 70,       # 使用 ΔT = 70°C
        'dt_alt': 165,      # 測試 ΔT = 165°C (JEDEC 標準)
        'f_use': 1/24,      # 1 次/天
        'f_alt': 2,         # 2 次/小時
        'alpha_tc': 0.33,   # 頻率指數
        'beta_tc': 1.9      # 溫度指數
    }

    result = calculate_af(params)

    print(f"AF_T (溫度):    {result['af_t']}")
    print(f"AF_RH (濕度):   {result['af_rh']}")
    print(f"AF_TC (熱循環): {result['af_tc']}")
    print(f"AF_Total:       {result['af_total']}")

    # 驗證熱循環 AF
    # AF_TC = (ΔT_alt/ΔT_use)^β × (f_alt/f_use)^α
    expected_af_tc = ((165 / 70) ** 1.9) * ((2 / (1/24)) ** 0.33)
    print(f"預期 AF_TC:     {expected_af_tc:.4f}")

    assert abs(result['af_tc'] - expected_af_tc) < 0.01, \
        f"熱循環 AF 計算錯誤: {result['af_tc']} vs {expected_af_tc}"

    expected_total = result['af_t'] * result['af_rh'] * result['af_tc']
    assert abs(result['af_total'] - expected_total) < 0.01, \
        f"AF Total 計算錯誤: {result['af_total']} vs {expected_total}"

    print("✓ 熱循環加速因子計算正確\n")
    return result

def test_with_vibration():
    """測試啟用振動加速因子"""
    print("=" * 60)
    print("測試 4: 啟用振動加速因子")
    print("=" * 60)

    params = {
        't_use': 32,
        'rh_use': 60,
        't_alt': 70,
        'rh_alt': 90,
        'ea': 1.0,
        'n_hum': 2.0,
        'enable_temp': True,
        'enable_hum': True,
        'enable_voltage': False,
        'enable_tc': False,
        'enable_vib': True,  # 啟用振動
        # 振動參數
        'g_use': 1.0,    # 使用 1g
        'g_alt': 20.0,   # 測試 20g (JEDEC 標準)
        'n_vib': 8.0     # 功率指數
    }

    result = calculate_af(params)

    print(f"AF_T (溫度):    {result['af_t']}")
    print(f"AF_RH (濕度):   {result['af_rh']}")
    print(f"AF_VIB (振動):  {result['af_vib']}")
    print(f"AF_Total:       {result['af_total']}")

    # 驗證振動 AF
    # AF_VIB = (G_alt/G_use)^n
    expected_af_vib = (20.0 / 1.0) ** 8.0
    print(f"預期 AF_VIB:    {expected_af_vib:.4f}")

    assert abs(result['af_vib'] - expected_af_vib) < 0.01, \
        f"振動 AF 計算錯誤: {result['af_vib']} vs {expected_af_vib}"

    expected_total = result['af_t'] * result['af_rh'] * result['af_vib']
    # 使用相對誤差來驗證（因為數值很大）
    rel_error = abs(result['af_total'] - expected_total) / expected_total
    assert rel_error < 0.0001, \
        f"AF Total 計算錯誤: {result['af_total']} vs {expected_total} (相對誤差: {rel_error*100:.4f}%)"

    print("✓ 振動加速因子計算正確\n")
    return result

def test_all_factors_enabled():
    """測試所有加速因子同時啟用"""
    print("=" * 60)
    print("測試 5: 所有加速因子同時啟用")
    print("=" * 60)

    params = {
        't_use': 32,
        'rh_use': 60,
        'v_use': 1.0,
        't_alt': 70,
        'rh_alt': 90,
        'v_alt': 1.2,
        'ea': 1.0,
        'n_hum': 2.0,
        'beta_v': 1.0,
        'enable_temp': True,
        'enable_hum': True,
        'enable_voltage': True,
        'enable_tc': True,
        'enable_vib': True,
        # 熱循環參數
        'dt_use': 70,
        'dt_alt': 165,
        'f_use': 1/24,
        'f_alt': 2,
        'alpha_tc': 0.33,
        'beta_tc': 1.9,
        # 振動參數
        'g_use': 1.0,
        'g_alt': 20.0,
        'n_vib': 8.0
    }

    result = calculate_af(params)

    print(f"AF_T (溫度):    {result['af_t']}")
    print(f"AF_RH (濕度):   {result['af_rh']}")
    print(f"AF_V (電壓):    {result['af_v']}")
    print(f"AF_TC (熱循環): {result['af_tc']}")
    print(f"AF_VIB (振動):  {result['af_vib']}")
    print(f"AF_Total:       {result['af_total']}")

    # 驗證總加速因子
    expected_total = result['af_t'] * result['af_rh'] * result['af_v'] * result['af_tc'] * result['af_vib']
    # 使用相對誤差來驗證（因為數值很大）
    rel_error = abs(result['af_total'] - expected_total) / expected_total
    assert rel_error < 0.0001, \
        f"AF Total 計算錯誤: {result['af_total']} vs {expected_total} (相對誤差: {rel_error*100:.4f}%)"

    print("✓ 所有加速因子同時啟用計算正確\n")
    return result

if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("加速因子兼容性測試")
    print("=" * 60 + "\n")

    try:
        # 執行所有測試
        test_original_calculation()
        test_with_voltage()
        test_with_thermal_cycling()
        test_with_vibration()
        test_all_factors_enabled()

        print("=" * 60)
        print("✓ 所有測試通過！")
        print("✓ 新功能不影響原有計算邏輯")
        print("=" * 60)

    except AssertionError as e:
        print(f"\n❌ 測試失敗: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 發生錯誤: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
