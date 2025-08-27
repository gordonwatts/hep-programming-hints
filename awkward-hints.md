# Awkward Array 2.0 Complex Operation Snippets

This document provides **code snippets** demonstrating complex operations using the Awkward Array 2.x library, with applications to typical High Energy Physics (HEP) analysis tasks. Each snippet is preceded by a short comment describing the operation, followed by a Python code example. These examples cover advanced usage patterns (beyond trivial array creation or slicing) to help an LLM or developer compose solutions to real-world problems. The Awkward Array library is typically used alongside NumPy and integrates with tools like the **Vector** library for physics vectors, as shown below.

As a general theme - it is always better to filter data early rather than wait until the last minute. The sooner you can apply a cut, the smaller the data you have to work with downstream, and the more can fit into core memory.

## Flattening Nested Arrays

Use **`ak.flatten`** to reduce nested list structure. By default, `ak.flatten(array)` removes one level of nesting (flattens along the axis=1). Setting `axis=None` will completely flatten an array, erasing all nesting (turning it into 1D):

```python
import awkward as ak

array = ak.Array([[0, 1, 2], [], [3, 4], [5, 6, 7]])
flat_level1 = ak.flatten(array, axis=1)          # Flatten one level (axis=1 by default):contentReference[oaicite:2]{index=2}
flat_all   = ak.flatten(array, axis=None)  # Flatten all levels into 1D:contentReference[oaicite:3]{index=3}

print(flat_level1)  # [0, 1, 2, 3, 4, 5, 6, 7]
print(flat_all)     # [0, 1, 2, 3, 4, 5, 6, 7]  (same here because only one level)
```

Notes:

- Always explicitly set the `axis` in the arguments to `flatten`. This will force us to think about what axis we are flattening and if the data has that access.
- If a variable has no array structure or is a 1D array, then `ak.flatten` will cause an error. Be sure your data has the requested `axis` if you are going to flatten.

## Combining Multiple Fields into Records

Use **`ak.zip`** to join parallel arrays into an array of records (structured data). The `ak.zip` function can combine arrays of equal length into one record per entry. For example, zipping an age array and a name array yields an array of records with fields `"age"` and `"name"`:

```python
import awkward as ak

ages = ak.Array([18, 32, 41])
names = ak.Array(["Dorit", "Caitlin", "Bryn"])
people = ak.zip({"age": ages, "name": names})   # Combine fields into records:contentReference[oaicite:5]{index=5}

print(ak.to_list(people))
# Output: [{'age': 18, 'name': 'Dorit'}, {'age': 32, 'name': 'Caitlin'}, {'age': 41, 'name': 'Bryn'}]:contentReference[oaicite:6]{index=6}
```

If the arrays are nested (jagged), `ak.zip` will create nested records correspondingly. You can also unzip a record array back into separate arrays of fields using `ak.unzip` (which returns a tuple of arrays for each field).

## Filtering Data by Value

Awkward Arrays support NumPy-like boolean filtering. You can create a mask with a condition and use it to select elements. For example, given a nested array of numbers, `array[array > 4]` will produce a new array with only the values greater than 4, preserving the nested structure (sublists where no element meets the condition become empty):

```python
import awkward as ak

array = ak.Array([[0, 1.1, 2.2], [3.3, 4.4], [], [5.5, 6.6, 7.7, 8.8]])
result = array[array > 4]

print(ak.to_list(result))
# Output: [[[], [4.4]], [], [], [[5.5, 6.6, 7.7, 8.8]]]  (only values >4 kept, others dropped):contentReference[oaicite:9]{index=9}
```

Filtering only works as long as the structure of the mask and the item you are masking are similar. For example:

