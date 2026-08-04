class IntelligenceEngine:

    def evaluate(self, event, zone, duration, person_count):

        event_type = event.get("type", "UNKNOWN")

        if event_type in ("LOITERING", "FALL_DETECTED", "WEAPON_DETECTED", "ABANDONED_OBJECT"):

            return "HIGH"

        if zone == "RESTRICTED":

            return "HIGH"

        if duration > 30:

            return "MEDIUM"

        if person_count > 5:

            return "MEDIUM"

        return "LOW"


def analyze(event):

    event_type = event.get("type", "UNKNOWN")

    zone = event.get("zone", "Unknown")

    severity = event.get("severity", "LOW")

    summaries = {

        "LOITERING": {

            "summary":
            f"Person remained inside {zone} for an extended period.",

            "recommendation":
            "Dispatch nearby security personnel."

        },

        "FALL_DETECTED": {

            "summary":
            f"Possible fall detected inside {zone}.",

            "recommendation":
            "Medical assistance recommended."

        },

        "WEAPON_DETECTED": {

            "summary":
            f"Potential weapon detected in {zone}.",

            "recommendation":
            "Trigger emergency response immediately."

        },

        "ABANDONED_OBJECT": {

            "summary":
            f"Suspicious unattended object detected in {zone}.",

            "recommendation":
            "Inspect object and isolate the area."

        }

    }

    default = {

        "summary":
        "Unknown incident detected.",

        "recommendation":
        "Continue monitoring."

    }

    data = summaries.get(event_type, default)

    return {

        "event": event_type,

        "severity": severity,

        "summary": data["summary"],

        "recommendation": data["recommendation"]

    }