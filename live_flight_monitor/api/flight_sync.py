import frappe
import requests

def sync_flight_statuses():
    api_key = frappe.db.get_single_value("Flight Settings", "api_key")
    if not api_key:
        frappe.log_error("API key not set in Flight Settings", "Flight Sync Error")
        return

    url = f"http://api.aviationstack.com/v1/flights?access_key={api_key}"
    response = requests.get(url)

    if response.status_code != 200:
        frappe.log_error(response.text, "Flight API Error")
        return

    data = response.json().get("data", [])

    for flight in data:
        update_or_insert_flight(flight)

def update_or_insert_flight(flight):
    try:
        doc = frappe.new_doc("Flight")
        doc.flight_number = flight.get("flight", {}).get("iata")
        doc.status = flight.get("flight_status")
        doc.departure_airport = flight.get("departure", {}).get("airport")
        doc.arrival_airport = flight.get("arrival", {}).get("airport")
        doc.airline = flight.get("airline", {}).get("name")
        doc.timestamp = frappe.utils.now()
        doc.insert(ignore_permissions=True)
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Insert Flight Error")
