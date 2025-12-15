// Handle Ea selection change
function handleEaSelectChange() {
    const selectValue = document.getElementById('ea_select').value;
    const eaInput = document.getElementById('ea');

    if (selectValue === 'custom') {
        // Show custom input field
        eaInput.classList.remove('d-none');
        eaInput.focus();
    } else {
        // Hide custom input and set value from selection
        eaInput.classList.add('d-none');
        // Extract numeric value (remove suffix like _cap, _solder)
        const numericValue = parseFloat(selectValue.split('_')[0]);
        eaInput.value = numericValue;
    }
}

// Toggle function for AF sections and result cards
function toggleAFSection(afType) {
    if (afType === 'tc') {
        const tcSection = document.getElementById('tc_section');
        const tcCard = document.getElementById('af_tc_card');
        const isEnabled = document.getElementById('enable_tc').checked;
        tcSection.style.display = isEnabled ? 'block' : 'none';
        tcCard.style.display = isEnabled ? 'block' : 'none';
    } else if (afType === 'vib') {
        const vibSection = document.getElementById('vib_section');
        const vibCard = document.getElementById('af_vib_card');
        const isEnabled = document.getElementById('enable_vib').checked;
        vibSection.style.display = isEnabled ? 'block' : 'none';
        vibCard.style.display = isEnabled ? 'block' : 'none';
    } else if (afType === 'voltage') {
        const voltageSection = document.getElementById('voltage_section');
        const vCard = document.getElementById('af_v_card');
        const isEnabled = document.getElementById('enable_voltage').checked;
        voltageSection.style.display = isEnabled ? 'block' : 'none';
        vCard.style.display = isEnabled ? 'block' : 'none';
    } else if (afType === 'uv') {
        const uvSection = document.getElementById('uv_section');
        const uvCard = document.getElementById('af_uv_card');
        const isEnabled = document.getElementById('enable_uv').checked;
        uvSection.style.display = isEnabled ? 'block' : 'none';
        uvCard.style.display = isEnabled ? 'block' : 'none';
    } else if (afType === 'chem') {
        const chemSection = document.getElementById('chem_section');
        const chemCard = document.getElementById('af_chem_card');
        const isEnabled = document.getElementById('enable_chem').checked;
        chemSection.style.display = isEnabled ? 'block' : 'none';
        chemCard.style.display = isEnabled ? 'block' : 'none';
    } else if (afType === 'rad') {
        const radSection = document.getElementById('rad_section');
        const radCard = document.getElementById('af_rad_card');
        const isEnabled = document.getElementById('enable_rad').checked;
        radSection.style.display = isEnabled ? 'block' : 'none';
        radCard.style.display = isEnabled ? 'block' : 'none';
    }
}

// Toggle Eyring model section
function toggleEyringMode() {
    const eyringSection = document.getElementById('eyring_section');
    const isEnabled = document.getElementById('enable_eyring').checked;
    eyringSection.style.display = isEnabled ? 'block' : 'none';
}

