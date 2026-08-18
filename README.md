# myFlight

HACS custom integration for a self-hosted myFlight server. Polls `GET /api/ha/status` and creates sensors, buttons, and device trackers.

Companion Lovelace plugin: [myflight-card](https://github.com/benalfoldi/myflight-card).

## Install

1. HACS → Integrations → **Custom repositories**
2. URL: `https://github.com/benalfoldi/myflight-home-assistant`
3. Category: **Integration** → Add → download **myFlight** → restart Home Assistant
4. **Settings → Devices & services → Add integration → myFlight**

| Field | Description |
|-------|-------------|
| Server URL | Base URL of your myFlight instance |
| API key | `HA_API_KEY` from the server environment |
| Username | Account on that server |
| Poll interval | Seconds (default 60, minimum 60) |
| Airport | Optional IATA code |
| Track registration | Optional aircraft registration |

```yaml
type: custom:myflight-next-duty-card
entity: sensor.myflight_status
theme: brand
```
