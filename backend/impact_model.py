import json
import math
import datetime
import numpy as np

# --- Constants based on NASA data and common scientific assumptions ---
# Density of a stony asteroid in kg/m^3
ASTEROID_DENSITY_KGM3 = 3500
# Conversion factor for Joules to Megatons of TNT
JOULES_PER_MEGATON_TNT = 4.184e15

def get_severity_details(energy_mt):
    """
    Determines the severity band, color, and recommended actions based on impact energy.
    Thresholds are based on well-known impact events (e.g., Chelyabinsk, Tunguska).
    """
    if energy_mt < 0.1: # Smaller than most notable airbursts
        return {
            "band": "Local Event",
            "color": "green",
            "actions": ["Monitor official news.", "No immediate public action required."]
        }
    elif energy_mt < 10: # Chelyabinsk was ~0.5 Mt
        return {
            "band": "City Level Event",
            "color": "yellow",
            "actions": ["Shelter away from windows.", "Expect shockwave.", "Follow local authority instructions."]
        }
    elif energy_mt < 1000: # Tunguska was ~10-15 Mt
        return {
            "band": "Regional Threat",
            "color": "red",
            "actions": ["Evacuate within precaution radius immediately.", "Seek high ground if in coastal area."]
        }
    else: # Dinosaur-level event
        return {
            "band": "Global Event",
            "color": "black",
            "actions": ["This is a globally significant event.", "Follow national emergency broadcast instructions."]
        }

def calculate_impact_effects(
    diameter_m,
    impact_speed_m_s,
    impact_angle_deg,
    lat,
    lon,
    impact_body="Earth",
    impact_in_water=False
):
    """
    Main function to calculate the effects of an asteroid impact.
    Takes UI inputs and returns a structured JSON object for the frontend.
    """
    # --- 1. Initial Check ---
    if impact_body != "Earth":
        return {
            "impact_body": impact_body,
            "notes": "No direct effect on Earth expected."
        }

    # --- 2. Energy Calculation ---
    # Mass = Volume * Density. Volume of a sphere = 4/3 * pi * r^3
    radius_m = diameter_m / 2
    volume_m3 = (4/3) * math.pi * (radius_m ** 3)
    mass_kg = ASTEROID_DENSITY_KGM3 * volume_m3

    # Kinetic Energy = 1/2 * mass * velocity^2
    kinetic_energy_J = 0.5 * mass_kg * (impact_speed_m_s ** 2)
    impact_energy_Mt = kinetic_energy_J / JOULES_PER_MEGATON_TNT

    # --- 3. Severity Classification ---
    severity = get_severity_details(impact_energy_Mt)

    # --- 4. Crater and Zone Calculations ---
    # Base crater diameter calculation using scaling law
    base_crater_diameter_m = 90 * (impact_energy_Mt ** (1/3))

    # Adjust crater shape for impact angle. A shallow angle creates an elongated crater.
    # We use numpy.sin and numpy.radians for trigonometric functions.
    impact_angle_rad = np.radians(impact_angle_deg)
    # The long axis of the oval crater increases as the angle gets shallower
    crater_long_axis_m = base_crater_diameter_m / np.sin(impact_angle_rad)
    crater_short_axis_m = base_crater_diameter_m

    # Precaution radius is based on the largest dimension of the crater
    precaution_radius_km = (3 * crater_long_axis_m) / 1000

    # --- 5. Shockwave Calculation ---
    is_airburst_risk = 0.1 <= impact_energy_Mt < 1000
    shockwave_damage_radius_km = 0
    if is_airburst_risk:
        # Simplified scaling law for shockwave damage radius
        shockwave_damage_radius_km = 30 * (impact_energy_Mt ** (1/3))

    # --- 6. Tsunami Risk ---
    tsunami_risk = impact_in_water and impact_energy_Mt > 1

    # --- 7. Assemble the Final JSON Output ---
    output = {
        "impact_body": "Earth",
        "impact_coords": {"lat": lat, "lon": lon},
        "impact_in_water": impact_in_water,
        "impact_energy_J": kinetic_energy_J,
        "impact_energy_Mt": impact_energy_Mt,
        "crater_details": {
            "shape": "oval" if impact_angle_deg < 80 else "circular",
            "long_axis_m_est": crater_long_axis_m,
            "short_axis_m_est": crater_short_axis_m
        },
        "precaution_radius_km_est": precaution_radius_km,
        "severity_band": severity["band"],
        "severity_color": severity["color"],
        "shockwave_effects": {
            "is_airburst_risk": is_airburst_risk,
            "damage_radius_km_est": shockwave_damage_radius_km,
            "description": "Widespread window breakage expected. Risk of injury from flying glass." if is_airburst_risk else "Negligible atmospheric shockwave effects."
        },
        "tsunami_risk": tsunami_risk,
        "recommended_actions": severity["actions"],
        "confidence_pct": 75, # Fixed confidence for prototype
        "notes": "Prototype estimate based on simplified models. Not for official use.",
        "timestamp_utc": datetime.datetime.utcnow().isoformat() + "Z"
    }

    return output

# --- This block allows you to test the script directly ---
if __name__ == "__main__":
    # Simulate a Chelyabinsk-like event
    print("--- Simulating a City Level Event ---")
    test_inputs = {
        "diameter_m": 20,
        "impact_speed_m_s": 20000,
        "impact_angle_deg": 45,
        "lat": 55.15,
        "lon": 61.40,
        "impact_in_water": False
    }
    
    results = calculate_impact_effects(**test_inputs)
    
    # Print the results as a nicely formatted JSON string
    print(json.dumps(results, indent=4))
