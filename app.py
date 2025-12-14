import os
import numpy as np
from flask import Flask, render_template, request, jsonify
from scipy import stats, special
from datetime import datetime

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

# --- 核心計算邏輯 ---

def calculate_af(params):
    """
    計算加速因子 (AF Total)
    基於 Arrhenius (溫度), Peck (濕度), Inverse Power Law (電壓),
    Coffin-Manson (熱循環), IPL (振動) 模型
    """
    try:
        # 提取基本參數
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

        # 提取啟用標誌 (預設溫度和濕度啟用，其他停用)
        enable_temp = params.get('enable_temp', True)
        enable_hum = params.get('enable_hum', True)
        enable_voltage = params.get('enable_voltage', False)
        enable_tc = params.get('enable_tc', False)  # Thermal Cycling
        enable_vib = params.get('enable_vib', False)  # Vibration
        enable_uv = params.get('enable_uv', False)  # UV Radiation
        enable_chem = params.get('enable_chem', False)  # Chemical Concentration

        # 溫度轉換 (Celsius to Kelvin)
        temp_use_k = t_use + 273.15
        temp_alt_k = t_alt + 273.15

        # 1. 溫度加速 (AF_T) - Arrhenius
        # Formula: exp( (Ea/k) * (1/T_use - 1/T_alt) )
        if enable_temp:
            af_t = np.exp((ea / kb) * (1/temp_use_k - 1/temp_alt_k))
        else:
            af_t = 1.0

        # 2. 濕度加速 (AF_RH) - Peck's Model
        # Formula: (RH_alt / RH_use) ^ n
        if enable_hum:
            af_rh = (rh_alt / rh_use) ** n_hum
        else:
            af_rh = 1.0

        # 3. 電壓加速 (AF_V) - Inverse Power Law
        # Formula: (V_alt / V_use) ^ beta
        # 注意：若 V_alt 和 V_use 相同，此項為 1
        if enable_voltage:
            af_v = (v_alt / v_use) ** beta_v
        else:
            af_v = 1.0

        # 4. 熱循環加速 (AF_TC) - Coffin-Manson Model
        # Formula: (ΔT_alt / ΔT_use)^β × (f_alt / f_use)^α
        # 參考：JESD22-A104C, Indium Corporation研究
        if enable_tc:
            dt_use = float(params.get('dt_use', 70))  # 使用溫度範圍 (°C)
            dt_alt = float(params.get('dt_alt', 165))  # 測試溫度範圍 (°C)
            f_use = float(params.get('f_use', 1/24))  # 使用循環頻率 (cycles/hr), 預設 1次/天
            f_alt = float(params.get('f_alt', 2))  # 測試循環頻率 (cycles/hr), 預設 2次/hr
            alpha_tc = float(params.get('alpha_tc', 0.33))  # 頻率指數, 典型值 0.33
            beta_tc = float(params.get('beta_tc', 1.9))  # 溫度指數, 典型值 1.9 (焊點)

            af_tc = ((dt_alt / dt_use) ** beta_tc) * ((f_alt / f_use) ** alpha_tc)
        else:
            af_tc = 1.0

        # 5. 振動加速 (AF_VIB) - Inverse Power Law
        # Formula: (G_alt / G_use)^n
        # 參考：JESD22-B103-B
        if enable_vib:
            g_use = float(params.get('g_use', 1.0))  # 使用振動加速度 (g)
            g_alt = float(params.get('g_alt', 20.0))  # 測試振動加速度 (g), JEDEC標準
            n_vib = float(params.get('n_vib', 8.0))  # 功率指數, 典型值 8.0 (焊點疲勞)

            af_vib = (g_alt / g_use) ** n_vib
        else:
            af_vib = 1.0

        # 6. 紫外線輻射加速 (AF_UV) - 實驗比對模型
        # Formula: t_field / t_accelerated
        # 參考：ASTM G155, ISO 4892
        if enable_uv:
            t_field_uv = float(params.get('t_field_uv', 8760))  # 現場暴露時間 (小時)
            t_accel_uv = float(params.get('t_accel_uv', 1000))  # 加速測試時間 (小時)

            af_uv = t_field_uv / t_accel_uv
        else:
            af_uv = 1.0

        # 7. 化學濃度加速 (AF_CHEM) - Inverse Power Law
        # Formula: (C_alt / C_use)^n
        # 參考：Corrosion degradation models
        if enable_chem:
            c_use = float(params.get('c_use', 1.0))  # 使用濃度 (相對單位)
            c_alt = float(params.get('c_alt', 5.0))  # 測試濃度 (相對單位)
            n_chem = float(params.get('n_chem', 2.0))  # 功率指數, 典型值 1.5-3.0

            af_chem = (c_alt / c_use) ** n_chem
        else:
            af_chem = 1.0

        # 8. 輻射劑量加速 (AF_RAD) - Total Ionizing Dose (TID) Model
        # Formula: (D_alt / D_use)^n
        # 參考：MIL-STD-883, ESCC Basic Specification No. 22900
        enable_rad = params.get('enable_rad', False)
        if enable_rad:
            d_use = float(params.get('d_use', 10))  # 使用環境累積劑量 (krad)
            d_alt = float(params.get('d_alt', 100))  # 測試累積劑量 (krad)
            n_rad = float(params.get('n_rad', 1.0))  # 劑量敏感度指數, 典型值 0.5-2.0
            # dose_rate 用於記錄但不直接影響AF（劑量率效應需要更複雜的模型）

            af_rad = (d_alt / d_use) ** n_rad
        else:
            af_rad = 1.0

        # 9. Eyring 模型 (應力交互作用)
        # 用於處理溫度與非熱應力的交互效應
        enable_eyring = params.get('enable_eyring', False)
        af_eyring_correction = 1.0  # Eyring修正因子

        if enable_eyring:
            # 提取Eyring參數
            stress_type = params.get('eyring_stress_type', 'voltage')
            eyring_d = float(params.get('eyring_d', 0.1))  # 交互作用參數
            eyring_a = float(params.get('eyring_a', 1000))  # 模型常數A
            eyring_b = float(params.get('eyring_b', 2.0))   # 應力指數B

            # 根據選擇的應力類型獲取應力值
            if stress_type == 'voltage':
                s_use = v_use
                s_alt = v_alt
            elif stress_type == 'humidity':
                s_use = rh_use
                s_alt = rh_alt
            else:
                s_use = 1.0
                s_alt = 1.0

            # 廣義Eyring模型: t = A × (1/S)^B × e^(Ea/kT) × e^(D×S/T)
            # 計算使用條件下的壽命 t_use
            t_use_eyring = (eyring_a *
                           (1.0 / s_use) ** eyring_b *
                           np.exp(ea / (kb * temp_use_k)) *
                           np.exp(eyring_d * s_use / temp_use_k))

            # 計算測試條件下的壽命 t_alt
            t_alt_eyring = (eyring_a *
                           (1.0 / s_alt) ** eyring_b *
                           np.exp(ea / (kb * temp_alt_k)) *
                           np.exp(eyring_d * s_alt / temp_alt_k))

            # Eyring 加速因子 = t_use / t_alt
            af_eyring = t_use_eyring / t_alt_eyring

            # 計算Eyring修正因子（相對於簡單相乘的差異）
            # 簡單模型: AF_simple = AF_T × AF_S
            if stress_type == 'voltage' and enable_voltage:
                af_simple = af_t * af_v
                af_eyring_correction = af_eyring / af_simple if af_simple > 0 else 1.0
            elif stress_type == 'humidity' and enable_hum:
                af_simple = af_t * af_rh
                af_eyring_correction = af_eyring / af_simple if af_simple > 0 else 1.0

        # 總加速因子計算
        if enable_eyring:
            # 使用Eyring模型時，應用修正因子
            af_total = af_t * af_rh * af_v * af_tc * af_vib * af_uv * af_chem * af_rad * af_eyring_correction
        else:
            # 簡化模型：假設應力獨立
            af_total = af_t * af_rh * af_v * af_tc * af_vib * af_uv * af_chem * af_rad

        return {
            "af_t": round(af_t, 4),
            "af_rh": round(af_rh, 4),
            "af_v": round(af_v, 4),
            "af_tc": round(af_tc, 4),
            "af_vib": round(af_vib, 4),
            "af_uv": round(af_uv, 4),
            "af_chem": round(af_chem, 4),
            "af_rad": round(af_rad, 4),
            "af_eyring_correction": round(af_eyring_correction, 4) if enable_eyring else None,
            "af_total": round(af_total, 4)
        }
    except Exception as e:
        return {"error": str(e)}

