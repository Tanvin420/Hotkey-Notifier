"""
PeopleSoft Log Analyzer - Core Analysis Engine
Implements comprehensive log analysis with user analytics, boot tracking, and AI anomaly detection.
"""

import pandas as pd
import numpy as np
import re
from datetime import datetime, timedelta
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.feature_extraction.text import TfidfVectorizer
import warnings
warnings.filterwarnings('ignore')

class LogAnalyzer:
    """Core log analysis engine with enhanced user analytics and AI-powered anomaly detection."""
    
    def __init__(self):
        self.isolation_forest = IsolationForest(contamination=0.1, random_state=42)
        self.scaler = StandardScaler()
        self.processed_data = None
        self.raw_data = None
        
        # Authentication patterns
        self.auth_success_pattern = re.compile(r'PeopleSoft Token authentication succeeded:(?!\s*PSADMIN@)', re.IGNORECASE)
        self.auth_failed_pattern = re.compile(r'PeopleSoft Token authentication failed:', re.IGNORECASE)
        
        # Error patterns
        self.error_patterns = [
            re.compile(r'An error has occurred', re.IGNORECASE),
            re.compile(r'Integration Gateway - External System Contact Error', re.IGNORECASE),
            re.compile(r'ORA-\d+', re.IGNORECASE)
        ]
        
        # Boot sequence patterns
        self.boot_start_pattern = re.compile(r'Begin boot attempt on domain', re.IGNORECASE)
        self.boot_end_pattern = re.compile(r'End boot attempt on domain', re.IGNORECASE)
    
    def process_log_file(self, file_content):
        """Process uploaded log file content and extract structured data."""
        lines = file_content.decode('utf-8').split('\n') if isinstance(file_content, bytes) else file_content.split('\n')
        
        processed_entries = []
        
        for line_num, line in enumerate(lines):
            if not line.strip():
                continue
                
            entry = {
                'line_number': line_num + 1,
                'raw_line': line.strip(),
                'timestamp': self._extract_timestamp(line),
                'log_type': self._classify_log_type(line),
                'user_id': self._extract_user_id(line),
                'message': line.strip(),
                'domain': self._extract_domain(line)
            }
            
            processed_entries.append(entry)
        
        self.raw_data = pd.DataFrame(processed_entries)
        self.processed_data = self.raw_data[self.raw_data['log_type'] != 'unknown'].copy()
        
        return self.processed_data
    
    def _extract_timestamp(self, line):
        """Extract timestamp from log line."""
        # Common timestamp patterns
        patterns = [
            r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})',
            r'(\d{2}/\d{2}/\d{4} \d{2}:\d{2}:\d{2})',
            r'(\d{2}-\d{2}-\d{4} \d{2}:\d{2}:\d{2})'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, line)
            if match:
                try:
                    return pd.to_datetime(match.group(1))
                except:
                    continue
        
        return pd.NaT
    
    def _classify_log_type(self, line):
        """Classify log line type based on patterns."""
        if self.auth_success_pattern.search(line):
            return 'auth_success'
        elif self.auth_failed_pattern.search(line):
            return 'auth_failed'
        elif any(pattern.search(line) for pattern in self.error_patterns):
            return 'error'
        elif self.boot_start_pattern.search(line):
            return 'boot_start'
        elif self.boot_end_pattern.search(line):
            return 'boot_end'
        else:
            return 'unknown'
    
    def _extract_user_id(self, line):
        """Extract user ID from log line."""
        # Pattern for user extraction after authentication messages
        patterns = [
            r'authentication (?:succeeded|failed):\s*([^\s]+)',
            r'User:\s*([^\s]+)',
            r'UserID:\s*([^\s]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                user_id = match.group(1).strip()
                # Filter out system users
                if user_id and user_id not in ['PSADMIN', 'SYSTEM', 'ANONYMOUS']:
                    return user_id
        
        return None
    
    def _extract_domain(self, line):
        """Extract domain information from log line."""
        domain_match = re.search(r'domain\s+([^\s]+)', line, re.IGNORECASE)
        return domain_match.group(1) if domain_match else 'unknown'
    
    def analyze_user_rankings(self):
        """Generate comprehensive user analytics and rankings."""
        if self.processed_data is None or self.processed_data.empty:
            return {}
        
        user_analytics = {}
        
        # Filter data with valid users
        user_data = self.processed_data[self.processed_data['user_id'].notna()].copy()
        
        if user_data.empty:
            return {
                'top_success_users': pd.DataFrame(),
                'top_failure_users': pd.DataFrame(),
                'top_error_users': pd.DataFrame(),
                'user_summary': pd.DataFrame()
            }
        
        # Top Users by Authentication Success
        success_users = user_data[user_data['log_type'] == 'auth_success'].groupby('user_id').agg({
            'line_number': 'count',
            'timestamp': ['min', 'max']
        }).round(2)
        
        success_users.columns = ['success_count', 'first_login', 'last_login']
        success_users = success_users.sort_values('success_count', ascending=False)
        
        # Calculate success rates
        total_auth_by_user = user_data[user_data['log_type'].isin(['auth_success', 'auth_failed'])].groupby('user_id')['line_number'].count()
        success_users['total_attempts'] = total_auth_by_user
        success_users['success_rate'] = (success_users['success_count'] / success_users['total_attempts'] * 100).round(1)
        
        # Top Users by Authentication Failures
        failure_users = user_data[user_data['log_type'] == 'auth_failed'].groupby('user_id').agg({
            'line_number': 'count',
            'timestamp': ['min', 'max']
        }).round(2)
        
        failure_users.columns = ['failure_count', 'first_failure', 'last_failure']
        failure_users = failure_users.sort_values('failure_count', ascending=False)
        
        # Calculate failure rates
        failure_users['total_attempts'] = total_auth_by_user
        failure_users['failure_rate'] = (failure_users['failure_count'] / failure_users['total_attempts'] * 100).round(1)
        
        # Top Users by Errors Encountered
        error_users = user_data[user_data['log_type'] == 'error'].groupby('user_id').agg({
            'line_number': 'count',
            'timestamp': ['min', 'max']
        }).round(2)
        
        error_users.columns = ['error_count', 'first_error', 'last_error']
        error_users = error_users.sort_values('error_count', ascending=False)
        
        # User Summary Statistics
        user_summary = user_data.groupby('user_id').agg({
            'line_number': 'count',
            'timestamp': ['min', 'max']
        })
        user_summary.columns = ['total_activities', 'first_activity', 'last_activity']
        
        # Add activity type breakdown
        activity_breakdown = user_data.groupby(['user_id', 'log_type'])['line_number'].count().unstack(fill_value=0)
        user_summary = user_summary.join(activity_breakdown)
        user_summary = user_summary.sort_values('total_activities', ascending=False)
        
        return {
            'top_success_users': success_users.head(20),
            'top_failure_users': failure_users.head(20),
            'top_error_users': error_users.head(20),
            'user_summary': user_summary.head(50)
        }
    
    def analyze_boot_sequences(self):
        """Analyze system boot sequences and calculate downtime."""
        if self.processed_data is None or self.processed_data.empty:
            return {}
        
        boot_data = self.processed_data[
            self.processed_data['log_type'].isin(['boot_start', 'boot_end'])
        ].copy()
        
        if boot_data.empty:
            return {
                'boot_sequences': pd.DataFrame(),
                'availability_metrics': {},
                'downtime_periods': pd.DataFrame()
            }
        
        boot_data = boot_data.sort_values('timestamp')
        
        boot_sequences = []
        downtime_periods = []
        
        # Group by domain for separate analysis
        for domain in boot_data['domain'].unique():
            domain_boots = boot_data[boot_data['domain'] == domain].copy()
            
            boot_start = None
            for _, row in domain_boots.iterrows():
                if row['log_type'] == 'boot_start':
                    boot_start = row
                elif row['log_type'] == 'boot_end' and boot_start is not None:
                    duration = (row['timestamp'] - boot_start['timestamp']).total_seconds()
                    
                    boot_sequences.append({
                        'domain': domain,
                        'boot_start': boot_start['timestamp'],
                        'boot_end': row['timestamp'],
                        'duration_seconds': duration,
                        'duration_minutes': duration / 60,
                        'status': 'completed'
                    })
                    
                    downtime_periods.append({
                        'domain': domain,
                        'start_time': boot_start['timestamp'],
                        'end_time': row['timestamp'],
                        'downtime_minutes': duration / 60
                    })
                    
                    boot_start = None
        
        boot_df = pd.DataFrame(boot_sequences)
        downtime_df = pd.DataFrame(downtime_periods)
        
        # Calculate availability metrics
        availability_metrics = {}
        if not boot_df.empty:
            availability_metrics = {
                'total_boot_attempts': len(boot_df),
                'average_boot_time_minutes': boot_df['duration_minutes'].mean(),
                'longest_boot_time_minutes': boot_df['duration_minutes'].max(),
                'shortest_boot_time_minutes': boot_df['duration_minutes'].min(),
                'total_downtime_hours': boot_df['duration_minutes'].sum() / 60,
                'domains_affected': boot_df['domain'].nunique()
            }
        
        return {
            'boot_sequences': boot_df,
            'availability_metrics': availability_metrics,
            'downtime_periods': downtime_df
        }
    
    def detect_anomalies_ai(self):
        """AI-powered anomaly detection across all log types."""
        if self.processed_data is None or self.processed_data.empty:
            return {}
        
        # Prepare data for anomaly detection
        df = self.processed_data.copy()
        
        # Feature engineering
        features_df = self._extract_features_for_anomaly_detection(df)
        
        if features_df.empty:
            return {
                'anomaly_scores': pd.DataFrame(),
                'anomalous_events': pd.DataFrame(),
                'anomaly_summary': {}
            }
        
        # Scale features
        try:
            scaled_features = self.scaler.fit_transform(features_df)
            
            # Apply Isolation Forest
            anomaly_labels = self.isolation_forest.fit_predict(scaled_features)
            anomaly_scores = self.isolation_forest.decision_function(scaled_features)
            
            # Normalize anomaly scores to 0-100 scale
            normalized_scores = ((anomaly_scores - anomaly_scores.min()) / 
                               (anomaly_scores.max() - anomaly_scores.min()) * 100)
            
            # Create results DataFrame
            results_df = df.copy()
            results_df['anomaly_score'] = normalized_scores
            results_df['is_anomaly'] = anomaly_labels == -1
            
            # Identify anomalous events
            anomalous_events = results_df[results_df['is_anomaly']].copy()
            anomalous_events = anomalous_events.sort_values('anomaly_score', ascending=False)
            
            # Calculate anomaly summary
            anomaly_summary = {
                'total_events': len(results_df),
                'anomalous_events': len(anomalous_events),
                'anomaly_rate': len(anomalous_events) / len(results_df) * 100,
                'high_severity_anomalies': len(anomalous_events[anomalous_events['anomaly_score'] > 80]),
                'medium_severity_anomalies': len(anomalous_events[
                    (anomalous_events['anomaly_score'] > 60) & (anomalous_events['anomaly_score'] <= 80)
                ]),
                'low_severity_anomalies': len(anomalous_events[anomalous_events['anomaly_score'] <= 60])
            }
            
            return {
                'anomaly_scores': results_df,
                'anomalous_events': anomalous_events.head(100),
                'anomaly_summary': anomaly_summary
            }
            
        except Exception as e:
            return {
                'anomaly_scores': pd.DataFrame(),
                'anomalous_events': pd.DataFrame(),
                'anomaly_summary': {'error': str(e)}
            }
    
    def _extract_features_for_anomaly_detection(self, df):
        """Extract features for anomaly detection."""
        if df.empty:
            return pd.DataFrame()
        
        # Time-based features
        df['hour'] = df['timestamp'].dt.hour
        df['day_of_week'] = df['timestamp'].dt.dayofweek
        df['minute'] = df['timestamp'].dt.minute
        
        # Activity frequency features
        df['events_per_hour'] = df.groupby(df['timestamp'].dt.floor('H'))['line_number'].transform('count')
        df['events_per_minute'] = df.groupby(df['timestamp'].dt.floor('min'))['line_number'].transform('count')
        
        # User activity features
        df['user_events_count'] = df.groupby('user_id')['line_number'].transform('count')
        
        # Log type encoding
        log_type_dummies = pd.get_dummies(df['log_type'], prefix='log_type')
        
        # Combine features
        feature_cols = ['hour', 'day_of_week', 'minute', 'events_per_hour', 
                       'events_per_minute', 'user_events_count']
        
        features_df = df[feature_cols].copy()
        features_df = pd.concat([features_df, log_type_dummies], axis=1)
        
        # Fill NaN values
        features_df = features_df.fillna(0)
        
        return features_df
    
    def get_analysis_summary(self):
        """Generate comprehensive analysis summary."""
        if self.processed_data is None or self.processed_data.empty:
            return {}
        
        df = self.processed_data
        
        # Overall statistics
        total_events = len(df)
        date_range = (df['timestamp'].min(), df['timestamp'].max()) if not df['timestamp'].isna().all() else (None, None)
        
        # Event type breakdown
        event_breakdown = df['log_type'].value_counts().to_dict()
        
        # User statistics
        unique_users = df['user_id'].nunique()
        active_users = df[df['user_id'].notna()]['user_id'].nunique()
        
        # Authentication statistics
        auth_data = df[df['log_type'].isin(['auth_success', 'auth_failed'])]
        total_auth = len(auth_data)
        success_rate = (len(df[df['log_type'] == 'auth_success']) / total_auth * 100) if total_auth > 0 else 0
        
        return {
            'total_events': total_events,
            'date_range': date_range,
            'event_breakdown': event_breakdown,
            'unique_users': unique_users,
            'active_users': active_users,
            'authentication_success_rate': round(success_rate, 1),
            'total_authentication_attempts': total_auth
        }