# xAOD Event Data Model Hints

Some hints to help with accessing xAOD objects.

Important note about units:

* All momentum, energy, and mass units are in MeV (e.g. `pt, E, m`). Unless asked otherwise, convert them to GeV by dividing by 1000 as early as possible.
* All distance units are in millimeters. Convert them to meters as early as possible.

## Jets, Muons, Taus, Photons, Electrons

It is possible to access all these objects from the top event level, e.g.,

```python
query = FuncADLQueryPHYS() \
    .Select(lambda e: e.Jets()) \
    .Select(lambda jets: {
        'pt': jets.Select(lambda j: j.pt()/1000.0),
        'eta': jets.Select(lambda j: j.eta()/1000.0),
    })
```

The only odd one are tau's, which use `e.TauJets("AnalysisTauJets")`.

These objects all have `pt, eta, phi` (with methods by those names). To access `px, py, pz` you have to get the 4-vector first:

```python
query = FuncADLQueryPHYS() \
    .Select(lambda e: e.Jets()) \
    .Select(lambda jets: {
        'pt': jets.Select(lambda j: j.p4().px()/1000.0),
    })
```

## MissingET

Access:

```python
query = FuncADLQueryPHYS() \
    .Select(lambda e: e.MissingET().First()) \
    .Select(lambda m: {"met": m.met() / 1000.0'})
```

Despite being only a single missing ET for the event, it is stored as a sequence. Thus you must get the first object and then access the `.met()` method from there. Note that the missing ET object has `met`, `mpy`, `mpx`, etc. It adds an `m` in front of everything.

## xAOD Tool Access

Lots of things have to be accessed by creating tools.

Copy the code below into your source if you are going to use a code. The methods it defines can be used to build in tool access.

```python
from dataclasses import dataclass
from typing import Callable, Iterable, List, Optional
from func_adl import ObjectStream
from func_adl import func_adl_callable

T = TypeVar("T")


@dataclass
class ToolInfo:
    name: str


def make_a_tool(
    query: ObjectStream[T],
    tool_name: str,
    tool_type: str,
    include_files: Optional[List[str]],
    init_lines: List[str] = [],
) -> Tuple[ObjectStream[T], ToolInfo]:
    """
    Injects C++ code into the query to initialize a tool of the specified type.

    This function sets up the necessary C++ code to create and initialize a tool (such as
    BTaggingSelectionTool) in the analysis workflow. The tool will be available in the C++
    code under the variable name specified by `tool_name`, which can be referenced in
    initialization lines and later code.

    Args:
        query: The ObjectStream to attach the tool initialization metadata to.
        tool_name: The variable name to use for the tool instance in the C++ code.
        tool_type: The C++ class name of the tool to instantiate.
        include_files: List of C++ header files to include for the tool.
        init_lines: List of C++ code lines to run for tool initialization. You can use
            `{tool_name}` in these lines to refer to the tool variable. You should
            include the call to `ANA_CHECK({tool_name}->initialize());`.

    Returns:
        A tuple containing:
            - The updated ObjectStream with the tool initialization metadata.
            - A ToolInfo object containing the tool's name. Pass this to `make_tool_accessor`
    """
    # Define the C++ for the tool initialization

    query_base = query.MetaData(
        {
            "metadata_type": "inject_code",
            "name": tool_name,
            "header_includes": include_files,
            "private_members": [f"{tool_type} *{tool_name};"],
            "instance_initialization": [
                f'{tool_name}(new {tool_type} ("{tool_name}"))'
            ],
            "initialize_lines": [l.format(tool_name=tool_name) for l in init_lines],
            "link_libraries": ["xAODBTaggingEfficiencyLib"],
        }
    )

    return query_base, ToolInfo(name=tool_name)


def make_tool_accessor(
    t_info: ToolInfo,
    function_name: str,
    source_code: List[str],
    arguments: Iterable[Tuple[str, type]],
    return_type_cpp: str,
    return_type_python: str
):
    """
    Creates a Python-callable accessor for a C++ tool in the func_adl query.

    This function generates a Python function that, when called in a func_adl query,
    injects C++ code to call a method or function on a C++ tool instance (such as
    BTaggingSelectionTool). The accessor function can be used in the query to access
    tool functionality as if it were a regular Python function.

    Args:
        t_info: ToolInfo object containing the tool's variable name.
        function_name: Name of the accessor function (used in C++ and Python).
        source_code: List of C++ code lines to execute for the accessor. You can use
            `{tool_name}` in these lines to refer to the tool variable.
        arguments: Iterable of (argument_name, type) tuples specifying the arguments
            for the accessor function.
        return_type_cpp: The C++ return type of the accessor function.
        return_type_python: The Python return type annotation as a string.

    Returns:
        A Python function that can be used in a func_adl query to access the tool.
        NOTE: YOU MUST use the same name as `function_name` to store this:

            `my_name = make_tool_accessor(.., function_name="my_name", ...)`
    """
    # Define the callback function that `func_adl` will use to inject the calling code.
    def tool_callback(
        s: ObjectStream[T], a: ast.Call
    ) -> Tuple[ObjectStream[T], ast.Call]:
        new_s = s.MetaData(
            {
                "metadata_type": "add_cpp_function",
                "name": function_name,
                "code": [
                    "double result;",
                    *[l.format(tool_name=t_info.name) for l in source_code],
                ],
                "result": "result",
                "include_files": [],
                "arguments": [a[0] for a in arguments],
                "return_type": return_type_cpp,
            }
        )
        return new_s, a

    # Build a function type-shed that tells `func_adl` what the function signature is.
    # This is used to generate the correct C++ code for the function.
    def tool_call(**arg_dict):
        """
        NOTE: This is a dummy function that injects C++ into the object stream to do the
        actual work.
        """
        ...
    tool_call.__name__ = function_name
    tool_call.__annotations__['return'] = eval(return_type_python)

    return func_adl_callable(tool_callback)(tool_call)
```

