# Awkward Array 2.0 Complex Operation Snippets

It is important to always use Awkward 2.0 syntax and calls.

As a general theme - it is always better to filter data early rather than wait until the last minute. The sooner you can apply a cut, the smaller the data you have to work with downstream, and the more can fit into core memory.

In general best practice is:

1. Build an Event Data Model with `ak.zip` or record
2. Apply filters that are needed at the event level
3. Build new calculations or combinatorics combinations.
4. When you have the best calculation or combination, add it back into the event data model.
5. Repeat steps 3 and 4 until you've build the final value to calculate,

## Combining Multiple Fields into Records

Use **`ak.zip`** to join parallel arrays into an array of records (structured data).

```python
import awkward as ak

ages = ak.Array([18, 32, 41])
names = ak.Array(["Dorit", "Caitlin", "Bryn"])
people = ak.zip({"age": ages, "name": names})   # Combine fields into records:contentReference[oaicite:5]{index=5}

print(ak.to_list(people))
# Output: [{'age': 18, 'name': 'Dorit'}, {'age': 32, 'name': 'Caitlin'}, {'age': 41, 'name': 'Bryn'}]:contentReference[oaicite:6]{index=6}
```

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

## Filtering Data by Value

Filtering uses the same syntax as one uses with `numpy`.

Filtering only works as long as the structure of the mask and the item you are masking are similar. For example:

There are several aggregate operations that can be used (for filtering or whatever).

## Aggregation Operations

It is often useful to aggregate a sub-list into a single number (mean, max, etc.). Here are operations that do that.

- `ak.sum` - sum numbers at an `axis` level.
- `ak.count` - counts the number of non-empty elements in an axis (remember to add `axis=n`). If the element is empty, it does not count. Useful for counting the number of jets in each event (`ak.count(e.jets, axis=1))`). Returns length per sublist. Counts values.
- `ak.num` - counts the number of elements. `ak.num(e)` is like `len(e)` - doesn't care of an array entry is empty or not. Returns a number (or nested number). Counts slots.

Awkward *does not* have a `ak.max` - but the `python` `max` and `min` functions work on awkward arrays.

## Sorting

Use **`ak.sort`**. By default `ak.sort(array)` sorts along the last axis (`axis=-1`, i.e. within each sublist). For example:

You can specify `ascending=False` to sort in descending order, or provide an `axis` if you need to sort at a higher level of nesting.

## Building Multi-Object Quantities

When trying to calculate an invariant mass or the opening angle (DeltaR) between objects, it is necessary to build arrays of the same size. Often this requires using combinatorics or combinations to build something new out of two or three (or whatever) objects.

There are two awkward array functions to build combinatorics:

- `ak.cartesian` - Takes one item from each list. For example, if you want to form pairs of muons and electrons from a list of muons and a list of electrons. Example: `pairs = ak.cartesian({"m": muons, "e": electrons}, axis=1)`. Then `pairs.m` will be all the muons.
- `ak.combinations` - Forms all n-way combinations from a list. For example, if you want to form all 3-jet combinations from a list of jets. Example: `combo = ak.combinations(jets, 3, fields=["j1", "j2", "j3"], axis=1)`, and `combo.j1` is all the first jets in the pairings.

If you are ever comparing electrons or muons to each other and you don't have exactly the same number of each in each event, then things like `DeltaR` will fail - you must use `ak.cartesian` or `ak.combinations` to pick the best combination and assure you have a 1-to-1 relationship between the types.

## Filtering sublists with `argmin` and `argmax` and friends

This is very tricky and you must be very careful in how you apply these very powerful functions.

Since `axis=0` is event lists, we often want to operated on the jagged arrays, e.g., `axis=1`. `argmin` and `argmax` are great for this, for example, when looking for two objects close to each other. However, `argmin` and `argmax` don't operate on `axis=1` (or deeper) the same way as `np.argmin` and `np.argmax` - and nor does the slicing, so we must be deliberate when using `argmin` and friends.

Instead, we need to use lists. For example:

```python
import awkward as ak

array = ak.Array([[7, 5, 7], [], [2], [8, 2]])
max_values = ak.argmax(array, axis=1, keepdims=True)
print(max_values) # prints out "[[0], [None], [0], [0]]"
print(array[max_values]) # prints out "[[7], [None], [2], [8]]"
print(ak.flatten(array[max_values], axis=0)) # prints out "[7, None, 2, 8]"
```

Note the `keepdims=True` - that makes sure you get that nested list, "[[0], [None], [0], [0]]", which can be correctly used for slicing.

Once you do the filtering (`array[max_values]`), if you want a list of the values, you must:

- Use `ak.flatten` to undo the downlevel caused by `keepdims=True`, or
- Use `ak.firsts` to pick out the first in the sub list.

Either of these will give you "[7, None, 2, 8]" in this example. But you *have* to do this for every item filtered by `max_values` - any filtering using `argmin` and friends. Note this trick is not necessary when filtering by values as describe in the above section.

## Flattening Nested Arrays

Use **`ak.flatten`** to reduce nested list structure. By default, `ak.flatten(array, axis=1)` removes one level of nesting (flattens along the axis=1). Setting `axis=None` will completely flatten an array, erasing all nesting (turning it into 1D):

```python
import awkward as ak

array = ak.Array([[0, 1, 2], [], [3, 4], [5, 6, 7]])
flat_level1 = ak.flatten(array, axis=1)          # Flatten one level (axis=1 by default):contentReference[oaicite:2]{index=2}
flat_all   = ak.flatten(array, axis=None)  # Flatten all levels into 1D:contentReference[oaicite:3]{index=3}

print(flat_level1)  # [0, 1, 2, 3, 4, 5, 6, 7]
print(flat_all)     # [0, 1, 2, 3, 4, 5, 6, 7]  (same here because only one level)
```

Notes:

- Always *explicitly set the `axis`* in the arguments to `flatten`. This will force us to think about what axis we are flattening and if the data has that access.
- If a variable has no array structure or is a 1D array, then `ak.flatten` with `axis=1` (the default) will cause an error. Be sure your data has the requested `axis` if you are going to flatten.

## Numpy Operations that *just work*

- `numpy` has a dispatch mechanism which allows some `numpy` functions to work on awkward arrays. But as a general rule, the arrays must be `numpy-like` even if they are awkward - that is, not awkward/jagged!
  - For example, `np.stack` works as expected on awkward arrays. And the rules for `np.stack` are the same for awkward arrays - you need a 2D array, not a jagged array (it can be awkward type, but it must be effectively 2D).
- `ak.stack` does not exist and its used will cause an undefined symbol error!

## Some Other Notes

From previous mistakes made by LLM's:

- `ak.fill_like(array, value)` - the value must be a numeric value (like a float or integer), not a string. It will return an array with the same structure as `array`, but with `value` in each occupied position.
- Python's `abs` works just fine on awkward arrays (there is no `ak.abs`)
- There is no `ak.take` - use filtering instead.
