import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import requests
from functools import reduce
import urllib.parse
import time

# ----------------------------------------------------
# 1. SETUP & SESSION STATE
# ----------------------------------------------------
st.set_page_config(page_title="TradeStat Analytics Hub", layout="wide", page_icon="🌍")

# --- ACTIVE GOOGLE APPS SCRIPT URL ---
AUTH_API_URL = "https://script.google.com/macros/s/AKfycbz3puku5wA6mVD1imgoNOhQ581h5nC3wVKltCxLE-iLTRWQE15fHMlMr_d1KTcTc50-/exec"

# Exact LSOD Chapters Requested
LSOD_CHAPTERS = [str(x).zfill(2) for x in [7,8,9,10,11,12,13,19,20,25,28,29,30,31,38,39,40,48,49,50,53,57,66,69,71,73,74,76,77,78,82,90,95,96]]

# Initialize Session States
for key in ['authenticated', 'username', 'user_id', 'is_master', 'password', 'user_prefs', 'lsod_mode', 'usd_rate']:
    if key not in st.session_state:
        st.session_state[key] = False if isinstance(key, bool) else None
        if key == 'user_prefs': st.session_state[key] = {}
        if key == 'usd_rate': st.session_state[key] = 0.0

# Master Filter State Initialization
filter_keys = {
    'filter_year': '25_26', 'filter_search': '', 'filter_sector': 'All',
    'filter_chapter': 'All', 'filter_tier': 'All', 'filter_growth': 'All Trends',
    'filter_products': []
}
for key, default_val in filter_keys.items():
    if key not in st.session_state:
        st.session_state[key] = default_val

def reset_filters():
    for key, default_val in filter_keys.items():
        st.session_state[key] = default_val

def call_api(payload):
    try:
        response = requests.post(AUTH_API_URL, json=payload)
        return response.json()
    except Exception as e:
        return {"success": False, "message": f"Network Error: {str(e)}"}

# ----------------------------------------------------
# 2. CUSTOM CSS STYLING
# ----------------------------------------------------
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
    #MainMenu {visibility: hidden;} footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# ----------------------------------------------------
# 3. HIGH-PERFORMANCE DATA PIPELINE
# ----------------------------------------------------
def get_sector(chapter_str):
    try: ch = int(chapter_str)
    except: return 'Miscellaneous'
    if ch in [1, 2, 3]: return 'Seafood & Meat'
    if 4 <= ch <= 24: return 'Agriculture & Food'
    if ch in [25, 26]: return 'Minerals & Mining'
    if ch == 27: return 'Petroleum & Fuels'
    if 28 <= ch <= 38: return 'Chemicals & Allied'
    if 39 <= ch <= 40: return 'Plastics & Rubber'
    if 41 <= ch <= 43: return 'Leather & Footwear'
    if 44 <= ch <= 49: return 'Wood & Paper'
    if 50 <= ch <= 63: return 'Textiles & Apparel'
    if 64 <= ch <= 67: return 'Leather & Footwear'
    if 68 <= ch <= 70: return 'Stone & Glass'
    if ch == 71: return 'Gems & Jewellery'
    if 72 <= ch <= 83: return 'Steel & Metals'
    if ch == 84: return 'Machinery & Engineering'
    if ch == 85: return 'Electronics & Electricals'
    if 86 <= ch <= 89: return 'Automobiles & Transport'
    if 90 <= ch <= 92: return 'Precision Instruments'
    if 94 <= ch <= 96: return 'Furniture & Lighting'
    return 'Miscellaneous'

