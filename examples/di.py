from dataclasses import dataclass

from fasteda.dependency import Injector


@dataclass
class A:
    pass


@dataclass
class B:
    a: A


@dataclass
class C:
    c: A
    b: B


@dataclass
class D:
    a: A
    b: B
    c: C


def provider_a() -> A:
    return A()


def provider_b(a: A) -> B:
    return B(a)


def provider_c(b: B, a: A) -> C:
    return C(a, b)


def provider_d(a: A, b: B, c: C) -> D:
    return D(a, b, c)


injectior = Injector()
injectior.add_provider(provider_a)
injectior.add_provider(provider_b)
injectior.add_provider(provider_c)
# injectior.add_provider(provider_d)

print(injectior.run(provider_d))
