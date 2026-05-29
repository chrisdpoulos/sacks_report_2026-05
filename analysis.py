# Streamlit app to report on Sacks' donations
# Created 5/26

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
import plotly.express as px
import io

# Import data

@st.cache_data
def load_data():
    df = pd.read_csv("receipts.csv")
    return df

# Streamlit app title
def main():    

    # Set page configuration

    st.set_page_config(
        page_title="Analysis of Sacks' Donations", 
        layout="centered",
        page_icon="💰",
        initial_sidebar_state="expanded"
    )

    # Load data
    df = load_data()
    if df.empty:
        st.error("No data found. Please check the CSV file.")
        return

    # change date from yyyy-mm-dd 00:00:00 to yyyy-mm-dd
    df["received_date"] = pd.to_datetime(df["received_date"]).dt.date


    df['year'] = pd.to_datetime(df['received_date']).dt.year
    df['month'] = pd.to_datetime(df['received_date']).dt.month
    
    #aggregate by year, month, and committee name
    df = df.groupby(['year', 'month', 'committee_name'])['amount'].sum().reset_index()

    # create a new received_date with year-month

    df['received_date'] = df['year'].astype(str) + '-' + df['month'].astype(str).str.zfill(2)

    df_agg = df.groupby('received_date')['amount'].sum().reset_index()
    df_freq = df.groupby('received_date')['amount'].count().reset_index()
    df_freq = df_freq.rename(columns={"amount": "frequency"})
    df_agg_committee = df.groupby(['committee_name'])['amount'].sum().reset_index()
    df_agg_committee = df_agg_committee.sort_values(by="amount", ascending=False)

    df["percentage"] = df["amount"] / df["amount"].sum()
    # Reverse cumulative percentage.
    df = df.sort_values(by="received_date", ascending=False)
    df["cumulative_percentage"] = df["percentage"].cumsum()

    # create column for periods: <2014, 2014-2020, >2020

    df['periods'] = ["<2014" if x < 2014 else "2014-2020" if x < 2021 else ">2020" for x in df['year']]

    df_periods = df.copy()

    # Report

    total_donations = df["amount"].sum()
    number_of_donations = len(df)
    first_donation_date = df["received_date"].min()
    last_donation_date = df["received_date"].max()
    

    # Figures

    fig1 = px.line(df_agg, x='received_date', y='amount')
    fig2 = px.line(df_freq, x='received_date', y='frequency')

    st.markdown(f"""<h1>Analysis of Sacks' Donations</h1>
<p><b>Author and researcher:</b> Chris Poulos (Public Finance Analyst, CTU).
<br>
<b>Date</b>: 2026-05-07.
<br>
<b>Data source</b>: Illinois Sunshine Database, search "Michael Sacks" download zip file, open receipts.csv.
<br>
<b>Objective</b>: Identify donation patterns for Michael Sacks.
<br><br>
<h2>Total Donations</h2>
<p>Michael Sacks has made a total of ${total_donations:,.2f} in donations from {number_of_donations} donations between {first_donation_date} and {last_donation_date}.
<br>
<p>Both the frequency and amount of Sacks' donations have increased in the last 16 years.
<br>
<br>
<b>Over 90% of these donations were spent in the last 16 years–coinciding with the rise of left-wing and progressive union candidates in local elections.</b>
<br>
<p>Figures 1 and 2 demonstrate this trend. Figure 1 shows the total amount of donations over time and Figure 2 shows the frequency. Sacks' donations increased beginning in 2015, and the peaks and troughs coincide the municipal election cycle. 2015 was the first election cycle saw a number of insurgent candidates for local elections (rank-and-file union candidates and socialist candidates).
""", unsafe_allow_html=True)
    st.markdown(f"""<h3>Figure 1. Total Amount of Donations Over Time</h3>""", unsafe_allow_html=True)
    st.plotly_chart(fig1)
    st.markdown(f"""<h3>Figure 2. Frequency of Donations Over Time</h3>""", unsafe_allow_html=True)
    st.plotly_chart(fig2)
    #Sum amount if period is >2020 
    df_periods_2020 = df_periods[df_periods["periods"] == ">2020"]
    total_donations_2020 = df_periods_2020["amount"].sum()
    # Make this a more readable number by dividing by 1 million and rounding to 1 decimal places
    total_donations_2020 = round(total_donations_2020 / 1000000, 1)

    st.markdown(f"""
<h2>Composition of Donations</h2>
<p>In conjunction with the analysis of total donations, Sacks' donations to key strategic local and state elections are increasing by frequency and amount. In the most recent period, 2020 through present, nearly half of Sacks' ${total_donations_2020:,.1f} million in post 2020 donations were made to Get Stuff Done PAC (business friendly PAC amed at elected "pragmatic" "Obama Democrats" to Chicago's City Council in the 2023 election (<a href="https://www.chicagotribune.com/2024/07/24/new-nonprofit-and-pac-aligned-with-business-community-launching-in-time-for-school-board-elections/">Quig, 2024</a>)) (21% of post 2020 donations), Citizen for Giannoulias (a potential Mayoral candidate in 2027) received 16% of post 2020 donations, and 10% when to the Common Ground Collective, which ran ads to defeat the Corporate Head Tax and lower support for CTU, Mayor Brandon Johnson, and a number of progressive and socialist candidates.),
</p>
""", unsafe_allow_html=True)
    select_period = st.selectbox("Select a period to filter by:", options=df["periods"].unique())
    if select_period:
        df_periods = df_periods[df_periods["periods"] == select_period]
        df_periods = df_periods.sort_values(by="amount", ascending=False)
    st.markdown(f"""<h3>Table 1,2,3. Donations by Committee and Period (sorted by amount).</h3>""", unsafe_allow_html=True,help="Table 1 corresponds to the period <2014, Table 2 corresponds to the period 2014-2020, and Table 3 corresponds to the period >2020.")
    st.dataframe(df_periods)
    st.markdown(f"""<h3>Figure 3,4,5. Donations by Committee and Period</h3>""", unsafe_allow_html=True,help="Figure 3 corresponds to the period <2014, Figure 4 corresponds to the period 2014-2020, and Figure 5 corresponds to the period >2020.")
    fig345 = px.bar(df_periods, x='received_date', y='amount',color='committee_name')
    fig345.update_layout(showlegend=False)
    st.plotly_chart(fig345)
    st.markdown(f"""<h3>Figure 6,7,8. Distribution of Donations by Committee and Period</h3>""", unsafe_allow_html=True,help="Figure 6 corresponds to the period <2014, Figure 7 corresponds to the period 2014-2020, and Figure 8 corresponds to the period >2020.")
    df_agg_periods = df_periods.groupby('committee_name')['amount'].sum().reset_index()
    fig678 = px.pie(df_agg_periods, values='amount', names='committee_name')
    fig678.update_layout(showlegend=False)
    st.plotly_chart(fig678)
    st.markdown(f"""<h3>All Donations, 1994-2026</h3>""", unsafe_allow_html=True)
    df_formatted = df.copy()
    df_formatted = df_formatted[["received_date", "committee_name", "amount"]]
    st.dataframe(df_formatted.style.format({
        "amount": "${:,.2f}"
    }), hide_index=True)
    
if __name__ == "__main__":
    main()