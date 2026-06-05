# Radded's Home Assistant Data Dumper

## Description

A robust app to dump the time-series Entity state data from Home Assistant. This application will pull all history that is currently available, and routinely poll as states change. This will create a large and detailed dataset that can be used for training Machine Learning models.

## Features

- On first installation, the app will collect all entity state history that is currently stored on the Home Assistant instance.
- For a user-configurable interval, the app will regularly collect new entity state history.
- This data is stored **locally and privately** on the instance in an SQLite database.
- The user can then choose which data to download from the addon, based on the following filters. Data will be exported as a `.sqlite3` database file.
  - Date and Time range
  - Entity domains (whitelist, blacklist)
  - Entity areas (whitelist, blacklist)
  - Entities (whitelist, blacklist)

## Installation

### Existing HA instance:

- Clone this repo (with `--recursive` ) into your Home Assistant `/root/addons` folder
- In Home Assistant, go to Settings > Apps (formerly Addons) > Install App > Local Apps and install "Radded's Home Assistant Data Dumper"
- You can also do development using VSCode Remote SSH

### Devcontainer (for local development)

- Dependencies: Docker, Python, Git
- Clone this repo to your system
- Open it with Visual Studio Code
- Run the Dev Container (you may be prompted to install a few extensions)
- Once the container is running, go to Terminal -> Run Task -> Start Home Assistant and continue from "Existing HA instance" above.