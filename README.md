# Splunk O11y Cloud — Active Users Script

A Python script to list users who have **actively logged in** to your [Splunk Observability Cloud](https://www.splunk.com/en_us/products/observability.html) (O11y Cloud) org within a given time window.

---
## Usage

```bash
python3 get-active-users.py --realm <realm> --token <token> --duration <duration>
```
---

## How it works

1. Fetches all current members of your O11y Cloud org via the `/v2/organization/member` API
2. Fetches login session events via the `/v2/event/find` API filtered by `SessionLog`
3. Returns the **intersection** — users who are both org members and have a recent session

---

## Requirements

- Python 3.7+
- A Splunk O11y Cloud account with an API access token
- `requests` library

---

## Installation

```bash
# Clone the repo
git clone https://github.com/<your-username>/olly-active-users.git
cd olly-active-users

# Install dependencies
python3 -m pip install -r requirements.txt
```

---

### Arguments

| Argument | Required | Description |
|---|---|---|
| `--realm` | No (prompted if missing) | Your O11y Cloud realm, e.g. `us0`, `us1`, `eu0` |
| `--token` | No (prompted if missing) | Your user API access token |
| `--duration` | No (default: `60d`) | Look-back window (see examples below) |

### Duration examples

| Flag | Meaning |
|---|---|
| `--duration 1h` | Last 1 hour |
| `--duration 12h` | Last 12 hours |
| `--duration 1day` | Last 1 day |
| `--duration 7d` | Last 7 days |
| `--duration 1week` | Last 1 week |
| `--duration 1month` | Last 30 days |
| `--duration 3months` | Last 90 days |
| `--duration 1year` | Last 365 days |

---

## Examples

```bash
# Active users in the last hour
python3 get-active-users.py --realm us1 --token <token> --duration 1h

# Active users in the last month
python3 get-active-users.py --realm us1 --token <token> --duration 1month

# Save results to a file
python3 get-active-users.py --realm us1 --token <token> --duration 30d > active-users.csv
```

---

## Finding your Realm and Token

**Realm:**
1. Log in to O11y Cloud
2. Go to **Settings → My Profile**
3. Your realm is listed there (e.g. `us1`, `eu0`)

**API Token:**
1. Go to **Settings → My Profile**
2. Scroll to **User API Access Tokens**
3. Click **Generate new token** and copy the value

> Note: You need **org admin** permissions to call the `organization/member` endpoint.

---

## Security Note

Never hardcode your API token in the script or commit it to Git.  
Use the `--token` argument at runtime or store it in an environment variable:

```bash
export OLLY_TOKEN="your-token-here"
python3 get-active-users.py --realm us1 --token $OLLY_TOKEN --duration 1month
```
