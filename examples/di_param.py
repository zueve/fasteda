import inspect
from dataclasses import dataclass

from fasteda.dependency import Injector


@dataclass
class A:
    name: str


@dataclass
class B:
    a_for_b: A


@dataclass
class C:
    a_for_c: A


def provider_a(p: inspect.Parameter) -> A:
    return A(p.name)


def provider_b(a_for_b: A) -> B:
    return B(a_for_b)


def provider_c(a_for_c: A) -> C:
    return C(a_for_c)


def main(b: B, c: C) -> None:
    print(f"{b=} &&  {c=}")


if __name__ == "__main__":
    injector = Injector()
    injector.add_provider(provider_a)
    injector.add_provider(provider_b)
    injector.add_provider(provider_c)

    injector.run(main)
