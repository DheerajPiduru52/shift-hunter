# Automated Shift Selection Bot for My shifts

## Overview

This project automates the process of selecting and requesting shifts from the UREC staff portal at the University of Texas at Dallas. The tool leverages Selenium WebDriver to interact with the staff scheduling platform and applies rule-based filters to avoid picking undesirable shifts. Notifications are sent via Telegram whenever a shift is successfully picked.

## Features

- Logs into the UTD UREC staff portal using Selenium
- Automatically monitors available shifts on the Trade Center page
- Skips shifts based on:
  - Time constraints (early morning and late night windows)
  - Shift type filters (e.g., "Shift Lead" or "Leadership" roles)
- Sends real-time shift pick notifications via Telegram
- Refreshes every few seconds to check for new shift availability

## How It Works

1. **Authentication**  
   The script navigates to the login page and allows the user to complete manual login and MFA authentication.

2. **Shift Scraping**  
   Once authenticated, the script navigates to the Trade Center page and identifies all available shift rows.

3. **Filtering Logic**  
   Each shift is parsed and checked against exclusion criteria:
   - Shifts falling within restricted time windows (e.g., 6:45 AM – 10:00 AM, 10:00 PM – 1:00 AM)
   - Shifts that include restricted keywords such as "leadership" or "shift lead"

4. **Shift Requesting**  
   For eligible shifts, the bot clicks the "Request" button, handles confirmation prompts, and sends a Telegram message with the shift details.

5. **Continuous Monitoring**  
   The script runs in a loop with a short delay, continuously checking for new shift availability.

## Technologies Used

- Python
- Selenium WebDriver
- WebDriver Manager (Chrome)
- Telegram Bot API
- datetime and time modules

## Telegram Integration

The script is integrated with Telegram to notify users of shift pickups in real time. You need to supply a bot token and a chat ID to enable this functionality.

## Disclaimer

- This tool is intended for personal productivity and convenience.
- Manual login and MFA authentication are required at the start of each session.
- Use responsibly and in accordance with your organization’s policies.
