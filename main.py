"""
PeopleSoft Log Analyzer - Main Streamlit Application
Comprehensive tabbed interface for log analysis with AI-powered insights.
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import io
import base64

from analyzer import LogAnalyzer
from visualizer import LogVisualizer

# Configure Streamlit page
st.set_page_config(
    page_title="PeopleSoft Log Analyzer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main > div {
        padding-top: 2rem;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #f0f2f6;
        border-radius: 10px;
        gap: 4px;
        padding-left: 12px;
        padding-right: 12px;
    }
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background-color: #1f77b4;
        color: white;
    }
    .metric-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #1f77b4;
    }
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables."""
    if 'analyzer' not in st.session_state:
        st.session_state.analyzer = LogAnalyzer()
    if 'visualizer' not in st.session_state:
        st.session_state.visualizer = LogVisualizer()
    if 'processed_data' not in st.session_state:
        st.session_state.processed_data = None
    if 'analysis_results' not in st.session_state:
        st.session_state.analysis_results = {}

def create_download_link(df, filename, file_format="csv"):
    """Create a download link for DataFrame."""
    if file_format == "csv":
        csv = df.to_csv(index=True)
        b64 = base64.b64encode(csv.encode()).decode()
        href = f'<a href="data:file/csv;base64,{b64}" download="{filename}.csv">📥 Download {filename}</a>'
    elif file_format == "excel":
        buffer = io.BytesIO()
        df.to_excel(buffer, index=True)
        b64 = base64.b64encode(buffer.getvalue()).decode()
        href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="{filename}.xlsx">📥 Download {filename}</a>'
    
    return href

def show_sidebar():
    """Display sidebar with file upload and configuration options."""
    st.sidebar.title("📊 PeopleSoft Log Analyzer")
    st.sidebar.markdown("---")
    
    # File upload section
    st.sidebar.header("📁 Upload Log File")
    uploaded_file = st.sidebar.file_uploader(
        "Choose a log file",
        type=['txt', 'log'],
        help="Upload your PeopleSoft log file for analysis"
    )
    
    if uploaded_file is not None:
        if st.sidebar.button("🔄 Process Log File", type="primary"):
            with st.spinner("Processing log file..."):
                # Read file content
                file_content = uploaded_file.read()
                
                # Process with analyzer
                processed_data = st.session_state.analyzer.process_log_file(file_content)
                st.session_state.processed_data = processed_data
                
                # Run all analyses
                with st.spinner("Running comprehensive analysis..."):
                    st.session_state.analysis_results = {
                        'summary': st.session_state.analyzer.get_analysis_summary(),
                        'user_analytics': st.session_state.analyzer.analyze_user_rankings(),
                        'boot_analysis': st.session_state.analyzer.analyze_boot_sequences(),
                        'anomaly_detection': st.session_state.analyzer.detect_anomalies_ai()
                    }
                
                st.sidebar.success(f"✅ Processed {len(processed_data)} log entries")
    
    # Analysis configuration
    st.sidebar.markdown("---")
    st.sidebar.header("⚙️ Analysis Settings")
    
    # Anomaly detection sensitivity
    anomaly_sensitivity = st.sidebar.slider(
        "Anomaly Detection Sensitivity",
        min_value=0.05,
        max_value=0.3,
        value=0.1,
        step=0.05,
        help="Lower values detect fewer, more significant anomalies"
    )
    
    # User ranking limit
    ranking_limit = st.sidebar.number_input(
        "Top Users Ranking Limit",
        min_value=5,
        max_value=50,
        value=20,
        help="Number of top users to display in rankings"
    )
    
    # Time filter
    st.sidebar.header("📅 Time Filter")
    if st.session_state.processed_data is not None and not st.session_state.processed_data.empty:
        min_date = st.session_state.processed_data['timestamp'].min().date()
        max_date = st.session_state.processed_data['timestamp'].max().date()
        
        date_range = st.sidebar.date_input(
            "Select Date Range",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date
        )
    
    return uploaded_file