```python
array = ak.Array([[0, 1.1, 2.2], [3.3, 4.4], [], [5.5, 6.6, 7.7, 8.8]])
result = array[array > 4]
extra_filtered_result = result[result > 5] # works
extra_filtered_result = array[result > 5] # fails with mismatched and misaligned errors!!
extra_filtered_result = result[array > 5] # Also fails with mismatched and misaligned errors!!

## Filtering by Counts (e.g. Require N Elements in Sublist)

It’s common in HEP analysis to require that an event (represented as a list) has a certain number of objects. Use **`ak.num`** to count the length of each sublist (at a given axis) and build a mask from that. For example, to select only those sublists of length 2:

```python
import awkward as ak

events = ak.Array([[1, 2, 3], [], [4, 5], [6, 7]])  # e.g. events with variable counts of objects
mask = ak.num(events, axis=1) == 2                  # True for sublists with length == 2:contentReference[oaicite:11]{index=11}
selected = events[mask]                             # filter events by the mask

print(ak.to_list(selected))
# Output: [[4, 5]]  (only the third sublist [4,5] had length 2):contentReference[oaicite:12]{index=12}
```

Here `ak.num(events, axis=1)` returns `[3, 0, 2, 2]` (the number of items in each sublist), and we then filter for equals 2.

Always be explicit about the `axis` argument in `ak.num`, never rely on the default.

## Sorting Elements in Each Sublist

To sort the items within each nested list, use **`ak.sort`**. By default `ak.sort(array)` sorts along the last axis (`axis=-1`, i.e. within each sublist). For example:

```python
import awkward as ak

array = ak.Array([[7, 5, 7], [], [2], [8, 2]])
sorted_array = ak.sort(array)  # Sort each sublist in ascending order:contentReference[oaicite:16]{index=16}

print(ak.to_list(sorted_array))
# Output: [[5, 7, 7], [], [2], [2, 8]]:contentReference[oaicite:17]{index=17}
```

You can specify `ascending=False` to sort in descending order, or provide an `axis` if you need to sort at a higher level of nesting.

## Filtering sublists with `argmin` and `argmax` and friends

Since `axis=0` is event lists, we often want to operated on the jagged arrays, e.g., `axis=1`. `argmin` and `argmax` are great for this, for example, when looking for two objects close to each other. However, `argmin` and `argmax` don't operate on `axis=1` (or deeper) the same way as `np.argmin` and `np.argmax` - and nor does the slicing, so we must be deliberate when using `argmin` and friends.

Instead, we need to use lists. For example:

```python
import awkward as ak

array = ak.Array([[7, 5, 7], [], [2], [8, 2]])
max_values = ak.argmax(array, axis=1, keepdims=True)
print(max_values) # prints out "[[0], [None], [0], [0]]"
print(array[max_values]) # prints out "[[7], [None], [2], [8]]"
print(ak.flatten(array[max_values])) # prints out "[7, None, 2, 8]"
```

Note the `keepdims=True` - that makes sure you get that nested list, "[[0], [None], [0], [0]]", which can be correctly used for slicing.

Once you do the filtering (`array[max_values]`), if you want a list of the values, you must:

- Use `ak.flatten` to undo the downlevel caused by `keepdims=True`, or
- Use `ak.first` to pick out the first in the sub list.

Either of these will give you "[7, None, 2, 8]" in this example. But you *have* to do this for every item filtered by `max_values` - any filtering using `argmin` and friends. Note this trick is not necessary when filtering by values as describe in the above section.

## Reducing Values in Nested Arrays (Sum, etc.)

Awkward Array supports reductions (like sum, min, max, etc.) over specified axes. For example, **`ak.sum`** can sum numbers across different dimensions:

- **Sum within each sublist:** Use `axis=1` (or `axis=-1` for the innermost axis) to sum each list of values independently.
- **Sum across outer lists:** Use `axis=0` to sum element-wise across the outermost dimension.
- **Total sum:** Use `axis=None` (or omit `axis`) to sum all elements into one scalar.

```python
import awkward as ak

arr = ak.Array([[1, 2, 3], [4, 5], [6]]) 
sum_per_list = ak.sum(arr, axis=1)   # sum of each sub-list (inner list):contentReference[oaicite:22]{index=22}
total_sum   = ak.sum(arr)            # sum of all values (axis=None combines everything):contentReference[oaicite:23]{index=23}

