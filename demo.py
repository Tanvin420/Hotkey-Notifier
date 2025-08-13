#!/usr/bin/env python3
"""
Demo script for PeopleSoft Log Analyzer
Demonstrates the analysis capabilities with sample data.
"""

from analyzer import LogAnalyzer
from visualizer import LogVisualizer
import pandas as pd

def main():
    """Run a demonstration of the log analyzer capabilities."""
    
    print("🔍 PeopleSoft Log Analyzer Demo")
    print("=" * 50)
    
    # Initialize analyzer
    analyzer = LogAnalyzer()
    visualizer = LogVisualizer()
    
    # Load sample data
    print("\n📁 Loading sample log data...")
    with open('sample_peoplesoft.log', 'r') as f:
        log_content = f.read()
    
    # Process the log file
    print("⚙️ Processing log entries...")
    processed_data = analyzer.process_log_file(log_content)
    
    # Display basic statistics
    print(f"\n📊 Processing Results:")
    print(f"   Total log entries processed: {len(processed_data)}")
    print(f"   Log types found: {processed_data['log_type'].value_counts().to_dict()}")
    print(f"   Unique users identified: {processed_data['user_id'].nunique()}")
    print(f"   Date range: {processed_data['timestamp'].min()} to {processed_data['timestamp'].max()}")
    
    # Run comprehensive analysis
    print("\n🔍 Running comprehensive analysis...")
    
    # Get analysis summary
    summary = analyzer.get_analysis_summary()
    print(f"\n📈 Analysis Summary:")
    print(f"   Authentication success rate: {summary['authentication_success_rate']}%")
    print(f"   Total authentication attempts: {summary['total_authentication_attempts']}")
    print(f"   Active users: {summary['active_users']}")
    
    # User analytics
    print("\n👥 Performing user analytics...")
    user_analytics = analyzer.analyze_user_rankings()
    
    if not user_analytics['top_success_users'].empty:
        print(f"   Top successful user: {user_analytics['top_success_users'].index[0]} " +
              f"({user_analytics['top_success_users'].iloc[0]['success_count']} successes)")
    
    if not user_analytics['top_failure_users'].empty:
        print(f"   Most failed attempts: {user_analytics['top_failure_users'].index[0]} " +
              f"({user_analytics['top_failure_users'].iloc[0]['failure_count']} failures)")
    
    # Boot sequence analysis
    print("\n🖥️ Analyzing system availability...")
    boot_analysis = analyzer.analyze_boot_sequences()
    
    if boot_analysis['availability_metrics']:
        metrics = boot_analysis['availability_metrics']
        print(f"   Total boot attempts: {metrics['total_boot_attempts']}")
        print(f"   Average boot time: {metrics['average_boot_time_minutes']:.1f} minutes")
        print(f"   Total downtime: {metrics['total_downtime_hours']:.2f} hours")
        print(f"   Domains affected: {metrics['domains_affected']}")
    
    # Anomaly detection
    print("\n🤖 Running AI-powered anomaly detection...")
    anomaly_results = analyzer.detect_anomalies_ai()
    
    if anomaly_results['anomaly_summary']:
        summary = anomaly_results['anomaly_summary']
        print(f"   Anomalous events detected: {summary['anomalous_events']}")
        print(f"   Anomaly rate: {summary['anomaly_rate']:.1f}%")
        print(f"   High severity anomalies: {summary['high_severity_anomalies']}")
        print(f"   Medium severity anomalies: {summary['medium_severity_anomalies']}")
        print(f"   Low severity anomalies: {summary['low_severity_anomalies']}")
    
    # Display top anomalous events
    if not anomaly_results['anomalous_events'].empty:
        print(f"\n⚠️ Top 3 Anomalous Events:")
        top_anomalies = anomaly_results['anomalous_events'].head(3)
        for idx, row in top_anomalies.iterrows():
            print(f"   {idx + 1}. Score: {row['anomaly_score']:.1f} - {row['log_type']} - {row['message'][:60]}...")
    
    print("\n✅ Analysis complete!")
    print("\n💡 To explore interactive visualizations, run: streamlit run main.py")
    print("   Then upload the sample_peoplesoft.log file through the web interface.")

if __name__ == "__main__":
    main()