def show_authentication_tab():
    """Display authentication analysis tab."""
    st.header("🔐 Authentication Analysis")
    
    if st.session_state.processed_data is None or st.session_state.processed_data.empty:
        st.info("Please upload and process a log file to see authentication analysis.")
        return
    
    df = st.session_state.processed_data
    auth_data = df[df['log_type'].isin(['auth_success', 'auth_failed'])]
    
    if auth_data.empty:
        st.warning("No authentication events found in the log data.")
        return
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    total_attempts = len(auth_data)
    successful_attempts = len(auth_data[auth_data['log_type'] == 'auth_success'])
    failed_attempts = len(auth_data[auth_data['log_type'] == 'auth_failed'])
    success_rate = (successful_attempts / total_attempts * 100) if total_attempts > 0 else 0
    
    with col1:
        st.metric("Total Attempts", total_attempts)
    with col2:
        st.metric("Successful", successful_attempts)
    with col3:
        st.metric("Failed", failed_attempts)
    with col4:
        st.metric("Success Rate", f"{success_rate:.1f}%")
    
    # Visualizations
    auth_charts = st.session_state.visualizer.create_authentication_analysis_charts(df)
    
    if 'auth_timeline' in auth_charts:
        st.plotly_chart(auth_charts['auth_timeline'], use_container_width=True)
    
    if 'success_rate_pie' in auth_charts:
        st.plotly_chart(auth_charts['success_rate_pie'], use_container_width=True)
    
    # Recent authentication events
    st.subheader("Recent Authentication Events")
    recent_auth = auth_data.head(100)[['timestamp', 'log_type', 'user_id', 'message']]
    st.dataframe(recent_auth, use_container_width=True)
    
    # Download link
    st.markdown(create_download_link(auth_data, "authentication_data"), unsafe_allow_html=True)

def show_error_analysis_tab():
    """Display error analysis tab."""
    st.header("❌ Error Analysis")
    
    if st.session_state.processed_data is None or st.session_state.processed_data.empty:
        st.info("Please upload and process a log file to see error analysis.")
        return
    
    df = st.session_state.processed_data
    error_data = df[df['log_type'] == 'error']
    
    if error_data.empty:
        st.warning("No error events found in the log data.")
        return
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    total_errors = len(error_data)
    unique_users_with_errors = error_data['user_id'].nunique()
    avg_errors_per_day = total_errors / max(1, (error_data['timestamp'].max() - error_data['timestamp'].min()).days)
    
    with col1:
        st.metric("Total Errors", total_errors)
    with col2:
        st.metric("Users Affected", unique_users_with_errors)
    with col3:
        st.metric("Avg Errors/Day", f"{avg_errors_per_day:.1f}")
    with col4:
        st.metric("Error Rate", f"{(total_errors/len(df)*100):.1f}%")
    
    # Visualizations
    error_charts = st.session_state.visualizer.create_error_analysis_charts(df)
    
    if 'error_timeline' in error_charts:
        st.plotly_chart(error_charts['error_timeline'], use_container_width=True)
    
    if 'hourly_errors' in error_charts:
        st.plotly_chart(error_charts['hourly_errors'], use_container_width=True)
    
    # Recent errors
    st.subheader("Recent Error Events")
    recent_errors = error_data.head(100)[['timestamp', 'user_id', 'message', 'raw_line']]
    st.dataframe(recent_errors, use_container_width=True)
    
    # Download link
    st.markdown(create_download_link(error_data, "error_data"), unsafe_allow_html=True)

