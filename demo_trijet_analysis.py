#!/usr/bin/env python3
"""
Demonstration script showing the trijet analysis functionality
with mock data (no ServiceX required).
"""

import numpy as np
import awkward as ak
import vector
import hist
import matplotlib.pyplot as plt
import mplhep

# Register vector behaviors
vector.register_awkward()

def create_mock_data(n_events=1000):
    """Create mock jet data that resembles real ATLAS data"""
    print("Creating mock jet data...")
    
    # Generate events with varying numbers of jets (3-6 jets per event)
    n_jets_per_event = np.random.choice([3, 4, 5, 6], size=n_events, p=[0.3, 0.4, 0.2, 0.1])
    
    # Create arrays for jet properties
    jet_pt_all = []
    jet_eta_all = []
    jet_phi_all = []
    jet_mass_all = []
    btag_disc_all = []
    
    for n_jets in n_jets_per_event:
        # Generate jet pT with realistic distribution (25-500 GeV)
        jet_pt = np.random.exponential(scale=80, size=n_jets) + 25
        jet_pt = np.clip(jet_pt, 25, 500)
        
        # Generate eta (pseudorapidity) within detector acceptance
        jet_eta = np.random.uniform(-2.5, 2.5, n_jets)
        
        # Generate phi (azimuthal angle)
        jet_phi = np.random.uniform(-np.pi, np.pi, n_jets)
        
        # Generate jet mass (mostly light jets, some heavier)
        jet_mass = np.random.exponential(scale=5, size=n_jets) + 0.5
        
        # Generate b-tag discriminant values (-1 to 1, with bias toward low values)
        btag_disc = np.random.beta(2, 5, n_jets) * 2 - 1
        
        jet_pt_all.append(jet_pt)
        jet_eta_all.append(jet_eta)
        jet_phi_all.append(jet_phi)
        jet_mass_all.append(jet_mass)
        btag_disc_all.append(btag_disc)
    
    # Convert to awkward arrays
    jets_data = {
        "jets": {
            "pt": ak.Array(jet_pt_all),
            "eta": ak.Array(jet_eta_all),
            "phi": ak.Array(jet_phi_all),
            "mass": ak.Array(jet_mass_all),
            "btag_disc": ak.Array(btag_disc_all)
        }
    }
    
    return jets_data

def analyze_mock_data():
    """Run the full analysis on mock data"""
    print("Running trijet analysis demonstration...")
    
    # Create mock data
    jets_data = create_mock_data(n_events=5000)
    
    # Convert to vector arrays
    print("Converting to vector arrays...")
    jets_vectors = ak.zip({
        "pt": jets_data["jets"]["pt"],
        "eta": jets_data["jets"]["eta"],
        "phi": jets_data["jets"]["phi"],
        "mass": jets_data["jets"]["mass"]
    }, with_name="Momentum4D")
    
    print(f"Processing {len(jets_vectors)} events")
    print(f"Average jets per event: {ak.mean(ak.num(jets_vectors, axis=1)):.1f}")
    
    # Get all possible 3-jet combinations per event
    print("Finding trijet combinations...")
    trijet_combinations = ak.combinations(jets_vectors, 3, axis=1)
    btag_combinations = ak.combinations(jets_data["jets"]["btag_disc"], 3, axis=1)
    
    # Unpack the combinations
    jet1, jet2, jet3 = ak.unzip(trijet_combinations)
    btag1, btag2, btag3 = ak.unzip(btag_combinations)
    
    # Calculate the invariant mass of each trijet combination
    trijet_4momentum = jet1 + jet2 + jet3
    trijet_mass = trijet_4momentum.mass
    trijet_pt = trijet_4momentum.pt
    
    # Find maximum b-tag discriminant for each combination
    max_btag_disc = ak.max(ak.concatenate([
        btag1[:, :, np.newaxis],
        btag2[:, :, np.newaxis], 
        btag3[:, :, np.newaxis]
    ], axis=2), axis=2)
    
    # Find the combination closest to 172.5 GeV (top mass)
    target_mass = 172.5  # GeV
    mass_diff = np.abs(trijet_mass - target_mass)
    
    # Get the index of the best combination per event
    best_combo_idx = ak.argmin(mass_diff, axis=1, keepdims=True)
    
    # Select the best combination's properties
    best_trijet_pt = ak.flatten(trijet_pt[best_combo_idx])
    best_max_disc = ak.flatten(max_btag_disc[best_combo_idx])
    best_trijet_mass = ak.flatten(trijet_mass[best_combo_idx])
    
    print(f"Selected {len(best_trijet_pt)} trijet combinations")
    print(f"Mean trijet pT: {np.mean(best_trijet_pt):.1f} GeV")
    print(f"Mean trijet mass: {np.mean(best_trijet_mass):.1f} GeV")
    print(f"Mean max b-tag discriminant: {np.mean(best_max_disc):.3f}")
    
    # Create histograms
    print("Creating histograms...")
    
    # pT histogram
    pt_hist = (
        hist.Hist.new
        .Reg(50, 0, 800, name="pt", label="Trijet $p_T$ [GeV]")
        .Weight()
    )
    
    # Discriminant histogram
    disc_hist = (
        hist.Hist.new
        .Reg(50, -1, 1, name="disc", label="Maximum b-tag discriminant")
        .Weight()
    )
    
    # Fill histograms
    pt_hist.fill(pt=best_trijet_pt)
    disc_hist.fill(disc=best_max_disc)
    
    # Plot and save
    print("Creating plots...")
    
    # Set ATLAS style
    plt.style.use(mplhep.style.ATLAS)
    
    # Plot pT histogram
    fig, ax = plt.subplots(figsize=(10, 8))
    pt_hist.plot(ax=ax, histtype="step", linewidth=2, color="blue")
    ax.set_xlabel("Trijet $p_T$ [GeV]")
    ax.set_ylabel("Events")
    ax.set_title("Trijet $p_T$ Distribution (Mock Data)")
    ax.grid(True, alpha=0.3)
    mplhep.atlas.label(ax=ax, loc=0, label="Internal")
    
    # Add statistics text
    stats_text = f"Entries: {len(best_trijet_pt)}\nMean: {np.mean(best_trijet_pt):.1f} GeV\nStd: {np.std(best_trijet_pt):.1f} GeV"
    ax.text(0.65, 0.95, stats_text, transform=ax.transAxes, verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    plt.tight_layout()
    plt.savefig("pt_trijet.png", dpi=300, bbox_inches="tight")
    plt.close()
    
    # Plot discriminant histogram
    fig, ax = plt.subplots(figsize=(10, 8))
    disc_hist.plot(ax=ax, histtype="step", linewidth=2, color="red")
    ax.set_xlabel("Maximum b-tag discriminant")
    ax.set_ylabel("Events")
    ax.set_title("Maximum b-tag Discriminant Distribution (Mock Data)")
    ax.grid(True, alpha=0.3)
    mplhep.atlas.label(ax=ax, loc=0, label="Internal")
    
    # Add statistics text
    stats_text = f"Entries: {len(best_max_disc)}\nMean: {np.mean(best_max_disc):.3f}\nStd: {np.std(best_max_disc):.3f}"
    ax.text(0.65, 0.95, stats_text, transform=ax.transAxes, verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    plt.tight_layout()
    plt.savefig("disc_trijet.png", dpi=300, bbox_inches="tight")
    plt.close()
    
    print("✓ Plots saved as 'pt_trijet.png' and 'disc_trijet.png'")
    print("Demonstration complete!")

if __name__ == "__main__":
    analyze_mock_data()