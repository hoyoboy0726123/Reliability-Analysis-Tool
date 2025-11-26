function calculate() {
    // 1. 收集 AF 參數
    const afParams = {
        t_use: document.getElementById('t_use').value,
        rh_use: document.getElementById('rh_use').value,
        v_use: document.getElementById('v_use').value,
        t_alt: document.getElementById('t_alt').value,
        rh_alt: document.getElementById('rh_alt').value,
        v_alt: document.getElementById('v_alt').value,
        ea: document.getElementById('ea').value,
        n_hum: document.getElementById('n_hum').value,
        beta_v: document.getElementById('beta_v').value
    };

    // 2. 收集 Weibull 數據
    const failuresInput = document.getElementById('failures_input').value;
    let failures = [];
    if (failuresInput.trim() !== "") {
        failures = failuresInput.split(/[,;\s]+/).map(Number).filter(n => !isNaN(n) && n > 0);
    }

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
            weibull_data: { failures: failures },
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

function updateUI(data, hasFailures) {
    // 更新 AF 結果
    document.getElementById('res_af_t').innerText = data.af_result.af_t;
    document.getElementById('res_af_rh').innerText = data.af_result.af_rh;
    document.getElementById('res_af_v').innerText = data.af_result.af_v;
    document.getElementById('res_af_total').innerText = data.af_result.af_total;

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
        document.getElementById('wb_b1').innerText = res.b1_life.toLocaleString() + " hrs";
        document.getElementById('wb_rel').innerText = (res.r_mission * 100).toFixed(4) + "%";
        document.getElementById('wb_rel_label').innerText = `Reliability (${missionYears} Years)`;

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

    let conclusionHTML = "";

    if (hasFailures && data.weibull_result && !data.weibull_result.error) {
        const res = data.reliability_result.weibull;
        const failuresInput = document.getElementById('failures_input').value;
        const n_failures = failuresInput.split(/[,;\s]+/).filter(n => n.trim() !== "").length;
        const b1_years = (res.b1_life / 8760).toFixed(2);
        const reliability_pct = (res.r_mission * 100).toFixed(2);

        // 判斷 B1% 壽命是否超過任務時間
        if (parseFloat(b1_years) >= mission_years) {
            // 正面結論：B1% 壽命 ≥ 任務時間
            conclusionHTML = `
                我們的測試模擬了現場使用壽命。計算結果顯示，這批樣品的 <strong>B1% 壽命</strong>（即預計只有 1% 的產品會失效的時間）為 <strong>${b1_years} 年</strong> (${Math.round(res.b1_life).toLocaleString()} 小時)。
                <br><br>
                在 <strong>${mission_years} 年</strong>的任務期間內，預期可靠度為 <strong>${reliability_pct}%</strong>。
                這個數值證明了即使有 <strong>${n_failures}</strong> 個樣品失效，產品的整體可靠性邊際仍然充足。
                不過，我們必須對這 ${n_failures} 個失效進行追蹤，以確認是否屬於可預防的早期製造缺陷。
            `;
        } else {
            // 否定結論：B1% 壽命 < 任務時間
            const failure_risk_pct = (100 - res.r_mission * 100).toFixed(2);
            conclusionHTML = `
                <strong class="text-warning">⚠️ 警告：可靠性不足</strong>
                <br><br>
                我們的測試模擬了現場使用壽命。計算結果顯示，這批樣品的 <strong>B1% 壽命</strong>僅為 <strong>${b1_years} 年</strong> (${Math.round(res.b1_life).toLocaleString()} 小時)，
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
                在我們的現場操作條件（<strong>${t_use}°C / ${rh_use}% RH</strong>）下，我們模擬了 <strong>${mission_years} 年</strong>的壽命。
                <br><br>
                我們的測試結果顯示，在 ${mission_years} 年任務期間內，這些樣品預計的失效率上限僅為 <strong>${failure_rate_pct}%</strong>
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
                在我們的現場操作條件（<strong>${t_use}°C / ${rh_use}% RH</strong>）下，我們模擬了 <strong>${mission_years} 年</strong>的壽命。
                <br><br>
                我們的測試結果顯示，在 ${mission_years} 年任務期間內，這些樣品預計的失效率上限為 <strong>${failure_rate_pct}%</strong>
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
                在我們的現場操作條件（<strong>${t_use}°C / ${rh_use}% RH</strong>）下，我們模擬了 <strong>${mission_years} 年</strong>的壽命。
                <br><br>
                我們的測試結果顯示，在 ${mission_years} 年任務期間內，這些樣品預計的失效率上限為 <strong class="text-danger">${failure_rate_pct}%</strong>
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