def show_availability_tab():
    """Display system availability analysis tab."""
    st.header("🖥️ System Availability")
    
    if 'boot_analysis' not in st.session_state.analysis_results:
        st.info("Please upload and process a log file to see availability analysis.")
        return
    
    boot_analysis = st.session_state.analysis_results['boot_analysis']
    
    if not boot_analysis or boot_analysis['boot_sequences'].empty:
        st.warning("No boot sequence data found in the log.")
        return
    
    # Key metrics
    metrics = boot_analysis['availability_metrics']
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Boot Attempts", metrics.get('total_boot_attempts', 0))
    with col2:
        st.metric("Avg Boot Time", f"{metrics.get('average_boot_time_minutes', 0):.1f} min")
    with col3:
        st.metric("Total Downtime", f"{metrics.get('total_downtime_hours', 0):.1f} hours")
    with col4:
        st.metric("Domains Affected", metrics.get('domains_affected', 0))
    
    # Visualizations
    boot_charts = st.session_state.visualizer.create_boot_timeline_chart(boot_analysis)
    
    if 'boot_timeline' in boot_charts:
        st.plotly_chart(boot_charts['boot_timeline'], use_container_width=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        if 'duration_distribution' in boot_charts:
            st.plotly_chart(boot_charts['duration_distribution'], use_container_width=True)
    
    with col2:
        if 'domain_frequency' in boot_charts:
            st.plotly_chart(boot_charts['domain_frequency'], use_container_width=True)
    
    # Boot sequences table
    st.subheader("Boot Sequences")
    boot_df = boot_analysis['boot_sequences']
    st.dataframe(boot_df, use_container_width=True)
    
    # Download link
    st.markdown(create_download_link(boot_df, "boot_sequences"), unsafe_allow_html=True)

def show_user_analytics_tab():
    """Display user analytics tab."""
    st.header("👥 User Analytics")
    
    if 'user_analytics' not in st.session_state.analysis_results:
        st.info("Please upload and process a log file to see user analytics.")
        return
    
    user_analytics = st.session_state.analysis_results['user_analytics']
    
    if not user_analytics or all(df.empty for df in user_analytics.values()):
        st.warning("No user analytics data available.")
        return
    
    # User ranking visualizations
    user_charts = st.session_state.visualizer.create_user_ranking_charts(user_analytics)
    
    # Display charts in columns
    col1, col2 = st.columns(2)
    
    with col1:
        if 'success_ranking' in user_charts:
            st.plotly_chart(user_charts['success_ranking'], use_container_width=True)
    
    with col2:
        if 'failure_ranking' in user_charts:
            st.plotly_chart(user_charts['failure_ranking'], use_container_width=True)
    
    if 'error_ranking' in user_charts:
        st.plotly_chart(user_charts['error_ranking'], use_container_width=True)
    
    if 'activity_heatmap' in user_charts:
        st.plotly_chart(user_charts['activity_heatmap'], use_container_width=True)
    
    # User summary tables
    st.subheader("User Rankings")
    
    tab1, tab2, tab3, tab4 = st.tabs(["🏆 Top Success Users", "❌ Top Failure Users", "🔥 Top Error Users", "📊 User Summary"])
    
    with tab1:
        if not user_analytics['top_success_users'].empty:
            st.dataframe(user_analytics['top_success_users'], use_container_width=True)
            st.markdown(create_download_link(user_analytics['top_success_users'], "top_success_users"), unsafe_allow_html=True)
    
    with tab2:
        if not user_analytics['top_failure_users'].empty:
            st.dataframe(user_analytics['top_failure_users'], use_container_width=True)
            st.markdown(create_download_link(user_analytics['top_failure_users'], "top_failure_users"), unsafe_allow_html=True)
    
    with tab3:
        if not user_analytics['top_error_users'].empty:
            st.dataframe(user_analytics['top_error_users'], use_container_width=True)
            st.markdown(create_download_link(user_analytics['top_error_users'], "top_error_users"), unsafe_allow_html=True)
    
    with tab4:
        if not user_analytics['user_summary'].empty:
            st.dataframe(user_analytics['user_summary'], use_container_width=True)
            st.markdown(create_download_link(user_analytics['user_summary'], "user_summary"), unsafe_allow_html=True)

def show_anomaly_detection_tab():
    """Display AI-powered anomaly detection tab."""
    st.header("🤖 AI Anomaly Detection")
    
    if 'anomaly_detection' not in st.session_state.analysis_results:
        st.info("Please upload and process a log file to see anomaly detection results.")
        return
    
    anomaly_data = st.session_state.analysis_results['anomaly_detection']
    
    if not anomaly_data or anomaly_data['anomaly_scores'].empty:
        st.warning("No anomaly detection data available.")
        return
    
    # Anomaly summary metrics
    summary = anomaly_data['anomaly_summary']
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Events", summary.get('total_events', 0))
    with col2:
        st.metric("Anomalous Events", summary.get('anomalous_events', 0))
    with col3:
        st.metric("Anomaly Rate", f"{summary.get('anomaly_rate', 0):.1f}%")
    with col4:
        st.metric("High Severity", summary.get('high_severity_anomalies', 0))
    
    # Anomaly visualizations
    anomaly_charts = st.session_state.visualizer.create_anomaly_heatmap(anomaly_data)
    
    if 'anomaly_heatmap' in anomaly_charts:
        st.plotly_chart(anomaly_charts['anomaly_heatmap'], use_container_width=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        if 'score_distribution' in anomaly_charts:
            st.plotly_chart(anomaly_charts['score_distribution'], use_container_width=True)
    
    with col2:
        if 'severity_breakdown' in anomaly_charts:
            st.plotly_chart(anomaly_charts['severity_breakdown'], use_container_width=True)
    
    # Anomalous events table
    st.subheader("Top Anomalous Events")
    anomalous_events = anomaly_data['anomalous_events']
    
    if not anomalous_events.empty:
        # Display top anomalous events with severity indicators
        display_cols = ['timestamp', 'log_type', 'user_id', 'anomaly_score', 'message']
        available_cols = [col for col in display_cols if col in anomalous_events.columns]
        
        st.dataframe(
            anomalous_events[available_cols].head(50),
            use_container_width=True
        )
        
        # Download link
        st.markdown(create_download_link(anomalous_events, "anomalous_events"), unsafe_allow_html=True)

def show_raw_data_tab():
    """Display raw data explorer tab."""
    st.header("📊 Raw Data Explorer")
    
    if st.session_state.processed_data is None or st.session_state.processed_data.empty:
        st.info("Please upload and process a log file to explore raw data.")
        return
    
    df = st.session_state.processed_data
    
    # Data summary
    st.subheader("Data Summary")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Records", len(df))
    with col2:
        st.metric("Date Range", f"{(df['timestamp'].max() - df['timestamp'].min()).days} days")
    with col3:
        st.metric("Unique Users", df['user_id'].nunique())
    with col4:
        st.metric("Log Types", df['log_type'].nunique())
    
    # Filters
    st.subheader("Data Filters")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        log_type_filter = st.multiselect(
            "Log Type",
            options=df['log_type'].unique(),
            default=df['log_type'].unique()
        )
    
    with col2:
        user_filter = st.multiselect(
            "User ID",
            options=df['user_id'].dropna().unique()[:50],  # Limit for performance
            default=[]
        )
    
    with col3:
        domain_filter = st.multiselect(
            "Domain",
            options=df['domain'].unique(),
            default=df['domain'].unique()
        )
    
    # Apply filters
    filtered_df = df[df['log_type'].isin(log_type_filter)]
    
    if user_filter:
        filtered_df = filtered_df[filtered_df['user_id'].isin(user_filter)]
    
    if domain_filter:
        filtered_df = filtered_df[filtered_df['domain'].isin(domain_filter)]
    
    # Display filtered data
    st.subheader(f"Filtered Data ({len(filtered_df)} records)")
    st.dataframe(filtered_df, use_container_width=True, height=600)
    
    # Download options
    st.subheader("Download Options")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(create_download_link(filtered_df, "filtered_data", "csv"), unsafe_allow_html=True)
    with col2:
        st.markdown(create_download_link(filtered_df, "filtered_data", "excel"), unsafe_allow_html=True)
    with col3:
        if st.button("📋 Copy to Clipboard"):
            filtered_df.to_clipboard()
            st.success("Data copied to clipboard!")

def main():
    """Main application function."""
    initialize_session_state()
    
    # Show sidebar
    uploaded_file = show_sidebar()
    
    # Main content area
    st.title("📊 PeopleSoft Log Analyzer")
    st.markdown("Comprehensive log analysis with AI-powered insights and user analytics")
    
    # Show overview if data is available
    if st.session_state.analysis_results and 'summary' in st.session_state.analysis_results:
        summary = st.session_state.analysis_results['summary']
        overview_chart = st.session_state.visualizer.create_overview_dashboard(summary)
        
        if overview_chart:
            st.plotly_chart(overview_chart, use_container_width=True)
    
    # Tabbed interface
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "🔐 Authentication", 
        "❌ Errors", 
        "🖥️ Availability", 
        "👥 User Analytics", 
        "🤖 AI Anomalies", 
        "📊 Raw Data"
    ])
    
    with tab1:
        show_authentication_tab()
    
    with tab2:
        show_error_analysis_tab()
    
    with tab3:
        show_availability_tab()
    
    with tab4:
        show_user_analytics_tab()
    
    with tab5:
        show_anomaly_detection_tab()
    
    with tab6:
        show_raw_data_tab()
    
    # Footer
    st.markdown("---")
    st.markdown(
        "**PeopleSoft Log Analyzer** - Advanced log analysis with AI-powered anomaly detection | "
        "Built with Streamlit and scikit-learn"
    )

if __name__ == "__main__":
    main()