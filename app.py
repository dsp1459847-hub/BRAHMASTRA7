import streamlit as st
import pandas as pd
import numpy as np
from datetime import timedelta
from collections import Counter

st.set_page_config(page_title="MAYA AI - Ikai Dahai Frequency", layout="wide")

st.title("MAYA AI 🧮: Ikai-Dahai Frequency Matrix (History Proven)")
st.markdown("Yeh system Dahai aur Ikai par 6 Timeframes lagakar unki **Frequency (Kitni Baar Aaye)** nikalta hai, aur pichle 30 din ki history se confirm karta hai ki kaunsa 'Baar' sabse strong hai.")

# --- 1. Direct Selection Interface ---
st.sidebar.header("📁 Data Settings")
uploaded_file = st.sidebar.file_uploader("Upload CSV/Excel", type=['csv', 'xlsx'])
shift_names = ["DS", "FD", "GD", "GL", "DB", "SG", "ZA"]
target_shift_name = st.sidebar.selectbox("🎯 Target Shift", shift_names)
selected_end_date = st.sidebar.date_input("Calculation Date")
max_limit = st.sidebar.slider("Max Repeat Limit (Digits)", 2, 5, 4)

if uploaded_file is not None:
    try:
        # --- 2. Data Cleaning ---
        if uploaded_file.name.endswith('.csv'): df = pd.read_csv(uploaded_file)
        else: df = pd.read_excel(uploaded_file)
        
        df['DATE'] = pd.to_datetime(df['DATE'], errors='coerce')
        df = df.sort_values(by='DATE').reset_index(drop=True)
        for col in shift_names:
            if col in df.columns: df[col] = pd.to_numeric(df[col], errors='coerce')

        filtered_df = df[df['DATE'].dt.date <= selected_end_date].copy()
        if len(filtered_df) == 0: st.stop()

        target_date_next = filtered_df['DATE'].iloc[-1] + timedelta(days=1)

        # --- 3. DIGIT SEPARATION & LOGIC ---
        def run_digit_elimination(digit_list, limit):
            digit_list = [int(x) for x in digit_list if pd.notna(x)]
            eliminated = set()
            scores = Counter()
            for days in range(1, 31):
                if len(digit_list) < days: continue
                sheet = digit_list[-days:]
                counts = Counter(sheet)
                if len(counts) == len(sheet) and len(sheet) > 1: eliminated.update(sheet)
                for num, freq in counts.items():
                    if freq >= limit: eliminated.add(num)
                    else: scores[num] += 1
            return eliminated, scores

        def get_top_digits(past_data):
            if len(past_data) < 2: return []
            e, s = run_digit_elimination(past_data, max_limit)
            safe = sorted([n for n in range(10) if n not in e], key=lambda x: s[x], reverse=True)
            return safe[:2] if safe else []

        # Function to get all votes from 6 timeframes for a given date
        def get_all_timeframe_votes(t_date):
            past_df = filtered_df[filtered_df['DATE'] < t_date]
            if len(past_df) < 30: return [], []
            
            main_valid = [int(x) for x in past_df[target_shift_name].tolist() if pd.notna(x)]
            d_list = [x // 10 for x in main_valid]
            i_list = [x % 10 for x in main_valid]
            
            curr_weekday = t_date.dayofweek
            war_df = past_df[past_df['DATE'].dt.dayofweek == curr_weekday]
            war_valid = [int(x) for x in war_df[target_shift_name].tolist() if pd.notna(x)]
            wd_list = [x // 10 for x in war_valid]
            wi_list = [x % 10 for x in war_valid]

            d_votes = get_top_digits(d_list[-3:]) + get_top_digits(d_list[-5:]) + get_top_digits(d_list[-10:]) + get_top_digits(d_list[-15:]) + get_top_digits(d_list[-30:]) + get_top_digits(wd_list[-15:])
            i_votes = get_top_digits(i_list[-3:]) + get_top_digits(i_list[-5:]) + get_top_digits(i_list[-10:]) + get_top_digits(i_list[-15:]) + get_top_digits(i_list[-30:]) + get_top_digits(wi_list[-15:])
            
            return d_votes, i_votes

        # --- 4. HISTORICAL BACKTESTING (Pichle 30 Din) ---
        valid_dates = filtered_df.dropna(subset=[target_shift_name])['DATE'].tolist()
        test_dates = valid_dates[-30:] if len(valid_dates) > 30 else valid_dates
        
        dahai_win_history = Counter()
        ikai_win_history = Counter()
        
        with st.spinner("⏳ Pichle 30 din ki Dahai aur Ikai ki History Check chal rahi hai..."):
            for t_date in test_dates:
                d_votes, i_votes = get_all_timeframe_votes(t_date)
                if not d_votes or not i_votes: continue
                
                d_counts = Counter(d_votes)
                i_counts = Counter(i_votes)
                
                actual_val = filtered_df[filtered_df['DATE'] == t_date][target_shift_name].values[0]
                if pd.notna(actual_val):
                    actual_num = int(actual_val)
                    actual_d = actual_num // 10
                    actual_i = actual_num % 10
                    
                    dahai_win_history[d_counts.get(actual_d, 0)] += 1
                    ikai_win_history[i_counts.get(actual_i, 0)] += 1

        # Find Historically Best Frequency
        best_dahai_freq = max(dahai_win_history, key=dahai_win_history.get) if dahai_win_history else 2
        best_ikai_freq = max(ikai_win_history, key=ikai_win_history.get) if ikai_win_history else 2

        # --- 5. LIVE CALCULATION FOR TODAY ---
        today_d_votes, today_i_votes = get_all_timeframe_votes(target_date_next)
        today_d_counts = Counter(today_d_votes)
        today_i_counts = Counter(today_i_votes)
        
        # Group today's digits by frequency
        live_d_groups = {6: [], 5: [], 4: [], 3: [], 2: [], 1: [], 0: []}
        live_i_groups = {6: [], 5: [], 4: [], 3: [], 2: [], 1: [], 0: []}
        
        for digit in range(10):
            d_cnt = today_d_counts.get(digit, 0)
            if d_cnt >= 6: live_d_groups[6].append(digit)
            elif d_cnt in live_d_groups: live_d_groups[d_cnt].append(digit)
            
            i_cnt = today_i_counts.get(digit, 0)
            if i_cnt >= 6: live_i_groups[6].append(digit)
            elif i_cnt in live_i_groups: live_i_groups[i_cnt].append(digit)

        # --- 6. DISPLAY RESULTS (Clean and Direct) ---
        st.markdown("---")
        st.header(f"📈 History Check Result (Pichle 30 Din)")
        
        col_A, col_B = st.columns(2)
        with col_A:
            st.warning(f"**🅰️ Andar (Dahai) ka Best Group:** [{best_dahai_freq} Baar Wale Digits]")
            st.write(f"*(Pichle 30 din mein sabse zyada Andar ke harf {best_dahai_freq} Baar common aaye huye dabbe se pass huye hain)*")
        with col_B:
            st.success(f"**🅱️ Bahar (Ikai) ka Best Group:** [{best_ikai_freq} Baar Wale Digits]")
            st.write(f"*(Pichle 30 din mein sabse zyada Bahar ke harf {best_ikai_freq} Baar common aaye huye dabbe se pass huye hain)*")

        st.markdown("---")
        st.header(f"🎯 Pure Digits for {target_date_next.strftime('%d %B %Y')}")
        
        c1, c2 = st.columns(2)
        
        def display_digit_group(col, title, groups, best_freq, is_dahai):
            with col:
                st.subheader(title)
                for freq in [6, 5, 4, 3, 2, 1]:
                    nums = groups[freq]
                    if not nums: continue
                    
                    if freq == best_freq:
                        st.success(f"**🔥 {freq} Baar Aaye:** {', '.join(map(str, sorted(nums)))}  **(🏆 RECOMMENDED)**")
                    else:
                        st.info(f"**{freq} Baar Aaye:** {', '.join(map(str, sorted(nums)))}")

        display_digit_group(c1, "🅰️ DAHAI (Andar) Groups", live_d_groups, best_dahai_freq, True)
        display_digit_group(c2, "🅱️ IKAI (Bahar) Groups", live_i_groups, best_ikai_freq, False)

        # --- 7. FINAL NUMBERS COMBINATION ---
        st.markdown("---")
        st.subheader("🔗 100% Calculated Target Numbers (Based on Best History)")
        st.write(f"Yahan Andar ke **{best_dahai_freq}-Baar** wale digits ko Bahar ke **{best_ikai_freq}-Baar** wale digits ke sath joda gaya hai:")
        
        best_dahai_digits = live_d_groups[best_dahai_freq]
        best_ikai_digits = live_i_groups[best_ikai_freq]
        
        if not best_dahai_digits or not best_ikai_digits:
            st.error("Aaj ke data mein History se match karne wale perfect digits nahi ban pa rahe. Thoda risk hai.")
        else:
            final_numbers = []
            for d in best_dahai_digits:
                for i in best_ikai_digits:
                    num = (d * 10) + i
                    final_numbers.append(num)
                    
            final_numbers.sort()
            pure_nums = [f"{n:02d}" for n in final_numbers]
            st.success(", ".join(pure_nums))
            st.write(f"**Total Confirm Numbers Generated:** {len(pure_nums)}")

    except Exception as e:
        st.error(f"Error processing data: {e}")
else:
    st.info("👈 Data upload karein aur Target Shift select karein.")
