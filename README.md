# Santander Cycle Station Notification

This application monitors the availability of empty docks at Santander Cycle stations in London and sends email notifications based on user-defined conditions.

## Features

- Fetch live Santander Cycle station data from Transport for London (TfL) API
- Monitor specific stations (default: Westminster Pier)
- Send email notifications based on available empty docks
- Configurable thresholds for notifications
- Easy setup with environment variables

## Setup

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/santander-notification.git
   cd santander-notification
   ```

2. Set up your Python environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -e .
   ```

3. Create a `.env` file with your configuration:
   ```
   SENDER_EMAIL=your.email@gmail.com
   RECIPIENT_EMAIL=your.email@gmail.com
   
   # TfL Cycle Station Settings
   CYCLE_STATION_NAME=Westminster Pier, Westminster
   EMPTY_DOCK_THRESHOLD=5
   
   # SMTP Server Configuration (defaults to Gmail)
   SMTP_SERVER=smtp.gmail.com
   SMTP_PORT=587
   ```

4. For Gmail integration:
   - Go to https://console.cloud.google.com/
   - Create a project and enable the Gmail API
   - Create OAuth credentials and download as `credentials.json`
   - Place `credentials.json` in the project directory
   - First time you run the app, it will open a browser window to authenticate

## Usage

### List Available Stations

To see all available stations or search for a specific station:

```bash
python src/santander-notification/list_stations.py
# Or search for a specific station
python src/santander-notification/list_stations.py westminster
```

### Check a Specific Station and Send Notification

```bash
python src/santander-notification/cycle_notification.py
```

This will:
1. Fetch the latest data for the station specified in your `.env` file
2. Send an email notification with the current status
3. If the number of empty docks is below the threshold, the email will include a warning

### Automating with Cron or Task Scheduler

To set up a recurring check, you can use cron (Linux/macOS) or Task Scheduler (Windows).

Example cron entry to check every hour:

```
0 * * * * cd /path/to/santander-notification && /path/to/venv/bin/python src/santander-notification/cycle_notification.py
```

## Automating with GitHub Actions

This repository includes a GitHub Actions workflow that automatically runs the cycle station check every day at 8:15am UK time. To use this feature:

1. Push this repository to GitHub
2. Go to your repository's "Settings" tab
3. Navigate to "Secrets and variables" → "Actions"
4. Add the following repository secrets:

   | Secret Name | Description |
   |-------------|-------------|
   | `SENDER_EMAIL` | Your Gmail address used to send notifications |
   | `RECIPIENT_EMAIL` | Email address to receive notifications |
   | `GOOGLE_CREDENTIALS` | The entire contents of your `credentials.json` file |
   | `GOOGLE_TOKEN` | (Optional) The entire contents of your `token.json` file if you have one |
   | `CYCLE_STATION_NAME` | (Optional) The name of the station to monitor |
   | `EMPTY_DOCK_THRESHOLD` | (Optional) Threshold for sending warnings |

5. The workflow will run automatically at 8:15am UK time daily
6. You can also trigger the workflow manually from the "Actions" tab

Note: If you don't provide the optional secrets, the workflow will use the default values (Westminster Pier station with a threshold of 5).

## Troubleshooting

- If email sending fails, check your Gmail account settings:
  - You may need to enable "Less secure app access" or use an App Password
  - Ensure your `credentials.json` file is correctly set up
  
- If the station you want is not found, use the `list_stations.py` script to find the exact station name

## License

This project is licensed under the MIT License - see the LICENSE file for details.