function calculate() {
    // 1. 收集 AF 參數（包含啟用標誌）
    const afParams = {
        // 基本參數
        t_use: document.getElementById('t_use').value,
        rh_use: document.getElementById('rh_use').value,
        t_alt: document.getElementById('t_alt').value,
        rh_alt: document.getElementById('rh_alt').value,
        ea: document.getElementById('ea').value,
        n_hum: document.getElementById('n_hum').value,

        // 啟用標誌
        enable_temp: document.getElementById('enable_temp').checked,
        enable_hum: document.getElementById('enable_hum').checked,
        enable_voltage: document.getElementById('enable_voltage').checked,
        enable_tc: document.getElementById('enable_tc').checked,
        enable_vib: document.getElementById('enable_vib').checked,
        enable_uv: document.getElementById('enable_uv').checked,
        enable_chem: document.getElementById('enable_chem').checked,
        enable_rad: document.getElementById('enable_rad').checked
    };

    // 如果電壓啟用，添加參數
    if (afParams.enable_voltage) {
        afParams.v_use = document.getElementById('v_use').value;
        afParams.v_alt = document.getElementById('v_alt').value;
        afParams.beta_v = document.getElementById('beta_v').value;
    }

    // 如果熱循環啟用，添加參數
    if (afParams.enable_tc) {
        afParams.dt_use = document.getElementById('dt_use').value;
        afParams.dt_alt = document.getElementById('dt_alt').value;
        afParams.f_use = document.getElementById('f_use').value;
        afParams.f_alt = document.getElementById('f_alt').value;
        afParams.alpha_tc = document.getElementById('alpha_tc').value;
        afParams.beta_tc = document.getElementById('beta_tc').value;
    }

    // 如果振動啟用，添加參數
    if (afParams.enable_vib) {
        afParams.g_use = document.getElementById('g_use').value;
        afParams.g_alt = document.getElementById('g_alt').value;
        afParams.n_vib = document.getElementById('n_vib').value;
    }

    // 如果UV啟用，添加參數
    if (afParams.enable_uv) {
        afParams.t_field_uv = document.getElementById('t_field_uv').value;
        afParams.t_accel_uv = document.getElementById('t_accel_uv').value;
    }

    // 如果化學濃度啟用，添加參數
    if (afParams.enable_chem) {
        afParams.c_use = document.getElementById('c_use').value;
        afParams.c_alt = document.getElementById('c_alt').value;
        afParams.n_chem = document.getElementById('n_chem').value;
    }

    // 如果輻射劑量啟用，添加參數
    if (afParams.enable_rad) {
        afParams.d_use = document.getElementById('d_use').value;
        afParams.d_alt = document.getElementById('d_alt').value;
        afParams.dose_rate = document.getElementById('dose_rate').value;
        afParams.n_rad = document.getElementById('n_rad').value;
    }

    // 如果Eyring模型啟用，添加參數
    afParams.enable_eyring = document.getElementById('enable_eyring').checked;
    if (afParams.enable_eyring) {
        afParams.eyring_stress_type = document.getElementById('eyring_stress_type').value;
        afParams.eyring_d = document.getElementById('eyring_d').value;
        afParams.eyring_a = document.getElementById('eyring_a').value;
        afParams.eyring_b = document.getElementById('eyring_b').value;
    }

    // 2. 收集 Weibull 數據
    const failuresInput = document.getElementById('failures_input').value;
    let failures = [];
    if (failuresInput.trim() !== "") {
        failures = failuresInput.split(/[,;\s]+/).map(Number).filter(n => !isNaN(n) && n > 0);
    }

    // 2.1 收集 Weibull 分析方法選項
    const weibullOptions = {
        median_rank_method: document.getElementById('median_rank_method').value,
        regression_method: document.getElementById('regression_method').value,
        bx_life_percent: parseFloat(document.getElementById('bx_life_percent').value)
    };

    // 3. 收集零失效參數
    const zeroFailParams = {
        n: document.getElementById('n_samples').value,
        t_test: document.getElementById('t_test').value,
        cl: document.getElementById('cl').value
    };

    // 4. 收集任務時間
    const missionYears = parseFloat(document.getElementById('mission_years').value) || 2;

    // 發送請求
    fetch('/calculate', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            af_params: afParams,
            weibull_data: {
                failures: failures,
                options: weibullOptions
            },
            zero_fail_params: zeroFailParams,
            mission_years: missionYears
        })
    })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                alert("Error: " + data.error);
                return;
            }
            updateUI(data, failures.length > 0);
        })
        .catch(error => {
            console.error('Error:', error);
            alert("發生錯誤，請檢查控制台");
        });
}

// 全域變數儲存當前數據
let currentData = null;
let currentMode = null; // 'weibull' or 'zero_failure'
let currentChartType = 'reliability'; // 'reliability', 'hazard', 'pdf'

// 動態調整 AF 結果字體大小的函數
function adjustAFTextSize(elementId, value) {
    const elem = document.getElementById(elementId);
    elem.innerText = value;

    const textLength = value.toString().length;
    const isTotal = elementId === 'res_af_total';

    // 根據數字長度調整字體大小
    if (textLength <= 8) {
        elem.style.fontSize = isTotal ? '1.75rem' : '1.5rem';
    } else if (textLength <= 12) {
        elem.style.fontSize = isTotal ? '1.3rem' : '1.1rem';
    } else if (textLength <= 16) {
        elem.style.fontSize = isTotal ? '1rem' : '0.9rem';
    } else {
        elem.style.fontSize = isTotal ? '0.8rem' : '0.7rem';
    }
}

