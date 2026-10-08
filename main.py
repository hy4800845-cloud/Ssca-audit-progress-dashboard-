import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, date, timedelta
import numpy as np

# Page config
st.set_page_config(page_title="SSCA Audit Tracker - 15 Projects", layout="wide")

# Title
st.title("🛡️ SSCA Audit Progress Dashboard")
st.markdown("**Tracking Awarding & Execution Review for 15 Projects**")

# Sidebar for filters
st.sidebar.header("🔍 Filters")
project_filter = st.sidebar.multiselect("Projects", options=[], default=[])
phase_filter = st.sidebar.multiselect("Phase", options=["Award", "Execution"], default=["Award", "Execution"])
status_filter = st.sidebar.multiselect("Status", options=[], default=[])
risk_filter = st.sidebar.slider("Risk Rating", 1, 5, (1,5))

# ✅ FIXED: Sample data - ALL arrays now exactly 15 elements
if 'df_projects' not in st.session_state:
    project_data = {
        'Project_ID': [f'P{i}' for i in range(1,16)],
        'Project_Name': [
            'Sahibabad Viaduct Civil Works', 'Ghaziabad Station Finishing', 'New Ashok Nagar Station', 
            'Mayur Vihar P1 Viaduct', 'Sarai Kale Khan Depot', 'Signalling Systems Package-1', 
            'OHE Electrification Pkg-1', 'SCADA & Telecom Systems', 'Ticketing & AFC System', 
            'Rolling Stock Lot-1 (25 trains)', 'Rolling Stock Lot-2', 'Jungpura TOD Development', 
            'Serviced Apartments Jungpura', 'Commercial Complex Jungpura', 'OCC Jungpura'
        ],
        'Package_Type': ['Civil', 'Civil', 'Civil', 'Civil', 'Civil', 'Systems', 'Systems', 
                        'Systems', 'Systems', 'Rolling Stock', 'Rolling Stock', 'TOD', 'TOD', 'TOD', 'TOD'],
        'Phase': ['Award', 'Execution', 'Award', 'Execution', 'Award', 'Award', 'Execution', 
                 'Award', 'Execution', 'Award', 'Execution', 'Award', 'Execution', 'Award', 'Execution'],
        'Auditor': ['Auditor A', 'Auditor B', 'Auditor A', 'Auditor C', 'Auditor B', 
                   'Auditor A', 'Auditor C', 'Auditor B', 'Auditor A', 'Auditor C', 
                   'Auditor B', 'Auditor A', 'Auditor C', 'Auditor B', 'Auditor A'],
        'Start_Date': pd.to_datetime(['2026-01-01', '2026-01-05', '2026-01-03', '2026-01-07', 
                                     '2026-01-02', '2026-01-04', '2026-01-06', '2026-01-08', 
                                     '2026-01-10', '2026-01-12', '2026-01-09', '2026-01-11', 
                                     '2026-01-13', '2026-01-14', '2026-01-15']),
        'Planned_End': pd.to_datetime(['2026-02-15', '2026-02-20', '2026-02-18', '2026-02-25', 
                                     '2026-02-12', '2026-02-22', '2026-02-28', '2026-02-19', 
                                     '2026-02-26', '2026-03-01', '2026-02-24', '2026-02-21', 
                                     '2026-03-05', '2026-02-27', '2026-03-02']),
        'Actual_End': pd.NaT,
        'Pct_Complete': [60, 25, 80, 10, 90, 45, 70, 30, 55, 85, 20, 65, 40, 75, 50],
        'Status': ['In Progress', 'Not Started', 'Completed', 'Not Started', 'Completed', 
                  'In Progress', 'Completed', 'Not Started', 'In Progress', 'Completed', 
                  'Not Started', 'In Progress', 'Not Started', 'Completed', 'In Progress'],
        'Risk_Rating': [3, 4, 2, 5, 1, 3, 2, 4, 3, 1, 5, 2, 4, 1, 3],
        'Key_Issues': ['Bid eval pending', 'Records incomplete', 'TEC approved', 'CPPP access delayed', 
                      'All records received', 'LOA pending', 'Site inspection done', 'Variation claims', 
                      'Payment certification', 'FAT completed', 'SAT pending', 'DDA approval pending', 
                      'EOI shortlisting', 'TOD scheme approval', 'OCC design review'],
        'Next_Milestone': ['TEC Report', 'Site visit', 'LOA issue', 'Records collection', 
                          'Contract signing', 'Board approval', 'Payment certification', 'Bid opening', 
                          'Quality audit', 'Commissioning', 'Delivery schedule', 'RFP preparation', 
                          'DPR submission', 'Financial closure', 'Board presentation']
    }
    st.session_state.df_projects = pd.DataFrame(project_data)

# File upload for real data
uploaded_file = st.sidebar.file_uploader("📁 Upload Excel/CSV", type=['xlsx','csv'])
if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith('.xlsx'):
            st.session_state.df_projects = pd.read_excel(uploaded_file)
        else:
            st.session_state.df_projects = pd.read_csv(uploaded_file)
        st.sidebar.success("✅ Data loaded successfully!")
    except Exception as e:
        st.sidebar.error(f"❌ Error loading file: {str(e)}")

df = st.session_state.df_projects.copy()

