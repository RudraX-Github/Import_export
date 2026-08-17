"""
Top 10 Export Markets Competitor Intelligence & Global Supply Analysis
Specialized Strategic Trade Intelligence Module for Indian Exporters
Seamlessly integrated with main app.py (TradeStat Analytics Hub)

Datasets Analyzed (2025 ITC Trade Map Import Data for India's Top 10 Syringe Export Destinations):
  1. United States of America (HS 90183100)
  2. Brazil (HS 90183100)
  3. United Kingdom (HS 90183100)
  4. Germany (HS 90183100)
  5. Switzerland (HS 90183100)
  6. France (HS 90183100)
  7. Nigeria (HS 90183100)
  8. Korea, Republic of (HS 90183100)
  9. Sudan (HS 90183100)
  10. Australia (HS 90183100)
"""

import streamlit as st
import pandas as pd
import numpy as np
import io
import os

try:
    import plotly.express as px
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    HAS_PLOTLY = True
except ImportError:
    HAS_PLOTLY = False

# ==============================================================================
# 1. DATA SOURCES & PARSING ENGINE
# ==============================================================================

COMPETITOR_SHEET_CONFIGS = {
    'United States of America': {
        'url': 'https://docs.google.com/spreadsheets/d/10GQNRXxCiVqZ0WJBME8Dfs9OTNlX7miEdqpV53elrxY/export?format=csv',
        'code': 'USA',
        'flag': '🇺🇸'
    },
    'Brazil': {
        'url': 'https://docs.google.com/spreadsheets/d/1kfI1lhUM3-9qWYDq7eiSWGOSq9_is4sdcrRWW1dfRCM/export?format=csv',
        'code': 'BRA',
        'flag': '🇧🇷'
    },
    'United Kingdom': {
        'url': 'https://docs.google.com/spreadsheets/d/1_eYm19u__H6as9brivWKizSD2seGBZDPqDR8CQA7Hfo/export?format=csv',
        'code': 'GBR',
        'flag': '🇬🇧'
    },
    'Germany': {
        'url': 'https://docs.google.com/spreadsheets/d/1oU3s7cxHLIHRMJoCA1jZsckvbjfvRdpqcYshAaJ2YcY/export?format=csv',
        'code': 'DEU',
        'flag': '🇩🇪'
    },
    'Switzerland': {
        'url': 'https://docs.google.com/spreadsheets/d/1s0HYtgZMgu3UHrbkz-g1xN9gK8jb3H8TPX51mN9kHJo/export?format=csv',
        'code': 'CHE',
        'flag': '🇨🇭'
    },
    'France': {
        'url': 'https://docs.google.com/spreadsheets/d/1xoFDcsBnGlAd9w8B175Vz6zTjGpdn7w_64RqWEV-BAM/export?format=csv',
        'code': 'FRA',
        'flag': '🇫🇷'
    },
    'Nigeria': {
        'url': 'https://docs.google.com/spreadsheets/d/1G_n0dsDiuWMVqGrClv0gYvY4MCbR4xkvgB2nilEIgdM/export?format=csv',
        'code': 'NGA',
        'flag': '🇳🇬'
    },
    'Korea, Republic of': {
        'url': 'https://docs.google.com/spreadsheets/d/1OWuzPu7i2xozqO-u93x5odvyUoEkLH7BA53bFV24fyY/export?format=csv',
        'code': 'KOR',
        'flag': '🇰🇷'
    },
    'Sudan': {
        'url': 'https://docs.google.com/spreadsheets/d/1m4eH6ziRSc3I3PIZbEPEygOM9LfEfnxC69KwSdvz84Q/export?format=csv',
        'code': 'SDN',
        'flag': '🇸🇩'
    },
    'Australia': {
        'url': 'https://docs.google.com/spreadsheets/d/1_Q0okVZIs8QT8BbYHsq7oMQHi4zDS9K7aAwYDFj9dUU/export?format=csv',
        'code': 'AUS',
        'flag': '🇦🇺'
    }
}

DEFAULT_FALLBACK_RATE = 83.5

def clean_val(x):
    if pd.isna(x) or str(x).strip() in ['', 'nan', 'None', '-']:
        return np.nan
    s = str(x).replace(',', '').replace('%', '').strip()
    try:
        return float(s)
    except Exception:
        return np.nan