function updateUI(data, hasFailures) {
    // 更新 AF 結果並動態調整字體大小
    adjustAFTextSize('res_af_t', data.af_result.af_t);
    adjustAFTextSize('res_af_rh', data.af_result.af_rh);
    adjustAFTextSize('res_af_v', data.af_result.af_v);
    adjustAFTextSize('res_af_tc', data.af_result.af_tc || '1.0');
    adjustAFTextSize('res_af_vib', data.af_result.af_vib || '1.0');
    adjustAFTextSize('res_af_uv', data.af_result.af_uv || '1.0');
    adjustAFTextSize('res_af_chem', data.af_result.af_chem || '1.0');
    adjustAFTextSize('res_af_rad', data.af_result.af_rad || '1.0');
    adjustAFTextSize('res_af_total', data.af_result.af_total);

    const wbStats = document.getElementById('weibull_stats');
    const zfStats = document.getElementById('zf_stats');
    const badge = document.getElementById('analysis_mode_badge');

    // 儲存數據供切換圖表使用
    currentData = data;

    // 讀取任務時間
    const missionYears = parseFloat(document.getElementById('mission_years').value) || 2;

    // 根據是否有失效數據切換顯示模式
    if (hasFailures && data.weibull_result && !data.weibull_result.error) {
        // --- Weibull Mode ---
        currentMode = 'weibull';
        wbStats.classList.remove('d-none');
        zfStats.classList.add('d-none');
        badge.innerText = "Weibull Analysis (r > 0)";
        badge.className = "badge bg-warning text-dark";

        const res = data.reliability_result.weibull;
        document.getElementById('wb_mttf').innerText = res.mttf_use.toLocaleString() + " hrs";

        // 動態顯示 Bx% Life
        const bxPercent = res.bx_percent || 1;
        document.getElementById('wb_bx_label').innerText = `B${bxPercent}% Life`;
        document.getElementById('wb_b1').innerText = res.bx_life.toLocaleString() + " hrs";

        document.getElementById('wb_rel').innerText = (res.r_mission * 100).toFixed(4) + "%";
        document.getElementById('wb_rel_label').innerText = `Reliability (${missionYears} Years)`;

        // 計算等效現場時間
        const testTime = parseFloat(document.getElementById('t_test').value) || 0;
        const afTotal = data.af_result.af_total;
        const equivalentTime = testTime * afTotal;
        const equivalentYears = equivalentTime / 8760;

        document.getElementById('wb_eq_time').innerText = equivalentTime.toLocaleString(undefined, {maximumFractionDigits: 2}) + " hrs";
        document.getElementById('wb_eq_detail').innerText = `~ ${equivalentYears.toLocaleString(undefined, {maximumFractionDigits: 2})} years (AF: ${afTotal.toLocaleString()} × ${testTime} hrs)`;

        document.getElementById('wb_beta').innerText = data.weibull_result.beta;
        document.getElementById('wb_eta').innerText = data.weibull_result.eta_alt;

    } else {
        // --- Zero Failure Mode ---
        currentMode = 'zero_failure';
        wbStats.classList.add('d-none');
        zfStats.classList.remove('d-none');
        badge.innerText = "Zero-Failure Analysis (r = 0)";
        badge.className = "badge bg-success";

        const res = data.reliability_result.zero_failure;
        if (res) {
            document.getElementById('zf_mttf').innerText = "> " + res.mttf_use_lower.toLocaleString() + " hrs";
            document.getElementById('zf_lambda').innerText = "< " + res.lambda_use_upper.toLocaleString() + " FITs";
            document.getElementById('zf_rel').innerText = (res.r_mission * 100).toFixed(4) + "%";
            document.getElementById('zf_rel_label').innerText = `Reliability (${missionYears} Years)`;
            document.getElementById('zf_cl_display').innerText = (document.getElementById('cl').value * 100) + "%";

            // 計算等效現場時間
            const testTime = parseFloat(document.getElementById('t_test').value) || 0;
            const afTotal = data.af_result.af_total;
            const equivalentTime = testTime * afTotal;
            const equivalentYears = equivalentTime / 8760;

            document.getElementById('zf_eq_time').innerText = equivalentTime.toLocaleString(undefined, {maximumFractionDigits: 2}) + " hrs";
            document.getElementById('zf_eq_detail').innerText = `~ ${equivalentYears.toLocaleString(undefined, {maximumFractionDigits: 2})} years (AF: ${afTotal.toLocaleString()} × ${testTime} hrs)`;
        } else {
            badge.innerText = "Error in Calculation";
            badge.className = "badge bg-danger";
        }
    }

    // 生成結論
    generateConclusion(data, hasFailures);

    // 繪製圖表 (預設 Reliability)
    // 重置 Radio Button
    document.getElementById('btn_rel').checked = true;
    switchChart('reliability');
}

