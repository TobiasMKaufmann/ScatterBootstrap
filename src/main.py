"""
This file was used for testing purposes.
"""

from core_shell_cylinder.wrapper import compute_form_factor
from core_shell_cylinder.hayter_msa_wrapper import compute_structure_factor
import matplotlib.pyplot as plt
import numpy as np

# Define global parameters for the core_shell_cylinder model  
q = 0.5  # scattering vector
core_sld = 7.7  # core scattering length density
shell_sld = 10.989  # shell scattering length density
solvent_sld = 9.4  # solvent scattering length density

radius = 13.84  # core radius
thickness = 6.60  # shell thickness
length = 35.21 # length of the cylinder

# Define global parameters for the Hayter-MSA structure factor
radius_effective = 24.8  # effective radius (Å)
vol_frac = 0.16363  # volume fraction (dimensionless)
zz = 28.288  # particle charge (elementary charges)
temp = 300  # temperature (K)
csalt = 0.093723  # salt concentration (M)
dialec = 78.3  # dielectric constant for water (dimensionless)

def main():
    F1, F2 = compute_form_factor(q, core_sld, shell_sld, solvent_sld, radius, thickness, length)
    
    S_q = compute_structure_factor(q, radius_effective, vol_frac, zz, temp, csalt, dialec)
    
    # Using F2 which is the integrated |F(q)|^2 value:
    I_q = F2 * S_q
    
    print(f"Form Factor F2: {F2}")
    print(f"Structure Factor S(q): {S_q}")
    print(f"Total Scattering Intensity I(q) = F²(q) × S(q): {I_q}")

def plot_scattering():
    q_values = np.logspace(-2, 0, 100)
    F2_values = []
    S_values = []
    I_values = []

    for q in q_values:
        _, F2 = compute_form_factor(q, core_sld, shell_sld, solvent_sld, radius, thickness, length)
        S_q = compute_structure_factor(q, radius_effective, vol_frac, zz, temp, csalt, dialec)
        I_q = F2 * S_q
        
        F2_values.append(F2)
        S_values.append(S_q)
        I_values.append(I_q)

    plt.figure(figsize=(12, 8))
    
    plt.subplot(2, 2, 1)
    plt.loglog(q_values, F2_values, 'b-', label=r'Form Factor $F^2(q)$', linewidth=2)
    plt.xlabel(r'Scattering Vector $q$ (Å$^{-1})$')
    plt.ylabel(r'Form Factor $F^2(q)$')
    plt.title(r'Form Factor $F^2(q)$')
    plt.grid(True, which="both", linestyle="--", linewidth=0.5)
    plt.legend()
    
    plt.subplot(2, 2, 2)
    plt.loglog(q_values, S_values, 'r-', label=r'Structure Factor $S(q)$', linewidth=2)
    plt.xlabel(r'Scattering Vector $q$ (Å$^{-1})$')
    plt.ylabel(r'Structure Factor $S(q)$')
    plt.title(r'Structure Factor $S(q)$')
    plt.grid(True, which="both", linestyle="--", linewidth=0.5)
    plt.legend()
    
    plt.subplot(2, 2, 3)
    plt.loglog(q_values, I_values, 'g-', label=r'Total Intensity $I(q) = F^2(q) S(q)$', linewidth=2)
    plt.xlabel(r'Scattering Vector $q$ (Å$^{-1})$')
    plt.ylabel(r'Scattering Intensity $I(q)$')
    plt.title(r'Total Scattering Intensity $I(q)$')
    plt.grid(True, which="both", linestyle="--", linewidth=0.5)
    plt.legend()
    
    plt.subplot(2, 2, 4)
    plt.loglog(q_values, F2_values, 'b-', label=r'Form Factor $F^2(q)$', linewidth=2, alpha=0.7)
    plt.loglog(q_values, S_values, 'r-', label=r'Structure Factor $S(q)$', linewidth=2, alpha=0.7)
    plt.loglog(q_values, I_values, 'g-', label=r'Total Intensity $I(q)$', linewidth=2)
    plt.xlabel(r'Scattering Vector $q$ (Å$^{-1})$')
    plt.ylabel('Intensity')
    plt.title('Combined Plot')
    plt.grid(True, which="both", linestyle="--", linewidth=0.5)
    plt.legend()
    
    plt.tight_layout()
    plt.savefig("scattering_analysis.png", dpi=150)
    print("Combined scattering analysis plot saved as 'scattering_analysis.png'")

if __name__ == "__main__":
    main()
    plot_scattering()