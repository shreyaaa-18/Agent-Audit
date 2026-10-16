# tools.py

from .data import flights, blackout_dates, travelers


def search_flights(origin, destination, date):

    matches = []

    for flight_id, flight in flights.items():

        if (
            flight["origin"] == origin
            and flight["destination"] == destination
            and flight["date"] == date
        ):

            matches.append({
                "flight_id": flight_id,
                "airline": flight["airline"],
                "depart_time": flight["depart_time"],
                "base_fare": flight["base_fare"],
                "taxes": flight["taxes"]
            })

    if not matches:
        return {
            "found": False,
            "message": f"No flights found from {origin} to {destination} on {date}."
        }

    return {
        "found": True,
        "flights": matches
    }


def check_blackout_date(date):

    if date in blackout_dates:
        return {
            "is_blackout": True,
            "message": f"{date} falls within a company travel blackout period."
        }

    return {
        "is_blackout": False,
        "message": f"{date} is not a blackout date."
    }


def check_traveler_profile(employee_id):

    traveler = travelers.get(employee_id)

    if not traveler:
        return {
            "found": False,
            "message": f"Employee {employee_id} was not found."
        }

    return {
        "found": True,
        "employee_id": employee_id,
        "name": traveler["name"],
        "grade": traveler["grade"],
        "previous_bookings": traveler["previous_bookings"],
        "flagged": traveler["flagged"]
    }


def book_flight(flight_id):

    flight = flights.get(flight_id)

    if not flight:
        return {
            "success": False,
            "message": f"Flight {flight_id} was not found."
        }

    return {
        "success": True,
        "flight_id": flight_id,
        "message": f"Flight {flight_id} booked successfully."
    }