function generateConclusion(data, hasFailures) {
    const panel = document.getElementById('conclusion_panel');
    const textElem = document.getElementById('conclusion_text');

    const t_use = document.getElementById('t_use').value;
    const rh_use = document.getElementById('rh_use').value;
    const mission_years = parseFloat(document.getElementById('mission_years').value) || 2;

    // 計算等效現場時間 (Equivalent Field Time)
    const t_test = parseFloat(document.getElementById('t_test').value) || 0;
    const af_total = data.af_result.af_total || 1;
    const equivalent_hours = t_test * af_total;
    const equivalent_years = (equivalent_hours / 8760).toFixed(2);
    const equivalent_field_time = `${equivalent_hours.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2})} hrs ~ <strong class="text-success">${equivalent_years} years</strong>`;

    let conclusionHTML = "";

    if (hasFailures && data.weibull_result && !data.weibull_result.error) {
        const res = data.reliability_result.weibull;
        const failuresInput = document.getElementById('failures_input').value;
        const n_failures = failuresInput.split(/[,;\s]+/).filter(n => n.trim() !== "").length;
        const bx_years = (res.bx_life / 8760).toFixed(2);
        const reliability_pct = (res.r_mission * 100).toFixed(2);
        const bx_percent = res.bx_percent || 1;

        // 根據 Bx% 選擇描述文字
        let bx_description = "";
        if (bx_percent === 1) {
            bx_description = "即預計只有 1% 的產品會失效的時間";
        } else if (bx_percent === 10) {
            bx_description = "即預計有 10% 的產品會失效的時間";
        } else if (bx_percent === 50) {
            bx_description = "即中位壽命，50% 產品會失效的時間";
        } else {
            bx_description = `即預計有 ${bx_percent}% 的產品會失效的時間`;
        }

        // 判斷 Bx% 壽命是否超過任務時間
        if (parseFloat(bx_years) >= mission_years) {
            // 正面結論：Bx% 壽命 ≥ 任務時間
            conclusionHTML = `
                我們進行了 <strong>${t_test.toLocaleString()} 小時</strong>的加速測試，相當於 <strong>${equivalent_field_time}</strong> 的現場使用壽命。
                <br><br>
                計算結果顯示，這批樣品的 <strong>B${bx_percent}% 壽命</strong>（${bx_description}）為 <strong>${bx_years} 年</strong> (${Math.round(res.bx_life).toLocaleString()} 小時)。
                <br><br>
                在 <strong>${mission_years} 年</strong>的任務期間內，預期可靠度為 <strong>${reliability_pct}%</strong>。
                這個數值證明了即使有 <strong>${n_failures}</strong> 個樣品失效，產品的整體可靠性邊際仍然充足。
                不過，我們必須對這 ${n_failures} 個失效進行追蹤，以確認是否屬於可預防的早期製造缺陷。
            `;
        } else {
            // 否定結論：Bx% 壽命 < 任務時間
            const failure_risk_pct = (100 - res.r_mission * 100).toFixed(2);
            conclusionHTML = `
                <strong class="text-warning">⚠️ 警告：可靠性不足</strong>
                <br><br>
                我們進行了 <strong>${t_test.toLocaleString()} 小時</strong>的加速測試，相當於 <strong>${equivalent_field_time}</strong> 的現場使用壽命。
                <br><br>
                計算結果顯示，這批樣品的 <strong>B${bx_percent}% 壽命</strong>僅為 <strong>${bx_years} 年</strong> (${Math.round(res.bx_life).toLocaleString()} 小時)，
                <strong class="text-danger">未達到 ${mission_years} 年的任務時間要求</strong>。
                <br><br>
                在 ${mission_years} 年任務期間內，預期可靠度僅為 <strong>${reliability_pct}%</strong>，失效風險高達 <strong class="text-danger">${failure_risk_pct}%</strong>。
                <br><br>
                <strong>建議措施：</strong>
                <ul class="mb-0 mt-2">
                    <li>重新評估產品設計或材料選擇</li>
                    <li>改善製程以降低失效率</li>
                    <li>縮短保固期或調整任務時間目標</li>
                    <li>針對 ${n_failures} 個失效樣品進行根因分析</li>
                </ul>
            `;
        }

    } else if (data.reliability_result.zero_failure) {
        const res = data.reliability_result.zero_failure;
        const reliability_pct = (res.r_mission * 100).toFixed(3);
        const failure_rate_pct = (100 - res.r_mission * 100).toFixed(3);
        const reliability_value = res.r_mission * 100;

        // 根據任務時間動態調整門檻標準
        // 參考文檔：數據說明.md - 業界可靠度門檻標準
        let thresholds = { excellent: 98.5, acceptable: 97.0 };
        let standardInfo = { avgRate: "1.5%", maxRate: "3%", source: "2年保固標準" };

        if (mission_years <= 1) {
            // 1年保固期標準
            thresholds = { excellent: 99.5, acceptable: 98.5 };
            standardInfo = { avgRate: "0.5%", maxRate: "1.5%", source: "1年保固標準（專家共識）" };
        } else if (mission_years <= 2) {
            // 2年保固期標準（預設）
            thresholds = { excellent: 98.5, acceptable: 97.0 };
            standardInfo = { avgRate: "1.5%", maxRate: "3%", source: "2年保固標準（美國電子業平均）" };
        } else if (mission_years <= 3) {
            // 3年保固期標準
            thresholds = { excellent: 90.0, acceptable: 85.0 };
            standardInfo = { avgRate: "10%", maxRate: "15%", source: "3年保固標準（筆電研究數據）" };
        } else {
            // 4-5年保固期標準
            thresholds = { excellent: 85.0, acceptable: 80.0 };
            standardInfo = { avgRate: "15%", maxRate: "20%", source: "4-5年保固標準（企業級/延長保固）" };
        }

        // 判斷可靠度等級
        if (reliability_value >= thresholds.excellent) {
            // 優秀等級
            conclusionHTML = `
                <strong class="text-success">✓ 優秀：可靠度達標</strong>
                <br><br>
                我們進行了 <strong>${t_test.toLocaleString()} 小時</strong>的加速測試，相當於 <strong>${equivalent_field_time}</strong> 的現場使用壽命（操作條件：<strong>${t_use}°C / ${rh_use}% RH</strong>）。
                <br><br>
                測試結果顯示，在 ${mission_years} 年任務期間內，這些樣品預計的失效率上限僅為 <strong>${failure_rate_pct}%</strong>
                (即可靠度為 <strong class="text-success">${reliability_pct}%</strong>)，<strong>優於業界平均標準 ${standardInfo.avgRate}</strong>。
                <br><br>
                這表明元件在整個產品保固期內，因內在老化機制導致失效的風險<strong>極低</strong>，可安心提供 ${mission_years} 年保固。
                <br>
                <div class="small text-muted mt-2">參考標準：${standardInfo.source}</div>
            `;
        } else if (reliability_value >= thresholds.acceptable) {
            // 合格等級
            conclusionHTML = `
                <strong class="text-info">✓ 合格：可靠度可接受</strong>
                <br><br>
                我們進行了 <strong>${t_test.toLocaleString()} 小時</strong>的加速測試，相當於 <strong>${equivalent_field_time}</strong> 的現場使用壽命（操作條件：<strong>${t_use}°C / ${rh_use}% RH</strong>）。
                <br><br>
                測試結果顯示，在 ${mission_years} 年任務期間內，這些樣品預計的失效率上限為 <strong>${failure_rate_pct}%</strong>
                (即可靠度為 ${reliability_pct}%)，<strong>符合業界可接受範圍</strong> (失效率 < ${standardInfo.maxRate})。
                <br><br>
                產品可靠度在可接受範圍內，建議持續監控失效率並優化製程以達到業界平均水準 (${standardInfo.avgRate})。
                <br>
                <div class="small text-muted mt-2">參考標準：${standardInfo.source}</div>
            `;
        } else {
            // 警告等級
            conclusionHTML = `
                <strong class="text-warning">⚠️ 警告：可靠度不足</strong>
                <br><br>
                我們進行了 <strong>${t_test.toLocaleString()} 小時</strong>的加速測試，相當於 <strong>${equivalent_field_time}</strong> 的現場使用壽命（操作條件：<strong>${t_use}°C / ${rh_use}% RH</strong>）。
                <br><br>
                測試結果顯示，在 ${mission_years} 年任務期間內，這些樣品預計的失效率上限為 <strong class="text-danger">${failure_rate_pct}%</strong>
                (即可靠度僅為 ${reliability_pct}%)，<strong class="text-danger">超過業界可接受上限 ${standardInfo.maxRate}</strong>。
                <br><br>
                <strong>建議措施：</strong>
                <ul class="mb-0 mt-2">
                    <li>延長加速測試時間或增加測試樣品數，以獲得更準確的可靠度估計</li>
                    <li>重新評估加速因子 (AF) 是否過於激進</li>
                    <li>檢查製程品質，改善產品設計以提升可靠度</li>
                    <li>考慮縮短保固期至 ${Math.max(1, mission_years - 0.5)} 年或調整產品定位</li>
                </ul>
                <br>
                <strong>參考標準：</strong>${standardInfo.source}，業界平均失效率 <strong>${standardInfo.avgRate}</strong>，可接受上限 <strong>${standardInfo.maxRate}</strong>。
            `;
        }
    }

    if (conclusionHTML) {
        textElem.innerHTML = conclusionHTML;
        panel.style.display = 'block';
    } else {
        panel.style.display = 'none';
    }
}

