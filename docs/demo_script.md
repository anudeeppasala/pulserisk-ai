# PulseRisk AI V3 Demo Script

## One-Line Pitch

PulseRisk AI converts customer feedback into risk signals, issue clusters, root-cause insights, internal tickets, alerts, audit history, and executive reports.

## Demo Flow

1. Open Streamlit dashboard.
2. Show ingestion source options:
   - Sample CSV
   - Upload CSV
   - Mock Google Play Reviews
   - Mock App Store Reviews
   - Combined Mock Store Reviews
   - Load From SQLite Database
3. Explain that real Google/Apple APIs require app-owner credentials, so this demo uses safe mock connectors.
4. Show executive dashboard metrics.
5. Show issue category, severity, risk type, and owner team charts.
6. Open Issue Clusters tab.
7. Explain root-cause suggestions.
8. Open Internal Tickets tab.
9. Save comments and tickets to SQLite.
10. Update a ticket status.
11. Open Alert Center.
12. Show high/critical alerts.
13. Update alert status.
14. Open Database & Audit tab.
15. Show persistent records and audit trail.
16. Open Executive Report tab.
17. Download the report.

## Key Talking Points

- V1 classified customer comments.
- V2 added issue clusters, root-cause insights, and action tickets.
- V3 adds enterprise workflow: ingestion layer, database, internal tickets, alerts, audit trail, and reports.
- Jira and Slack are not required for the demo because PulseRisk has its own internal ticket and alert center.
- Real integrations can be added later as external adapters.