def calculate_weibull(failures, suspensions, options=None):
    """
    Weibull 分析 - 支持多種中位秩方法和回歸方法

    Args:
        failures: 失效時間列表
        suspensions: 截尾數據（保留兼容性）
        options: 選項字典 {
            'median_rank_method': 'benard' | 'exact' | 'mean',
            'regression_method': 'rry' | 'rrx' | 'mle'
        }
    """
    try:
        # 設定預設選項
        if options is None:
            options = {}
        median_rank_method = options.get('median_rank_method', 'benard')
        regression_method = options.get('regression_method', 'rry')

        # 數據預處理
        failures = sorted([float(x) for x in failures])
        n_failures = len(failures)
        n_total = max(n_failures, 64) # 預設總數

        if n_failures < 2:
            return {"error": "失效數據不足，無法進行 Weibull 擬合 (至少需要 2 點)"}

        # 計算中位秩
        ranks = []
        for i in range(1, n_failures + 1):
            if median_rank_method == 'benard':
                # Benard's Approximation (最常用)
                f = (i - 0.3) / (n_total + 0.4)
            elif median_rank_method == 'exact':
                # 精確中位秩 (使用 Beta 分佈的中位數)
                # F = Beta_inv(0.5, i, n-i+1)
                f = stats.beta.ppf(0.5, i, n_total - i + 1)
            elif median_rank_method == 'mean':
                # 平均秩 (Mean Rank)
                f = i / (n_total + 1)
            else:
                # 預設使用 Benard's
                f = (i - 0.3) / (n_total + 0.4)

            ranks.append(f)

        # 準備回歸數據
        t_vals = []
        f_vals = []
        for i, (t, f) in enumerate(zip(failures, ranks)):
            if t <= 0 or f >= 1 or f <= 0:
                continue
            t_vals.append(t)
            f_vals.append(f)

        # 根據回歸方法選擇
        if regression_method == 'mle':
            # 最大似然估計 (MLE)
            # 使用 scipy.stats.weibull_min.fit
            shape, loc, scale = stats.weibull_min.fit(failures, floc=0)
            beta = shape
            eta_alt = scale
            r_squared = 0.999  # MLE 不提供 R²，給一個高值表示最優擬合

        else:
            # Rank Regression (RRX 或 RRY)
            # 轉換為線性關係: ln(-ln(1-F)) = beta * ln(t) - beta * ln(eta)
            x_vals = []  # ln(t)
            y_vals = []  # ln(-ln(1-F))

            for t, f in zip(t_vals, f_vals):
                x = np.log(t)
                y = np.log(-np.log(1 - f))
                x_vals.append(x)
                y_vals.append(y)

            if regression_method == 'rrx':
                # Rank Regression on X (minimize x residuals)
                # 相當於 y = f(x) 的反函數，交換 x 和 y
                slope, intercept, r_value, _, _ = stats.linregress(y_vals, x_vals)
                beta = 1 / slope
                eta_alt = np.exp(intercept / slope)
                r_squared = r_value ** 2
            else:
                # Rank Regression on Y (預設，minimize y residuals)
                slope, intercept, r_value, _, _ = stats.linregress(x_vals, y_vals)
                beta = slope
                eta_alt = np.exp(-intercept / beta)
                r_squared = r_value ** 2

        return {
            "beta": round(beta, 4),
            "eta_alt": round(eta_alt, 4),
            "r_squared": round(r_squared, 4),
            "method": f"{median_rank_method.upper()} + {regression_method.upper()}",
            "plot_data": {
                "x": [np.log(t) for t in t_vals],  # ln(t) for plotting line
                "y": [np.log(-np.log(1 - f)) for f in f_vals],  # Transformed probability
                "t": t_vals,  # Original time for scatter
                "f": f_vals   # Probability for scatter
            }
        }
    except Exception as e:
        return {"error": str(e)}

