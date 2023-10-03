# This is a sample Python script.
from __future__ import annotations
from pyetg1510.mailbox.sdo_application_interface import SdoMetadata
from abc import ABCMeta, abstractmethod
from dataclasses import dataclass, field
from typing import List
from pyetg1510.helper import SysLog

logger = SysLog.logger


@dataclass
class Component(metaclass=ABCMeta):
    """
    The base Component class declares common operations for both simple and
    complex objects of a composition.
    """

    parent: Component = field(default=None)

    def __new__(cls, *args, **kwargs):
        dataclass(cls)
        return super().__new__(cls)

    @abstractmethod
    def add(self, component: Component) -> None:
        pass

    @abstractmethod
    def remove(self, component: Component) -> None:
        pass

    @abstractmethod
    def operation(self) -> str:
        """
        The base Component may implement some default behavior or leave it to
        concrete classes (by declaring the method containing the behavior as
        "abstract").
        """
        pass

    @abstractmethod
    def is_composite(self) -> bool:
        pass


class Leaf(Component, SdoMetadata):
    """
    The Leaf class represents the end objects of a composition. A leaf can't
    have any children.

    Usually, it's the Leaf objects that do the actual work, whereas Composite
    objects only delegate to their sub-components.
    """

    @property
    def upstream(self):
        if self.parent is not None:
            current_index = self.parent.children.index(self)
            if current_index > 0:
                return self.parent.children[current_index - 1]
            else:
                return None
        else:
            return None

    @property
    def downstream(self):
        if self.parent is not None:
            current_index = self.parent.children.index(self)
            if current_index < len(self.parent.children):
                return self.parent.children[current_index + 1]
            else:
                return None
        else:
            return None

    def is_composite(self) -> bool:
        """
        You can provide a method that lets the client code figure out whether a
        component can bear children.
        """

        return False


class Composite(Component):
    """
    The Composite class represents the complex components that may have
    children. Usually, the Composite objects delegate the actual work to their
    children and then "sum-up" the result.
    """

    children: List[Component] = field(default_factory=list, init=True)

    """
    A composite object can add or remove other components (both simple or
    complex) to or from its child list.
    """

    def add(self, component: Component) -> None:
        self.children.append(component)
        component.parent = self

    def remove(self, component: Component) -> None:
        self.children.remove(component)
        component.parent = None

    def is_composite(self) -> bool:
        return True

    def operation(self) -> str:
        """
        The Composite executes its primary logic in a particular way. It
        traverses recursively through all its children, collecting and summing
        their results. Since the composite's children pass these calls to their
        children and so forth, the whole object tree is traversed as a result.
        """

        results = []
        for child in self.children:
            results.append(child.operation())
        return f"Branch({'+'.join(results)})"
