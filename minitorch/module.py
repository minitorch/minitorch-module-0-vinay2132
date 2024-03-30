from __future__ import annotations

from typing import Any, Dict, Optional, Sequence, Tuple


class Module:
    """
    Modules form a tree that store parameters and other
    submodules. They make up the basis of neural network stacks.

    Attributes:
        _modules (dict of name x :class:`Module`): Storage of the child modules
        _parameters (dict of name x :class:`Parameter`): Storage of the module's parameters
        training (bool): Whether the module is in training mode or evaluation mode

    """

    _modules: Dict[str, Module]
    _parameters: Dict[str, Parameter]
    training: bool

    def __init__(self) -> None:
        self._modules = {}
        self._parameters = {}
        self.training = True

    # def modules(self) -> Sequence[Module]:
    #     "Return the direct child modules of this module."
    #     return self.__dict__["_modules"].values()

    def modules(self) -> Sequence[Module]:
        "Return the direct child modules of this module."
        m: Dict[str, Module] = self.__dict__["_modules"]
        return list(m.values())

    def train(self) -> None:
        """Set the mode of this module and all descendent modules to `train`."""
        self.training = True  # Set current module to train mode

        # Iterate through descendant modules and set them to train mode
        for m in self.modules():
            m.train()

    def eval(self) -> None:
        "Set the mode of this module and all descendent modules to `eval`."

        self.training = False  # Set current module to eval mode
        for m in self.modules():  # Iterate through child modules
            m.eval()

    def named_parameters(self) -> Sequence[Tuple[str, Parameter]]:
        """
        Collect all the parameters of this module and its descendents.


        Returns:
            list of pairs: Contains the name and :class:`Parameter` of each ancestor parameter.
        """

        def _named_parameters(module: Any, prefix: str = "") -> Any:
            for name, param in module._parameters.items():
                yield prefix + name, param
            for name, module in module._modules.items():
                yield from _named_parameters(module, prefix + name + ".")

        return list(_named_parameters(self))

    def parameters(self) -> Sequence[Parameter]:
        "Enumerate over all the parameters of this module and its descendents."

        # def _parameters(module):
        #     for param in module._parameters.values():
        #         yield param
        #     for module in module._modules.values():
        #         yield from _parameters(module)

        return [param for _, param in self.named_parameters()]

    def add_parameter(self, k: str, v: Optional[Any]) -> Parameter:
        """
        Manually add a parameter. Useful helper for scalar parameters.

        Args:
            k (str): Local name of the parameter.
            v (value): Value for the parameter.

        Returns:
            Parameter: Newly created parameter.
        """
        val = Parameter(v, k)
        self.__dict__["_parameters"][k] = val
        return val

    def __setattr__(self, key: str, val: Parameter) -> None:
        if isinstance(val, Parameter):
            self.__dict__["_parameters"][key] = val
        elif isinstance(val, Module):
            self.__dict__["_modules"][key] = val
        else:
            super().__setattr__(key, val)

    def __getattr__(self, key: str) -> Any:
        if key in self.__dict__["_parameters"]:
            return self.__dict__["_parameters"][key]

        if key in self.__dict__["_modules"]:
            return self.__dict__["_modules"][key]

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        return self.forward(*args, **kwargs)

    def forward(self) -> int:
        assert False, "Not Implemented"

    def __repr__(self) -> str:
        def _addindent(s_: str, numSpaces: int) -> str:
            s2 = s_.split("\n")
            if len(s2) == 1:
                return s_
            first = s2.pop(0)
            s2 = [(numSpaces * " ") + line for line in s2]
            s = "\n".join(s2)
            s = first + "\n" + s
            return s

        child_lines = []

        for key, module in self._modules.items():
            mod_str = repr(module)
            mod_str = _addindent(mod_str, 2)
            child_lines.append("(" + key + "): " + mod_str)
        lines = child_lines

        main_str = self.__class__.__name__ + "("
        if lines:
            # simple one-liner info, which most builtin Modules will use
            main_str += "\n  " + "\n  ".join(lines) + "\n"

        main_str += ")"
        return main_str


class Parameter:
    """
    A Parameter is a special container stored in a :class:`Module`.

    It is designed to hold a :class:`Variable`, but we allow it to hold
    any value for testing.
    """

    def __init__(self, x: Any, name: Optional[str] = None) -> None:
        self.value = x
        self.name = name
        if hasattr(x, "requires_grad_"):
            self.value.requires_grad_(True)
            if self.name:
                self.value.name = self.name

    def update(self, x: Any) -> None:
        "Update the parameter value."
        self.value = x
        if hasattr(x, "requires_grad_"):
            self.value.requires_grad_(True)
            if self.name:
                self.value.name = self.name

    def __repr__(self) -> str:
        return repr(self.value)

    def __str__(self) -> str:
        return str(self.value)
