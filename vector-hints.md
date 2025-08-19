# Scikit-HEP Vector Library – Complex Usage Snippets

The **vector** library allows you to do 4-vector operations, transformation, calculations (like `deltaR`) easily and efficiently. For these operations do not write your own code - instead create an awkward array with the appropriate vector behavior, and then use the `vector` methods to do the calculation.

## Registering Awkward Behavior for Vector

Use `vector.register_awkward()` to load Vector’s Awkward Array behaviors so that any Awkward records named `"Vector2D"`, `"Vector3D"`, `"Vector4D"`, or `"Momentum4D"` (etc.) with recognized field names get Vector properties and methods. This should be done at the start of your session/script.

```python
import awkward as ak
import vector
vector.register_awkward()  # Enable Vector methods on Awkward arrays:contentReference[oaicite:2]{index=2}
```

## Creating an Awkward Array of Lorentz Vectors and Spacial Vectors

To construct an Awkward Array of Lorentz vectors, create records with standard field names (e.g. `pt`, `eta`, `phi`, `mass`) and assign a vector type name (e.g. `"Momentum4D"`). For example, here we build a Momentum4D array from Python lists of components:

```python
# Assuming vector.register_awkward() has been called
events = ak.Array({ 
    "electron": ak.zip({
        "pt":  [50.0, 30.2], 
        "eta": [1.4, -0.8], 
        "phi": [2.1, 0.5], 
        "mass": [0.0005, 0.0005]
    }, with_name="Momentum4D")  # tell this array to behave as a 4D vector
})
# 'events["electron"]' is now an array of Momentum4D vectors with pt, eta, phi, mass:contentReference[oaicite:4]{index=4}
```

Use the `3D` spatial vector (`Momentum3D`) if you only need 3-vector operations (e.g. `deltaR`), and `4D` Lorentz vectors (`Momentum4D`) if you need to calculate something like an invariant mass.

## Accessing Vector Components and Properties

Once the vector Awkward Array is created, you can use physical property names to access computed components. For instance, given `particles = ak.zip({"px": ..., "py": ..., "pz": ..., "E": ...}, with_name="Vector4D")`, you could retrieve cylindrical or spherical coordinates:

```python
particles.pt    # transverse momentum (alias for rho in XY-plane)
particles.phi   # azimuthal angle in radians
particles.eta   # pseudorapidity = -ln[tan(theta/2)]
particles.mass  # invariant mass (for Momentum4D, alias for proper time tau)
```

## Calculating ΔR between Two Collections of Particles

The Vector library provides a `deltaR` method to compute the separation \$\Delta R = \sqrt{\Delta\phi^2 + \Delta\eta^2}\$ between two vectors. For example, to calculate ΔR between every electron and muon in the same event (assuming `events.electron` and `events.muon` are Momentum4D Awkward arrays), first form all pair combinations with `ak.cartesian`, then call `deltaR`:

```python
# events.electron and events.muon are both awkward arrays with the `Momentum3D` behavior.
pairs = ak.cartesian([events.electron, events.muon])       # all electron-muon pairs per event
electrons, muons = ak.unzip(pairs)
dR = electrons.deltaR(muons)  # ΔR for each electron-muon pair:contentReference[oaicite:7]{index=7}
```

Each entry in `dR` is an array of ΔR values for the corresponding event’s electron–muon pairs.

The `.deltaR` can only be applied to awkward arrays behaving as 3D or 4D vectors!!

## Combining Lorentz Vectors and Invariant Mass

You can add two Lorentz vectors (Momentum4D) to get their combined 4-vector, then access its `.mass` property for the invariant mass. For instance, to get all unique dielectron masses in each event:

```python
first_e, second_e = ak.unzip(ak.combinations(events.electron, 2))  # unique e⁺e⁻ pairs per event
inv_mass = (first_e + second_e).mass  # invariant mass of each pair:contentReference[oaicite:9]{index=9}
```

Here `first_e + second_e` produces a Momentum4D sum for each pair, and `.mass` gives the invariant mass of that pair.

## Boosting Lorentz Vectors to a Different Frame

The `boostCM_of_p4` method boosts a Lorentz vector to the center-of-mass frame of a given 4-vector. For example, to boost two decay products into their parent’s rest frame, first sum them to get the parent momentum, then boost each:

```python
parent = particle1 + particle2
particle1_rf = particle1.boostCM_of_p4(parent)  # boost particle1 to parent’s rest frame:contentReference[oaicite:11]{index=11}
particle2_rf = particle2.boostCM_of_p4(parent)  # boost particle2 to parent’s rest frame
```

After this operation, `particle1_rf` and `particle2_rf` are in the parent’s center-of-mass frame (their combined spatial momentum is \~0, and the parent’s energy is now split between them).

## Other methods

Vector has a lot of other methods you can call

* `cross` - takes the cross product of two arrays of vectors
