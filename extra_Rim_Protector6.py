import streamlit as st
import pandas as pd
import numpy as np
from scipy.optimize import linprog

titles = ["PG", "SG", "G", "SF", "PF", "F", "C", "PF/C", "FLX1", "FLX2", "FLX3", "FLX4", "FLX5"]

st.markdown(
    """
    <style>
    .main {
        background-color: #6f4e37;  /* Αλλαγή φόντου σε καφέ */
        font-family: Arial, sans-serif;
    }
    .title {
        color: #d46f4d;
        font-size: 3em;
        text-align: center;
        margin-bottom: 0.5em;
    }
    .header {
        color: #ffffff;
        font-size: 2em;
        text-align: center;
        margin-bottom: 1em;
    }
    .section {
        background-color: #ffffff;
        padding: 2em;
        border-radius: 10px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        margin-bottom: 1em;
        color: #000000;
    }
    .section-title {
        color: #d46f4d;
        font-size: 1.5em;
        margin-bottom: 0.5em;
    }
    .section-content {
        font-size: 1em;
        color: #444444;
    }
    .sidebar .sidebar-content {
        background-color: #ffffff;
        padding: 1em;
        border-radius: 10px;
    }
    .punt-category {
        color: #ff0000;
    }
    .comparison-box {
        background-color: #add8e6;
        padding: 1em;
        border-radius: 10px;
        margin-bottom: 1em;
    }
    .progress-bar {
        background-color: #ddd;
        border-radius: 13px;
        padding: 3px;
        margin: 0.5em 0;
        width: 100%;
    }
    .progress-bar-fill {
        background-color: #4CAF50;
        height: 12px;
        border-radius: 10px;
        width: 0;
        transition: width 0.4s ease;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown('<div class="title">RimProtector</div>', unsafe_allow_html=True)
st.image("C:\\Users\\hlio4\\Desktop\\Python\\ergasia\\image-Mar-28-2024-06-38-59-7211-PM.jpg")
st.markdown('<div class="header">Ένα site για το Fantasy NBA</div>', unsafe_allow_html=True)

st.markdown(
    '<div class="section"><div class="section-title">Περιγραφή</div><div class="section-content">Μπορείτε να δηλώσετε όσους παίκτες θέλετε και το salary cap της λίγκας, Το σύστημα θα σας προτείνει τους παίκτες που θα συμπλήρωναν κατάλληλα την ομάδα σας για να κερδίσετε τη λίγκα στην οποία παίζετε.</div></div>',
    unsafe_allow_html=True
)

st.markdown('<div class="section"><div class="section-title">Εισάγετε το Salary Cap</div>', unsafe_allow_html=True)
salary_cap_input = st.number_input("Salary Cap", min_value=0, value=185000000)
st.markdown('</div>', unsafe_allow_html=True)

if 'selected_players' not in st.session_state:
    st.session_state.selected_players = {title: {"name": "Κενή θέση", "salary": 0, "performance_index": 0} for title in titles}

selected_players = st.session_state.selected_players

file_path = "C:\\Users\\hlio4\\Desktop\\Combined_Players_Data33.xlsx"
df = pd.read_excel(file_path)

df = df[df['Team'] != '(N/A)']
df['FG%'] = df['FG%'] * 100
df['FT%'] = df['FT%'] * 100
df['2024/25'] = df['2024/25'].replace('[\€,]', '', regex=True).astype(float)
df = df[df['2024/25'] >= 1000000]
df['Positions'] = df['Position'].str.split('/')
df['A/TO'] = df['A/TO'].apply(lambda x: 0 if x > 10 else x)

performance_columns = ['FG%', 'FT%', '3PTM', 'PTS', 'OREB', 'DREB', 'AST', 'ST', 'BLK', 'TO', 'A/TO']
for column in performance_columns:
    df[column + '_z'] = (df[column] - df[column].mean()) / df[column].std()

players = df["Player"].tolist()

st.markdown('<div class="section"><div class="section-title">Επιλογή Παίκτων</div>', unsafe_allow_html=True)
selected_players_list = []
for title in titles:
    available_players = [player for player in players if player not in selected_players_list]
    selected_player = st.selectbox(f'Επίλεξε παίκτη για θέση {title}', options=["Κενή θέση"] + available_players)
    if selected_player != "Κενή θέση":
        player_data = df[df["Player"] == selected_player].iloc[0]
        selected_players[title] = {
            "name": selected_player,
            "salary": player_data['2024/25'],
            "performance_index": player_data[[col + '_z' for col in performance_columns]].sum()
        }
        selected_players_list.append(selected_player)
    else:
        selected_players[title] = {"name": "Κενή θέση", "salary": 0, "performance_index": 0}
st.markdown('</div>', unsafe_allow_html=True)

st.session_state.selected_players = selected_players

st.markdown('<div class="section"><div class="section-title">Επιλογή punt categories</div>', unsafe_allow_html=True)
punt_option = st.checkbox("Επιλογή punt categories")

if punt_option:
    if 'punt_categories' not in st.session_state:
        st.session_state.punt_categories = []

    punt_categories = []
    for category in performance_columns:
        if st.checkbox(f"Αγνόηση {category}", key=category):
            punt_categories.append(category)
    st.session_state.punt_categories = punt_categories
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="section"><div class="section-title">Αποκλεισμός Παίκτων</div>', unsafe_allow_html=True)
if 'excluded_players' not in st.session_state:
    st.session_state.excluded_players = []

excluded_players = st.multiselect("Επιλέξτε παίκτες για αποκλεισμό", options=players)
st.session_state.excluded_players = excluded_players
st.markdown('</div>', unsafe_allow_html=True)

if 'submit_count' not in st.session_state:
    st.session_state.submit_count = 0

if st.button("Υποβολή και Προτάσεις"):
    st.session_state.submit_count += 1
    st.write(f"Το κουμπί υποβολής έχει πατηθεί {st.session_state.submit_count} φορές.")

    punt_categories = st.session_state.get('punt_categories', [])
    excluded_players = st.session_state.get('excluded_players', [])

    active_performance_columns = [col for col in performance_columns if col not in punt_categories]
    df['Performance_Index'] = df[[col + '_z' for col in active_performance_columns]].sum(axis=1)

    fixed_players = {k: v for k, v in selected_players.items() if v["name"] != "Κενή θέση"}
    fixed_salaries = sum(player["salary"] for player in fixed_players.values())

    if fixed_salaries > salary_cap_input:
        st.error("Οι μισθοί των επιλεγμένων παικτών υπερβαίνουν το salary cap. Προσοχή!!!")
        st.image("C:\\Users\\hlio4\\Desktop\\Python\\ergasia\\360_F_358908973_k9y31m50zOnbIMOZYEEyNLBPbRanQig1.jpg")
    else:
        df = df[~df["Player"].isin(player["name"] for player in fixed_players.values())]
        df = df[~df["Player"].isin(excluded_players)]

        salary_cap = salary_cap_input - fixed_salaries
        c = -df['Performance_Index'].values
        A = [df['2024/25'].values]
        b = [salary_cap]

        position_constraints = {
            "PG": ["PG"],
            "SG": ["SG"],
            "G": ["G"],
            "SF": ["SF"],
            "PF": ["PF"],
            "F": ["F"],
            "C": ["C"],
            "PF/C": ["PF/C", "C", "PF"],
            "FLX1": titles,
            "FLX2": titles,
            "FLX3": titles,
            "FLX4": titles,
            "FLX5": titles
        }

        for position in titles:
            if position in fixed_players:
                continue
            A.append(df['Positions'].apply(lambda x: any(
                pos in position_constraints[position] for pos in (x if isinstance(x, list) else []))).astype(
                int).values)
            b.append(1)

        A.append(np.ones(len(df)))
        b.append(13 - len(fixed_players))

        A = np.vstack(A)
        x_bounds = [(0, 1) for _ in range(len(df))]

        result = linprog(c, A_ub=A, b_ub=b, bounds=x_bounds, method='highs')

        if result.success:
            selected_indices = result.x.round().astype(bool)
            suggested_players = df[selected_indices]
        else:
            suggested_players = pd.DataFrame()

        st.markdown(
            '<div class="section"><div class="section-title">Επιλεγμένοι Παίκτες</div><div class="section-content">',
            unsafe_allow_html=True)
        selected_players_df = pd.DataFrame([(k, v["name"], v["salary"], v["performance_index"]) for k, v in selected_players.items() if v["name"] != "Κενή θέση"],
                                           columns=['Position', 'Player', '2024/25', 'Performance_Index'])
        selected_players_df['Performance_Index'] = selected_players_df['Performance_Index'].round(3)

        st.write(selected_players_df[['Position', 'Player', '2024/25', 'Performance_Index']])
        st.markdown('</div></div>', unsafe_allow_html=True)

        st.markdown(
            '<div class="section"><div class="section-title">Προτεινόμενοι Παίκτες για τις υπόλοιπες θέσεις</div><div class="section-content">',
            unsafe_allow_html=True)
        st.write(suggested_players[["Player", "Position", "2024/25", "Performance_Index"]])
        st.markdown('</div></div>', unsafe_allow_html=True)

        output_file_selected = r'C:\Users\hlio4\Desktop\selected_players.xlsx'
        selected_players_df.to_excel(output_file_selected, index=False)

        output_file_suggested = r'C:\Users\hlio4\Desktop\suggested_players.xlsx'
        suggested_players.to_excel(output_file_suggested, index=False)

        combined_df = pd.concat([selected_players_df, suggested_players])
        output_file_combined = r'C:\Users\hlio4\Desktop\Champion.xlsx'
        combined_df.to_excel(output_file_combined, index=False)

        st.write(f"Οι επιλεγμένοι παίκτες αποθηκεύτηκαν στο αρχείο: {output_file_selected}")
        st.write(f"Οι προτεινόμενοι παίκτες αποθηκεύτηκαν στο αρχείο: {output_file_suggested}")
        st.write(f"Το συνολικό ρόστερ αποθηκεύτηκε στο αρχείο: {output_file_combined}")

        st.subheader("Συνολικό Ρόστερ")
        st.write(combined_df[['Position', 'Player', '2024/25', 'Performance_Index']])

        c = -df['Performance_Index'].values
        A = [df['2024/25'].values]
        b = [salary_cap_input]

        for position in titles:
            A.append(df['Positions'].apply(lambda x: any(
                pos in position_constraints[position] for pos in (x if isinstance(x, list) else []))).astype(
                int).values)
            b.append(1)

        A.append(np.ones(len(df)))
        b.append(13)

        A = np.vstack(A)
        x_bounds = [(0, 1) for _ in range(len(df))]

        result = linprog(c, A_ub=A, b_ub=b, bounds=x_bounds, method='highs')

        if result.success:
            best_team_indices = result.x.round().astype(bool)
            best_team = df[best_team_indices]
        else:
            best_team = pd.DataFrame()

        st.subheader("Προτεινόμενη Ομάδα Καλύτερων Παικτών")
        st.write(best_team[['Player', 'Position', '2024/25', 'Performance_Index']])

        user_team_performance = combined_df['Performance_Index'].sum()
        best_team_performance = best_team['Performance_Index'].sum()

        st.subheader("Σύγκριση Ομάδων")
        st.write(f"Συνολικός Performance Index της ομάδας σας: {user_team_performance}")
        st.write(f"Συνολικός Performance Index της προτεινόμενης ομάδας: {best_team_performance}")

        comparison_ratio = user_team_performance / best_team_performance if best_team_performance > 0 else 0

        st.markdown('<div class="progress-bar"><div class="progress-bar-fill" style="width: {}%;"></div></div>'.format(comparison_ratio * 100), unsafe_allow_html=True)

        if user_team_performance >= best_team_performance:
            st.success(
                "Η ομάδα σας είναι εξαιρετική! Συγκρίνεται θετικά με την προτεινόμενη ομάδα των καλύτερων παικτών.")
        elif user_team_performance < best_team_performance / 2:
            st.error(
                "Ο δείκτης επιδόσεων της ομάδας σας είναι κάτω από το μισό της προτεινόμενης ομάδας. Καλύτερα να κάνετε rebuild.")
        else:
            st.warning(
                "Η ομάδα σας είναι καλή, αλλά υπάρχει περιθώριο βελτίωσης σε σχέση με την προτεινόμενη ομάδα των καλύτερων παικτών.")
