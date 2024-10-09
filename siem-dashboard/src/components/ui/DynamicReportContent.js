import { parseISO, format } from 'date-fns';

export default function DynamicReportContent({ report }) {
  if (!report || !report.content) {
    return <p>No report data available</p>
  }

  const { report_type, content } = report;

  const formatDate = (dateString) => {
    try {
      return format(parseISO(dateString), 'PPP p');
    } catch (error) {
      console.error('Error parsing date:', error);
      return 'Invalid Date';
    }
  };

  return (
    <div className="mt-4">
      <h3 className="text-lg font-semibold">Generated Report</h3>
      <p>Report Type: {report_type}</p>
      <p>Start Date: {formatDate(content.start_date)}</p>
      <p>End Date: {formatDate(content.end_date)}</p>
      <p>Total Events: {content.total_events}</p>
      <p>Total Alerts: {content.total_alerts}</p>
      {content.event_types && (
        <>
          <h4 className="text-md font-semibold mt-2">Event Types:</h4>
          <ul>
            {content.event_types.map((eventType, index) => (
              <li key={index}>{eventType.event_type}: {eventType.count}</li>
            ))}
          </ul>
        </>
      )}
      {content.alert_severities && (
        <>
          <h4 className="text-md font-semibold mt-2">Alert Severities:</h4>
          <ul>
            {content.alert_severities.map((severity, index) => (
              <li key={index}>Severity {severity.severity}: {severity.count}</li>
            ))}
          </ul>
        </>
      )}
    </div>
  );
}