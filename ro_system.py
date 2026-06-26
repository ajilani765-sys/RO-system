# ==========================================
# Reverse Osmosis Engineering Model
# Version 1.0
# ==========================================

import numpy as np
import matplotlib.pyplot as plt

# -------------------------
# Constants
# -------------------------

R = 8.314          # J/(mol·K) Ideal gas constant
T = 298.15         # Kelvin
i = 2              # Van't Hoff factor for NaCl

molar_mass = 58.44     # g/mol

# Literature value:
# 1–2 LMH/bar (Recent SWRO membranes) How RO membrane permeability and other performance factors affect process cost and energy use: A review
# Converted to SI:
# 2.78e-12 – 5.56e-12 m/(Pa·s)

membrane_permeability = 4.0e-12
membrane_area = 40                # m², industry standard
pump_efficiency = 0.85            # Industry standard for large scale plants
feed_flow_rate = 0.001   # m³/s (1 L/s)
feed_salinity = 35                # g/L
operating_pressure = 60           # bar
# Concentration Polarisation
cp_coefficient = 2000000     # s/m (tunable parameter)
# Membrane mechanical properties
membrane_thickness = 150e-6      # m (150 μm)
tensile_strength = 35e6          # Pa (35 MPa)
youngs_modulus = 120e6           # Pa (120 MPa)

def osmotic_pressure(salinity):
    """
    Calculates osmotic pressure from salinity.

    Parameters
    ----------
    salinity : float
        Feed salinity in g/L

    Returns
    -------
    float
        Osmotic pressure (Pa)
    """

    concentration = (salinity / molar_mass) * 1000    # mol/m³

    pi = i * concentration * R * T

    return pi



def water_flux(pressure_bar, osmotic_pressure_pa):
    """
    Calculates water flux including concentration polarisation.
    Returns water flux in m/s.
    """

    pressure_pa = pressure_bar * 1e5

    # Initial estimate (no CP)
    driving_pressure = pressure_pa - osmotic_pressure_pa

    if driving_pressure <= 0:
        return 0

    flux = membrane_permeability * driving_pressure

    # Fixed-point iteration
    for _ in range(10):

        effective_osmotic_pressure = osmotic_pressure_pa * (1 + cp_coefficient * flux)

        driving_pressure = pressure_pa - effective_osmotic_pressure

        if driving_pressure <= 0:
            return 0

        flux = membrane_permeability * driving_pressure

    return flux
print(water_flux(operating_pressure, osmotic_pressure(feed_salinity)))

pi = osmotic_pressure(feed_salinity)

flux = water_flux(operating_pressure, pi)

print(f"Osmotic pressure: {pi/1e5:.2f} bar")
print(f"Water flux: {flux:.3e} m/s")

pressures = np.linspace(20, 80, 100)

fluxes = []

pi = osmotic_pressure(feed_salinity)

for p in pressures:
    fluxes.append(water_flux(p, pi))

def freshwater_production(flux):
    """
    Calculates freshwater production.

    Parameters
    ----------
    flux : float
        Water flux (m/s)

    Returns
    -------
    float
        Freshwater production (m³/s)
    """

    return flux * membrane_area

pressures = np.linspace(20, 80, 100)

productions = []

pi = osmotic_pressure(feed_salinity)

for p in pressures:

    flux = water_flux(p, pi)

    production = freshwater_production(flux)

    productions.append(production)

#Pump power 

def pump_power(pressure_bar):
    """
    Calculates pump power.

    Parameters
    ----------
    pressure_bar : float
        Operating pressure in bar

    Returns
    -------
    float
        Pump power (W)
    """

    pressure_pa = pressure_bar * 1e5

    power = (feed_flow_rate * pressure_pa) / pump_efficiency

    return power


print("Pump power:", pump_power(operating_pressure), "W")

def specific_energy(power, production):
    """
    Calculates specific energy consumption.

    Returns kWh/m³.
    """

    if production == 0:
        return np.nan

    sec_j = power / production          # J/m³

    sec_kwh = sec_j / 3.6e6             # Convert J → kWh

    return sec_kwh


print("Specific energy consumption:", specific_energy(pump_power(operating_pressure), freshwater_production(flux)), "J/m³")

# Membrane Stress

def membrane_stress(pressure_bar):
    """
    Estimates membrane stress due to operating pressure.

    Returns
    -------
    float
        Stress (Pa)
    """

    pressure_pa = pressure_bar * 1e5

    # Simple approximation:
    stress = pressure_pa

    return stress

print("Membrane stress:", membrane_stress(operating_pressure), "Pa")

#Factor of Safety

def safety_factor(stress):
    """
    Calculates membrane safety factor.
    """

    return tensile_strength / stress

print("Safety factor:", safety_factor(membrane_stress(operating_pressure)))

# prepare lists for results
productions = []
powers = []
secs = []
stress_values = []
safety_factors = []

for p in pressures:
    flux = water_flux(p, pi)
    production = freshwater_production(flux)
    power = pump_power(p)
    sec = specific_energy(power, production)
    stress = membrane_stress(p)
    safety = safety_factor(stress)

    productions.append(production)
    powers.append(power)
    secs.append(sec)
    stress_values.append(stress / 1e6)  # convert to MPa for plotting
    safety_factors.append(safety)

#Graphs

fig, ax = plt.subplots(2, 2, figsize=(12, 10))
ax = ax.flatten()

# Freshwater Production
ax[0].plot(pressures, productions)
ax[0].set_xlabel("Operating Pressure (bar)")
ax[0].set_ylabel("Freshwater Production (m³/s)")
ax[0].set_title("Freshwater Production vs Pressure")
ax[0].grid(True)

# Specific Energy Consumption
ax[1].plot(pressures, secs)
ax[1].set_xlabel("Operating Pressure (bar)")
ax[1].set_ylabel("Specific Energy (kWh/m³)")
ax[1].set_title("Specific Energy Consumption vs Pressure")
ax[1].grid(True)
ax[1].set_xlim(30, 80)
ax[1].set_ylim(0, 50)

# Membrane Stress
ax[2].plot(pressures, stress_values)
ax[2].set_xlabel("Operating Pressure (bar)")
ax[2].set_ylabel("Stress (MPa)")
ax[2].set_title("Membrane Stress vs Pressure")
ax[2].grid(True)

# Safety Factor
ax[3].plot(pressures, safety_factors)
ax[3].set_xlabel("Operating Pressure (bar)")
ax[3].set_ylabel("Safety Factor")
ax[3].set_title("Safety Factor vs Pressure")
ax[3].grid(True)

plt.tight_layout()
plt.show()

# End of script