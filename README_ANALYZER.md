# PeopleSoft Log Analyzer

A comprehensive log analysis tool with AI-powered insights, user analytics, and system monitoring capabilities.

## Features

### 📊 Overview Dashboard
- Real-time metrics and KPIs
- Event breakdown visualization
- Authentication success rate gauge
- Interactive pie charts and indicators

### 🔐 Authentication Analysis
- Success/failure rate tracking
- Timeline visualization of authentication events
- User-specific authentication patterns
- Detailed event logs with download capability

### ❌ Error Analysis  
- Error frequency and pattern detection
- Hourly error distribution
- Error categorization and tracking
- Affected users identification

### 🖥️ System Availability
- Boot sequence tracking and analysis
- Downtime period calculation
- System availability metrics (MTBF, MTTR)
- Domain-specific availability monitoring

### 👥 User Analytics
- Top users by authentication success
- Top users by authentication failures  
- Top users by errors encountered
- User activity pattern heatmaps
- Comprehensive user ranking tables

### 🤖 AI-Powered Anomaly Detection
- Machine learning-based anomaly identification
- Anomaly scoring (0-100 scale)
- Temporal and behavioral anomaly detection
- Severity classification (High/Medium/Low)
- Interactive anomaly heatmaps

### 📊 Raw Data Explorer
- Interactive data filtering and search
- Export capabilities (CSV, Excel)
- Time-based data filtering
- Full raw log line preservation

## Technical Implementation

### Core Technologies
- **Frontend**: Streamlit with custom CSS styling
- **Data Processing**: Pandas, NumPy for data manipulation
- **Machine Learning**: scikit-learn (Isolation Forest) for anomaly detection
- **Visualization**: Plotly for interactive charts and graphs
- **Data Export**: Excel, CSV support with openpyxl

### Architecture

#### `analyzer.py` - Core Analysis Engine
- `LogAnalyzer` class with comprehensive data processing
- Pattern matching for authentication, errors, and boot sequences
- AI-powered anomaly detection with feature engineering
- User analytics and ranking algorithms
- Raw log line preservation

#### `visualizer.py` - Advanced Visualization Engine  
- `LogVisualizer` class with interactive chart creation
- Plotly-based charts with drill-down capabilities
- Custom color schemes and styling
- Export functionality for all visualizations

#### `main.py` - Streamlit Application
- Tabbed interface with 6 distinct analysis categories
- File upload and processing workflow
- Interactive configuration options
- Real-time analysis and visualization updates

### Key Features Implementation

#### Pattern Recognition Rules
```python
# Authentication patterns
auth_success_pattern = r'PeopleSoft Token authentication succeeded:(?!\s*PSADMIN@)'
auth_failed_pattern = r'PeopleSoft Token authentication failed:'

# Error patterns  
error_patterns = [
    r'An error has occurred',
    r'Integration Gateway - External System Contact Error', 
    r'ORA-\d+'  # Oracle database errors
]

# Boot sequence patterns
boot_start_pattern = r'Begin boot attempt on domain'
boot_end_pattern = r'End boot attempt on domain'
```

#### Anomaly Detection Features
- **Temporal Anomalies**: Unusual activity patterns by time
- **Volume Anomalies**: Unexpected spikes/drops in log volume
- **User Behavior Anomalies**: Deviations from normal user patterns
- **Event Sequence Anomalies**: Unusual patterns in event ordering

#### Machine Learning Pipeline
```python
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

class LogAnomalyDetector:
    def __init__(self):
        self.isolation_forest = IsolationForest(contamination=0.1, random_state=42)
        self.scaler = StandardScaler()
    
    def detect_anomalies(self, features):
        scaled_features = self.scaler.fit_transform(features)
        anomaly_scores = self.isolation_forest.fit_predict(scaled_features)
        return anomaly_scores
```

## Usage

### Prerequisites
```bash
pip install -r requirements.txt
```

### Running the Application
```bash
streamlit run main.py
```

### File Upload and Processing
1. Upload PeopleSoft log files (TXT, LOG formats)
2. Click "Process Log File" to analyze
3. Explore results across 6 analytical tabs
4. Download reports and visualizations

### Configuration Options
- **Anomaly Detection Sensitivity**: Adjust ML model sensitivity (0.05-0.3)
- **User Ranking Limit**: Control number of top users displayed (5-50)
- **Time Range Filtering**: Filter analysis by date ranges

## Sample Log Format

The analyzer supports PeopleSoft log entries in the following format:

```
2024-01-15 08:30:45 INFO PeopleSoft Token authentication succeeded: USER@DOMAIN.COM
2024-01-15 08:31:20 ERROR An error has occurred: Database connection timeout
2024-01-15 08:32:15 INFO Begin boot attempt on domain HRPROD
2024-01-15 08:35:30 INFO End boot attempt on domain HRPROD
```

## Output and Reports

### Analytics Reports
- User ranking reports (CSV/Excel)
- Authentication analysis summaries
- System availability metrics
- Anomaly detection results

### Visualizations
- Interactive charts with zoom and filter capabilities
- Exportable PNG/SVG formats
- Real-time data updates
- Drill-down functionality

### Key Metrics Tracked
- **Authentication Success Rate**: Percentage of successful logins
- **Mean Time Between Failures (MTBF)**: System reliability metric
- **Mean Time To Recovery (MTTR)**: System recovery efficiency
- **User Activity Patterns**: Behavioral analysis and anomaly detection
- **System Uptime**: Availability and downtime tracking

## Performance Optimization

- Efficient data processing with Pandas vectorization
- Memory management for large datasets
- Caching mechanisms for repeated analysis
- Optimized ML algorithms with appropriate feature selection

## Security Considerations

- No data persistence - all analysis is session-based
- Raw log lines preserved for audit trails
- User ID filtering to exclude system accounts
- Secure file upload with size and type validation

## Future Enhancements

- Real-time log streaming capabilities
- Advanced ML models for predictive analytics
- Custom alert and notification systems
- Integration with enterprise monitoring tools
- Multi-tenant support for different organizations

## Support

For issues, feature requests, or contributions, please refer to the project repository.