print(ak.to_list(sum_per_list))  # [6, 9, 6]  (e.g., 1+2+3 = 6, 4+5 = 9, 6 = 6)
print(total_sum)                # 21          (sum of all numbers in the array)
```

In another example, summing along `axis=0` across jagged lists will align elements by index: e.g., summing `[[1,2,3], [], [3,4]]` with `axis=0` yields `[4, 6, 3]` because it adds element-wise down columns (missing values are treated as 0).

## Cartesian Products of Lists (All Combinations)

To generate all combinations of elements between two lists (or within one list), use **`ak.cartesian`**. By default, `ak.cartesian([arr1, arr2])` with `axis=1` produces the Cartesian product for each corresponding pair of sublists in `arr1` and `arr2`. The result is an array of tuple records, where each tuple is one combination. For example:

```python
import awkward as ak

one = ak.Array([[1, 2, 3], [], [4, 5], [6]])
two = ak.Array([["a", "b"], ["c"], ["d"], ["e", "f"]])
pairs = ak.cartesian([one, two],  axis=1)  # all combinations per event/list:contentReference[oaicite:27]{index=27}

print(ak.to_list(pairs))
# Output: [
#   [(1,'a'), (1,'b'), (2,'a'), (2,'b'), (3,'a'), (3,'b')],
#   [],
#   [(4,'d'), (5,'d')],
#   [(6,'e'), (6,'f')]
# ]
```

Each element of `pairs` is a list of tuples. In the first element above, `[1,2,3]` crossed with `["a","b"]` gives 6 tuples. The second element is empty because one list was empty, etc. If you want the tuples to be records with field names, provide a dict instead of a list:

```python
pairs_named = ak.cartesian({"x": one, "y": two}, axis=1)  # named fields instead of tuple indices
print(str(pairs_named.type))
# type: 4 * var * {"x": type(int64), "y": type(string)}  (each tuple now has fields x and y):contentReference[oaicite:28]{index=28}
```

You can also set `nested=True` to group combinations by common elements (increasing nesting depth).

## Adding Custom Behavior to Records (Awkward Behaviors)

Awkward Array allows you to define **behaviors** (methods and properties) for custom record types. This is useful to attach domain-specific operations (e.g., vector math for Lorentz vectors, distance computations, etc.) to your data model.

For example, suppose we have records named `"point"` with fields `"x"` and `"y"`, and we want to add a method to compute the distance between two points. We can subclass `ak.Record` and register it for the `"point"` record type via `ak.behavior`. We can also subclass `ak.Array` for vectorized (array-level) operations:

```python
import numpy as np
import awkward as ak

# Define custom Record behavior for "point" records
class Point(ak.Record):
    def distance(self, other):
        return np.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)

ak.behavior["point"] = Point       # associate the "point" record name with Point class:contentReference[oaicite:34]{index=34}

# Define custom Array behavior for vectorized distance on arrays of points
class PointArray(ak.Array):
    def distance(self, other):
        return np.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)

ak.behavior["*", "point"] = PointArray  # "*" means any level of nesting of "point":contentReference[oaicite:35]{index=35}

# Now any ak.Array with __record__ = "point" will use these behaviors.
points1 = ak.Array([{"x": 1, "y": 1.1}, {"x": 2, "y": 2.2}, {"x": 3, "y": 3.3}], with_name="point")
points2 = ak.Array([{"x": 0.9, "y": 1}, {"x": 2, "y": 2.2}, {"x": 2.9, "y": 3}], with_name="point")

# Because of our behavior, we can now call the custom method:
print(points1[0].distance(points2[0]))   # distance between first records
# 0.14142135623730953:contentReference[oaicite:36]{index=36}