@st.cache_data(ttl=3600)
def fetch_base_data():
    sheet_ids = {
        '21_22': '19YxzZy-BzYpdr03IMpf6dXoVyECxB2bAaGn2AIYU09A',
        '22_23': '1_4GiS_8MhxZ9lmL7bOHWiAFMs-OF1JF7sezkGTciNZw',
        '23_24': '1bIUSFgi78MV9_YzCu_cKYDAOR-dYjPqfqgUQ7J4Escg',
        '24_25': '1CrHauthrBLLz9JzeBMj5K08YNAiQeYbZ3KzRWPJHJo8',
        '25_26': '1AaK43fFKf29BK1nVVXFjrAkjmFXPcVisAwB5UNeriWw'
    }
    base_url = "https://docs.google.com/spreadsheets/d/{}/export?format=csv"
    dataframes, commodity_dict = [], {}

    for year, sheet_id in sheet_ids.items():
        df = pd.read_csv(base_url.format(sheet_id), dtype=str)
        cols = df.columns
        df = df.rename(columns={
            cols[1]: 'HSCode', cols[2]: 'Commodity',
            cols[3]: f'Base_Val_{year}', cols[5]: f'Curr_Val_{year}', cols[7]: f'Growth_{year}'
        })
        df = df[['HSCode', 'Commodity', f'Base_Val_{year}', f'Curr_Val_{year}', f'Growth_{year}']]
        df = df.dropna(subset=['HSCode'])
        df = df[df['HSCode'].str.match(r'^\d+$', na=False)] 
        df['HSCode'] = df['HSCode'].str.zfill(8)
        
        for _, row in df.iterrows():
            if pd.notna(row['Commodity']): commodity_dict[row['HSCode']] = row['Commodity']
        df = df.drop(columns=['Commodity'])
        
        for num_col in [f'Base_Val_{year}', f'Curr_Val_{year}', f'Growth_{year}']:
            df[num_col] = df[num_col].str.replace(',', '', regex=False)
            df[num_col] = pd.to_numeric(df[num_col], errors='coerce').fillna(0)
        dataframes.append(df)

    merged_df = reduce(lambda left, right: pd.merge(left, right, on='HSCode', how='outer'), dataframes)
    merged_df['Curr_Val_All'] = merged_df[['Curr_Val_21_22', 'Curr_Val_22_23', 'Curr_Val_23_24', 'Curr_Val_24_25', 'Curr_Val_25_26']].sum(axis=1)
    merged_df['Base_Val_All'] = merged_df[['Base_Val_21_22', 'Base_Val_22_23', 'Base_Val_23_24', 'Base_Val_24_25', 'Base_Val_25_26']].sum(axis=1)
    merged_df['Growth_All'] = np.where(merged_df['Base_Val_All'] > 0, ((merged_df['Curr_Val_All'] - merged_df['Base_Val_All']) / merged_df['Base_Val_All']) * 100, 0)
    
    merged_df['Commodity'] = merged_df['HSCode'].map(commodity_dict).fillna("Unknown")
    merged_df = merged_df.fillna(0)
    merged_df['Chapter'] = merged_df['HSCode'].str[:2]
    merged_df['Sector'] = merged_df['Chapter'].apply(get_sector)
    merged_df['Product_Select'] = merged_df['HSCode'] + " - " + merged_df['Commodity']
    merged_df['Product Image'] = "https://www.google.com/search?tbm=isch&q=" + merged_df['HSCode'] + "+" + merged_df['Commodity'].apply(lambda x: urllib.parse.quote_plus(str(x)))
    
    return merged_df

def get_processed_data():
    df = fetch_base_data().copy()
    
    # 1. LSOD vs ALL Filter
    if st.session_state.lsod_mode == "LSOD":
        df = df[df['Chapter'].isin(LSOD_CHAPTERS)]
        
    # 2. USD Conversion
    if st.session_state.usd_rate > 0:
        rate = st.session_state.usd_rate
        val_cols = [c for c in df.columns if 'Val' in c]
        for col in val_cols:
            # USD = (Amount in Crores * 10000000) / USD rate
            df[col] = (df[col] * 10000000) / rate
            
    # 3. Inject User Preferences for the Data Editor State mapping
    prefs = st.session_state.user_prefs
    df['⭐ Preferred'] = df['HSCode'].apply(lambda x: True if x in prefs else False)
    df['📝 Analysis Note'] = df['HSCode'].apply(lambda x: prefs.get(x, ''))
    
    return df

