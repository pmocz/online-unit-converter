from flask import Flask, render_template, request
from astropy import units as u
from astropy.units import Quantity
from astropy.constants import (
    G,
    N_A,
    R,
    Ryd,
    a0,
    alpha,
    atm,
    c,
    e,
    eps0,
    g0,
    h,
    hbar,
    k_B,
    m_e,
    m_n,
    m_p,
    mu0,
    muB,
    sigma_T,
    sigma_sb,
    GM_earth,
    GM_jup,
    GM_sun,
    L_bol0,
    L_sun,
    M_earth,
    M_jup,
    M_sun,
    R_earth,
    R_jup,
    R_sun,
)
import re

#  G / (km/s)^2 * (mass of sun) / kpc


app = Flask(__name__)

UNIT_SYSTEMS = {
    "cgs": u.cgs,
    "SI": u.si,
}

# Map common names to astropy constants
CONSTANTS = {
    "G": G,
    "Gravitationalconstant": G,
    "gravitationalconstant": G,
    "newton'sconstant": G,
    "Newton'sconstant": G,
    "N_A": N_A,
    "Avogadro'snumber": N_A,
    "avogadro'snumber": N_A,
    "R": R,
    "Gasconstant": R,
    "gasconstant": R,
    "Ryd": Ryd,
    "Rydbergconstant": Ryd,
    "rydbergconstant": Ryd,
    "a0": a0,
    "Bohrradius": a0,
    "bohrradius": a0,
    "alpha": alpha,
    "Fine-structureconstant": alpha,
    "fine-structureconstant": alpha,
    "atm": atm,
    "Standardatmosphere": atm,
    "standardatmosphere": atm,
    "c": c,
    "Speedoflight": c,
    "speedoflight": c,
    "Electroncharge": e,
    "electroncharge": e,
    "eps0": eps0,
    "Vacuumelectricpermittivity": eps0,
    "vacuumelectricpermittivity": eps0,
    "g0": g0,
    "Standardgravity": g0,
    "standardgravity": g0,
    "h": h,
    "Planckconstant": h,
    "planckconstant": h,
    "hbar": hbar,
    "ReducedPlanckconstant": hbar,
    "Reducedplanckconstant": hbar,
    "reducedPlanckconstant": hbar,
    "reducedplanckconstant": hbar,
    "k_B": k_B,
    "Boltzmannconstant": k_B,
    "boltzmannconstant": k_B,
    "m_e": m_e,
    "Electronmass": m_e,
    "electronmass": m_e,
    "Massofelectron": m_e,
    "massofelectron": m_e,
    "m_n": m_n,
    "Neutronmass": m_n,
    "neutronmass": m_n,
    "Massofneutron": m_n,
    "massofneutron": m_n,
    "m_p": m_p,
    "Protonmass": m_p,
    "protonmass": m_p,
    "Massofproton": m_p,
    "massofproton": m_p,
    "mu0": mu0,
    "Vacuummagneticpermeability": mu0,
    "vacuummagneticpermeability": mu0,
    "muB": muB,
    "Bohrmagneton": muB,
    "bohrmagneton": muB,
    "sigma_T": sigma_T,
    "Thomsoncrosssection": sigma_T,
    "thomsoncrosssection": sigma_T,
    "sigma_sb": sigma_sb,
    "Stefan-Boltzmannconstant": sigma_sb,
    "stefan-boltzmannconstant": sigma_sb,
    "GM_earth": GM_earth,
    "GM_jup": GM_jup,
    "GM_sun": GM_sun,
    "L_bol0": L_bol0,
    "L_sun": L_sun,
    "Solarluminosity": L_sun,
    "luminosityofsun": L_sun,
    "Luminosityofsun": L_sun,
    "luminosityofsun": L_sun,
    "M_earth": M_earth,
    "massofearth": M_earth,
    "Massofearth": M_earth,
    "massofEarth": M_earth,
    "MassofEarth": M_earth,
    "Earthmass": M_earth,
    "earthmass": M_earth,
    "M_jup": M_jup,
    "massofjupiter": M_jup,
    "Massofjupiter": M_jup,
    "massofJupiter": M_jup,
    "MassofJupiter": M_jup,
    "Jupitermass": M_jup,
    "jupitermass": M_jup,
    "M_sun": M_sun,
    "massofsun": M_sun,
    "massofSun": M_sun,
    "Solarmass": M_sun,
    "solarmass": M_sun,
    "Msun": M_sun,
    "m_sun": M_sun,
    "msun": M_sun,
    "R_earth": R_earth,
    "Radiusofearth": R_earth,
    "radiusofearth": R_earth,
    "RadiusofEarth": R_earth,
    "radiusofEarth": R_earth,
    "Earthradius": R_earth,
    "earthradius": R_earth,
    "R_jup": R_jup,
    "Radiusofjupiter": R_jup,
    "radiusofjupiter": R_jup,
    "RadiusofJupiter": R_jup,
    "radiusofJupiter": R_jup,
    "Jupiterradius": R_jup,
    "jupiterradius": R_jup,
    "R_sun": R_sun,
    "Radiusofsun": R_sun,
    "radiusofsun": R_sun,
    "RadiusofSun": R_sun,
    "radiusofSun": R_sun,
    "Solarradius": R_sun,
    "solarradius": R_sun,
}


@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    error = None
    expr = ""
    system = "cgs"
    if request.method == "POST":
        expr = request.form.get("expression", "")
        system = request.form.get("system", "cgs")
        try:
            expr_mod = expr
            # replace ^ with **
            expr_mod = expr_mod.replace("^", "**")
            # remove spaces
            expr_mod = expr_mod.replace(" ", "")
            # is "e" is sandwiched by numbers, replace with "10**"
            expr_mod = re.sub(r"(\d+\.?d*)[eE]([+\-]?\d+)", r"\1*10**(\2)", expr_mod)
            # if a number is followed by a letter , insert *
            expr_mod = re.sub(r"(\d)([a-zA-Z(])", r"\1*\2", expr_mod)
            # if ) is followed by a letter , insert *
            expr_mod = re.sub(r"(\))([a-zA-Z(])", r"\1*\2", expr_mod)
            print(expr_mod)
            # Evaluate the expression safely
            qty = eval(expr_mod, {**u.__dict__, **CONSTANTS, "__builtins__": {}})
            # Convert to base units of selected system
            qty = Quantity(qty)  # (in case expression is just a number)
            converted = qty.decompose(bases=UNIT_SYSTEMS[system].bases)
            # result = f"{converted}"
            result = "".join(
                [
                    f"{base}^{power} "
                    for base, power in zip(converted.unit.bases, converted.unit.powers)
                ]
            )
            result = f"{converted.value} " + result.strip(" ")
        except Exception as e:
            error = str(e)
    return render_template(
        "index.html",
        result=result,
        error=error,
        expr=expr,
        system=system,
        systems=UNIT_SYSTEMS.keys(),
    )


if __name__ == "__main__":
    app.run(debug=True)