@st.cache_data(ttl=3600, show_spinner=False)
def load_all_competitor_datasets():
    """
    Loads and standardizes all 10 competitor supplying market datasets directly from Google Sheets.
    """
    all_market_dfs = {}
    market_summaries = []

    for market_name, cfg in COMPETITOR_SHEET_CONFIGS.items():
        try:
            df = pd.read_csv(cfg['url'])
            records = []
            for idx, row in df.iterrows():
                exp = str(row.iloc[0]).strip()
                if not exp or exp.lower() == 'nan':
                    continue
                if exp.lower() == 'world':
                    continue

                val = clean_val(row.iloc[1])
                bal = clean_val(row.iloc[2])
                share = clean_val(row.iloc[3])
                qty = clean_val(row.iloc[4])
                unit = str(row.iloc[5]).strip() if pd.notna(row.iloc[5]) else ''
                unit_val = clean_val(row.iloc[6])

                if market_name == 'Nigeria':
                    g_val_2125 = clean_val(row.iloc[7])
                    g_qty_2125 = clean_val(row.iloc[9])
                    g_val_2425 = clean_val(row.iloc[11])
                    w_rank = clean_val(row.iloc[13])
                    w_share = clean_val(row.iloc[14])
                    w_growth = clean_val(row.iloc[15])
                    dist = np.nan
                    conc = np.nan
                    tariff = np.nan
                else:
                    g_val_2125 = clean_val(row.iloc[7])
                    g_qty_2125 = clean_val(row.iloc[8])
                    g_val_2425 = clean_val(row.iloc[9])
                    w_rank = clean_val(row.iloc[10])
                    w_share = clean_val(row.iloc[11])
                    w_growth = clean_val(row.iloc[12])
                    dist = clean_val(row.iloc[13]) if len(row) > 13 else np.nan
                    conc = clean_val(row.iloc[14]) if len(row) > 14 else np.nan
                    tariff = clean_val(row.iloc[15]) if len(row) > 15 else np.nan

                records.append({
                    'Market': market_name,
                    'Market_Code': cfg['code'],
                    'Market_Flag': cfg['flag'],
                    'Rank': len(records) + 1,
                    'Exporter': exp,
                    'Import_Val_USD_K': val,
                    'Trade_Balance_USD_K': bal,
                    'Import_Share_Pct': share,
                    'Quantity': qty,
                    'Quantity_Unit': unit,
                    'Unit_Value_USD': unit_val,
                    'Growth_Val_2021_2025_Pct': g_val_2125,
                    'Growth_Qty_2021_2025_Pct': g_qty_2125,
                    'Growth_Val_2024_2025_Pct': g_val_2425,
                    'World_Export_Rank': w_rank,
                    'World_Export_Share_Pct': w_share,
                    'Partner_Export_Growth_Pct': w_growth,
                    'Avg_Distance_KM': dist,
                    'Import_Concentration': conc,
                    'Applied_Tariff_Pct': tariff
                })

            df_m = pd.DataFrame(records)
            all_market_dfs[market_name] = df_m

            # Market Summary Stats
            total_m_val = df_m['Import_Val_USD_K'].sum()
            top1_exp = df_m.iloc[0]['Exporter'] if not df_m.empty else 'N/A'
            top1_share = df_m.iloc[0]['Import_Share_Pct'] if not df_m.empty else 0.0
            top1_price = df_m.iloc[0]['Unit_Value_USD'] if not df_m.empty else 0.0

            india_row = df_m[df_m['Exporter'].str.contains('India', case=False, na=False)]
            if not india_row.empty:
                i_rank = int(india_row['Rank'].values[0])
                i_val = india_row['Import_Val_USD_K'].values[0]
                i_share = india_row['Import_Share_Pct'].values[0]
                i_price = india_row['Unit_Value_USD'].values[0]
                i_g2125 = india_row['Growth_Val_2021_2025_Pct'].values[0]
                i_gyoy = india_row['Growth_Val_2024_2025_Pct'].values[0]
            else:
                i_rank = np.nan
                i_val = 0.0
                i_share = 0.0
                i_price = np.nan
                i_g2125 = np.nan
                i_gyoy = np.nan

            market_summaries.append({
                'Market': market_name,
                'Flag': cfg['flag'],
                'Total_Import_USD_K': total_m_val,
                'Top_Supplier_1': top1_exp,
                'Top_Supplier_Share_Pct': top1_share,
                'Top_Supplier_Price_USD': top1_price,
                'India_Rank': i_rank,
                'India_Import_Val_USD_K': i_val,
                'India_Share_Pct': i_share,
                'India_Price_USD': i_price,
                'India_Growth_2021_2025_Pct': i_g2125,
                'India_YoY_Growth_2024_2025_Pct': i_gyoy
            })

        except Exception as e:
            st.error(f"Error loading {market_name} dataset: {e}")

    df_summary = pd.DataFrame(market_summaries)
    return all_market_dfs, df_summary


# ==============================================================================
# 2. MAIN COMPETITOR INTELLIGENCE RENDERER
# ==============================================================================

