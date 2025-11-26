import os
import numpy as np
from flask import Flask, render_template, request, jsonify
from scipy import stats, special

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

# --- 核心計算邏輯 ---

def calculate_af(params):
    """
    計算加速因子 (AF Total)
    基於 Arrhenius (溫度), Peck (濕度), Inverse Power Law (電壓) 模型
    """
    try:
        # 提取參數
        t_use = float(params.get('t_use', 32))
        rh_use = float(params.get('rh_use', 60))
        v_use = float(params.get('v_use', 1.0)) # 假設 V_use = V_rated
        
        t_alt = float(params.get('t_alt', 70))
        rh_alt = float(params.get('rh_alt', 90))
        v_alt = float(params.get('v_alt', 1.0)) # 假設 V_alt = V_rated (或使用者輸入)
        
        ea = float(params.get('ea', 1.0))
        n_hum = float(params.get('n_hum', 2.0))
        beta_v = float(params.get('beta_v', 1.0))
        
        kb = 8.617e-5  # Boltzmann constant eV/K

        # 溫度轉換 (Celsius to Kelvin)
        temp_use_k = t_use + 273.15
        temp_alt_k = t_alt + 273.15

        # 1. 溫度加速 (AF_T) - Arrhenius
        # Formula: exp( (Ea/k) * (1/T_use - 1/T_alt) )
        af_t = np.exp((ea / kb) * (1/temp_use_k - 1/temp_alt_k))

        # 2. 濕度加速 (AF_RH) - Peck's Model
        # Formula: (RH_alt / RH_use) ^ n
        af_rh = (rh_alt / rh_use) ** n_hum

        # 3. 電壓加速 (AF_V) - Inverse Power Law
        # Formula: (V_alt / V_use) ^ beta
        # 注意：若 V_alt 和 V_use 相同，此項為 1
        af_v = (v_alt / v_use) ** beta_v

        # 總加速因子
        af_total = af_t * af_rh * af_v
        
        return {
            "af_t": round(af_t, 4),
            "af_rh": round(af_rh, 4),
            "af_v": round(af_v, 4),
            "af_total": round(af_total, 4)
        }
    except Exception as e:
        return {"error": str(e)}

def calculate_weibull(failures, suspensions):
    """
    Weibull 分析 (Rank Regression on X and Y)
    使用 Benard's Approximation 處理秩
    """
    try:
        # 數據預處理
        failures = sorted([float(x) for x in failures])
        n_failures = len(failures)
        n_total = 64 # 預設總數，或由前端傳入 (failures + suspensions)
        
        # 如果前端傳來的是具體的截尾時間列表，則計算數量；
        # 這裡簡化假設使用者輸入的是「失效時間列表」和「總樣品數N」
        # 實際上，Rank計算需要知道總樣本數 N
        
        # 為了符合 Rank Regression 的標準做法：
        # 1. 將所有數據排序 (失效 + 截尾)
        # 2. 計算 Order Number (i)
        # 3. 計算 Median Rank (F)
        # 4. 僅對「失效數據」進行線性迴歸
        
        # 這裡簡化實作：假設截尾數據都大於失效數據 (Type I/II Censoring)
        # 這是最常見的情境 (測試到某個時間點停止，存活的都算截尾)
        # 在這種情況下，失效數據的 Rank 就是它們在排序後的自然順序 1, 2, ..., r
        
        if n_failures < 2:
            return {"error": "失效數據不足，無法進行 Weibull 擬合 (至少需要 2 點)"}

        # 準備迴歸數據
        x_vals = [] # ln(t)
        y_vals = [] # ln(-ln(1-F))
        ranks = []
        
        for i in range(1, n_failures + 1):
            # Benard's Approximation
            # F = (i - 0.3) / (N + 0.4)
            # 注意：這裡的 N 應該是總樣本數 (失效 + 存活)
            # 我們需要從前端獲取 N，這裡暫時假設 N = 64 (根據題目)
            # 為了通用性，我們應該讓 N = max(64, n_failures + suspensions)
            # 這裡我們先用傳入的參數
            
            n_total_calc = max(n_failures, 64) # 預設 64，若失效更多則取失效數
            
            f = (i - 0.3) / (n_total_calc + 0.4)
            ranks.append(f)
            
            t = failures[i-1]
            if t <= 0: continue # 忽略非正時間
            
            x = np.log(t)
            y = np.log(-np.log(1 - f))
            
            x_vals.append(x)
            y_vals.append(y)

        # 線性迴歸
        slope, intercept, r_value, p_value, std_err = stats.linregress(x_vals, y_vals)
        
        beta = slope
        # intercept = -beta * ln(eta)  =>  ln(eta) = -intercept / beta  => eta = exp(...)
        eta_alt = np.exp(-intercept / beta)
        
        return {
            "beta": round(beta, 4),
            "eta_alt": round(eta_alt, 4),
            "r_squared": round(r_value**2, 4),
            "plot_data": {
                "x": x_vals, # ln(t) for plotting line
                "y": y_vals, # Transformed probability
                "t": failures, # Original time for scatter
                "f": ranks     # Probability for scatter
            }
        }
    except Exception as e:
        return {"error": str(e)}