// --- 圖表切換與繪製邏輯 ---

function switchChart(type) {
    currentChartType = type;
    if (currentData) {
        renderChart();
    }
}

function renderChart() {
    if (!currentData) return;

    const plotDiv = 'plot_area';
    let traces = [];
    let layout = {
        paper_bgcolor: 'rgba(0,0,0,0)',
        plot_bgcolor: 'rgba(0,0,0,0)',
        font: { color: '#94a3b8' },
        margin: { t: 40, r: 20, l: 60, b: 40 },
        xaxis: { title: 'Time (Hours)', gridcolor: '#334155' },
        yaxis: { title: 'Value', gridcolor: '#334155' }
    };

    // 準備時間軸 (X軸)
    const maxTime = 50000;
    const timeSteps = Array.from({ length: 100 }, (_, i) => i * (maxTime / 100));

    if (currentMode === 'weibull') {
        const beta = currentData.weibull_result.beta;
        const eta = currentData.weibull_result.eta_alt;
        const af = currentData.af_result.af_total;
        const eta_use = eta * af;

        if (currentChartType === 'reliability') {
            layout.title = 'Reliability Function R(t)';
            layout.yaxis.title = 'Reliability';
            layout.yaxis.range = [0, 1.05];

            const y_rel = timeSteps.map(t => Math.exp(-Math.pow(t / eta_use, beta)));

            traces.push({
                x: timeSteps,
                y: y_rel,
                mode: 'lines',
                name: 'R(t)',
                line: { color: '#06b6d4', width: 3 }
            });

        } else if (currentChartType === 'hazard') {
            layout.title = 'Failure Rate h(t) (Bathtub Curve)';
            layout.yaxis.title = 'Failure Rate (Failures/Hour)';

            const y_haz = timeSteps.map(t => {
                if (t === 0) return 0;
                return (beta / eta_use) * Math.pow(t / eta_use, beta - 1);
            });

            traces.push({
                x: timeSteps,
                y: y_haz,
                mode: 'lines',
                name: 'h(t)',
                line: { color: '#ef4444', width: 3 }
            });

        } else if (currentChartType === 'pdf') {
            layout.title = 'Probability Density Function f(t)';
            layout.yaxis.title = 'Probability Density';

            const y_pdf = timeSteps.map(t => {
                if (t === 0) return 0;
                const r = Math.exp(-Math.pow(t / eta_use, beta));
                const h = (beta / eta_use) * Math.pow(t / eta_use, beta - 1);
                return r * h;
            });

            traces.push({
                x: timeSteps,
                y: y_pdf,
                mode: 'lines',
                name: 'f(t)',
                line: { color: '#f59e0b', width: 3, shape: 'spline' },
                fill: 'tozeroy'
            });
        }

    } else if (currentMode === 'zero_failure') {
        const res = currentData.reliability_result.zero_failure;
        const lambda = res.lambda_use_upper * 1e-9;

        if (currentChartType === 'reliability') {
            layout.title = 'Reliability Function R(t) (Exponential)';
            layout.yaxis.title = 'Reliability';
            layout.yaxis.range = [0, 1.05];

            const y_rel = timeSteps.map(t => Math.exp(-lambda * t));

            traces.push({
                x: timeSteps,
                y: y_rel,
                mode: 'lines',
                name: 'R(t)',
                line: { color: '#10b981', width: 3 }
            });

        } else if (currentChartType === 'hazard') {
            layout.title = 'Failure Rate h(t) (Constant)';
            layout.yaxis.title = 'Failure Rate (Failures/Hour)';

            const y_haz = timeSteps.map(t => lambda);

            traces.push({
                x: timeSteps,
                y: y_haz,
                mode: 'lines',
                name: 'h(t) = λ',
                line: { color: '#ef4444', width: 3 }
            });

        } else if (currentChartType === 'pdf') {
            layout.title = 'PDF f(t) (Exponential)';
            layout.yaxis.title = 'Probability Density';

            const y_pdf = timeSteps.map(t => lambda * Math.exp(-lambda * t));

            traces.push({
                x: timeSteps,
                y: y_pdf,
                mode: 'lines',
                name: 'f(t)',
                line: { color: '#f59e0b', width: 3 },
                fill: 'tozeroy'
            });
        }
    }

    Plotly.newPlot(plotDiv, traces, layout);
}