# ----------------------------------------------------
# 4. LOGIN & MASTER UI
# ----------------------------------------------------
def login_screen():
    st.markdown("<h1 style='text-align: center; color: #3b82f6;'>TradeStat Secure Portal</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("auth_form"):
            user_input = st.text_input("User Name")
            pass_input = st.text_input("Password", type="password")
            
            # Additional Login Parameters
            mode_input = st.selectbox("Data Mode", ["ALL", "LSOD"])
            usd_input = st.number_input("USD Rate (Optional, 0 to ignore)", min_value=0.0, value=0.0, step=0.1)
            
            c_btn1, c_btn2 = st.columns(2)
            with c_btn1: submit_login = st.form_submit_button("Sign In", use_container_width=True)
            with c_btn2: submit_register = st.form_submit_button("Register", use_container_width=True)
                
            if submit_login:
                with st.spinner("Authenticating..."):
                    res = call_api({"action": "login", "username": user_input, "password": pass_input})
                    if res.get("success"):
                        st.session_state['authenticated'] = True
                        st.session_state['username'] = user_input
                        st.session_state['password'] = pass_input
                        st.session_state['user_id'] = res.get("userId")
                        st.session_state['is_master'] = res.get("isMaster", False)
                        st.session_state['lsod_mode'] = mode_input
                        st.session_state['usd_rate'] = usd_input
                        
                        pref_res = call_api({"action": "get_prefs", "userId": st.session_state['user_id']})
                        if pref_res.get("success"):
                            st.session_state['user_prefs'] = pref_res.get("prefs", {})
                        st.rerun()
                    else: st.error("Invalid credentials.")
                        
            if submit_register:
                with st.spinner("Registering..."):
                    res = call_api({"action": "register", "username": user_input, "password": pass_input})
                    if res.get("success"): st.success(res.get("message"))
                    else: st.error(res.get("message"))

def master_dashboard():
    st.title("👑 Master Admin Dashboard")
    if st.button("⬅ Return to Analytics"):
        st.session_state['viewing_master'] = False
        st.rerun()
    st.divider()
    
    colA, colB = st.columns(2)
    with colA:
        st.subheader("👥 Manage Users")
        with st.spinner("Fetching live users..."):
            res = call_api({"action": "get_users", "masterUser": st.session_state['username'], "masterPass": st.session_state['password']})
        if res.get("success"):
            users = res.get("users", [])
            for u in users:
                c1, c2, c3, c4 = st.columns([2, 3, 3, 2])
                c1.code(u['id'][:8] + "...")
                c2.markdown(f"**{u['username']}**")
                c3.markdown(f"*{u['password']}*")
                if c4.button("Delete User", key=u['id'], type="primary"):
                    call_api({"action": "delete_user", "id": u['id'], "masterUser": st.session_state['username'], "masterPass": st.session_state['password']})
                    st.rerun()
        else: st.error("Failed to load user data.")
        
    with colB:
        st.subheader("🗑️ Data Management")
        st.warning("Warning: Deleting a chapter removes it permanently from all 5 Google Sheets.")
        
        df = fetch_base_data()
        chaps = sorted(list(df['Chapter'].unique()))
        ch_to_del = st.selectbox("Select Chapter to Delete", chaps)
        
        if st.button("Delete Entire Chapter", type="primary"):
            with st.spinner(f"Deleting Chapter {ch_to_del} from all databases..."):
                del_res = call_api({"action": "delete_chapter", "chapter": ch_to_del, "masterUser": st.session_state['username'], "masterPass": st.session_state['password']})
                if del_res.get("success"):
                    st.success(del_res.get("message"))
                    st.cache_data.clear() # Force re-fetch from sheets
                    time.sleep(2)
                    st.rerun()
                else:
                    st.error(del_res.get("message"))

# ----------------------------------------------------
# 5. MAIN ANALYTICS DASHBOARD
# ----------------------------------------------------
def analytics_dashboard():
    sym = "$" if st.session_state.usd_rate > 0 else "₹"
    unit_label = f"({sym})" if st.session_state.usd_rate > 0 else f"({sym} Cr)"

    head_c1, head_c2 = st.columns([4, 1])
    with head_c1: st.title(f"🌍 TradeStat {'LSOD' if st.session_state.lsod_mode == 'LSOD' else 'Global'} Analytics")
    with head_c2:
        st.markdown(f"<div style='text-align:right; color:#94a3b8;'>User: <strong>{st.session_state['username']}</strong></div>", unsafe_allow_html=True)
        btn_cols = st.columns(2) if st.session_state['is_master'] else [st.container()]
        if st.session_state['is_master']:
            if btn_cols[0].button("👑 Master"):
                st.session_state['viewing_master'] = True
                st.rerun()
        logout_container = btn_cols[1] if st.session_state['is_master'] else btn_cols[0]
        if logout_container.button("Logout"):
            for key in ['authenticated', 'username', 'user_id', 'password', 'is_master']: st.session_state[key] = None
            st.session_state['authenticated'] = False
            st.rerun()

    with st.spinner("Processing Data Pipeline..."):
        df = get_processed_data()

    # --- SIDEBAR CONTROLS ---
    st.sidebar.button("🏠 Reset / Home", on_click=reset_filters, type="primary", use_container_width=True)
    
    target_year = st.sidebar.selectbox("📅 Financial Year", ['All', '25_26', '24_25', '23_24', '22_23', '21_22'], key='filter_year')
    curr_col = f'Curr_Val_{target_year}'
    base_col = f'Base_Val_{target_year}'
    growth_col = f'Growth_{target_year}'

    # Dynamic Market Tier Calculation (accounting for USD Conversion formula shift)
    def get_tier(val):
        if st.session_state.usd_rate == 0:
            tier_well = 250
            tier_emerg = 10
        else:
            tier_well = (250 * 10000000) / st.session_state.usd_rate
            tier_emerg = (10 * 10000000) / st.session_state.usd_rate
            
        if val > tier_well: return 'Well Established'
        elif val >= tier_emerg: return 'Emerging Market'
        else: return 'Just Started'
        
    df['Market Tier'] = df[curr_col].apply(get_tier)

    # --- STANDARD FILTERS ---
    st.sidebar.markdown("### 🔍 Advanced Filters")
    st.sidebar.text_input("Search HS Code / Commodity", key='filter_search')
    st.sidebar.selectbox("🏭 Sector", ["All"] + sorted(list(df['Sector'].unique())), key='filter_sector')
    st.sidebar.selectbox("📂 HS Chapter", ["All"] + sorted(list(df['Chapter'].unique())), key='filter_chapter')
    st.sidebar.radio("📊 Market Tier", ["All", "Well Established", "Emerging Market", "Just Started"], key='filter_tier')
    
    growth_options = ["All Trends", "🚀 Volume Surge (> 50%)", "📈 Positive Growth (> 0%)", "📉 Negative Growth (< 0%)", "🔻 Sharp Drop (< -50%)", "✨ Newly Emerged (Base=0, Curr>0)", "⏸️ Discontinued (Base>0, Curr=0)"]
    st.sidebar.selectbox("📈 Growth Trend", growth_options, key='filter_growth')

    # --- SPECIFIC PRODUCT ISOLATION ---
    st.sidebar.markdown("### 🎯 Specific Product Analysis")
    st.sidebar.multiselect("Isolate Analytics to Specific Commodities:", options=df['Product_Select'].tolist(), key='filter_products')

    # --- APPLY FILTERS ---
    f_df = df.copy()
    if st.session_state.filter_products: f_df = f_df[f_df['Product_Select'].isin(st.session_state.filter_products)]
    search = st.session_state.filter_search
    if search: f_df = f_df[f_df['HSCode'].str.contains(search, case=False) | f_df['Commodity'].str.contains(search, case=False)]
    if st.session_state.filter_sector != "All": f_df = f_df[f_df['Sector'] == st.session_state.filter_sector]
    if st.session_state.filter_chapter != "All": f_df = f_df[f_df['Chapter'] == st.session_state.filter_chapter]
    if st.session_state.filter_tier != "All": f_df = f_df[f_df['Market Tier'] == st.session_state.filter_tier]
    
    growth_f = st.session_state.filter_growth
    if growth_f == "🚀 Volume Surge (> 50%)": f_df = f_df[f_df[growth_col] > 50]
    elif growth_f == "📈 Positive Growth (> 0%)": f_df = f_df[f_df[growth_col] > 0]
    elif growth_f == "📉 Negative Growth (< 0%)": f_df = f_df[f_df[growth_col] < 0]
    elif growth_f == "🔻 Sharp Drop (< -50%)": f_df = f_df[f_df[growth_col] < -50]
    elif growth_f == "✨ Newly Emerged (Base=0, Curr>0)": f_df = f_df[(f_df[base_col] == 0) & (f_df[curr_col] > 0)]
    elif growth_f == "⏸️ Discontinued (Base>0, Curr=0)": f_df = f_df[(f_df[base_col] > 0) & (f_df[curr_col] == 0)]

    # --- MACRO KPIs ---
    c1, c2, c3, c4 = st.columns(4)
    total_export = f_df[curr_col].sum()
    well_est_val = f_df[f_df['Market Tier'] == 'Well Established'][curr_col].sum()
    emerging_val = f_df[f_df['Market Tier'] == 'Emerging Market'][curr_col].sum()
    just_started_val = f_df[f_df['Market Tier'] == 'Just Started'][curr_col].sum()

    with c1: st.markdown(f"""<div class="metric-card"><div class="metric-title"><i class="fa-solid fa-wallet"></i> Total Export {unit_label}</div><div class="metric-value">{sym}{total_export:,.0f}</div><div class="metric-sub" style="color:#94a3b8;">{len(f_df):,} Items</div></div>""", unsafe_allow_html=True)
    with c2: st.markdown(f"""<div class="metric-card" style="border-left-color: #10b981;"><div class="metric-title"><i class="fa-solid fa-award"></i> Well Established</div><div class="metric-value">{sym}{well_est_val:,.0f}</div><div class="metric-sub" style="color:#10b981;">Highest Tier</div></div>""", unsafe_allow_html=True)
    with c3: st.markdown(f"""<div class="metric-card" style="border-left-color: #f59e0b;"><div class="metric-title"><i class="fa-solid fa-chart-line-up"></i> Emerging Market</div><div class="metric-value">{sym}{emerging_val:,.0f}</div><div class="metric-sub" style="color:#f59e0b;">Middle Tier</div></div>""", unsafe_allow_html=True)
    with c4: st.markdown(f"""<div class="metric-card" style="border-left-color: #8b5cf6;"><div class="metric-title"><i class="fa-solid fa-seedling"></i> Just Started</div><div class="metric-value">{sym}{just_started_val:,.0f}</div><div class="metric-sub" style="color:#8b5cf6;">Lowest Tier</div></div>""", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    # --- TABS: REORDERED EXACTLY AS REQUESTED ---
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📋 Master Catalog", "📊 Visual Analytics", "🚀 Growth & Trends", 
        "📁 Chapter Aggregation", "💡 AI Insights", "⭐ My Personal Watchlist"
    ])

    with tab1:
        st.markdown(f"**Unified Trade Catalog ({target_year.replace('_','-')})**")
        st.caption("Check the **⭐ Preferred** box or write a **📝 Analysis Note** below, then click the Save button to update your Google Sheet Database.")
        
        display_cols = ['HSCode', 'Commodity', '⭐ Preferred', '📝 Analysis Note', 'Sector', 'Chapter', 'Market Tier', base_col, curr_col, growth_col, 'Product Image']
        edit_df = f_df[display_cols].sort_values(curr_col, ascending=False).reset_index(drop=True)
        
        # Render Interactive Data Editor (Product Image is included and disabled)
        st.data_editor(
            edit_df,
            use_container_width=True, hide_index=True, height=500,
            disabled=['HSCode', 'Commodity', 'Sector', 'Chapter', 'Market Tier', base_col, curr_col, growth_col, 'Product Image'],
            column_config={
                base_col: st.column_config.NumberColumn(f"Base Val {unit_label}", format="%.2f"),
                curr_col: st.column_config.NumberColumn(f"Curr Val {unit_label}", format="%.2f"),
                growth_col: st.column_config.NumberColumn("Growth (%)", format="%.2f%%"),
                "⭐ Preferred": st.column_config.CheckboxColumn("⭐ Preferred", default=False),
                "📝 Analysis Note": st.column_config.TextColumn("📝 Analysis Note"),
                "Product Image": st.column_config.LinkColumn("Product Images", display_text="🖼️ View Gallery")
            },
            key="master_catalog_editor"
        )
        
        if st.button("💾 Save Preferences to Database", type="primary"):
            changes_made = False
            with st.spinner("Synchronizing edits with Google Sheets..."):
                edited_rows = st.session_state["master_catalog_editor"].get("edited_rows", {})
                for row_idx, edits in edited_rows.items():
                    hs_code = edit_df.iloc[row_idx]['HSCode']
                    is_pref = edits.get('⭐ Preferred', edit_df.iloc[row_idx]['⭐ Preferred'])
                    note = edits.get('📝 Analysis Note', edit_df.iloc[row_idx]['📝 Analysis Note'])
                    
                    payload = { "action": "save_pref", "userId": st.session_state['user_id'], "username": st.session_state['username'], "hscode": hs_code, "note": note, "is_preferred": is_pref }
                    res = call_api(payload)
                    if res.get("success"):
                        changes_made = True
                        if is_pref: st.session_state['user_prefs'][hs_code] = note
                        else: st.session_state['user_prefs'].pop(hs_code, None)
            
            if changes_made:
                st.success("Successfully synchronized all changes.")
                time.sleep(1)
                st.rerun()
            elif not edited_rows:
                st.info("No changes detected in the catalog.")

    with tab2:
        colA, colB = st.columns(2)
        with colA:
            st.markdown(f"**Market Tier Distribution ({target_year.replace('_','-')})**")
            tier_df = f_df.groupby('Market Tier')[curr_col].sum().reset_index()
            fig_pie = px.pie(tier_df, values=curr_col, names='Market Tier', hole=0.4,
                             color='Market Tier', color_discrete_map={'Well Established':'#10b981', 'Emerging Market':'#f59e0b', 'Just Started':'#8b5cf6'})
            fig_pie.update_layout(margin=dict(t=10, b=10), template="plotly_dark", plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig_pie, use_container_width=True)

        with colB:
            st.markdown(f"**Top 10 Export Sectors {unit_label}**")
            sec_df = f_df.groupby('Sector')[curr_col].sum().reset_index().sort_values(curr_col, ascending=False).head(10)
            fig_bar = px.bar(sec_df, x=curr_col, y='Sector', orientation='h', text_auto='.2s', color=curr_col, color_continuous_scale='Blues')
            fig_bar.update_layout(yaxis={'categoryorder':'total ascending'}, margin=dict(t=10, b=10), template="plotly_dark", plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig_bar, use_container_width=True)

    with tab3:
        st.markdown(f"**Top 20 Surging Commodities ({target_year.replace('_','-')})**")
        # Scale the base threshold to avoid dividing by 0 anomalies
        base_thresh = 5 if st.session_state.usd_rate == 0 else (5 * 10000000)/st.session_state.usd_rate
        valid_growth_df = f_df[f_df[base_col] > base_thresh].sort_values(growth_col, ascending=False).head(20)
        
        if len(valid_growth_df) > 0:
            fig_growth = px.bar(valid_growth_df, x='HSCode', y=growth_col, hover_name='Commodity', text=growth_col, color=growth_col, color_continuous_scale='Emrld')
            fig_growth.update_layout(xaxis_type='category', template="plotly_dark", plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig_growth, use_container_width=True)
        else: st.info("No commodities match the growth criteria for the selected filters.")

    with tab4:
        st.markdown(f"### Aggregation by Chapter ({target_year.replace('_','-')})")
        chap_agg = f_df.groupby('Chapter').agg(Total_Val=(curr_col, 'sum'), Item_Count=('HSCode', 'count')).reset_index().sort_values('Total_Val', ascending=False)
        st.dataframe(chap_agg, hide_index=True, use_container_width=True, column_config={"Total_Val": st.column_config.NumberColumn(f"Total Value {unit_label}", format="%.2f")})

    with tab5:
        if total_export > 0:
            top_driver = f_df.sort_values(curr_col, ascending=False).iloc[0]
            st.markdown(f"### Strategic Market Insights")
            st.info(f"**Macro Overview:** The dataset captures **{len(f_df):,}** commodities generating a combined value of **{sym}{total_export:,.2f}**.")
            st.success(f"**Dominant Value Driver:** The highest contributing commodity is **HS {top_driver['HSCode']}** ({top_driver['Commodity']}). It accounted for **{sym}{top_driver[curr_col]:,.2f}**.")
        else: st.write("No data available.")

    with tab6:
        st.markdown("### ⭐ My Personal Watchlist & 360 Analysis")
        
        if not st.session_state['user_prefs']:
            st.info("Your watchlist is empty. Go to the 'Master Catalog' tab to check '⭐ Preferred' for commodities you want to track.")
        else:
            st.markdown("**Your Bookmarked Commodities:**")
            pref_hs_codes = list(st.session_state['user_prefs'].keys())
            watchlist_df = df[df['HSCode'].isin(pref_hs_codes)].copy()
            watchlist_df['My Saved Note'] = watchlist_df['HSCode'].map(st.session_state['user_prefs'])
            
            st.dataframe(watchlist_df[['HSCode', 'Commodity', 'My Saved Note', curr_col, growth_col]], use_container_width=True, hide_index=True)
            
            st.markdown("---")
            st.markdown("### 🔎 Product 360 Deep-Dive")
            st.caption("Select a commodity strictly from your watchlist below to view its 5-year trend analysis.")
            
            selected_hs = st.radio(
                "Select Bookmarked Commodity:", 
                options=watchlist_df['HSCode'].tolist(), 
                format_func=lambda x: f"HS {x} - {watchlist_df[watchlist_df['HSCode']==x]['Commodity'].values[0]}"
            )
            
            if selected_hs:
                prod_data = watchlist_df[watchlist_df['HSCode'] == selected_hs].iloc[0]
                
                c_chart, c_details = st.columns([2, 1])
                with c_chart:
                    trend_data = {
                        'Financial Year': ['20-21', '21-22', '22-23', '23-24', '24-25', '25-26'],
                        f'Export Value {unit_label}': [prod_data['Base_Val_21_22'], prod_data['Curr_Val_21_22'], prod_data['Curr_Val_22_23'], prod_data['Curr_Val_23_24'], prod_data['Curr_Val_24_25'], prod_data['Curr_Val_25_26']]
                    }
                    fig = px.bar(pd.DataFrame(trend_data), x='Financial Year', y=f'Export Value {unit_label}', text_auto='.2s', color=f'Export Value {unit_label}', color_continuous_scale='Blues')
                    fig.update_layout(margin=dict(t=10, b=10), template="plotly_dark", plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
                    st.plotly_chart(fig, use_container_width=True)
                    
                with c_details:
                    st.markdown(f"**Analysis Details for HS {selected_hs}**")
                    st.info(f"**Your Saved Note:**\n\n{prod_data['My Saved Note']}")
                    st.markdown(f"**Sector:** {prod_data['Sector']}")
                    st.markdown(f"**Chapter:** Ch {prod_data['Chapter']}")
                    st.markdown(f"**Market Tier:** {prod_data['Market Tier']}")
                    st.markdown(f"**Latest Growth:** {prod_data['Growth_25_26']:.2f}%")
                    st.markdown(f"[🖼️ View Product Images]({prod_data['Product Image']})")

if __name__ == "__main__":
    if not st.session_state['authenticated']:
        login_screen()
    elif st.session_state.get('viewing_master', False) and st.session_state['is_master']:
        master_dashboard()
    else:
        analytics_dashboard()