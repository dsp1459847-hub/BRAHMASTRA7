import streamlit as st
import pandas as pd
import numpy as np
from datetime import timedelta
from collections import Counter

st.set_page_config(page_title="MAYA AI - TF Digit Engine", layout="wide")

st.title("MAYA AI 🧮: Timeframe-Wise Ikai & Dahai Engine")
st.markdown("Yeh AI har timeframe mein Dahai aur Ikai ko alag-alag test karta hai. Ab aap khud select kar sakte hain ki aapko kitne digits chahiye!")

# --- 1. Direct Selection Interface ---
st.sidebar.header("📁 Data Settings")
uploaded_file = st.sidebar.file_uploader("Upload CSV/Excel", type=['csv', 'xlsx'])
shift_names = ["DS", "FD", "GD", "GL", "DB", "SG", "ZA"]
target_shift_name = st.sidebar.selectbox("🎯 Target Shift", shift_names)
selected_end_date = st.sidebar.date_input("Calculation Date")
max_limit = st.sidebar.slider("Max Repeat Limit (Digits)", 2, 5, 4)

# NAYA UPDATE: Andar aur Bahar ke digit select karne ke buttons
st.sidebar.markdown("---")
st.sidebar.header("🎛️ Digits Selection (Andar / Bahar)")
dahai_count = st.sidebar.radio("🅰️ Andar (Dahai) ke kitne digit chahiye?", [2, 3, 4, 5, 6], index=1, horizontal=True)
ikai_count = st.sidebar.radio("🅱️ Bahar (Ikai) ke kitne digit chahiye?", [2, 3, 4, 5, 6], index=1, horizontal=True)

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
        curr_weekday = target_date_next.dayofweek

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

        def get_top_digits(past_data, count):
            if len(past_data) < 2: return []
            e, s = run_digit_elimination(past_data, max_limit)
            safe = sorted([n for n in range(10) if n not in e], key=lambda x: s[x], reverse=True)
            # User ke select kiye gaye ginti (count) ke hisaab se digit bhejna
            return safe[:count] if safe else []

        # --- 4. CALCULATE ACROSS ALL TIMEFRAMES ---
        with st.spinner("Sabhi timeframes mein Dahai aur Ikai check ho rahe hain..."):
            past_df = filtered_df[filtered_df['DATE'] < target_date_next]
            main_list = past_df[target_shift_name].tolist()
            main_valid = [int(x) for x in main_list if pd.notna(x)]
            
            dahai_list = [x // 10 for x in main_valid]
            ikai_list = [x % 10 for x in main_valid]

            war_df = past_df[past_df['DATE'].dt.dayofweek == curr_weekday]
            war_valid = [int(x) for x in war_df[target_shift_name].tolist() if pd.notna(x)]
            war_dahai = [x // 10 for x in war_valid]
            war_ikai = [x % 10 for x in war_valid]

            # Results Dictionary
            tf_results = {
                "3-Day Trend": {"Dahai": get_top_digits(dahai_list[-3:], dahai_count), "Ikai": get_top_digits(ikai_list[-3:], ikai_count)},
                "5-Day Trend": {"Dahai": get_top_digits(dahai_list[-5:], dahai_count), "Ikai": get_top_digits(ikai_list[-5:], ikai_count)},
                "10-Day Trend": {"Dahai": get_top_digits(dahai_list[-10:], dahai_count), "Ikai": get_top_digits(ikai_list[-10:], ikai_count)},
                "15-Day Trend": {"Dahai": get_top_digits(dahai_list[-15:], dahai_count), "Ikai": get_top_digits(ikai_list[-15:], ikai_count)},
                "30-Day Trend": {"Dahai": get_top_digits(dahai_list[-30:], dahai_count), "Ikai": get_top_digits(ikai_list[-30:], ikai_count)},
                "War-Wise (Din)": {"Dahai": get_top_digits(war_dahai[-15:], dahai_count), "Ikai": get_top_digits(war_ikai[-15:], ikai_count)}
            }

        # --- 5. INDIVIDUAL TIMEFRAME DISPLAY ---
        st.markdown("---")
        st.subheader(f"📊 Timeframe Breakdown for {target_date_next.strftime('%d %B %Y')}")
        
        c1, c2, c3 = st.columns(3)
        c4, c5, c6 = st.columns(3)
        cols = [c1, c2, c3, c4, c5, c6]
        
        all_dahai_votes = []
        all_ikai_votes = []

        for idx, (tf_name, data) in enumerate(tf_results.items()):
            d_str = ", ".join([str(x) for x in data["Dahai"]]) if data["Dahai"] else "N/A"
            i_str = ", ".join([str(x) for x in data["Ikai"]]) if data["Ikai"] else "N/A"
            
            with cols[idx]:
                st.info(f"**{tf_name}**\n\n🅰️ Andar: **{d_str}**\n\n🅱️ Bahar: **{i_str}**")
            
            all_dahai_votes.extend(data["Dahai"])
            all_ikai_votes.extend(data["Ikai"])

        # --- 6. VOTING & COMBINATION ---
        dahai_counts = Counter(all_dahai_votes)
        ikai_counts = Counter(all_ikai_votes)

        # Sirf utne hi top digits nikalna jitna user ne manga hai
        top_dahai = sorted(dahai_counts.items(), key=lambda x: x[1], reverse=True)[:dahai_count]
        top_ikai = sorted(ikai_counts.items(), key=lambda x: x[1], reverse=True)[:ikai_count]

        st.markdown("---")
        st.header("🏆 Final Master Voting & Numbers")
        
        col_A, col_B = st.columns(2)
        with col_A:
            st.warning(f"### 🅰️ Final DAHAI (Top {dahai_count})")
            for digit, count in top_dahai:
                st.write(f"**Digit {digit}** ({count}/6 Timeframes ne support kiya)")
        
        with col_B:
            st.success(f"### 🅱️ Final IKAI (Top {ikai_count})")
            for digit, count in top_ikai:
                st.write(f"**Digit {digit}** ({count}/6 Timeframes ne support kiya)")

        # Generate Final Numbers
        st.markdown("---")
        st.subheader("🔗 100% Calculated Target Numbers")
        
        final_numbers = []
        for d, d_count in top_dahai:
            for i, i_count in top_ikai:
                num = (d * 10) + i
                total_power = d_count + i_count
                final_numbers.append((num, total_power))
                
        # Sort by total power
        final_numbers = sorted(final_numbers, key=lambda x: x[1], reverse=True)
        
        # Displaying numbers in a clean line
        pure_nums = [f"{n:02d}" for n, power in final_numbers]
        st.success(", ".join(pure_nums))
        
        st.write(f"**Total Numbers Generated:** {len(pure_nums)}")

    except Exception as e:
        st.error(f"Error processing data: {e}")
else:
    st.info("👈 Data upload karein aur Date/Shift select karein.")
            
