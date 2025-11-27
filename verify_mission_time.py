import urllib.request
import json

# 設定 API URL
url = "http://127.0.0.1:5000/calculate"

# 基礎參數 (Zero Failure Mode)
base_payload = {
    "af_params": {
        "t_use": 32, "rh_use": 60, "v_use": 1.0,
        "t_alt": 70, "rh_alt": 90, "v_alt": 1.0,
        "ea": 1.0, "n_hum": 2.0, "beta_v": 1.0
    },
    "weibull_data": { "failures": [] }, # 無失效數據 -> 觸發零失效模式
    "zero_fail_params": {
        "n": 64,
        "t_test": 1196,
        "cl": 0.6
    }
}

def test_mission_time(years):
    payload = base_payload.copy()
    payload["mission_years"] = years
    
    try:
        req = urllib.request.Request(url)
        req.add_header('Content-Type', 'application/json; charset=utf-8')
        jsondata = json.dumps(payload)
        jsondataasbytes = jsondata.encode('utf-8')
        req.add_header('Content-Length', len(jsondataasbytes))
        
        response = urllib.request.urlopen(req, jsondataasbytes)
        data = json.loads(response.read())
        
        zf_result = data["reliability_result"]["zero_failure"]
        r_mission = zf_result["r_mission"]
        print(f"--- 測試任務時間: {years} 年 ---")
        print(f"可靠度 R(t): {r_mission * 100:.4f}%")
        return r_mission

    except Exception as e:
        print(f"Connection Error: {e}")
        return None

print("開始驗證任務時間功能...\n")

# 測試 1: 2 年 (標準)
r_2_years = test_mission_time(2)

# 測試 2: 5 年 (更長)
r_5_years = test_mission_time(5)

print("\n--- 驗證結果 ---")
if r_2_years is not None and r_5_years is not None:
    if r_5_years < r_2_years:
        print("✅ 通過: 5 年的可靠度低於 2 年 (符合預期)")
        print(f"   差異: {(r_2_years - r_5_years)*100:.4f}%")
    else:
        print("❌ 失敗: 5 年的可靠度不應高於或等於 2 年")
else:
    print("❌ 測試無法完成 (API 連線失敗)")