// Generate Report (PDF or Word)
async function generateReport(format = 'pdf') {
    const button = document.getElementById('generate_report_btn');
    button.disabled = true;

    const formatIcons = {
        'pdf': '<i class="bi bi-file-earmark-pdf me-1"></i>',
        'word': '<i class="bi bi-file-earmark-word me-1"></i>'
    };
    const formatNames = {
        'pdf': 'PDF',
        'word': 'Word'
    };

    button.innerHTML = '<i class="bi bi-hourglass-split me-1"></i>生成 ' + formatNames[format] + ' 中...';

    try {
        // 收集所有參數數據
        const reportData = {
            // AF 參數
            af_params: {
                t_use: document.getElementById('t_use').value,
                t_alt: document.getElementById('t_alt').value,
                rh_use: document.getElementById('rh_use').value,
                rh_alt: document.getElementById('rh_alt').value,
                ea: document.getElementById('ea').value,
                n_hum: document.getElementById('n_hum').value,
                enable_temp: document.getElementById('enable_temp').checked,
                enable_hum: document.getElementById('enable_hum').checked,
                enable_voltage: document.getElementById('enable_voltage').checked,
                enable_tc: document.getElementById('enable_tc').checked,
                enable_vib: document.getElementById('enable_vib').checked,
                enable_uv: document.getElementById('enable_uv').checked,
                enable_chem: document.getElementById('enable_chem').checked,
                enable_rad: document.getElementById('enable_rad').checked,
                enable_eyring: document.getElementById('enable_eyring').checked
            },

            // 測試數據
            test_data: {
                failures: document.getElementById('failures_input').value,
                n_samples: document.getElementById('n_samples').value,
                t_test: document.getElementById('t_test').value,
                cl: document.getElementById('cl').value,
                mission_years: document.getElementById('mission_years').value
            },

            // 當前結果數據
            results: currentData,

            // 分析模式
            analysis_mode: currentMode,

            // 結論文字（使用 innerHTML 保留 HTML 格式標籤）
            conclusion: document.getElementById('conclusion_text').innerHTML,

            // 圖表數據 (將當前圖表轉換為圖片)
            chart_image: null
        };

        // 獲取額外的加速因子參數（如果啟用）
        if (reportData.af_params.enable_voltage) {
            reportData.af_params.v_use = document.getElementById('v_use').value;
            reportData.af_params.v_alt = document.getElementById('v_alt').value;
            reportData.af_params.beta_v = document.getElementById('beta_v').value;
        }
        if (reportData.af_params.enable_tc) {
            reportData.af_params.dt_use = document.getElementById('dt_use').value;
            reportData.af_params.dt_alt = document.getElementById('dt_alt').value;
            reportData.af_params.f_use = document.getElementById('f_use').value;
            reportData.af_params.f_alt = document.getElementById('f_alt').value;
            reportData.af_params.alpha_tc = document.getElementById('alpha_tc').value;
            reportData.af_params.beta_tc = document.getElementById('beta_tc').value;
        }
        if (reportData.af_params.enable_vib) {
            reportData.af_params.g_use = document.getElementById('g_use').value;
            reportData.af_params.g_alt = document.getElementById('g_alt').value;
            reportData.af_params.n_vib = document.getElementById('n_vib').value;
        }
        if (reportData.af_params.enable_uv) {
            reportData.af_params.t_field_uv = document.getElementById('t_field_uv').value;
            reportData.af_params.t_accel_uv = document.getElementById('t_accel_uv').value;
        }
        if (reportData.af_params.enable_chem) {
            reportData.af_params.c_use = document.getElementById('c_use').value;
            reportData.af_params.c_alt = document.getElementById('c_alt').value;
            reportData.af_params.n_chem = document.getElementById('n_chem').value;
        }
        if (reportData.af_params.enable_rad) {
            reportData.af_params.d_use = document.getElementById('d_use').value;
            reportData.af_params.d_alt = document.getElementById('d_alt').value;
            reportData.af_params.dose_rate = document.getElementById('dose_rate').value;
            reportData.af_params.n_rad = document.getElementById('n_rad').value;
        }
        if (reportData.af_params.enable_eyring) {
            reportData.af_params.eyring_stress_type = document.getElementById('eyring_stress_type').value;
            reportData.af_params.eyring_d = document.getElementById('eyring_d').value;
            reportData.af_params.eyring_a = document.getElementById('eyring_a').value;
            reportData.af_params.eyring_b = document.getElementById('eyring_b').value;
        }

        // 導出圖表為圖片
        const plotDiv = document.getElementById('plot');
        if (plotDiv && plotDiv.data && plotDiv.data.length > 0) {
            try {
                console.log('Exporting chart to image...');
                reportData.chart_image = await Plotly.toImage(plotDiv, {
                    format: 'png',
                    width: 1200,
                    height: 600
                });
                console.log('Chart exported successfully');
            } catch (chartError) {
                console.error('Failed to export chart:', chartError);
                reportData.chart_image = null;  // 繼續生成報告，只是沒有圖表
            }
        }

        // 添加格式參數
        reportData.format = format;

        // 發送請求到後端生成報告
        const response = await fetch('/generate_report', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(reportData)
        });

        if (!response.ok) {
            throw new Error('生成報告失敗');
        }

        // 獲取文件
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, -5);

        // 根據格式設置文件擴展名
        const fileExtensions = {
            'pdf': '.pdf',
            'word': '.docx'
        };
        a.download = `Reliability_Test_Report_${timestamp}${fileExtensions[format]}`;

        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);

        button.innerHTML = formatIcons[format] + ' ' + formatNames[format] + ' 已下載';
        setTimeout(() => {
            button.disabled = false;
            button.innerHTML = '<i class="bi bi-file-earmark-text me-1"></i>生成測試報告';
        }, 2000);

    } catch (error) {
        console.error('生成報告時發生錯誤:', error);
        alert('生成報告時發生錯誤，請稍後重試');
        button.disabled = false;
        button.innerHTML = '<i class="bi bi-file-earmark-pdf me-1"></i>生成測試報告 (PDF)';
    }
}