def render_competitor_page():
    """
    Main Renderer for India's Top 10 Export Markets Competitor Analysis.
    Protected by app.py single-portal master authentication.
    """
    # 1. STRICT ACCESS CONTROL
    if not st.session_state.get("authenticated", False):
        st.error("⛔ **Direct Access Denied**: This specialized competitor intelligence module is strictly protected and accessible only via the main TradeStat portal (`app.py`). Please sign in through `app.py`.")
        st.stop()

    # 2. Extract User-Defined USD Rate
    user_usd_rate = float(st.session_state.get('usd_rate', 0.0))
    effective_usd_rate = user_usd_rate if user_usd_rate > 0 else DEFAULT_FALLBACK_RATE

    # 3. Styling matching app.py dark theme
    st.markdown("""
        <style>
        .metric-card { 
            background: #151c2c; border: 1px solid #26334d; padding: 1.5rem; 
            border-radius: 12px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.4); 
            border-left: 5px solid #2563eb;
        }
        .metric-title { color: #94a3b8; font-size: 0.85rem; font-weight: 700; text-transform: uppercase; margin-bottom: 0.5rem;}
        .metric-value { color: #f8fafc; font-size: 1.8rem; font-weight: 800; font-family: 'Courier New', Courier, monospace; }
        .metric-sub { color: #34d399; font-size: 0.85rem; font-weight: 600; margin-top: 0.25rem; }
        .page-header { font-size: 2.1rem; font-weight: 800; color: #3b82f6; margin-bottom: 0.2rem; }
        .page-subheader { font-size: 1.05rem; color: #94a3b8; margin-bottom: 1.2rem; }
        </style>
    """, unsafe_allow_html=True)

    head_c1, head_c2 = st.columns([4, 1])
    with head_c1:
        st.markdown('<div class="page-header">⚔️ Competitor Intelligence in India\'s Top 10 Export Markets</div>', unsafe_allow_html=True)
        st.markdown('<div class="page-subheader">Benchmarking India against Global Suppliers (China, USA, Mexico, Taiwan, Germany, Switzerland & Italy) across $4.37 Billion Import Demand (2025)</div>', unsafe_allow_html=True)
    with head_c2:
        st.markdown(f"<div style='text-align:right; color:#94a3b8;'>User: <strong>{st.session_state.get('username', 'User')}</strong></div>", unsafe_allow_html=True)
        if st.button("Logout", key="comp_logout_btn"):
            for key in ['authenticated', 'username', 'user_id', 'password', 'is_master']:
                st.session_state[key] = None
            st.session_state['authenticated'] = False
            st.rerun()

    with st.spinner("Connecting to 10 ITC Trade Map Supplying Market Google Sheets..."):
        all_market_dfs, df_summary_raw = load_all_competitor_datasets()

    if not all_market_dfs:
        st.error("⚠️ Failed to load competitor datasets. Please check network connection.")
        return

    # SIDEBAR CONTROLS & UNIFIED CURRENCY CONFIGURATION
    with st.sidebar:
        st.markdown("### 💱 Currency Standardization")
        default_curr_idx = 0 if user_usd_rate > 0 else 1
        selected_currency = st.radio(
            "Select Display Currency:",
            options=["USD ($) — Thousands / Millions", "INR (₹) — Crores / Lakhs"],
            index=default_curr_idx,
            key="comp_currency_choice"
        )
        is_usd = "USD" in selected_currency

        if is_usd:
            curr_sym = "$"
            curr_val_label = "USD Thousand ($K)"
            curr_val_macro_label = "USD Million ($M)"
            curr_price_label = "$ / Unit"
            val_scale = 1.0
            macro_scale = 1.0 / 1e3
            price_scale = 1.0
        else:
            curr_sym = "₹"
            curr_val_label = "₹ Crore"
            curr_val_macro_label = "₹ Crore"
            curr_price_label = "₹ / Unit"
            val_scale = (1e3 * effective_usd_rate) / 1e7
            macro_scale = (1e3 * effective_usd_rate) / 1e7
            price_scale = effective_usd_rate

        st.caption(f"ℹ️ Active Conversion Rate: **1 USD = ₹{effective_usd_rate:.2f}** {'(Defined at Login)' if user_usd_rate > 0 else '(Default Benchmark)'}.")

        st.markdown("---")
        st.markdown("### 🔍 Filter & Navigation")

        if st.button("🔄 Reset All Filters & Sorting", key="comp_reset_all_btn", use_container_width=True):
            for k in ["comp_sort_field", "comp_search_term", "comp_country_filter"]:
                if k in st.session_state:
                    del st.session_state[k]
            st.rerun()

        search_supplier = st.text_input("Filter by Supplying Country / Competitor:", "", key="comp_search_term").strip().upper()

        st.markdown("---")
        st.markdown("### 📋 Connected Google Sheets")
        for m, cfg in COMPETITOR_SHEET_CONFIGS.items():
            st.markdown(f"- [{cfg['flag']} {m}]({cfg['url']})")

    # PREPARE DATA ACCORDING TO UNIFIED CURRENCY
    df_summary = df_summary_raw.copy()
    df_summary['Total_Import_Unified'] = df_summary['Total_Import_USD_K'] * macro_scale
    df_summary['India_Import_Unified'] = df_summary['India_Import_Val_USD_K'] * (macro_scale if not is_usd else 1.0)
    df_summary['Top_Supplier_Price_Unified'] = df_summary['Top_Supplier_Price_USD'] * price_scale
    df_summary['India_Price_Unified'] = df_summary['India_Price_USD'] * price_scale

    # MACRO OVERVIEW METRICS ACROSS ALL 10 MARKETS
    tot_addressable_val_usd = df_summary_raw['Total_Import_USD_K'].sum()
    tot_addressable_val_unified = tot_addressable_val_usd * (macro_scale if not is_usd else 1.0 / 1e3)
    tot_india_val_usd = df_summary_raw['India_Import_Val_USD_K'].sum()
    tot_india_val_unified = tot_india_val_usd * (macro_scale if not is_usd else 1.0 / 1e3)
    india_combined_share = (tot_india_val_usd / tot_addressable_val_usd) * 100

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(f"""<div class="metric-card"><div class="metric-title"><i class="fa-solid fa-earth-americas"></i> Top 10 Markets Total Demand</div><div class="metric-value">{curr_sym}{tot_addressable_val_unified:,.2f} {'M' if is_usd else 'Cr'}</div><div class="metric-sub">10 Destination Countries</div></div>""", unsafe_allow_html=True)
    with m2:
        st.markdown(f"""<div class="metric-card" style="border-left-color: #10b981;"><div class="metric-title"><i class="fa-solid fa-flag-checkered"></i> India's Current Capture</div><div class="metric-value">{curr_sym}{tot_india_val_unified:,.2f} {'M' if is_usd else 'Cr'}</div><div class="metric-sub" style="color:#10b981;">{india_combined_share:.2f}% Combined Share</div></div>""", unsafe_allow_html=True)
    with m3:
        st.markdown(f"""<div class="metric-card" style="border-left-color: #f59e0b;"><div class="metric-title"><i class="fa-solid fa-crown"></i> India Top Positions</div><div class="metric-value">#1 NGA | #2 SDN</div><div class="metric-sub" style="color:#f59e0b;">#4 in Brazil (9.7% share)</div></div>""", unsafe_allow_html=True)
    with m4:
        st.markdown(f"""<div class="metric-card" style="border-left-color: #8b5cf6;"><div class="metric-title"><i class="fa-solid fa-rocket"></i> Highest Surging Markets</div><div class="metric-value">+1431% USA</div><div class="metric-sub" style="color:#8b5cf6;">+906% DEU | +305% CHE</div></div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # UNNUMBERED TABBED MODULES
    tab_matrix, tab_usa, tab_bra, tab_gbr, tab_deu, tab_che, tab_fra, tab_nga, tab_kor, tab_sdn, tab_aus, tab_down = st.tabs([
        "🌐 Cross-Market Strategic Matrix",
        "🇺🇸 United States",
        "🇧🇷 Brazil",
        "🇬🇧 United Kingdom",
        "🇩🇪 Germany",
        "🇨🇭 Switzerland",
        "🇫🇷 France",
        "🇳🇬 Nigeria",
        "🇰🇷 Korea RP",
        "🇸🇩 Sudan",
        "🇦🇺 Australia",
        "📥 Download Competitor Data"
    ])

    # --------------------------------------------------------------------------
    # TAB: CROSS-MARKET STRATEGIC MATRIX
    # --------------------------------------------------------------------------
    with tab_matrix:
        st.subheader("Global Supply Landscape & Competitor Dominance Matrix (2025)")
        st.caption("Comparative assessment of India vs. Primary Competitor across each of India's Top 10 Export Destination Markets.")

        matrix_sort = st.selectbox(
            "Sort Comparative Table Strictly By:",
            options=[
                "Total Destination Market Size (High to Low)",
                "India Market Share (%) (High to Low)",
                "India Import Value (High to Low)",
                "India YoY Growth (%) (High to Low)",
                "Top Competitor Market Share (%) (High to Low)"
            ],
            index=0,
            key="comp_matrix_sort_field"
        )

        if matrix_sort == "Total Destination Market Size (High to Low)":
            sorted_matrix_df = df_summary.sort_values('Total_Import_Unified', ascending=False).copy()
        elif matrix_sort == "India Market Share (%) (High to Low)":
            sorted_matrix_df = df_summary.sort_values('India_Share_Pct', ascending=False).copy()
        elif matrix_sort == "India Import Value (High to Low)":
            sorted_matrix_df = df_summary.sort_values('India_Import_Unified', ascending=False).copy()
        elif matrix_sort == "India YoY Growth (%) (High to Low)":
            sorted_matrix_df = df_summary.sort_values('India_YoY_Growth_2024_2025_Pct', ascending=False).copy()
        else:
            sorted_matrix_df = df_summary.sort_values('Top_Supplier_Share_Pct', ascending=False).copy()

        table_cols = sorted_matrix_df[['Flag', 'Market', 'Total_Import_Unified', 'Top_Supplier_1', 'Top_Supplier_Share_Pct', 'India_Rank', 'India_Import_Unified', 'India_Share_Pct', 'India_YoY_Growth_2024_2025_Pct', 'India_Growth_2021_2025_Pct']].copy()
        table_cols.columns = [
            '',
            'Destination Market',
            f'Total Imports ({curr_val_macro_label})',
            'Primary Competitor (#1)',
            'Competitor Share (%)',
            'India Rank',
            f'India Import ({curr_val_macro_label if not is_usd else curr_val_label})',
            'India Share (%)',
            'India YoY Growth (%)',
            'India 2021-25 Growth (%)'
        ]
        st.dataframe(table_cols.round(2), use_container_width=True, hide_index=True)

        st.markdown("---")

        col_in1, col_in2 = st.columns(2)
        with col_in1:
            st.success(f"""
            ### 🎯 Key Competitor Moats & Vulnerabilities
            1. **The Chinese Vacuum in USA & Nigeria**:
               - China's syringe shipments to the **USA fell -26% YoY (-20% 4-Yr CAGR)** and to **Nigeria fell -36% 4-Yr CAGR**.
               - India capitalized directly, surging **+1,431% in the USA ($14.83M)** and capturing **74.8% of Nigeria ($3.70M)**.
            2. **High-Value Intra-European Moat**:
               - Germany, Switzerland, France, and Italy trade primarily with each other (20–27% mutual market shares) at high unit values ($30–$140/unit).
               - India's triple-digit growth in **Germany (+906% YoY)** and **Switzerland (+305% YoY)** shows Indian specialized syringes are breaking European entry barriers.
            3. **Nearshoring Competitor Advantage**:
               - **Mexico** holds 22.3% of the USA ($345.9M) and 10.1% of France ($84.9M) via duty-free agreements and geographical proximity.
            """)
        with col_in2:
            st.info(f"""
            ### 💡 Actionable Playbook for Indian Exporters
            1. **Target USA & German Mid-Tier Disruption**:
               - Mexico and Taiwan dominate US/German hospitals with auto-disable and safety syringes. Indian exporters with US FDA 510(k) clearances can offer 30–50% cost savings against Taiwanese and Italian suppliers.
            2. **Defend & Expand in Brazil**:
               - India is **Rank #4 (9.7% share)** behind China (22.1%) and Paraguay (21.2%). Matching Paraguay's Mercosur tariff advantage through bilateral medical trade channels will unlock the #1 spot.
            3. **Consolidate African Leadership**:
               - India controls **74.8% of Nigeria** and **31.8% of Sudan**. Establishing regional warehousing in Lagos and Port Sudan can lock in 85%+ market control against Chinese competition.
            """)

        if HAS_PLOTLY and len(df_summary) > 0:
            c_v1, c_v2 = st.columns(2)
            with c_v1:
                fig_share = px.bar(
                    df_summary.sort_values('India_Share_Pct', ascending=True),
                    y='Market',
                    x='India_Share_Pct',
                    orientation='h',
                    text_auto='.1f',
                    color='India_Share_Pct',
                    color_continuous_scale='Blues',
                    title="India's Market Share (%) in Top 10 Export Destinations",
                    labels={'India_Share_Pct': "India Market Share (%)", 'Market': 'Destination Country'}
                )
                fig_share.update_layout(template="plotly_dark", plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", height=380)
                st.plotly_chart(fig_share, use_container_width=True)

            with c_v2:
                fig_yoy = px.bar(
                    df_summary[df_summary['India_YoY_Growth_2024_2025_Pct'] > 0].sort_values('India_YoY_Growth_2024_2025_Pct', ascending=True),
                    y='Market',
                    x='India_YoY_Growth_2024_2025_Pct',
                    orientation='h',
                    text_auto='.0f',
                    color='India_YoY_Growth_2024_2025_Pct',
                    color_continuous_scale='Viridis',
                    title="India's 2024–2025 YoY Import Value Growth (%) by Market",
                    labels={'India_YoY_Growth_2024_2025_Pct': "YoY Growth (%)", 'Market': 'Destination Country'}
                )
                fig_yoy.update_layout(template="plotly_dark", plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", height=380)
                st.plotly_chart(fig_yoy, use_container_width=True)

    # --------------------------------------------------------------------------
    # HELPER FUNCTION FOR RENDERING INDIVIDUAL DESTINATION MARKET TABS
    # --------------------------------------------------------------------------
    def render_single_market_tab(market_name, strategic_notes):
        df_m = all_market_dfs.get(market_name, pd.DataFrame())
        if df_m.empty:
            st.warning(f"No competitor data available for {market_name}.")
            return

        df_disp = df_m.copy()
        if search_supplier:
            df_disp = df_disp[df_disp['Exporter'].str.contains(search_supplier, na=False)]

        df_disp['Import_Val_Unified'] = df_disp['Import_Val_USD_K'] * (val_scale if is_usd else macro_scale)
        df_disp['Unit_Value_Unified'] = df_disp['Unit_Value_USD'] * price_scale

        tot_m_val_unified = df_m['Import_Val_USD_K'].sum() * (val_scale if is_usd else macro_scale)

        st.subheader(f"{COMPETITOR_SHEET_CONFIGS[market_name]['flag']} {market_name} — Total Import Market: {curr_sym}{tot_m_val_unified:,.2f} {curr_val_macro_label if not is_usd else curr_val_label}")

        top1 = df_m.iloc[0]
        india_r = df_m[df_m['Exporter'].str.contains('India', case=False, na=False)]

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Market Leader (#1)", f"{top1['Exporter']}", f"{top1['Import_Share_Pct']:.1f}% Share")
        c2.metric(f"Leader Value", f"{curr_sym}{top1['Import_Val_USD_K']*(val_scale if is_usd else macro_scale):,.1f} {'K' if is_usd else 'Cr'}", f"Price: {curr_sym}{top1['Unit_Value_USD']*price_scale:.2f}" if pd.notna(top1['Unit_Value_USD']) else "N/A")
        if not india_r.empty:
            c3.metric("India Rank & Share", f"Rank #{int(india_r['Rank'].values[0])}", f"{india_r['Import_Share_Pct'].values[0]:.2f}% Share")
            c4.metric(f"India Growth", f"{india_r['Growth_Val_2024_2025_Pct'].values[0]:+.1f}% YoY", f"{india_r['Growth_Val_2021_2025_Pct'].values[0]:+.1f}% 4-Yr CAGR")
        else:
            c3.metric("India Rank", "Outside Top List", "0.0% Share")
            c4.metric("India Growth", "N/A", "Untapped Opportunity")

        st.markdown("<br>", unsafe_allow_html=True)

        col_t, col_p = st.columns([1.3, 0.7])
        with col_t:
            st.markdown(f"#### 📊 Supplying Country Rankings ({market_name})")
            table_show = df_disp[['Rank', 'Exporter', 'Import_Val_Unified', 'Import_Share_Pct', 'Quantity', 'Quantity_Unit', 'Unit_Value_Unified', 'Growth_Val_2021_2025_Pct', 'Growth_Val_2024_2025_Pct', 'Applied_Tariff_Pct']].copy()
            table_show.columns = [
                'Rank',
                'Supplying Country (Competitor)',
                f'Import Value ({curr_val_macro_label if not is_usd else curr_val_label})',
                'Market Share (%)',
                'Quantity',
                'Unit',
                f'Unit Price ({curr_price_label})',
                '2021-25 Growth (%)',
                '2024-25 YoY Growth (%)',
                'Tariff (%)'
            ]
            st.dataframe(table_show.round(2), use_container_width=True, hide_index=True)

        with col_p:
            if HAS_PLOTLY and len(df_m) > 0:
                fig_p = px.pie(
                    df_m.head(7),
                    names='Exporter',
                    values='Import_Val_USD_K',
                    title=f"Top Suppliers Market Share in {market_name}",
                    color_discrete_sequence=px.colors.sequential.Blues_r
                )
                fig_p.update_layout(template="plotly_dark", plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", height=350, margin=dict(t=35, b=0, l=0, r=0))
                st.plotly_chart(fig_p, use_container_width=True)

        st.info(f"### 🛡️ Strategic Intelligence & Indian Exporter Playbook for **{market_name}**\n\n{strategic_notes}")

        if HAS_PLOTLY and len(df_m) > 0:
            top_comp_bar = df_m.head(10).copy()
            top_comp_bar['Import_Val_Unified'] = top_comp_bar['Import_Val_USD_K'] * (val_scale if is_usd else macro_scale)
            fig_b = px.bar(
                top_comp_bar,
                x='Exporter',
                y='Import_Val_Unified',
                color='Import_Share_Pct',
                color_continuous_scale='Viridis',
                title=f"Top 10 Supplying Competitors to {market_name} - Import Value ({curr_val_macro_label if not is_usd else curr_val_label})",
                labels={'Import_Val_Unified': f"Import Value ({curr_val_macro_label if not is_usd else curr_val_label})", 'Exporter': 'Supplying Nation'}
            )
            fig_b.update_layout(template="plotly_dark", plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", height=350)
            st.plotly_chart(fig_b, use_container_width=True)

    # --------------------------------------------------------------------------
    # INDIVIDUAL MARKET TABS WITH TAILORED STRATEGIC PLAYBOOKS
    # --------------------------------------------------------------------------
    with tab_usa:
        render_single_market_tab(
            'United States of America',
            """
            - **Market Dominance**: Mexico ($345.9M, 22.3%), Chinese Taipei ($246.0M, 15.8%), Italy ($218.6M, 14.1%), China ($127.3M, 8.2%), and Switzerland ($112.7M, 7.3%).
            - **China's Retreat (-26% YoY)**: China's supply to the US dropped by 26% in 2024-25 due to Section 301 tariffs and FDA warning letters.
            - **India's Massive Breakthrough**: India ranks **#12 ($14.83M, 1.0% share)** with an explosive **+1,431% YoY growth**!
            - **Exporter Strategy**: Indian suppliers should leverage US FDA 510(k) approvals and target GPO (Group Purchasing Organization) hospital contracts to replace declining Chinese volume.
            """
        )

    with tab_bra:
        render_single_market_tab(
            'Brazil',
            """
            - **Market Dominance**: China ($16.38M, 22.1%), Paraguay ($15.68M, 21.2%), USA ($8.33M, 11.3%), and **India ($7.19M, 9.7%, Rank #4)**.
            - **Mercosur Dynamics**: Paraguay enjoys 0% Mercosur tariff preference, while China and India face standard import tariffs.
            - **Exporter Strategy**: India already supplies over 2 billion syringes cumulatively. Establishing an ANVISA-compliant direct distribution hub in São Paulo will eliminate intermediaries and push India past China and Paraguay to Rank #1.
            """
        )

    with tab_gbr:
        render_single_market_tab(
            'United Kingdom',
            """
            - **Market Dominance**: USA ($48.97M, 19.1%), Finland ($35.79M, 13.9%), Germany ($32.67M, 12.7%), China ($28.76M, 11.2%), and Chinese Taipei ($17.24M, 6.7%).
            - **NHS Procurement Opportunity**: India is currently **Rank #22 ($1.06M, 0.4% share)**, but grew **+68% YoY**.
            - **Exporter Strategy**: UK NHS Supply Chain tenders prioritize sustainability and cost effectiveness. Indian manufacturers with UKCA markings and carbon footprint audits can displace expensive US ($40.5/unit) and Finnish ($154.9/unit) suppliers.
            """
        )

    with tab_deu:
        render_single_market_tab(
            'Germany',
            """
            - **Market Dominance**: Switzerland ($269.18M, 24.5%), France ($158.44M, 14.4%), Chinese Taipei ($126.88M, 11.5%), Hungary ($92.82M, 8.4%), and Netherlands ($80.85M, 7.4%).
            - **High-Tech Premium**: Europe's largest medical market ($1.09 Billion). Switzerland and France command massive premium unit values.
            - **India Surge (+906% YoY)**: India reached **Rank #19 ($4.43M, 0.4% share)** with a +906% surge in 2024-25.
            - **Exporter Strategy**: Secure full EU MDR (Medical Device Regulation 2017/745) certification and ISO 13485 audits to partner with German OEM medical device packagers.
            """
        )

    with tab_che:
        render_single_market_tab(
            'Switzerland',
            """
            - **Market Dominance**: Germany ($108.10M, 27.5%), Italy ($105.09M, 26.8%), Chinese Taipei ($59.57M, 15.2%), France ($34.89M, 8.9%), and USA ($30.14M, 7.7%).
            - **India Position**: India ranks **#13 ($2.61M, 0.7% share)** with **+305% YoY growth** and **+167% 4-year growth**.
            - **Exporter Strategy**: Switzerland is a global pharmaceutical hub (Novartis, Roche). Focus on supplying pre-fillable glass and cyclic olefin polymer (COP) syringes for Swiss biopharma clinical pipelines.
            """
        )

    with tab_fra:
        render_single_market_tab(
            'France',
            """
            - **Market Dominance**: USA ($154.06M, 18.3%), Hungary ($112.04M, 13.3%), Germany ($86.48M, 10.3%), Italy ($85.44M, 10.1%), and Mexico ($84.88M, 10.1%).
            - **India Position**: India ranks **#27 ($0.51M, 0.1% share)**.
            - **Exporter Strategy**: French hospital purchasing central (UniHA) demands CE marked safety auto-disable syringes. Collaborate with French distributors (e.g., in Lyon and Paris) to bid for multi-year public hospital tenders.
            """
        )

    with tab_nga:
        render_single_market_tab(
            'Nigeria',
            """
            - **India Dominance**: **India is the uncontested Market Leader (#1, $3.70M, 74.8% Market Share)**!
            - **Competitor Landscape**: China (#2, $0.87M, 17.5%), Hong Kong (#3, $0.09M, 1.8%), UK (#4, $0.08M, 1.7%).
            - **Exporter Strategy**: Protect Indian dominance against Chinese low-cost dumping by partnering with NAFDAC for anti-counterfeiting serialization and establishing local bonded inventory in Lagos.
            """
        )

    with tab_kor:
        render_single_market_tab(
            'Korea, Republic of',
            """
            - **Market Dominance**: Chinese Taipei ($35.45M, 23.5%), France ($19.57M, 13.0%), USA ($17.40M, 11.5%), Mexico ($16.77M, 11.1%), and China ($12.57M, 8.3%).
            - **Taiwan's Stronghold**: Taiwan holds nearly a quarter of Korean imports with specialized insulin and beauty/dermatology micro-syringes.
            - **India Position**: India ranks **#19 ($0.08M, 0.1% share)**, growing **+144% YoY**.
            - **Exporter Strategy**: Obtain MFDS (Ministry of Food and Drug Safety) clearance and target Korea's booming medical aesthetics and Botox/filler micro-syringe market.
            """
        )

    with tab_sdn:
        render_single_market_tab(
            'Sudan',
            """
            - **Market Battle**: China (#1, $3.25M, 50.7%) vs **India (#2, $2.03M, 31.8% Market Share)**.
            - **Competitor Landscape**: Egypt (#3, $0.69M, 10.8%), Kenya (#4, $0.16M, 2.5%), Spain (#5, $0.07M, 1.1%).
            - **Exporter Strategy**: Indian quality is highly regarded in humanitarian healthcare tenders (UNICEF, WHO, Red Cross). Secure direct humanitarian supply contracts to overtake China as the #1 supplier.
            """
        )

    with tab_aus:
        render_single_market_tab(
            'Australia',
            """
            - **Market Dominance**: USA ($22.13M, 22.0%), China ($13.22M, 13.1%), UK ($12.60M, 12.5%), Singapore ($8.08M, 8.0%), and Spain ($6.51M, 6.5%).
            - **India Position**: India ranks **#13 ($2.01M, 2.0% share)** with **+105% YoY growth**.
            - **Exporter Strategy**: Leverage the India-Australia Economic Cooperation and Trade Agreement (ECTA) for 0% preferential tariffs and TGA (Therapeutic Goods Administration) fast-track recognition.
            """
        )

    # --------------------------------------------------------------------------
    # TAB: DATA EXPORT
    # --------------------------------------------------------------------------
    with tab_down:
        st.subheader("📥 Export Complete Competitor Intelligence Datasets")
        st.markdown("Download full structured tables containing all supplying competitors, import values, market shares, unit prices, growth metrics, and tariffs across all 10 destination markets.")

        combined_records = []
        for m_name, df_m in all_market_dfs.items():
            df_export = df_m.copy()
            df_export['Import_Val_Unified'] = df_export['Import_Val_USD_K'] * (val_scale if is_usd else macro_scale)
            df_export['Unit_Value_Unified'] = df_export['Unit_Value_USD'] * price_scale
            combined_records.append(df_export)

        if combined_records:
            full_export_df = pd.concat(combined_records, ignore_index=True)
            csv_buf = io.StringIO()
            full_export_df.to_csv(csv_buf, index=False)

            st.dataframe(full_export_df.head(20), use_container_width=True, hide_index=True)

            st.download_button(
                label=f"💾 Download Complete Top 10 Markets Competitor Dataset ({curr_val_macro_label if not is_usd else curr_val_label})",
                data=csv_buf.getvalue(),
                file_name=f"top10_markets_competitor_intelligence_2025_{'usd' if is_usd else 'inr'}.csv",
                mime="text/csv"
            )


if __name__ == "__main__":
    render_competitor_page()