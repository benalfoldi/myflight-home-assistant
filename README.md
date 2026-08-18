# myFlight

HACS custom integration for a self-hosted myFlight server.

Companion Lovelace plugin: [myflight-card](https://github.com/benalfoldi/myflight-card).

## Install

1. HACS → Integrations → **Custom repositories**
2. URL: `https://github.com/benalfoldi/myflight-home-assistant`
3. Category: **Integration** → Add → download **myFlight** → restart Home Assistant
4. **Settings → Devices & services → Add integration → myFlight**

| Field | Description |
|-------|-------------|
| Server URL | Base URL of your myFlight instance |
| API key | From the server environment |
| Username | Account on that server |
| Poll interval | Seconds (default 60, minimum 60) |

Leave any extra fields blank if you do not need them.

```yaml
type: custom:myflight-next-duty-card
entity: sensor.myflight_status
theme: brand
```
