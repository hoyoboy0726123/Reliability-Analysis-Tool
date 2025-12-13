"""
圖表生成模組
使用 matplotlib 生成可靠度分析圖表，用於 PDF 報告
"""

import matplotlib
matplotlib.use('Agg')  # 使用非 GUI 後端
import matplotlib.pyplot as plt
import numpy as np
from io import BytesIO
import base64

# 設置中文字體
plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False  # 正確顯示負號

def generate_reliability_chart(beta, eta_use, max_time=50000, mode='weibull'):
    """
    生成可靠度函數 R(t) 圖表

    Args:
        beta: Weibull 形狀參數
        eta_use: 現場特性壽命
        max_time: 最大時間範圍
        mode: 'weibull' 或 'exponential'

    Returns:
        BytesIO: PNG 圖片的二進制流
    """
    fig, ax = plt.subplots(figsize=(10, 6), facecolor='white')

    # 生成時間軸
    t = np.linspace(0, max_time, 500)

    if mode == 'weibull':
        # Weibull 可靠度函數: R(t) = exp(-(t/η)^β)
        R = np.exp(-np.power(t / eta_use, beta))
        title = f'Reliability Function R(t) - Weibull Distribution\nβ={beta:.3f}, η={eta_use:.0f} hrs'
        color = '#06b6d4'
    else:
        # 指數分佈: R(t) = exp(-λt)
        lambda_rate = 1 / eta_use
        R = np.exp(-lambda_rate * t)
        title = f'Reliability Function R(t) - Exponential Distribution\nMTTF={eta_use:.0f} hrs'
        color = '#10b981'

    # 繪製圖表
    ax.plot(t, R, linewidth=3, color=color, label='R(t)')
    ax.fill_between(t, R, alpha=0.2, color=color)

    # 添加參考線
    ax.axhline(y=0.5, color='gray', linestyle='--', linewidth=1, alpha=0.5, label='50% Reliability')
    ax.axhline(y=0.9, color='gray', linestyle='--', linewidth=1, alpha=0.5, label='90% Reliability')

    # 設置標籤和標題
    ax.set_xlabel('Time (Hours)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Reliability R(t)', fontsize=12, fontweight='bold')
    ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
    ax.set_ylim([0, 1.05])
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.legend(loc='upper right', fontsize=10)

    # 優化佈局
    plt.tight_layout()

    # 保存到內存
    buf = BytesIO()
    plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
    buf.seek(0)
    plt.close(fig)

    return buf


