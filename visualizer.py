"""
PeopleSoft Log Analyzer - Advanced Visualization Engine
Creates comprehensive charts and interactive visualizations for log analysis results.
"""

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
import streamlit as st

class LogVisualizer:
    """Advanced visualization engine for log analysis results."""
    
    def __init__(self):
        self.color_palette = {
            'primary': '#1f77b4',
            'success': '#2ca02c',
            'failure': '#d62728',
            'warning': '#ff7f0e',
            'error': '#ff0000',
            'info': '#17becf',
            'secondary': '#9467bd'
        }
    
    def create_user_ranking_charts(self, user_analytics):
        """Create comprehensive user ranking visualizations."""
        charts = {}
        
        if not user_analytics or all(df.empty for df in user_analytics.values()):
            return charts
        
        # Top Users by Success Count
        if not user_analytics['top_success_users'].empty:
            success_df = user_analytics['top_success_users'].head(10)
            
            fig_success = go.Figure(data=[
                go.Bar(
                    x=success_df['success_count'],
                    y=success_df.index,
                    orientation='h',
                    marker_color=self.color_palette['success'],
                    text=success_df['success_rate'].astype(str) + '%',
                    textposition='auto',
                    hovertemplate='<b>%{y}</b><br>' +
                                'Success Count: %{x}<br>' +
                                'Success Rate: %{text}<br>' +
                                '<extra></extra>'
                )
            ])
            
            fig_success.update_layout(
                title='Top 10 Users by Authentication Success',
                xaxis_title='Success Count',
                yaxis_title='User ID',
                height=500,
                yaxis={'categoryorder': 'total ascending'}
            )
            
            charts['success_ranking'] = fig_success
        
        # Top Users by Failure Count
        if not user_analytics['top_failure_users'].empty:
            failure_df = user_analytics['top_failure_users'].head(10)
            
            fig_failure = go.Figure(data=[
                go.Bar(
                    x=failure_df['failure_count'],
                    y=failure_df.index,
                    orientation='h',
                    marker_color=self.color_palette['failure'],
                    text=failure_df['failure_rate'].astype(str) + '%',
                    textposition='auto',
                    hovertemplate='<b>%{y}</b><br>' +
                                'Failure Count: %{x}<br>' +
                                'Failure Rate: %{text}<br>' +
                                '<extra></extra>'
                )
            ])
            
            fig_failure.update_layout(
                title='Top 10 Users by Authentication Failures',
                xaxis_title='Failure Count',
                yaxis_title='User ID',
                height=500,
                yaxis={'categoryorder': 'total ascending'}
            )
            
            charts['failure_ranking'] = fig_failure
        
        # Top Users by Error Count
        if not user_analytics['top_error_users'].empty:
            error_df = user_analytics['top_error_users'].head(10)
            
            fig_error = go.Figure(data=[
                go.Bar(
                    x=error_df['error_count'],
                    y=error_df.index,
                    orientation='h',
                    marker_color=self.color_palette['error'],
                    hovertemplate='<b>%{y}</b><br>' +
                                'Error Count: %{x}<br>' +
                                '<extra></extra>'
                )
            ])
            
            fig_error.update_layout(
                title='Top 10 Users by Errors Encountered',
                xaxis_title='Error Count',
                yaxis_title='User ID',
                height=500,
                yaxis={'categoryorder': 'total ascending'}
            )
            
            charts['error_ranking'] = fig_error
        
        # User Activity Heatmap
        if not user_analytics['user_summary'].empty:
            summary_df = user_analytics['user_summary'].head(20)
            
            # Create activity pattern heatmap
            activity_cols = [col for col in summary_df.columns if col in ['auth_success', 'auth_failed', 'error']]
            if activity_cols:
                heatmap_data = summary_df[activity_cols].fillna(0)
                
                fig_heatmap = go.Figure(data=go.Heatmap(
                    z=heatmap_data.values,
                    x=activity_cols,
                    y=summary_df.index,
                    colorscale='Viridis',
                    hovertemplate='User: %{y}<br>Activity: %{x}<br>Count: %{z}<extra></extra>'
                ))
                
                fig_heatmap.update_layout(
                    title='User Activity Pattern Heatmap (Top 20 Users)',
                    xaxis_title='Activity Type',
                    yaxis_title='User ID',
                    height=600
                )
                
                charts['activity_heatmap'] = fig_heatmap
        
        return charts
    
    def create_boot_timeline_chart(self, boot_analysis):
        """Create system boot and downtime timeline."""
        charts = {}
        
        if not boot_analysis or boot_analysis['boot_sequences'].empty:
            return charts
        
        boot_df = boot_analysis['boot_sequences']
        
        # Boot Duration Timeline
        fig_timeline = go.Figure()
        
        for i, row in boot_df.iterrows():
            fig_timeline.add_trace(go.Scatter(
                x=[row['boot_start'], row['boot_end']],
                y=[row['domain'], row['domain']],
                mode='lines+markers',
                line=dict(width=8, color=self.color_palette['warning']),
                marker=dict(size=8),
                name=f"Boot {i+1}",
                hovertemplate=f"<b>{row['domain']}</b><br>" +
                            f"Start: {row['boot_start']}<br>" +
                            f"End: {row['boot_end']}<br>" +
                            f"Duration: {row['duration_minutes']:.1f} min<br>" +
                            "<extra></extra>"
            ))
        
        fig_timeline.update_layout(
            title='System Boot Sequences Timeline',
            xaxis_title='Time',
            yaxis_title='Domain',
            height=400,
            showlegend=False
        )
        
        charts['boot_timeline'] = fig_timeline
        
        # Boot Duration Distribution
        fig_duration = go.Figure(data=[
            go.Histogram(
                x=boot_df['duration_minutes'],
                nbinsx=20,
                marker_color=self.color_palette['primary'],
                opacity=0.7
            )
        ])
        
        fig_duration.update_layout(
            title='Boot Duration Distribution',
            xaxis_title='Duration (minutes)',
            yaxis_title='Frequency',
            height=400
        )
        
        charts['duration_distribution'] = fig_duration
        
        # Domain Boot Frequency
        domain_counts = boot_df['domain'].value_counts()
        
        fig_domain = go.Figure(data=[
            go.Bar(
                x=domain_counts.index,
                y=domain_counts.values,
                marker_color=self.color_palette['info']
            )
        ])
        
        fig_domain.update_layout(
            title='Boot Frequency by Domain',
            xaxis_title='Domain',
            yaxis_title='Boot Count',
            height=400
        )
        
        charts['domain_frequency'] = fig_domain
        
        return charts
    
    def create_anomaly_heatmap(self, anomaly_data):
        """Create time-based anomaly detection heatmap."""
        charts = {}
        
        if not anomaly_data or anomaly_data['anomaly_scores'].empty:
            return charts
        
        df = anomaly_data['anomaly_scores']
        
        # Time-based anomaly heatmap
        if 'timestamp' in df.columns and not df['timestamp'].isna().all():
            df['hour'] = df['timestamp'].dt.hour
            df['day'] = df['timestamp'].dt.date
            
            # Create hourly anomaly intensity
            hourly_anomalies = df.groupby(['day', 'hour']).agg({
                'anomaly_score': 'mean',
                'is_anomaly': 'sum'
            }).reset_index()
            
            if not hourly_anomalies.empty:
                # Pivot for heatmap
                heatmap_data = hourly_anomalies.pivot(index='day', columns='hour', values='anomaly_score')
                
                fig_heatmap = go.Figure(data=go.Heatmap(
                    z=heatmap_data.values,
                    x=heatmap_data.columns,
                    y=[str(d) for d in heatmap_data.index],
                    colorscale='Reds',
                    hovertemplate='Date: %{y}<br>Hour: %{x}<br>Avg Anomaly Score: %{z:.1f}<extra></extra>'
                ))
                
                fig_heatmap.update_layout(
                    title='Anomaly Intensity Heatmap by Time',
                    xaxis_title='Hour of Day',
                    yaxis_title='Date',
                    height=500
                )
                
                charts['anomaly_heatmap'] = fig_heatmap
        
        # Anomaly Score Distribution
        fig_dist = go.Figure(data=[
            go.Histogram(
                x=df['anomaly_score'],
                nbinsx=30,
                marker_color=self.color_palette['warning'],
                opacity=0.7
            )
        ])
        
        fig_dist.update_layout(
            title='Anomaly Score Distribution',
            xaxis_title='Anomaly Score',
            yaxis_title='Frequency',
            height=400
        )
        
        charts['score_distribution'] = fig_dist
        
        # Anomaly Severity Breakdown
        if 'anomaly_summary' in anomaly_data:
            summary = anomaly_data['anomaly_summary']
            
            if 'high_severity_anomalies' in summary:
                severity_data = {
                    'High (>80)': summary.get('high_severity_anomalies', 0),
                    'Medium (60-80)': summary.get('medium_severity_anomalies', 0),
                    'Low (≤60)': summary.get('low_severity_anomalies', 0)
                }
                
                fig_severity = go.Figure(data=[
                    go.Pie(
                        labels=list(severity_data.keys()),
                        values=list(severity_data.values()),
                        hole=0.3,
                        marker_colors=[self.color_palette['error'], 
                                     self.color_palette['warning'],
                                     self.color_palette['info']]
                    )
                ])
                
                fig_severity.update_layout(
                    title='Anomaly Severity Distribution',
                    height=400
                )
                
                charts['severity_breakdown'] = fig_severity
        
        return charts
    
    def create_authentication_analysis_charts(self, df):
        """Create authentication analysis visualizations."""
        charts = {}
        
        if df.empty:
            return charts
        
        auth_data = df[df['log_type'].isin(['auth_success', 'auth_failed'])]
        
        if auth_data.empty:
            return charts
        
        # Authentication Success/Failure Over Time
        if not auth_data['timestamp'].isna().all():
            auth_data['date'] = auth_data['timestamp'].dt.date
            daily_auth = auth_data.groupby(['date', 'log_type']).size().unstack(fill_value=0)
            
            fig_timeline = go.Figure()
            
            if 'auth_success' in daily_auth.columns:
                fig_timeline.add_trace(go.Scatter(
                    x=daily_auth.index,
                    y=daily_auth['auth_success'],
                    mode='lines+markers',
                    name='Success',
                    line=dict(color=self.color_palette['success'])
                ))
            
            if 'auth_failed' in daily_auth.columns:
                fig_timeline.add_trace(go.Scatter(
                    x=daily_auth.index,
                    y=daily_auth['auth_failed'],
                    mode='lines+markers',
                    name='Failed',
                    line=dict(color=self.color_palette['failure'])
                ))
            
            fig_timeline.update_layout(
                title='Authentication Attempts Over Time',
                xaxis_title='Date',
                yaxis_title='Count',
                height=400
            )
            
            charts['auth_timeline'] = fig_timeline
        
        # Success Rate Pie Chart
        success_count = len(auth_data[auth_data['log_type'] == 'auth_success'])
        failure_count = len(auth_data[auth_data['log_type'] == 'auth_failed'])
        
        fig_pie = go.Figure(data=[
            go.Pie(
                labels=['Success', 'Failed'],
                values=[success_count, failure_count],
                hole=0.3,
                marker_colors=[self.color_palette['success'], self.color_palette['failure']]
            )
        ])
        
        fig_pie.update_layout(
            title='Overall Authentication Success Rate',
            height=400
        )
        
        charts['success_rate_pie'] = fig_pie
        
        return charts
    
    def create_error_analysis_charts(self, df):
        """Create error analysis visualizations."""
        charts = {}
        
        if df.empty:
            return charts
        
        error_data = df[df['log_type'] == 'error']
        
        if error_data.empty:
            return charts
        
        # Error Frequency Over Time
        if not error_data['timestamp'].isna().all():
            error_data['date'] = error_data['timestamp'].dt.date
            daily_errors = error_data.groupby('date').size()
            
            fig_timeline = go.Figure(data=[
                go.Scatter(
                    x=daily_errors.index,
                    y=daily_errors.values,
                    mode='lines+markers',
                    line=dict(color=self.color_palette['error']),
                    marker=dict(size=6)
                )
            ])
            
            fig_timeline.update_layout(
                title='Error Frequency Over Time',
                xaxis_title='Date',
                yaxis_title='Error Count',
                height=400
            )
            
            charts['error_timeline'] = fig_timeline
        
        # Error Distribution by Hour
        if not error_data['timestamp'].isna().all():
            error_data['hour'] = error_data['timestamp'].dt.hour
            hourly_errors = error_data.groupby('hour').size()
            
            fig_hourly = go.Figure(data=[
                go.Bar(
                    x=hourly_errors.index,
                    y=hourly_errors.values,
                    marker_color=self.color_palette['error'],
                    opacity=0.7
                )
            ])
            
            fig_hourly.update_layout(
                title='Error Distribution by Hour of Day',
                xaxis_title='Hour',
                yaxis_title='Error Count',
                height=400
            )
            
            charts['hourly_errors'] = fig_hourly
        
        return charts
    
    def create_overview_dashboard(self, summary_stats):
        """Create overview dashboard with key metrics."""
        if not summary_stats:
            return None
        
        # Create metrics cards layout
        fig = make_subplots(
            rows=2, cols=3,
            subplot_titles=[
                'Total Events', 'Active Users', 'Success Rate',
                'Event Breakdown', 'Authentication Stats', 'System Status'
            ],
            specs=[[{"type": "indicator"}, {"type": "indicator"}, {"type": "indicator"}],
                   [{"type": "pie"}, {"type": "bar"}, {"type": "indicator"}]]
        )
        
        # Total Events
        fig.add_trace(
            go.Indicator(
                mode="number",
                value=summary_stats.get('total_events', 0),
                title={"text": "Total Events"},
                number={'font': {'size': 40}}
            ),
            row=1, col=1
        )
        
        # Active Users
        fig.add_trace(
            go.Indicator(
                mode="number",
                value=summary_stats.get('active_users', 0),
                title={"text": "Active Users"},
                number={'font': {'size': 40}}
            ),
            row=1, col=2
        )
        
        # Success Rate
        fig.add_trace(
            go.Indicator(
                mode="number+gauge",
                value=summary_stats.get('authentication_success_rate', 0),
                title={"text": "Auth Success Rate (%)"},
                number={'font': {'size': 40}},
                gauge={'axis': {'range': [None, 100]},
                      'bar': {'color': self.color_palette['success']},
                      'steps': [{'range': [0, 50], 'color': "lightgray"},
                               {'range': [50, 80], 'color': "gray"}],
                      'threshold': {'line': {'color': "red", 'width': 4},
                                   'thickness': 0.75, 'value': 90}}
            ),
            row=1, col=3
        )
        
        # Event Breakdown Pie
        event_breakdown = summary_stats.get('event_breakdown', {})
        if event_breakdown:
            fig.add_trace(
                go.Pie(
                    labels=list(event_breakdown.keys()),
                    values=list(event_breakdown.values()),
                    hole=0.3
                ),
                row=2, col=1
            )
        
        fig.update_layout(
            height=800,
            title_text="PeopleSoft Log Analysis Overview Dashboard",
            showlegend=False
        )
        
        return fig