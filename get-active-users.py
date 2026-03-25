from datetime import datetime, timedelta
import argparse
import requests as rq


UNIT_TO_DAYS = {
    "hour":  1 / 24,
    "hours": 1 / 24,
    "h":     1 / 24,
    "day":   1,
    "days":  1,
    "d":     1,
    "week":  7,
    "weeks": 7,
    "w":     7,
    "month": 30,
    "months": 30,
    "m":     30,
    "year":  365,
    "years": 365,
    "y":     365,
}


def parse_duration(value: str) -> float:
    """Convert a human-friendly duration string like '1 day', '2 weeks', '3h' to days."""
    value = value.strip().lower()
    # Allow formats: "30", "1d", "1 day", "2 weeks", "1hour"
    for unit, multiplier in UNIT_TO_DAYS.items():
        if value.endswith(unit):
            number_part = value[: -len(unit)].strip()
            number = float(number_part) if number_part else 1
            return number * multiplier
    # Plain number → treat as days
    return float(value)


def fetch_all_org_users(url, headers):
    get_users_url = url + "organization/member?limit=9999"
    response = rq.get(get_users_url, headers=headers)
    json_response = response.json()
    if response.status_code == 200:
        # Note that the return limit is set to 9999
        print("Total # of org users: ", json_response["count"])
        results = json_response["results"]
        org_members = {r["email"] for r in results}
        return org_members
    else:
        print(f"Failed to fetch org users. Status Code: {response.status_code}")
        return set()


def fetch_active_members(url, headers, days: float):
    """Return emails of users who have logged in within the last `days` days."""
    since_ts = int((datetime.now() - timedelta(days=days)).timestamp() * 1000)
    active_session_url = (
        url
        + "event/find?query=sf_eventType%3ASessionLog%20AND%20sessionType%3Auser"
        + "&start_time="
        + str(since_ts)
    )
    response = rq.get(active_session_url, headers=headers)
    json_response = response.json()
    if response.status_code == 200:
        active_members = set()
        for event in json_response:
            email = event.get("properties", {}).get("email")
            if email:
                active_members.add(email)
        return active_members
    else:
        print(f"Failed to fetch session events. Status Code: {response.status_code}")
        return set()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="List O11y Cloud users who have been active within a given time window.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Duration examples:
  --duration 1h          last 1 hour
  --duration 12h         last 12 hours
  --duration 1day        last 1 day
  --duration 7d          last 7 days
  --duration 1week       last 1 week
  --duration 1month      last 30 days
  --duration 3months     last 90 days
  --duration 1year       last 365 days
  --duration 60          plain number = days (default)
        """,
    )
    parser.add_argument("--realm",    required=False, help="O11y Cloud realm, e.g. us1")
    parser.add_argument("--token",    required=False, help="User API access token")
    parser.add_argument(
        "--duration",
        default="60d",
        help="Look-back window (default: 60d).  Accepts hours/days/weeks/months/years.",
    )
    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    realm = args.realm or input("Enter the realm: ").strip()
    token = args.token or input("Enter your user API access token for the org: ").strip()

    try:
        days = parse_duration(args.duration)
    except ValueError:
        parser.error(f"Cannot parse duration '{args.duration}'. See --help for examples.")

    url = f"https://api.{realm}.signalfx.com/v2/"
    headers = {
        "Content-Type": "application/json",
        "X-SF-TOKEN": token,
    }

    # Human-readable label for the window
    if days < 1:
        window_label = f"{int(days * 24)} hour(s)"
    elif days % 7 == 0 and days >= 7:
        window_label = f"{int(days // 7)} week(s)"
    elif days % 30 == 0 and days >= 30:
        window_label = f"{int(days // 30)} month(s)"
    else:
        window_label = f"{int(days)} day(s)"

    org_members = fetch_all_org_users(url, headers)
    active_members = fetch_active_members(url, headers, days=days)

    # Only count users who are both active AND current org members
    active_org_members = sorted(active_members & org_members)

    print(f"\nActive org users in the last {window_label}: {len(active_org_members)}")
    for email in active_org_members:
        print(email)


if __name__ == "__main__":
    main()