print(ak.to_list(points1.distance(points2)))  # distance between all corresponding points (array-level)
# [0.14142135623730953, 0.0, 0.31622776601683783]:contentReference[oaicite:37]{index=37}:contentReference[oaicite:38]{index=38}
```

In this snippet, we created a `Point` class for individual records and a `PointArray` for arrays of those records, then registered them under the `"point"` key in `ak.behavior`. This allows calling `distance` on either a single record or an array of records. (Note: If an array was created *before* the behavior was registered, you may need to recreate it via `ak.Array(old_array)` to re-instantiate with the new behavior.)

Note that it was possible to add extra fields to a record with the `Momentum3D` (or any other) behavior. `Momentum3D` will ignore the extra fields, and we can reference them normally. This prevents having to make lots of nested records for a single object (e.g. a jet 4-vector with properties like JVT (Jet Vertex Fraction)).

## Adding a New Field to Records

To add a new field to an existing record-type Awkward Array, you can use **`ak.with_field`**. This function returns a new array with the additional field (it does not modify in-place). For example, let's add a field `"z"` to each record in an array:

```python
import awkward as ak

arr = ak.Array([{"x": 1, "y": 2}, {"x": 3, "y": 4}])
new_field_values = ak.Array([100, 200])
arr_with_z = ak.with_field(arr, new_field_values, where="z")  # attach new field "z":contentReference[oaicite:42]{index=42}

print(ak.to_list(arr_with_z))
# Output: [{'x': 1, 'y': 2, 'z': 100}, {'x': 3, 'y': 4, 'z': 200}]
```

Under the hood, `ak.with_field` can take any array-like as the new field (`what` parameter) and a name or path (`where`) indicating where to add it. Alternatively, you can use the syntax `arr["newfield"] = values` for an in-place update (which uses `ak.with_field` internally).

## Constructing and Using Lorentz Vectors (Physics Example)

Awkward Array integrates with the [Vector](https://github.com/scikit-hep/vector) library to handle 2D/3D/4D vectors in a physics context using behaviors. To represent Lorentz vectors (four-momentum with energy), we create an Awkward record array with fields like `"px"`, `"py"`, `"pz"`, `"E"` and assign it a record name `"Momentum4D"` (a name recognized by the Vector library behaviors). We must also ensure the Vector behaviors are registered in Awkward.

First, register vector behaviors and construct the array of vectors:

```python
import awkward as ak
import vector

vector.register_awkward()  # make Vector's Awkward behaviors available:contentReference[oaicite:46]{index=46}

px = ak.Array([100.0, 30.0, 50.0])
py = ak.Array([0.0,   20.0, 40.0])
pz = ak.Array([-10.0, 5.0,  25.0])
energy = ak.Array([105.0, 40.0, 65.0])
vecs = ak.zip({"px": px, "py": py, "pz": pz, "E": energy}, with_name="Momentum4D")
# "Momentum4D" with fields px,py,pz,E is a recognized 4-vector record type:contentReference[oaicite:47]{index=47}

print(vecs.type)
# 3 * Momentum4D[px: float64, py: float64, pz: float64, E: float64]
```

Now, `vecs` behaves like an array of Lorentz vectors. We can use vector library properties and methods on it. For example, compute the invariant mass of each four-vector (which is provided by the Vector behavior as `.mass`):

```python
masses = vecs.mass    # invariant mass for each 4-vector (uses E^2 - p^2):contentReference[oaicite:48]{index=48}:contentReference[oaicite:49]{index=49}
pt = vecs.pt          # transverse momentum for each vector
rapidity = vecs.eta   # pseudorapidity for each vector