### BTaggingSelectionTool: getting jet b-tagging results

Use the `BTaggingSelectionTool` tool to get either a tag weight/discriminant for b-or-charm tagging or to see if a jet is "tagged" for a particular working point (e.g. passed an experiment defined threshold). These are provided by the FTAG group in ATLAS.

Operating Point Info:

Operating points define different b-tagging efficiency and light/charm rejection.

* Known operating point names: `FixedCutBEff_65`, `FixedCutBEff_70`, `FixedCutBEff_77`, `FixedCutBEff_85`, `FixedCutBEff_90`
* [Further information for user](https://ftag.docs.cern.ch/recommendations/algs/r22-preliminary/#gn2v01-b-tagging)
* By default choose the `FixedCutBEff_77` working point.
* Make sure to let the user know what operating point in your text explanation.

Make sure the `tool_name` is different if you need to define multiple tools (because user needs more than one operating point)! Name them something reasonable so the code makes sense!

Make sure to copy in the code block shown in the section above `xAOD Tool Access`.

```python
# Specific for the below code
from func_adl_servicex_xaodr25.xAOD.jet_v1 import Jet_v1

# Define the tool
query_base, tag_tool_info = make_a_tool(
    physlite,
    "btag_discriminator",
    "BTaggingSelectionTool",
    include_files=["xAODBTaggingEfficiency/BTaggingSelectionTool.h"],
    init_lines=[
        'ANA_CHECK(asg::setProperty({tool_name}, "OperatingPoint", "FixedCutBEff_77"));',
        "ANA_CHECK({tool_name}->initialize());",
    ],
)

# If you need the tag weight. Tag weights, output of a GNN, are between -10 and 15.
tag_weight = make_tool_accessor(
    tag_tool_info,
    function_name="tag_weight",
    # false in next line for b-tagging weight, true for c-tagging weight
    source_code=["ANA_CHECK({tool_name}->getTaggerWeight(*jet, result, false));"],
    arguments=[("jet", Jet_v1)],
    return_type_cpp="double",
    return_type_python="float",
)

# If you need to know if a jet is tagged or not.
jet_is_tagged = make_tool_accessor(
    tag_tool_info,
    function_name="jet_is_tagged",
    source_code=[
        "result = static_cast<bool>({tool_name}->accept(*jet));"
    ],
    arguments=[("jet", Jet_v1)],
    return_type_cpp="bool",
    return_type_python="bool",
)

Usage of `jet_is_tagged` in `func_adl` is straight forward:

```python
query = (FuncADLQueryPHYSLITE()
    .Select(lambda e: e.Jets().Select(lambda j: jet_is_tagged(j)))
```
