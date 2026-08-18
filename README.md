# myFlight — Home Assistant integration

HACS custom integration for the self-hosted **myFlight** app. Polls `GET /api/ha/status` and exposes sensors, binary sensors, device trackers, and buttons for dashboards and automations.

Pair with the **[myFlight Card](https://github.com/benalfoldi/myflight-card)** Lovelace plugin for Home-page cards (next duty, mission, live track, airport stats, fleet, partner flight).

## Features

- **Status sensor** — master entity with the full home snapshot in attributes
- **Sensors** — next duty date, pending roster changes, airborne count, partner status
- **Binary sensors** — roster changes pending, partner live flight
- **Device trackers** — mission tail, partner aircraft, optional tracked tail
- **Buttons** — refresh now, push snapshot to webhook
- **Service** — `myflight.refresh`

## Requirements

- Home Assistant 2023.8+
- A self-hosted myFlight instance with `HA_API_KEY` set
- Network access from Home Assistant to your myFlight URL

## Install via HACS

1. **HACS → Integrations → ⋮ → Custom repositories**
2. URL: `https://github.com/benalfoldi/myflight-home-assistant`
3. Category: **Integration** → **Add**
4. Search **myFlight** → **Download**
5. Restart Home Assistant

## Configure

**Settings → Devices & services → Add integration → myFlight**

| Field | Description |
|-------|-------------|
| **Server URL** | Base URL of *your* myFlight server (e.g. `https://myflight.example.com`) |
| **API key** | The `HA_API_KEY` value from `/etc/myflight/env` |
| **Username** | myFlight username whose roster/home data to show |
| **Poll interval** | Seconds between polls (default 60, minimum 60) |
| **Airport** | Optional IATA for the airport-departures card (falls back to profile base) |
| **Track registration** | Optional tail for the live flight-track card (falls back to next-duty tail) |

Credentials stay in your Home Assistant config.

## Dashboard cards

```yaml
type: custom:myflight-next-duty-card
entity: sensor.myflight_status
theme: brand
```

Install the cards from [myflight-card](https://github.com/benalfoldi/myflight-card).

## Service

```yaml
service: myflight.refresh
```
