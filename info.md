# Solis Cloud Monitoring

Home Assistant cloud integration for Solis string inverters using the Solis Cloud v2 API. Tested with an S6-GR1P5K-S (0115) inverter and supports up to five units per account at a 60-second polling interval.

## Highlights
- Asynchronous DataUpdateCoordinator implementation
- Full Energy Dashboard support — solar production, grid import, and grid export sensors included
- Real-time grid import/export power, home load power, self-sufficiency and self-consumption percentages
- Automatic inverter discovery via the Solis Cloud API
- English translations and config flow localization included

## Requirements
- Home Assistant 2024.8+
- Solis Cloud account with API access (KeyID/KeySecret)
- API endpoint hosted on `https://www.soliscloud.com:13333/`

## Links
- [Documentation](https://github.com/BoiledFunn/HomeAssistant-SolisCloudMonitoring#readme)
- [Issue tracker](https://github.com/BoiledFunn/HomeAssistant-SolisCloudMonitoring/issues)
