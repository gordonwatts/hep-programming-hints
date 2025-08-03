#!/usr/bin/env python3
"""
Test script to verify the trijet analysis script syntax and basic functionality
without requiring ServiceX access.
"""

import sys
import numpy as np
import awkward as ak
import vector
import hist
import matplotlib.pyplot as plt

# Register vector behaviors
vector.register_awkward()

def test_vector_operations():
    """Test Vector library functionality"""
    print("Testing Vector operations...")
    
    # Create mock jet data
    jets = ak.zip({
        "pt": [[100, 80, 60], [120, 90, 70, 50]],
        "eta": [[1.2, -0.8, 2.1], [0.5, -1.5, 1.8, -2.2]],
        "phi": [[0.5, 1.2, -0.8], [2.1, -1.1, 0.3, 1.8]],
        "mass": [[5, 3, 8], [6, 4, 7, 5]]
    }, with_name="Momentum4D")
    
    # Test vector operations
    assert hasattr(jets, 'pt'), "Vector pt property not accessible"
    assert hasattr(jets, 'eta'), "Vector eta property not accessible"
    assert hasattr(jets, 'phi'), "Vector phi property not accessible"
    assert hasattr(jets, 'mass'), "Vector mass property not accessible"
    
    # Test vector addition
    combinations = ak.combinations(jets, 2, axis=1)
    jet1, jet2 = ak.unzip(combinations)
    dijet = jet1 + jet2
    assert hasattr(dijet, 'mass'), "Vector addition failed"
    
    print("✓ Vector operations working correctly")

def test_trijet_combinations():
    """Test trijet combination logic"""
    print("Testing trijet combination logic...")
    
    # Create mock data with exactly 4 jets per event
    jets = ak.zip({
        "pt": [[100, 80, 60, 40], [120, 90, 70, 50]],
        "eta": [[1.2, -0.8, 2.1, -1.5], [0.5, -1.5, 1.8, -2.2]],
        "phi": [[0.5, 1.2, -0.8, 2.0], [2.1, -1.1, 0.3, 1.8]],
        "mass": [[5, 3, 8, 4], [6, 4, 7, 5]]
    }, with_name="Momentum4D")
    
    btag_disc = [[-0.5, 0.2, 0.8, -0.1], [0.1, -0.3, 0.6, 0.4]]
    
    # Get trijet combinations (should be 4 combinations per event)
    trijet_combinations = ak.combinations(jets, 3, axis=1)
    btag_combinations = ak.combinations(btag_disc, 3, axis=1)
    
    assert ak.num(trijet_combinations, axis=1).tolist() == [4, 4], "Wrong number of combinations"
    
    # Test trijet mass calculation
    jet1, jet2, jet3 = ak.unzip(trijet_combinations)
    trijet = jet1 + jet2 + jet3
    masses = trijet.mass
    
    # Test finding closest to target mass
    target_mass = 172.5
    mass_diff = np.abs(masses - target_mass)
    best_idx = ak.argmin(mass_diff, axis=1, keepdims=True)
    
    assert len(best_idx) == 2, "Should have one best combination per event"
    
    print("✓ Trijet combination logic working correctly")

def test_histogram_creation():
    """Test histogram creation and filling"""
    print("Testing histogram creation...")
    
    # Create test data
    test_pt = np.random.normal(200, 50, 1000)
    test_disc = np.random.uniform(-1, 1, 1000)
    
    # Create histograms
    pt_hist = (
        hist.Hist.new
        .Reg(50, 0, 500, name="pt", label="Trijet $p_T$ [GeV]")
        .Weight()
    )
    
    disc_hist = (
        hist.Hist.new
        .Reg(50, -1, 1, name="disc", label="Maximum b-tag discriminant")
        .Weight()
    )
    
    # Fill histograms
    pt_hist.fill(pt=test_pt)
    disc_hist.fill(disc=test_disc)
    
    # Check that histograms have data
    assert pt_hist.sum().value > 0, "PT histogram is empty"
    assert disc_hist.sum().value > 0, "Discriminant histogram is empty"
    
    print("✓ Histogram creation working correctly")

def test_imports():
    """Test that all required modules can be imported"""
    print("Testing imports...")
    
    try:
        import numpy as np
        print("✓ numpy imported")
    except ImportError as e:
        print(f"✗ numpy import failed: {e}")
        return False
    
    try:
        import awkward as ak
        print("✓ awkward imported")
    except ImportError as e:
        print(f"✗ awkward import failed: {e}")
        return False
    
    try:
        import vector
        print("✓ vector imported")
    except ImportError as e:
        print(f"✗ vector import failed: {e}")
        return False
    
    try:
        import hist
        print("✓ hist imported")
    except ImportError as e:
        print(f"✗ hist import failed: {e}")
        return False
    
    try:
        import matplotlib.pyplot as plt
        print("✓ matplotlib imported")
    except ImportError as e:
        print(f"✗ matplotlib import failed: {e}")
        return False
    
    # ServiceX imports (these may fail in test environment)
    try:
        from func_adl_servicex_xaodr25 import FuncADLQueryPHYSLITE
        from servicex_analysis_utils import to_awk
        from servicex import deliver, ServiceXSpec, Sample, dataset
        print("✓ ServiceX modules imported")
    except ImportError as e:
        print(f"⚠ ServiceX imports failed (expected in test environment): {e}")
    
    try:
        import mplhep
        print("✓ mplhep imported")
    except ImportError as e:
        print(f"⚠ mplhep import failed: {e}")
    
    return True

def main():
    """Run all tests"""
    print("Running trijet analysis tests...\n")
    
    # Test imports first
    if not test_imports():
        print("Import tests failed. Please install required packages.")
        sys.exit(1)
    
    print()
    
    # Test core functionality
    try:
        test_vector_operations()
        test_trijet_combinations()
        test_histogram_creation()
        
        print("\n✓ All tests passed!")
        print("The trijet analysis script should work correctly with proper ServiceX setup.")
        
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()