# Apply filters
if project_filter:
    df = df[df['Project_ID'].isin(project_filter)]
if phase_filter:
    df = df[df['Phase'].isin(phase_filter)]
if status_filter:
    df = df[df['Status'].isin(status_filter)]
df = df[(df['Risk_Rating'] >= risk_filter[0]) & (df['Risk_Rating'] <= risk_filter[1])]

# Update filter options based on current data
if 'Project_ID' in df.columns:
    st.sidebar.multiselect("Projects", options=df['Project_ID'].unique().tolist(), 
                          key="proj_filter", default=df['Project_ID'].unique().tolist()[:3])
if 'Status' in df.columns:
    st.sidebar.multiselect("Status", options=df['Status'].unique().tolist(), 
                          key="status_filter", default=df['Status'].unique().tolist())

# KPI Cards (Row 1)
col1, col2, col3, col4, col5, col6 = st.columns(6)
total_projects = len(df)
with col1:
    st.metric("📊 Total Projects", total_projects)
with col2:
    completed = len(df[df['Status']=='Completed'])
    st.metric("✅ Completed", completed, delta=f"{completed/total_projects*100:.0f}%" if total_projects > 0 else 0)
with col3:
    progress = df['Pct_Complete'].mean()
    st.metric("📈 Avg Progress", f"{progress:.0f}%", delta_color="normal")
with col4:
    high_risk = len(df[df['Risk_Rating']>=4])
    st.metric("🔴 High Risk", high_risk)
with col5:
    overdue = len(df[df['Planned_End'] < pd.Timestamp.now()])
    st.metric("⏰ Overdue", overdue)
with col6:
    overall_progress = (df['Pct_Complete'].sum() / len(df)) if len(df) > 0 else 0
    st.metric("🎯 Overall %", f"{overall_progress:.0f}%")

# Charts Row 1
col1, col2 = st.columns(2)
with col1:
    st.subheader("📊 Progress by Phase")
    phase_progress = df.groupby('Phase')['Pct_Complete'].mean().reset_index()
    fig_pie = px.pie(phase_progress, values='Pct_Complete', names='Phase', 
                     color_discrete_sequence=['#FF6B6B','#4ECDC4', '#45B7D1'])
    st.plotly_chart(fig_pie, use_container_width=True)

with col2:
    st.subheader("🎯 Risk Distribution")
    fig_scatter = px.scatter(df, x='Project_ID', y='Pct_Complete', 
                            size='Risk_Rating', color='Risk_Rating', size_max=30,
                            hover_data=['Status','Key_Issues','Next_Milestone'],
                            color_continuous_scale='RdYlGn_r')
    st.plotly_chart(fig_scatter, use_container_width=True)

# Charts Row 2
col1, col2 = st.columns(2)
with col1:
    st.subheader("📅 Project Timeline (Gantt)")
    fig_gantt = px.timeline(df, x_start='Start_Date', x_end='Planned_End',
                           y='Project_Name', color='Status',
                           hover_data=['Pct_Complete','Risk_Rating','Auditor'])
    fig_gantt.update_yaxes(autorange="reversed")
    st.plotly_chart(fig_gantt, use_container_width=True)

with col2:
    st.subheader("📈 Status Distribution")
    status_counts = df['Status'].value_counts()
    fig_bar = px.bar(x=status_counts.index, y=status_counts.values, 
                    color=status_counts.index,
                    color_discrete_map={
                        'Completed': '#00FF00', 'In Progress': '#FFA500', 
                        'Not Started': '#FF0000'
                    })
    st.plotly_chart(fig_bar, use_container_width=True)

# Data Tables
col1, col2 = st.columns([2,1])
with col1:
    st.subheader("📋 All Projects")
    st.dataframe(df[['Project_ID','Project_Name','Phase','Status','Pct_Complete','Risk_Rating','Next_Milestone']].style
                .format({'Pct_Complete': '{:.0f}%'}), use_container_width=True)

with col2:
    st.subheader("⚠️ High Risk Projects")
    high_risk_df = df[df['Risk_Rating']>=4][['Project_ID','Status','Key_Issues','Auditor']]
    st.dataframe(high_risk_df, use_container_width=True)

# Update Data Section
st.header("✏️ Quick Update")
with st.expander("Update Project Status"):
    project_to_update = st.selectbox("Select Project", df['Project_ID'])
    new_status = st.selectbox("New Status", ['Not Started', 'In Progress', 'Completed'])
    new_pct = st.slider("Progress %", 0, 100, 50)
    
    if st.button("Update"):
        idx = st.session_state.df_projects[st.session_state.df_projects['Project_ID'] == project_to_update].index[0]
        st.session_state.df_projects.loc[idx, 'Status'] = new_status
        st.session_state.df_projects.loc[idx, 'Pct_Complete'] = new_pct
        st.success(f"✅ Updated {project_to_update}")
        st.rerun()

# Export
@st.cache_data
def convert_df(df):
    return df.to_csv(index=False).encode('utf-8')

csv = convert_df(df)
st.download_button("📥 Download CSV Report", csv, "ssca_audit_report.csv", "text/csv")

# Footer
st.markdown("---")
st.caption(f"🔄 Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M IST')} | SSCA Audit Tracker v2.0")