print(ak.to_list(masses))    # e.g. [15.0, 5.0, 35.3553...] based on given components
print(ak.to_list(pt))        # [100.0, ~36.06, ~64.03] transverse momentum magnitudes 
print(ak.to_list(rapidity))  # [some values] pseudorapidity
```

Because we used `with_name="Momentum4D"` and called `vector.register_awkward()`, the array `vecs` automatically gained methods like `.mass`, `.pt`, `.eta`, etc., as defined by Vector’s Awkward behaviors. We can also do vectorized operations: for instance, adding two such Awkward vector arrays `vecs1 + vecs2` will yield a new Awkward array of the same type (provided the behavior for addition is defined, which the Vector library handles).

## Combining and Zipping Jagged Arrays (Building Composite Objects)

In HEP analyses, you often build composite objects (like jets or dimuon pairs) from constituents. Awkward's **zipping and unflattening** operations can help with that. For example, if you have flat arrays of particle properties and an array of counts that tell how many particles per event, you can **group** them into an event structure:

```python
import awkward as ak
import numpy as np

# Flat data for 6 particles (energies and etas), and counts per event
energy = ak.Array([50, 20, 30, 25, 40, 15])
eta    = ak.Array([2.1,  1.5, 0.3, -0.7, 0.9,  2.4])
counts = ak.Array([3, 2, 1])  # e.g., 3 particles in event1, 2 in event2, 1 in event3

# Group particles into events using ak.unflatten:
energies_by_event = ak.unflatten(energy, counts)
etas_by_event     = ak.unflatten(eta, counts)
events = ak.zip({"energy": energies_by_event, "eta": etas_by_event})
print(ak.to_list(events))
# Output: [
#   [{'energy': 50, 'eta': 2.1}, {'energy': 20, 'eta': 1.5}, {'energy': 30, 'eta': 0.3}], 
#   [{'energy': 25, 'eta': -0.7}, {'energy': 40, 'eta': 0.9}], 
#   [{'energy': 15, 'eta': 2.4}]
# ]
```

Now suppose we want to form all **pairs** of particles *within each event* (for example, to consider all di-object combinations in an event). We can use `ak.combinations` for "n choose k" selections on each list. Below, we find all unique 2-combinations of particles per event and compute the sum of their energies:

```python
pairs = ak.combinations(events, 2, fields=["p1", "p2"], axis=1)  # all 2-combinations per event
# 'pairs' is an array of records {p1: {energy,eta}, p2: {energy,eta}} for each pair

# Compute sum of energies for each pair:
pair_energies = pairs.p1.energy + pairs.p2.energy

print(ak.to_list(pair_energies))
# Example output: [[70, 80, 50], [65], []] 
# (energy sums of each pair in each event; last event has no pairs because only 1 particle)
```

In this snippet, `ak.combinations(array, 2, fields=[...])` produced an array of records with two fields (`p1` and `p2`) for each pair. We then utilized vectorized field access (`pairs.p1.energy`) and arithmetic to get the combined energy of each pair.

Always use the `fields` argument to label the fields. It makes it much easier to understand what is going on later.

## Numpy Operations that *just work*

- `numpy` has a dispatch mechanism which allows some `numpy` functions to work on awkward arrays. But as a general rule, the arrays must be `numpy-like` even if they are awkward - that is, not awkward/jagged!
  - For example, `np.stack` works as expected on awkward arrays. And the rules for `np.stack` are the same for awkward arrays - you need a 2D array, not a jagged array (it can be awkward type, but it must be effectively 2D).
- `ak.stack` does not exist and its used will cause an undefined symbol error!

## Some Other Notes

From previous mistakes made by LLM's:

- `ak.fill_like(array, value)` - the value must be a numeric value (like a float or integer), not a string. It will return an array with the same structure as `array`, but with `value` in each occupied position.

---

Each of these snippets demonstrates a building block for complex operations with Awkward Array 2.x. By combining these techniques—**flattening**, **zipping fields into records**, **masking/filtering**, **sorting**, **reductions**, **combinatorics**, and **custom behaviors**—LLMs or developers can construct solutions to typical HEP data analysis tasks. The Awkward Array library is designed to handle irregular, nested data with high performance, enabling elegant, vectorized operations where one might otherwise write slow Python loops. By referencing and reusing patterns from this "library of techniques," an LLM like GPT-4 can better generate correct code against Awkward Array’s API.