def calculate_reliability_results(af_total, weibull_params, zero_fail_params, t_mission=17520, bx_percent=1):
    """
    整合計算：可靠度推算 (包含 Weibull 模式與零失效模式)
    t_mission: 任務時間（小時），預設 17520 小時 (2 年)
    bx_percent: Bx% 壽命的百分比 (1, 10, 50 等)，預設 1
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
        # t_mission 由參數傳入
        r_mission = np.exp(-((t_mission / eta_use) ** beta))

        # Bx% Life (動態計算)
        # t = eta * (-ln(1-x/100))^(1/beta)
        bx_life = eta_use * ((-np.log(1 - bx_percent / 100)) ** (1/beta))

        results["weibull"] = {
            "eta_use": round(eta_use, 2),
            "mttf_use": round(mttf_use, 2),
            "r_mission": round(r_mission, 6),
            "bx_life": round(bx_life, 2),
            "bx_percent": bx_percent  # 記錄使用的百分比
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
            # t_mission 由參數傳入
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

@app.route('/guide')
def guide():
    return render_template('guide.html')

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
    weibull_data = data.get('weibull_data', {})
    failures = weibull_data.get('failures', [])
    weibull_options = weibull_data.get('options', {})
    if failures and len(failures) > 0:
        weibull_result = calculate_weibull(failures, 0, weibull_options)

    # 3. 零失效分析參數
    zero_fail_params = data.get('zero_fail_params', {})

    # 4. Mission Time (Mission Time)
    try:
        mission_years = float(data.get('mission_years', 2))
        if mission_years <= 0:
            mission_years = 2
    except:
        mission_years = 2

    t_mission = mission_years * 8760 # Convert to hours

    # 5. 提取 Bx% 選項
    bx_percent = weibull_options.get('bx_life_percent', 1)  # 預設 B1%

    # 6. 綜合結果
    final_results = calculate_reliability_results(af_total, weibull_result, zero_fail_params, t_mission, bx_percent)
    
    return jsonify({
        "af_result": af_result,
        "weibull_result": weibull_result,
        "reliability_result": final_results
    })

@app.route('/generate_report', methods=['POST'])
def generate_report():
    """生成測試報告 (PDF 或 Word)"""
    try:
        from flask import send_file
        import traceback

        # 獲取請求數據
        data = request.get_json()

        if not data:
            print("ERROR: No data received")
            return jsonify({"error": "No data received"}), 400

        # 獲取格式參數 (默認為 PDF)
        report_format = data.get('format', 'pdf').lower()
        print(f"\n=== Report Generation Request (Format: {report_format.upper()}) ===")
        print(f"Received data with keys: {data.keys()}")

        # 根據格式生成報告
        if report_format == 'word':
            # 生成 Word 文件
            from word_generator import generate_report_from_request as generate_word
            print("Calling Word generator...")
            report_buffer = generate_word(data)
            print("Word buffer generated successfully")

            # 返回 Word 文件
            filename = f'Reliability_Test_Report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.docx'
            mimetype = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        else:
            # 生成 PDF 文件 (默認)
            from report_generator import generate_report_from_request as generate_pdf
            print("Calling PDF generator...")
            report_buffer = generate_pdf(data)
            print("PDF buffer generated successfully")

            # 返回 PDF 文件
            filename = f'Reliability_Test_Report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
            mimetype = 'application/pdf'

        print(f"Sending file: {filename}")

        return send_file(
            report_buffer,
            mimetype=mimetype,
            as_attachment=True,
            download_name=filename
        )

    except Exception as e:
        print(f"\n!!! ERROR in generate_report: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e), "traceback": traceback.format_exc()}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
