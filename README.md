# Radded's Home Assistant Data Dumper

## Description

This robust app will dump the time-series Entity state data that Home Assistant collects in its Activity panel.
Unlike Home Assistant's official data collection, this addon will extend the data collection beyond the original 10 days.
It will also perform serialization of the data, enabling easy filtering.
I will use this repository for training Machine Learning models in future work.

[See the Wiki for more information](https://github.com/Raddeds-PLA-Project/home-assistant-data-dumper/wiki)


## Usage

- On first run, the app collects all data available in the Activity panel.
- This collection will run every day (at the time the app was ran) to store the new data.
- You can then download this data as a `.sqlite3` database file.

## Installation
- In your Home Assistant, go to Settings > Apps (formerly Addons) > Install app > triple-dots (top-right) > Repositories
- Add the "Radded's Personal Life Automation Project" repository:
`https://github.com/Raddeds-PLA-Project/home-assistant-addon-repo`
- Return to "App Store" and scroll down until you see "Radded's Personal Life Automation Project"
- Install "Radded's Home Assistant Data Dumper"