def calculate_reliability_results(af_total, weibull_params, zero_fail_params):
    """
    整合計算：可靠度推算 (包含 Weibull 模式與零失效模式)
    """
    results = {}
    
    # --- 模式 1: Weibull 分析 (r > 0) ---
    if weibull_params and "beta" in weibull_params:
        beta = weibull_params["beta"]
        eta_alt = weibull_params["eta_alt"]
        
        # 現場特性壽命
        eta_use = eta_alt * af_total
        
        # MTTF (Weibull Mean) = eta * Gamma(1 + 1/beta)
        mttf_use = eta_use * special.gamma(1 + 1/beta)
        
        # 任務可靠度 R(t)
        t_mission = 17520 # 2 years in hours
        r_mission = np.exp(-((t_mission / eta_use) ** beta))
        
        # B1% Life
        # t = eta * (-ln(1-0.01))^(1/beta)
        b1_life = eta_use * ((-np.log(1 - 0.01)) ** (1/beta))
        
        results["weibull"] = {
            "eta_use": round(eta_use, 2),
            "mttf_use": round(mttf_use, 2),
            "r_mission": round(r_mission, 6),
            "b1_life": round(b1_life, 2)
        }

    # --- 模式 2: 零失效分析 (r = 0) ---
    if zero_fail_params:
        try:
            n_samples = int(zero_fail_params.get("n", 64))
            t_test = float(zero_fail_params.get("t_test", 1196))
            cl = float(zero_fail_params.get("cl", 0.6)) # Confidence Level (e.g., 0.6)
            
            # 總元件時數
            total_hours_alt = n_samples * t_test
            
            # Chi-Squared Value
            # Excel: CHISQ.INV.RT(1-CL, 2) -> Python: chi2.ppf(CL, 2)
            # Degrees of freedom = 2*(r+1) where r=0 => df=2
            chi_sq = stats.chi2.ppf(cl, 2)
            
            # MTTF Lower Limit (ALT)
            mttf_alt_lower = (2 * total_hours_alt) / chi_sq
            
            # Failure Rate Upper Limit (ALT) in FITs
            # FITs = (1/MTTF) * 10^9
            lambda_alt_upper = (1 / mttf_alt_lower) * 1e9
            
            # 轉換至現場條件
            mttf_use_lower = mttf_alt_lower * af_total
            lambda_use_upper = lambda_alt_upper / af_total
            
            # 任務可靠度 R(t) - 指數分佈
            # R(t) = exp(-lambda * t)
            # lambda 單位需換回 failures/hour: lambda_use_upper * 1e-9
            t_mission = 17520
            lambda_use_raw = lambda_use_upper * 1e-9
            r_mission_zf = np.exp(-lambda_use_raw * t_mission)
            
            results["zero_failure"] = {
                "total_hours_alt": total_hours_alt,
                "chi_sq": round(chi_sq, 4),
                "mttf_alt_lower": round(mttf_alt_lower, 2),
                "lambda_alt_upper": round(lambda_alt_upper, 2),
                "mttf_use_lower": round(mttf_use_lower, 2),
                "lambda_use_upper": round(lambda_use_upper, 2),
                "r_mission": round(r_mission_zf, 6)
            }
            
        except Exception as e:
            results["zero_failure_error"] = str(e)

    return results

# --- Routes ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/calculate', methods=['POST'])
def calculate():
    data = request.json
    
    # 1. 計算 AF
    af_params = data.get('af_params', {})
    af_result = calculate_af(af_params)
    
    if "error" in af_result:
        return jsonify({"error": "AF 計算錯誤: " + af_result["error"]}), 400
        
    af_total = af_result["af_total"]
    
    # 2. Weibull 分析 (如果有的話)
    weibull_result = {}
    failures = data.get('weibull_data', {}).get('failures', [])
    if failures and len(failures) > 0:
        weibull_result = calculate_weibull(failures, 0) # 暫時忽略 suspensions 參數，假設 N=64 固定或由前端處理
    
    # 3. 零失效分析參數
    zero_fail_params = data.get('zero_fail_params', {})
    
    # 4. 綜合結果
    final_results = calculate_reliability_results(af_total, weibull_result, zero_fail_params)
    
    return jsonify({
        "af_result": af_result,
        "weibull_result": weibull_result,
        "reliability_result": final_results
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)
