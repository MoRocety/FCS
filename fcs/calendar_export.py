"""RFC 5545 weekly calendar export using explicit student-supplied dates."""

import hashlib
from datetime import date, datetime, time, timedelta, timezone


def calendar_text(sections, start, end):
    try:
        start, end = date.fromisoformat(start), date.fromisoformat(end)
    except (ValueError, TypeError):
        raise ValueError("Choose valid semester start and end dates")
    if not 0 <= (end - start).days <= 366:
        raise ValueError("The semester must end after it starts, within one year")

    def escape(value):
        return (
            str(value)
            .replace("\\", "\\\\")
            .replace("\r", "")
            .replace("\n", "\\n")
            .replace(";", "\\;")
            .replace(",", "\\,")
        )

    until = (
        datetime.combine(
            end, time(23, 59, 59), timezone(timedelta(hours=5))
        ).astimezone(timezone.utc)
    ).strftime("%Y%m%dT%H%M%SZ")
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//FCS//Course Planner//EN",
        "CALSCALE:GREGORIAN",
        "BEGIN:VTIMEZONE",
        "TZID:Asia/Karachi",
        "BEGIN:STANDARD",
        "DTSTART:19700101T000000",
        "TZOFFSETFROM:+0500",
        "TZOFFSETTO:+0500",
        "TZNAME:PKT",
        "END:STANDARD",
        "END:VTIMEZONE",
    ]
    for section in sections:
        for index, meeting in enumerate(section["meetings"]):
            for day in meeting["days"]:
                weekday = "MTWRFSU".index(day)
                first = start + timedelta(days=(weekday - start.weekday()) % 7)
                if first > end:
                    continue
                uid = hashlib.sha256(
                    f"{section['id']}:{index}:{day}:{start}".encode()
                ).hexdigest()[:32]
                lines.extend(
                    [
                        "BEGIN:VEVENT",
                        f"UID:{uid}@fcs",
                        f"DTSTAMP:{stamp}",
                        f"DTSTART;TZID=Asia/Karachi:{first.strftime('%Y%m%d')}T{meeting['start'].replace(':','')}00",
                        f"DTEND;TZID=Asia/Karachi:{first.strftime('%Y%m%d')}T{meeting['end'].replace(':','')}00",
                        f"RRULE:FREQ=WEEKLY;UNTIL={until}",
                        f"SUMMARY:{escape(section['department']+' '+section['number']+' / '+section['section']+' · '+section['name'])}",
                        f"LOCATION:{escape(meeting['room'])}",
                        f"DESCRIPTION:{escape(section['instructor'])}",
                        "END:VEVENT",
                    ]
                )
    lines.append("END:VCALENDAR")
    # Fold by bytes, without splitting a UTF-8 character.
    folded = []
    for line in lines:
        part = ""
        for character in line:
            if len((part + character).encode("utf-8")) > 73:
                folded.append(part)
                part = " " + character
            else:
                part += character
        folded.append(part)
    return "\r\n".join(folded) + "\r\n"
