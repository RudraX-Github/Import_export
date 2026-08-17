"""
Overall Strategic Trade Intelligence Report & Action Plan
Specialized Strategic Executive Module for Syringes (HS Code: 90183100)
Synthesizes 5-Year Indian Exports, 2025 Global World Imports, and Top 10 Competitor Supply Matrices.
Seamlessly integrated with main app.py (TradeStat Analytics Hub)
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

# Import loaders from sibling modules
from syringe_90183100_page import load_and_process_all_data
from competitor_analysis_page import load_all_competitor_datasets, COMPETITOR_SHEET_CONFIGS

DEFAULT_FALLBACK_RATE = 83.5

def render_overall_report_page():
    """
    Renders the Executive Strategic Report & Action Plan for Syringe (HS 90183100).
    Protected by app.py master authentication.
    """
    # 1. STRICT ACCESS CONTROL
    if not st.session_state.get("authenticated", False):
        st.error("⛔ **Direct Access Denied**: This executive strategy report is strictly protected and accessible only via the main TradeStat portal (`app.py`). Please sign in through `app.py`.")
        st.stop()

    # Initialize all market data structures safely
    all_market_dfs = {}
    all_comp_dfs = {}
    df_exp = pd.DataFrame()
    df_tm = pd.DataFrame()
    df_comp_summary_raw = pd.DataFrame()

    # 2. Extract User-Defined USD Rate from app.py login page
    user_usd_rate = float(st.session_state.get('usd_rate', 0.0))
    effective_usd_rate = user_usd_rate if user_usd_rate > 0 else DEFAULT_FALLBACK_RATE

    # 3. Custom Dark Theme Styling matching app.py
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
        st.markdown('<div class="page-header">📑 Executive Overall Strategic Report & Action Plan</div>', unsafe_allow_html=True)
        st.markdown('<div class="page-subheader">Syringe (HS 90183100) — Master Synthesis of Indian Exports, Global Import Demand & Competitor Intelligence</div>', unsafe_allow_html=True)
    with head_c2:
        st.markdown(f"<div style='text-align:right; color:#94a3b8;'>User: <strong>{st.session_state.get('username', 'User')}</strong></div>", unsafe_allow_html=True)
        if st.button("Logout", key="overall_logout_btn"):
            for key in ['authenticated', 'username', 'user_id', 'password', 'is_master']:
                st.session_state[key] = None
            st.session_state['authenticated'] = False
            st.rerun()

    # Load All Core Datasets Safely
    with st.spinner("Synthesizing Indian export records, global trade map & competitor supplying matrices..."):
        try:
            df_exp, df_tm = load_and_process_all_data()
        except Exception as e:
            st.warning(f"Note: Indian export data loaded with partial records ({e})")
            
        try:
            all_comp_dfs, df_comp_summary_raw = load_all_competitor_datasets()
            all_market_dfs = all_comp_dfs if all_comp_dfs else {}
        except Exception as e:
            st.warning(f"Note: Competitor datasets loaded with partial records ({e})")
            all_market_dfs = {}

    if df_comp_summary_raw.empty:
        st.error("⚠️ Unable to load competitor summary. Please check your data connection.")
        return

    # SIDEBAR CONTROLS & UNIFIED CURRENCY CONFIGURATION
    with st.sidebar:
        st.markdown("### 💱 Currency Standardization")
        default_curr_idx = 0 if user_usd_rate > 0 else 1
        selected_currency = st.radio(
            "Select Display Currency:",
            options=["USD ($) — Millions / Pieces", "INR (₹) — Crores / Pieces"],
            index=default_curr_idx,
            key="overall_currency_choice"
        )
        is_usd = "USD" in selected_currency

        if is_usd:
            curr_sym = "$"
            curr_val_label = "USD Million ($M)"
            curr_price_label = "$ / Piece"
            val_scale = 1.0 / 1e3 # USD Thousand to USD Million
            exp_val_scale = (1e7 / effective_usd_rate) / 1e6 # INR Cr to USD Million
            price_scale = 1.0
        else:
            curr_sym = "₹"
            curr_val_label = "₹ Crore"
            curr_price_label = "₹ / Piece"
            val_scale = (1e3 * effective_usd_rate) / 1e7 # USD Thousand to INR Crore
            exp_val_scale = 1.0 # Already in INR Crore
            price_scale = effective_usd_rate

        st.caption(f"ℹ️ Active Conversion Rate: **1 USD = ₹{effective_usd_rate:.2f}** {'(Defined at Login)' if user_usd_rate > 0 else '(Default Benchmark)'}.")

        st.markdown("---")
        st.markdown("### 🔍 Global Reset")
        if st.button("🔄 Reset Report Views", key="overall_reset_btn", use_container_width=True):
            st.rerun()

        st.markdown("---")
        st.markdown("### 📚 Integrated Intelligence Layers")
        st.markdown("""
        1. **Indian Export Engine**: 192 Destination Countries (2021-22 to 2025-26)
        2. **Global Trade Map**: 214 Importing Countries ($9.53B Global Demand)
        3. **10 Supplying Competitor Matrices**: Detailed Market Shares, Pricing & Tariffs
        """)

    # SYNTHESIS & SCORING CALCULATIONS
    df_comp_summary = df_comp_summary_raw.copy()
    df_comp_summary['Total_Import_Unified'] = df_comp_summary['Total_Import_USD_K'] * val_scale
    df_comp_summary['India_Import_Unified'] = df_comp_summary['India_Import_Val_USD_K'] * val_scale
    df_comp_summary['White_Space_USD_K'] = df_comp_summary['Total_Import_USD_K'] - df_comp_summary['India_Import_Val_USD_K']
    df_comp_summary['White_Space_Unified'] = df_comp_summary['White_Space_USD_K'] * val_scale

    # Compute Weighted Strategic Opportunity Score (0-100)
    max_m_size = df_comp_summary['Total_Import_USD_K'].max() if not df_comp_summary.empty else 1.0
    
    def calc_opp_score(row):
        size_score = (row['Total_Import_USD_K'] / max_m_size) * 30.0 if max_m_size > 0 else 0
        
        gyoy = row['India_YoY_Growth_2024_2025_Pct']
        if pd.isna(gyoy) or gyoy <= 0: g_score = 5.0
        elif gyoy > 500: g_score = 25.0
        elif gyoy > 100: g_score = 20.0
        elif gyoy > 20: g_score = 15.0
        else: g_score = 10.0
        
        ws_pct = 100.0 - row['India_Share_Pct']
        ws_score = (ws_pct / 100.0) * 20.0
        
        p = row['Top_Supplier_Price_USD']
        if pd.isna(p) or p < 1.0: p_score = 5.0
        elif p > 50.0: p_score = 15.0
        elif p > 10.0: p_score = 12.0
        else: p_score = 8.0
        
        rank = row['India_Rank']
        if pd.isna(rank): f_score = 2.0
        elif rank <= 3: f_score = 10.0
        elif rank <= 10: f_score = 8.0
        elif rank <= 20: f_score = 5.0
        else: f_score = 3.0
        
        return round(size_score + g_score + ws_score + p_score + f_score, 1)

    df_comp_summary['Opportunity_Score'] = df_comp_summary.apply(calc_opp_score, axis=1)

    def assign_tier(score):
        if score >= 85: return "Tier 1: Priority Expansion"
        elif score >= 75: return "Tier 2: High Growth Frontier"
        else: return "Tier 3: Strategic Consolidation"

    df_comp_summary['Strategic_Tier'] = df_comp_summary['Opportunity_Score'].apply(assign_tier)

    # Macro Aggregates
    tot_world_import = (df_tm['Value imported in 2025 (USD thousand)'].sum() * val_scale) if not df_tm.empty else 9534604.0 * val_scale
    tot_10_import = df_comp_summary['Total_Import_Unified'].sum()
    tot_10_india = df_comp_summary['India_Import_Unified'].sum()
    tot_10_white_space = df_comp_summary['White_Space_Unified'].sum()
    india_top10_share = (tot_10_india / tot_10_import) * 100 if tot_10_import > 0 else 0.0

    # TOP MACRO KPI CARDS
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""<div class="metric-card"><div class="metric-title"><i class="fa-solid fa-earth-americas"></i> Global Import Market</div><div class="metric-value">{curr_sym}{tot_world_import/1e3:,.2f} {'B' if is_usd else 'Cr'}</div><div class="metric-sub">214 Countries Tracked</div></div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div class="metric-card" style="border-left-color: #10b981;"><div class="metric-title"><i class="fa-solid fa-bullseye"></i> Top 10 Addressable Demand</div><div class="metric-value">{curr_sym}{tot_10_import:,.2f} {'M' if is_usd else 'Cr'}</div><div class="metric-sub" style="color:#10b981;">{tot_10_import/tot_world_import*100:.1f}% of Global Demand</div></div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""<div class="metric-card" style="border-left-color: #f59e0b;"><div class="metric-title"><i class="fa-solid fa-flag"></i> India's Capture (Top 10)</div><div class="metric-value">{curr_sym}{tot_10_india:,.2f} {'M' if is_usd else 'Cr'}</div><div class="metric-sub" style="color:#f59e0b;">{india_top10_share:.2f}% Market Share</div></div>""", unsafe_allow_html=True)
    with c4:
        st.markdown(f"""<div class="metric-card" style="border-left-color: #8b5cf6;"><div class="metric-title"><i class="fa-solid fa-unlock"></i> Uncaptured White Space</div><div class="metric-value">{curr_sym}{tot_10_white_space:,.2f} {'M' if is_usd else 'Cr'}</div><div class="metric-sub" style="color:#8b5cf6;">{100.0 - india_top10_share:.2f}% Expansion Room</div></div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # UNNUMBERED TABBED MODULES
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "📊 Strategic Executive Summary",
        "🎯 Market Opportunity Matrix",
        "⚔️ Competitor Displacement (China+1)",
        "💎 Value Addition & Margin Growth",
        "🧭 3-Phase Action Roadmap",
        "🎛️ Revenue Simulator & Scenario Planner",
        "📥 Export Executive Strategy Plan"
    ])

    # --------------------------------------------------------------------------
    # TAB 1: STRATEGIC EXECUTIVE SUMMARY
    # --------------------------------------------------------------------------
    with tab1:
        st.subheader("Executive Strategic Synthesis for Indian Syringe Exporters")
        
        st.info("""
        ### 📌 Key Strategic Findings:
        1. **Enormous Uncaptured Demand ($4.33 Billion White Space)**:
           - India's top 10 export destination markets represent **$4.37 Billion USD (₹36,490 Cr)** in annual syringe import demand, but India currently supplies only **$38.45 Million USD (0.88%)**.
           - Increasing India's market share in these 10 countries to just **5%** unlocks an additional **$180 Million USD (~₹1,500 Crore)** in annual export revenue.
        2. **Structural Competitor Shift (China's Retreat in the West)**:
           - China's syringe shipments to the **USA fell -26% YoY**, to the **UK fell -18% YoY**, and to **Nigeria fell -36% 4-year CAGR** due to geopolitical realignment, US Section 301 tariffs, and strict regulatory enforcement.
           - India has proven its capability to capitalize on this shift, surging **+1,431% in the USA**, **+906% in Germany**, and **+305% in Switzerland**.
        3. **Polarized Market Dynamics**:
           - **Scale & Volume Anchors**: Brazil, Nigeria, and Sudan provide reliable base volume (~2.3 billion units/year) but at commoditized prices ($0.03–$0.06/piece).
           - **High-Margin Value Frontiers**: USA, Germany, France, Switzerland, and UK import specialized, pre-fillable, and safety auto-disable syringes at **10x to 50x higher price realizations ($0.69 to $120/piece)**.
        """)

        if HAS_PLOTLY and len(df_comp_summary) > 0:
            col_b1, col_b2 = st.columns(2)
            with col_b1:
                fig_ws = go.Figure()
                fig_ws.add_trace(go.Bar(
                    name="India Captured Value",
                    x=df_comp_summary['Market'],
                    y=df_comp_summary['India_Import_Unified'],
                    marker_color='#10B981'
                ))
                fig_ws.add_trace(go.Bar(
                    name="Uncaptured White Space",
                    x=df_comp_summary['Market'],
                    y=df_comp_summary['White_Space_Unified'],
                    marker_color='#3B82F6'
                ))
                fig_ws.update_layout(
                    barmode='stack',
                    title=f"Addressable Market Demand: Captured vs. White Space ({curr_val_label})",
                    template="plotly_dark", plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                    height=380, legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                )
                st.plotly_chart(fig_ws, use_container_width=True)

            with col_b2:
                top_suppliers_agg = df_comp_summary.groupby('Top_Supplier_1')['Total_Import_Unified'].sum().reset_index()
                fig_comp_pie = px.pie(
                    top_suppliers_agg,
                    names='Top_Supplier_1',
                    values='Total_Import_Unified',
                    title="Share of Total Demand Controlled by Primary Suppliers",
                    color_discrete_sequence=px.colors.sequential.Blues_r
                )
                fig_comp_pie.update_layout(template="plotly_dark", plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", height=380, margin=dict(t=40, b=0, l=0, r=0))
                st.plotly_chart(fig_comp_pie, use_container_width=True)

    # --------------------------------------------------------------------------
    # TAB 2: MARKET OPPORTUNITY MATRIX
    # --------------------------------------------------------------------------
    with tab2:
        st.subheader("Market Prioritization & Composite Opportunity Index")
        st.caption("Multivariate scoring evaluating Market Size (30%), YoY Growth Momentum (25%), White Space Headroom (20%), Price Realization (15%), and Foothold (10%).")

        sorted_opp = df_comp_summary.sort_values('Opportunity_Score', ascending=False).copy()
        
        display_opp = sorted_opp[['Flag', 'Market', 'Strategic_Tier', 'Opportunity_Score', 'Total_Import_Unified', 'India_Import_Unified', 'India_Share_Pct', 'India_YoY_Growth_2024_2025_Pct', 'Top_Supplier_1', 'Top_Supplier_Price_USD']].copy()
        display_opp.columns = [
            '',
            'Market',
            'Strategic Tier',
            'Opportunity Score (0-100)',
            f'Market Size ({curr_val_label})',
            f'India Current ({curr_val_label})',
            'India Share (%)',
            'India YoY Growth (%)',
            'Dominant Competitor',
            'Competitor Price ($/unit)'
        ]
        st.dataframe(display_opp.round(2), use_container_width=True, hide_index=True)

        if HAS_PLOTLY and len(sorted_opp) > 0:
            fig_bubble = px.scatter(
                sorted_opp,
                x='Total_Import_Unified',
                y='Opportunity_Score',
                size='White_Space_Unified',
                color='Strategic_Tier',
                hover_name='Market',
                text='Market',
                log_x=True,
                title=f"Market Opportunity Matrix: Market Size (Log Scale) vs. Opportunity Score (Bubble Size = White Space)",
                labels={'Total_Import_Unified': f'Market Size ({curr_val_label})', 'Opportunity_Score': 'Strategic Opportunity Score (0-100)'},
                color_discrete_map={
                    'Tier 1: Priority Expansion': '#10B981',
                    'Tier 2: High Growth Frontier': '#F59E0B',
                    'Tier 3: Strategic Consolidation': '#8B5CF6'
                }
            )
            fig_bubble.update_traces(textposition='top center')
            fig_bubble.update_layout(template="plotly_dark", plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", height=450)
            st.plotly_chart(fig_bubble, use_container_width=True)

    # --------------------------------------------------------------------------
    # TAB 3: COMPETITOR DISPLACEMENT (CHINA+1)
    # --------------------------------------------------------------------------
    with tab3:
        st.subheader("Competitor Displacement & 'China + 1' Global Strategy")

        st.markdown("""
        #### 🥊 Head-to-Head Battle: India vs. Key Global Competitors
        Global syringe procurement is undergoing massive supply chain diversification. Below is India's competitive positioning against the four main supplier archetypes:
        """)

        comp_matrix_data = [
            {
                "Competitor": "🇨🇳 China",
                "Key Strengths": "Massive automated manufacturing capacity, ultra-low pricing on bulk standard syringes ($0.04-$0.08/unit).",
                "Critical Vulnerabilities": "Subject to US Section 301 tariffs (25-50%), FDA import alerts/warning letters, quality perception issues in EU, supply reliability concerns.",
                "India Attack Strategy": "Displace Chinese volume in US and European hospital tenders by marketing superior quality compliance (US FDA 510(k), ISO 13485) at near-equivalent price points."
            },
            {
                "Competitor": "🇲🇽 Mexico",
                "Key Strengths": "Duty-free USMCA access to USA (22.3% share) and preferential bilateral trade with France (10.1% share), short logistics lead times.",
                "Critical Vulnerabilities": "High production labor costs compared to Asia ($0.69/unit avg price in USA), limited independent raw material resin base.",
                "India Attack Strategy": "Partner with US distributors looking for lower landed cost alternatives for non-urgent bulk and outpatient clinic supplies."
            },
            {
                "Competitor": "🇹🇼 Chinese Taipei",
                "Key Strengths": "Dominates high-precision micro-syringes, insulin delivery, and specialty medical plastics in USA (15.8%), Germany (11.5%), and Korea (23.5%).",
                "Critical Vulnerabilities": "Extremely high unit prices ($11-$105/unit), geopolitical supply chain risks.",
                "India Attack Strategy": "Invest in multi-cavity precision tooling to develop indigenous insulin and cosmetic micro-syringes at 40–60% lower price realizations."
            },
            {
                "Competitor": "🇪🇺 Intra-European (DEU, CHE, FRA, ITA)",
                "Key Strengths": "Unchallenged brand equity, advanced pre-fillable glass/COC syringes, strict EU MDR integration.",
                "Critical Vulnerabilities": "Prohibitive manufacturing cost structures ($30-$140/unit), energy cost inflation.",
                "India Attack Strategy": "Act as contract manufacturing and OEM components partner for European pharma giants (pre-sterilized plungers, barrels, needles)."
            }
        ]
        st.dataframe(pd.DataFrame(comp_matrix_data), use_container_width=True, hide_index=True)

        st.markdown("---")
        st.markdown("#### 📉 China's Import Share Trajectory in Key Western & African Markets (2025)")

        china_shares = []
        if all_market_dfs:
            for m_name, df_m in all_market_dfs.items():
                if df_m is not None and not df_m.empty:
                    ch_r = df_m[df_m['Exporter'].str.contains('China', case=False, na=False)]
                    ind_r = df_m[df_m['Exporter'].str.contains('India', case=False, na=False)]
                    ch_val = ch_r['Import_Val_USD_K'].values[0] if not ch_r.empty else 0
                    ch_share = ch_r['Import_Share_Pct'].values[0] if not ch_r.empty else 0
                    ch_gyoy = ch_r['Growth_Val_2024_2025_Pct'].values[0] if not ch_r.empty else np.nan
                    ind_val = ind_r['Import_Val_USD_K'].values[0] if not ind_r.empty else 0
                    ind_share = ind_r['Import_Share_Pct'].values[0] if not ind_r.empty else 0
                    ind_gyoy = ind_r['Growth_Val_2024_2025_Pct'].values[0] if not ind_r.empty else np.nan

                    china_shares.append({
                        'Market': m_name,
                        'China_Import_Val_USD_K': ch_val,
                        'China_Share_Pct': ch_share,
                        'China_YoY_Growth_Pct': ch_gyoy,
                        'India_Import_Val_USD_K': ind_val,
                        'India_Share_Pct': ind_share,
                        'India_YoY_Growth_Pct': ind_gyoy
                    })

        if china_shares:
            df_china_comp = pd.DataFrame(china_shares)
            df_china_disp = df_china_comp.copy()
            df_china_disp['China_Val_Unified'] = df_china_disp['China_Import_Val_USD_K'] * val_scale
            df_china_disp['India_Val_Unified'] = df_china_disp['India_Import_Val_USD_K'] * val_scale
            
            c_show = df_china_disp[['Market', 'China_Val_Unified', 'China_Share_Pct', 'China_YoY_Growth_Pct', 'India_Val_Unified', 'India_Share_Pct', 'India_YoY_Growth_Pct']].copy()
            c_show.columns = ['Market', f'China Import ({curr_val_label})', 'China Share (%)', 'China YoY (%)', f'India Import ({curr_val_label})', 'India Share (%)', 'India YoY (%)']
            st.dataframe(c_show.round(2), use_container_width=True, hide_index=True)
        else:
            st.info("Competitor detailed comparison matrix is preparing...")

    # --------------------------------------------------------------------------
    # TAB 4: VALUE ADDITION & MARGIN GROWTH
    # --------------------------------------------------------------------------
    with tab4:
        st.subheader("Value Addition, Product Evolution & Margin Multipliers")

        st.info("""
        ### 💡 Strategic Pricing Arbitrage:
        Currently, over **85% of Indian syringe export volume** consists of standard 2-piece and 3-piece disposable syringes realizing **$0.03 – $0.06 per unit (₹2.50 – ₹5.00)** in bulk markets like Brazil and Sudan.
        
        By moving up the manufacturing complexity hierarchy, Indian exporters can multiply revenue realization by **5x to 50x** on the same volume output:
        """)

        tier_ladder = pd.DataFrame([
            {
                "Product Tier": "Tier 1: Standard Bulk Disposable",
                "Product Category": "Standard 2-piece & 3-piece luer lock syringes",
                "Avg Realized Price": f"{curr_sym}{0.04*price_scale:.3f} / pc ($0.04 USD)",
                "Key Destination Markets": "Brazil, Sudan, Nigeria, Egypt",
                "Competitive Strategy": "Low-cost high-speed automation, scale economies, direct tender bidding"
            },
            {
                "Product Tier": "Tier 2: Safety & Auto-Disable Syringes",
                "Product Category": "Auto-disable (AD), retractable needle, needle-stick prevention safety syringes",
                "Avg Realized Price": f"{curr_sym}{0.25*price_scale:.2f} / pc ($0.25 USD) [6x Premium]",
                "Key Destination Markets": "USA, UK (NHS), Germany, Australia",
                "Competitive Strategy": "WHO PQS certification, GPO hospital contracts, US OSHA compliance"
            },
            {
                "Product Tier": "Tier 3: Specialized Delivery Devices",
                "Product Category": "Insulin delivery micro-syringes, dermatology/Botox syringes, dental cartridges",
                "Avg Realized Price": f"{curr_sym}{3.50*price_scale:.2f} / pc ($3.50 USD) [80x Premium]",
                "Key Destination Markets": "Korea RP, Germany, UK, Chinese Taipei",
                "Competitive Strategy": "Precision silicone lubrication, ultra-fine gauge needle integration (31G-33G)"
            },
            {
                "Product Tier": "Tier 4: Bio-Pharma Pre-filled & COP Syringes",
                "Product Category": "Sterile ready-to-fill glass barrels, cyclic olefin polymer (COP) biopharma syringes",
                "Avg Realized Price": f"{curr_sym}{45.00*price_scale:.2f} / pc ($45.00 USD) [1,000x Premium]",
                "Key Destination Markets": "Switzerland, Germany, France, USA",
                "Competitive Strategy": "Pharma OEM partnerships, cleanroom class 100 validation, drug-container compatibility"
            }
        ])
        st.dataframe(tier_ladder, use_container_width=True, hide_index=True)

        if HAS_PLOTLY:
            ladder_chart = pd.DataFrame({
                'Tier': ['Tier 1: Standard Bulk', 'Tier 2: Safety Auto-Disable', 'Tier 3: Micro/Insulin', 'Tier 4: Bio-Pharma Pre-filled'],
                'Unit Price ($ USD)': [0.04, 0.25, 3.50, 45.00],
                'Gross Margin (%)': [15, 35, 60, 85]
            })
            fig_ladder = px.bar(
                ladder_chart,
                x='Tier',
                y='Unit Price ($ USD)',
                color='Gross Margin (%)',
                text='Unit Price ($ USD)',
                log_y=True,
                color_continuous_scale='Viridis',
                title="Value Ladder: Realized Unit Price ($ USD, Log Scale) vs. Gross Profit Margin (%)"
            )
            fig_ladder.update_layout(template="plotly_dark", plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", height=380)
            st.plotly_chart(fig_ladder, use_container_width=True)

    # --------------------------------------------------------------------------
    # TAB 5: 3-PHASE ACTION ROADMAP
    # --------------------------------------------------------------------------
    with tab5:
        st.subheader("Comprehensive 3-Phase Action Roadmap for Indian Manufacturers")

        r1, r2, r3 = st.columns(3)
        with r1:
            st.markdown("""
            <div class="metric-card" style="border-left-color: #3b82f6;">
                <h4 style="color:#60a5fa;">🚀 Phase 1: 0–6 Months</h4>
                <p style="color:#94a3b8; font-weight:700;">Tactical Wins & Volume Consolidation</p>
                <ul style="color:#f8fafc; font-size:0.9rem; line-height:1.6;">
                    <li><strong>Brazil ANVISA Hub</strong>: Partner with bonded logistics providers in Santos/São Paulo to eliminate intermediary margins.</li>
                    <li><strong>Consolidate Africa</strong>: Protect 74.8% Nigeria monopoly via NAFDAC anti-counterfeiting serialization.</li>
                    <li><strong>US Tender Inroads</strong>: Direct sales outreach to US outpatient surgery centers and dental suppliers capitalizing on China tariffs.</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)

        with r2:
            st.markdown("""
            <div class="metric-card" style="border-left-color: #f59e0b;">
                <h4 style="color:#fbbf24;">⚙️ Phase 2: 6–18 Months</h4>
                <p style="color:#94a3b8; font-weight:700;">Regulatory Upgrades & Value Addition</p>
                <ul style="color:#f8fafc; font-size:0.9rem; line-height:1.6;">
                    <li><strong>US FDA 510(k) Fast-Track</strong>: Secure cleared 510(k) submissions for safety auto-disable syringes.</li>
                    <li><strong>EU MDR 2017/745 Certification</strong>: Complete CE notified body audits for European hospital tender eligibility.</li>
                    <li><strong>Australia ECTA Utilization</strong>: Utilize India-Australia trade pact for 0% duty entry to capture 5%+ market share.</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)

        with r3:
            st.markdown("""
            <div class="metric-card" style="border-left-color: #10b981;">
                <h4 style="color:#34d399;">💎 Phase 3: 18–36 Months</h4>
                <p style="color:#94a3b8; font-weight:700;">Biopharma OEM & High-Tech Ecosystem</p>
                <ul style="color:#f8fafc; font-size:0.9rem; line-height:1.6;">
                    <li><strong>Swiss/German Pharma OEM</strong>: Establish cleanroom sterile syringe lines for injectable biologics and GLP-1 pens.</li>
                    <li><strong>Aesthetic Micro-Syringes</strong>: Launch ultra-fine gauge (32G/33G) product lines for Korean and EU cosmetic clinics.</li>
                    <li><strong>Global Brand Establishment</strong>: Evolve from contract supplier to recognized global medical brand.</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)

    # --------------------------------------------------------------------------
    # TAB 6: REVENUE SIMULATOR & SCENARIO PLANNER
    # --------------------------------------------------------------------------
    with tab6:
        st.subheader("Interactive Export Revenue Simulator & Growth Scenario Planner")
        st.caption("Model target market share expansions across top destination markets to project incremental revenue and profit generation.")

        sim_c1, sim_c2 = st.columns([1, 1.2])
        with sim_c1:
            st.markdown("#### 🎛️ Adjust Target Market Shares (%)")
            usa_target = st.slider("USA Target Share (Current: 1.0%):", 1.0, 15.0, 3.5, 0.5, format="%.1f%%")
            deu_target = st.slider("Germany Target Share (Current: 0.4%):", 0.4, 10.0, 2.0, 0.2, format="%.1f%%")
            bra_target = st.slider("Brazil Target Share (Current: 9.7%):", 9.7, 30.0, 18.0, 1.0, format="%.1f%%")
            gbr_target = st.slider("UK Target Share (Current: 0.4%):", 0.4, 10.0, 3.0, 0.5, format="%.1f%%")
            aus_target = st.slider("Australia Target Share (Current: 2.0%):", 2.0, 15.0, 5.0, 0.5, format="%.1f%%")
            other_target_pct = st.slider("Other 5 Markets Target Share Increase (%):", 0.0, 20.0, 5.0, 1.0, format="+%.1f%%")

        with sim_c2:
            st.markdown("#### 📈 Projected Revenue & Impact")
            
            # Calculations
            usa_r = df_comp_summary[df_comp_summary['Market'] == 'United States of America']
            deu_r = df_comp_summary[df_comp_summary['Market'] == 'Germany']
            bra_r = df_comp_summary[df_comp_summary['Market'] == 'Brazil']
            gbr_r = df_comp_summary[df_comp_summary['Market'] == 'United Kingdom']
            aus_r = df_comp_summary[df_comp_summary['Market'] == 'Australia']

            usa_tot = usa_r['Total_Import_USD_K'].values[0] if not usa_r.empty else 1476953.0
            deu_tot = deu_r['Total_Import_USD_K'].values[0] if not deu_r.empty else 1090284.0
            bra_tot = bra_r['Total_Import_USD_K'].values[0] if not bra_r.empty else 66548.0
            gbr_tot = gbr_r['Total_Import_USD_K'].values[0] if not gbr_r.empty else 254072.0
            aus_tot = aus_r['Total_Import_USD_K'].values[0] if not aus_r.empty else 95044.0
            
            other_markets = df_comp_summary[~df_comp_summary['Market'].isin(['United States of America', 'Germany', 'Brazil', 'United Kingdom', 'Australia'])]
            
            sim_usa = (usa_tot * (usa_target / 100.0))
            sim_deu = (deu_tot * (deu_target / 100.0))
            sim_bra = (bra_tot * (bra_target / 100.0))
            sim_gbr = (gbr_tot * (gbr_target / 100.0))
            sim_aus = (aus_tot * (aus_target / 100.0))
            sim_others = other_markets['India_Import_Val_USD_K'].sum() + (other_markets['Total_Import_USD_K'].sum() * (other_target_pct / 100.0))
            
            projected_tot_usd_k = sim_usa + sim_deu + sim_bra + sim_gbr + sim_aus + sim_others
            current_tot_usd_k = df_comp_summary['India_Import_Val_USD_K'].sum()
            incremental_usd_k = projected_tot_usd_k - current_tot_usd_k
            
            proj_unified = projected_tot_usd_k * val_scale
            inc_unified = incremental_usd_k * val_scale
            cur_unified = current_tot_usd_k * val_scale

            st.markdown(f"""
            <div class="metric-card" style="border-left-color: #10b981; margin-bottom: 1rem;">
                <div class="metric-title">Projected Annual Export Revenue</div>
                <div class="metric-value" style="color: #34d399;">{curr_sym}{proj_unified:,.2f} {'M' if is_usd else 'Cr'}</div>
                <div class="metric-sub" style="color:#38bdf8;">Current Base: {curr_sym}{cur_unified:,.2f} {'M' if is_usd else 'Cr'}</div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown(f"""
            <div class="metric-card" style="border-left-color: #8b5cf6;">
                <div class="metric-title">Incremental New Export Gains</div>
                <div class="metric-value" style="color: #c084fc;">+{curr_sym}{inc_unified:,.2f} {'M' if is_usd else 'Cr'}</div>
                <div class="metric-sub" style="color:#a7f3d0;">+{(incremental_usd_k/current_tot_usd_k)*100:.1f}% Strategic Revenue Growth</div>
            </div>
            """, unsafe_allow_html=True)

        if HAS_PLOTLY:
            sim_breakdown = pd.DataFrame([
                {'Market': 'USA', 'Projected Value': sim_usa * val_scale},
                {'Market': 'Germany', 'Projected Value': sim_deu * val_scale},
                {'Market': 'Brazil', 'Projected Value': sim_bra * val_scale},
                {'Market': 'UK', 'Projected Value': sim_gbr * val_scale},
                {'Market': 'Australia', 'Projected Value': sim_aus * val_scale},
                {'Market': 'Other 5 Markets', 'Projected Value': sim_others * val_scale}
            ])
            fig_sim = px.bar(
                sim_breakdown,
                x='Market',
                y='Projected Value',
                color='Projected Value',
                color_continuous_scale='Blues',
                text_auto='.1f',
                title=f"Projected Export Revenue Breakdown by Destination ({curr_val_label})",
                labels={'Projected Value': f"Revenue ({curr_val_label})"}
            )
            fig_sim.update_layout(template="plotly_dark", plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", height=350)
            st.plotly_chart(fig_sim, use_container_width=True)

    # --------------------------------------------------------------------------
    # TAB 7: EXPORT EXECUTIVE STRATEGY PLAN
    # --------------------------------------------------------------------------
    with tab7:
        st.subheader("📥 Download Executive Strategy Dossier & Target Blueprint")
        st.markdown("Download the complete strategic synthesis dataset containing addressable market sizes, competitive scores, white space gaps, price targets, and prioritized action tiers.")

        export_report_df = df_comp_summary[['Market', 'Strategic_Tier', 'Opportunity_Score', 'Total_Import_Unified', 'India_Import_Unified', 'White_Space_Unified', 'India_Share_Pct', 'India_YoY_Growth_2024_2025_Pct', 'Top_Supplier_1', 'Top_Supplier_Share_Pct', 'Top_Supplier_Price_USD', 'India_Price_USD']].copy()
        export_report_df.columns = [
            'Destination Market',
            'Strategic Tier',
            'Opportunity Score (0-100)',
            f'Total Market Demand ({curr_val_label})',
            f'India Current Supply ({curr_val_label})',
            f'Uncaptured White Space ({curr_val_label})',
            'India Market Share (%)',
            'India YoY Growth (%)',
            'Dominant Competitor',
            'Competitor Market Share (%)',
            'Competitor Unit Price ($ USD)',
            'India Unit Price ($ USD)'
        ]

        st.dataframe(export_report_df.round(2), use_container_width=True, hide_index=True)

        csv_buf = io.StringIO()
        export_report_df.to_csv(csv_buf, index=False)
        st.download_button(
            label=f"💾 Download Complete Executive Strategy Dossier ({'USD' if is_usd else 'INR'})",
            data=csv_buf.getvalue(),
            file_name=f"syringe_hs90183100_executive_strategic_report_{'usd' if is_usd else 'inr'}.csv",
            mime="text/csv"
        )


if __name__ == "__main__":
    render_overall_report_page()