def generate_failure_rate_chart(beta, eta_use, max_time=50000, mode='weibull'):
    """
    生成失效率 h(t) 圖表（浴盆曲線）

    Args:
        beta: Weibull 形狀參數
        eta_use: 現場特性壽命
        max_time: 最大時間範圍
        mode: 'weibull' 或 'exponential'

    Returns:
        BytesIO: PNG 圖片的二進制流
    """
    fig, ax = plt.subplots(figsize=(10, 6), facecolor='white')

    # 生成時間軸（避免 t=0）
    t = np.linspace(1, max_time, 500)

    if mode == 'weibull':
        # Weibull 失效率: h(t) = (β/η) * (t/η)^(β-1)
        h = (beta / eta_use) * np.power(t / eta_use, beta - 1)
        title = f'Failure Rate h(t) - Weibull Distribution\nβ={beta:.3f}, η={eta_use:.0f} hrs'

        # 根據 β 值標註失效模式
        if beta < 1:
            failure_mode = 'Early Failure (Infant Mortality)'
        elif beta == 1:
            failure_mode = 'Random Failure (Constant Rate)'
        else:
            failure_mode = 'Wear-out Failure'

    else:
        # 指數分佈: h(t) = λ (常數)
        lambda_rate = 1 / eta_use
        h = np.ones_like(t) * lambda_rate
        title = f'Failure Rate h(t) - Exponential Distribution\nλ={lambda_rate:.2e} /hr'
        failure_mode = 'Random Failure (Constant Rate)'

    # 繪製圖表
    ax.plot(t, h, linewidth=3, color='#ef4444', label='h(t)')

    # 設置標籤和標題
    ax.set_xlabel('Time (Hours)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Failure Rate (Failures/Hour)', fontsize=12, fontweight='bold')
    ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.legend(loc='upper right', fontsize=10)

    # 添加失效模式註釋
    ax.text(0.02, 0.98, f'Failure Mode: {failure_mode}',
            transform=ax.transAxes, fontsize=10, verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

    # 優化佈局
    plt.tight_layout()

    # 保存到內存
    buf = BytesIO()
    plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
    buf.seek(0)
    plt.close(fig)

    return buf


def generate_pdf_chart(beta, eta_use, max_time=50000, mode='weibull'):
    """
    生成機率密度函數 f(t) 圖表

    Args:
        beta: Weibull 形狀參數
        eta_use: 現場特性壽命
        max_time: 最大時間範圍
        mode: 'weibull' 或 'exponential'

    Returns:
        BytesIO: PNG 圖片的二進制流
    """
    fig, ax = plt.subplots(figsize=(10, 6), facecolor='white')

    # 生成時間軸（避免 t=0）
    t = np.linspace(1, max_time, 500)

    if mode == 'weibull':
        # Weibull PDF: f(t) = (β/η) * (t/η)^(β-1) * exp(-(t/η)^β)
        f = (beta / eta_use) * np.power(t / eta_use, beta - 1) * np.exp(-np.power(t / eta_use, beta))
        title = f'Probability Density Function f(t) - Weibull\nβ={beta:.3f}, η={eta_use:.0f} hrs'
        color = '#f59e0b'
    else:
        # 指數分佈 PDF: f(t) = λ * exp(-λt)
        lambda_rate = 1 / eta_use
        f = lambda_rate * np.exp(-lambda_rate * t)
        title = f'Probability Density Function f(t) - Exponential\nMTTF={eta_use:.0f} hrs'
        color = '#f59e0b'

    # 繪製圖表
    ax.plot(t, f, linewidth=3, color=color, label='f(t)')
    ax.fill_between(t, f, alpha=0.3, color=color)

    # 設置標籤和標題
    ax.set_xlabel('Time (Hours)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Probability Density', fontsize=12, fontweight='bold')
    ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.legend(loc='upper right', fontsize=10)

    # 優化佈局
    plt.tight_layout()

    # 保存到內存
    buf = BytesIO()
    plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
    buf.seek(0)
    plt.close(fig)

    return buf


def generate_all_charts(analysis_mode, weibull_result=None, reliability_result=None, max_time=50000):
    """
    生成所有三張圖表

    Args:
        analysis_mode: 'weibull' 或 'zero_failure'
        weibull_result: Weibull 分析結果字典
        reliability_result: 可靠度分析結果字典
        max_time: 最大時間範圍

    Returns:
        dict: {'reliability': BytesIO, 'failure_rate': BytesIO, 'pdf': BytesIO}
    """
    charts = {}

    if analysis_mode == 'weibull' and weibull_result:
        beta = weibull_result.get('beta', 2)
        eta_alt = weibull_result.get('eta_alt', 1000)
        af_total = reliability_result.get('weibull', {}).get('eta_use', eta_alt) / eta_alt
        eta_use = eta_alt * af_total

        charts['reliability'] = generate_reliability_chart(beta, eta_use, max_time, mode='weibull')
        charts['failure_rate'] = generate_failure_rate_chart(beta, eta_use, max_time, mode='weibull')
        charts['pdf'] = generate_pdf_chart(beta, eta_use, max_time, mode='weibull')

    elif analysis_mode == 'zero_failure' and reliability_result:
        zf_result = reliability_result.get('zero_failure', {})
        mttf_use = zf_result.get('mttf_use_lower', 10000)

        charts['reliability'] = generate_reliability_chart(1, mttf_use, max_time, mode='exponential')
        charts['failure_rate'] = generate_failure_rate_chart(1, mttf_use, max_time, mode='exponential')
        charts['pdf'] = generate_pdf_chart(1, mttf_use, max_time, mode='exponential')

    return charts


def charts_to_base64(charts):
    """
    將圖表轉換為 base64 編碼（用於嵌入 HTML 或 PDF）

    Args:
        charts: 圖表字典 {'reliability': BytesIO, ...}

    Returns:
        dict: {'reliability': 'base64_string', ...}
    """
    base64_charts = {}
    for key, buf in charts.items():
        if buf:
            buf.seek(0)
            base64_str = base64.b64encode(buf.read()).decode('utf-8')
            base64_charts[key] = base64_str
    return base64_charts
