import streamlit as st
import pandas as pd
import numpy as np
from datetime import timedelta
from collections import Counter

st.set_page_config(page_title="MAYA AI - Ikai & Dahai Engine", layout="wide")

st.title("MAYA AI 🧮: Ikai & Dahai Separation Engine")
st.markdown("Yeh system numbers ko **Dahai (Andar)** aur **Ikai (Bahar)** mein tod kar un par alag-alag patterns lagata hai, aur fir unhe jod kar Final 2-Digit Number banata hai.")

# --- 1. Simple Selection Interface ---
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

        # --- 3. DIGIT SEPARATION LOGIC (Dahai & Ikai) ---
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

        def get_best_digits(past_data):
            if len(past_data) < 2: return []
            e, s = run_digit_elimination(past_data, max_limit)
            safe = sorted([n for n in range(10) if n not in e], key=lambda x: s[x], reverse=True)
            if not safe: return []
            # Returning Top 3 Digits for the pattern
            return safe[:3]

        # --- 4. ENGINE: GET DIGIT FREQUENCIES FOR TIMEFRAMES ---
        def get_digit_frequencies(target_date):
            past_df = filtered_df[filtered_df['DATE'] < target_date]
            if len(past_df) < 30: return [], []
            
            main_list = past_df[target_shift_name].tolist()
            main_valid = [int(x) for x in main_list if pd.notna(x)]
            
            # Todna (Separating Ikai and Dahai)
            dahai_list = [x // 10 for x in main_valid]
            ikai_list = [x % 10 for x in main_valid]
            
            # Timeframes for DAHAI
            d_3d = get_best_digits(dahai_list[-3:])
            d_5d = get_best_digits(dahai_list[-5:])
            d_10d = get_best_digits(dahai_list[-10:])
            d_15d = get_best_digits(dahai_list[-15:])
            d_30d = get_best_digits(dahai_list[-30:])
            
            # War-Wise for DAHAI
            curr_weekday = target_date.dayofweek
            war_df = past_df[past_df['DATE'].dt.dayofweek == curr_weekday]
            war_valid = [int(x) for x in war_df[target_shift_name].tolist() if pd.notna(x)]
            d_war = get_best_digits([x // 10 for x in war_valid][-15:])
            
            all_dahai = d_3d + d_5d + d_10d + d_15d + d_30d + d_war

            # Timeframes for IKAI
            i_3d = get_best_digits(ikai_list[-3:])
            i_5d = get_best_digits(ikai_list[-5:])
            i_10d = get_best_digits(ikai_list[-10:])
            i_15d = get_best_digits(ikai_list[-15:])
            i_30d = get_best_digits(ikai_list[-30:])
            
            i_war = get_best_digits([x % 10 for x in war_valid][-15:])
            
            all_ikai = i_3d + i_5d + i_10d + i_15d + i_30d + i_war
            
            return all_dahai, all_ikai

        # --- 5. LIVE CALCULATION FOR TODAY ---
        with st.spinner("Dahai aur Ikai ko alag karke patterns lagaye ja rahe hain..."):
            today_dahai, today_ikai = get_digit_frequencies(target_date_next)
            
            dahai_counts = Counter(today_dahai)
            ikai_counts = Counter(today_ikai)
            
            # Top Dahai aur Top Ikai nikalna (Jo sabse zyada timeframes me common hain)
            top_dahai = sorted(dahai_counts.items(), key=lambda x: x[1], reverse=True)[:4]
            top_ikai = sorted(ikai_counts.items(), key=lambda x: x[1], reverse=True)[:4]

        # --- 6. DISPLAY RESULTS ---
        st.markdown("---")
        st.header(f"🎯 Pure Digits for {target_date_next.strftime('%d %B %Y')}")
        
        c1, c2 = st.columns(2)
        
        with c1:
            st.warning("### 🅰️ Strong DAHAI (Andar)")
            for digit, count in top_dahai:
                st.write(f"**Digit {digit}** (Matched in {count} Patterns)")
                
        with c2:
            st.success("### 🅱️ Strong IKAI (Bahar)")
            for digit, count in top_ikai:
                st.write(f"**Digit {digit}** (Matched in {count} Patterns)")

        # --- 7. THE MASTER COMBINATION (Final Numbers) ---
        st.markdown("---")
        st.subheader("🔗 Final Master Numbers (Dahai + Ikai Combinations)")
        
        final_numbers = []
        for d, d_count in top_dahai:
            for i, i_count in top_ikai:
                # Combining Tens and Units (e.g., Dahai 4, Ikai 2 = 42)
                num = (d * 10) + i
                total_power = d_count + i_count
                final_numbers.append((num, total_power))
                
        # Sort by total power (Highest overlap)
        final_numbers = sorted(final_numbers, key=lambda x: x[1], reverse=True)
        
        # Displaying Final Numbers cleanly
        st.info("Niche diye gaye numbers Dahai aur Ikai ke sabse powerful pattern intersections se banaye gaye hain:")
        
        pure_nums = [f"{n:02d}" for n, power in final_numbers]
        st.write(", ".join(pure_nums))

    except Exception as e:
        st.error(f"Error processing data: {e}")
else:
    st.info("👈 Data upload karein aur seedha Target Shift select karein.")
          
