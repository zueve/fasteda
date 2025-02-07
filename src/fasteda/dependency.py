import inspect
from collections.abc import Callable
from typing import Any, Generic, NamedTuple, TypeVar

T = TypeVar("T")

ResultKey = tuple[type[T], str]
Provider = Callable[..., T]
ProviderResolver = Callable[[type[T]], Provider[T] | None]


class _Row(Generic[T], NamedTuple):
    provider: "_Provider[T]"
    param_map: dict[str, ResultKey[Any]]
    result_key: ResultKey[T]
    cachable: bool


class _Provider[T]:
    def __init__(self, provider: Callable[..., T], cachable: bool) -> None:
        self.run = provider
        self.signature = inspect.signature(provider)
        self.cachable = cachable

        self.validate()

    def get_dependencies(self) -> set[inspect.Parameter]:
        return {
            p for p in self.signature.parameters.values() if p.name != "result"
        }

    def get_result_key(self, parameter: inspect.Parameter) -> ResultKey[T]:
        key = parameter.name if self.depends_on_parameter() else ""
        return self.get_result_annotation(), key

    def get_result_annotation(self) -> type[Any]:
        return self.signature.return_annotation

    def depends_on_parameter(self) -> bool:
        parameter_types = {p.annotation for p in self.get_dependencies()}
        return inspect.Parameter in parameter_types

    def validate(self) -> None:
        """
        All Provider parameters must have annotation and be keyword

        """
        for p in self.signature.parameters.values():
            if p.annotation == inspect.Parameter.empty:
                raise ValueError(
                    f"Provider {self.run!r} parameter {p.name!r} "
                    "must have type annotation"
                )
            if p.kind not in (
                inspect.Parameter.POSITIONAL_OR_KEYWORD,
                inspect.Parameter.KEYWORD_ONLY,
            ):
                raise ValueError(
                    f"Provider {self.run!r} parameter {p.name!r} "
                    "must be keyword"
                )

    def __repr__(self) -> str:
        return f"_Provider[{self.run!r}]"


class _ProviderResolver(Generic[T]):
    def __init__(self, resolver: ProviderResolver[T], cachable: bool) -> None:
        self._resolver = resolver
        self._cachable = cachable

    def resolve(self, cls: type[T]) -> _Provider[T] | None:
        provider = self._resolver(cls)
        if provider:
            return _Provider(provider, self._cachable)
        return None

    def __repr__(self) -> str:
        return f"_ProviderResolver[{self._resolver!r}]"


class Injector:
    def __init__(self) -> None:
        self._providers: dict[type[Any], _Provider[Any]] = {}
        self._provide_resolvers: list[_ProviderResolver[Any]] = []
        self._cache_stack: dict[Callable[..., Any], list[_Row[Any]]] = {}
        self._cache: dict[ResultKey[Any], Any] = {}

    def add_provider_resolver(
        self, resolver: ProviderResolver[Any], cachable: bool = False
    ) -> None:
        self._provide_resolvers.append(_ProviderResolver(resolver, cachable))

    def add_provider(
        self, provider: Provider[Any], cachable: bool = False
    ) -> None:
        provider_ = _Provider(provider, cachable)
        self._providers[provider_.get_result_annotation()] = provider_

    def bind_provider(
        self,
        cls: type[Any],
        provider: Callable[..., Any],
        cachable: bool = False,
    ) -> None:
        provider_ = _Provider(provider, cachable)
        self._providers[cls] = provider_

    def run(self, func: Callable[..., T]) -> T:
        privider = _Provider(func, cachable=False)
        parameter = inspect.Parameter(
            "result", inspect.Parameter.KEYWORD_ONLY, annotation=func
        )
        return self._run(privider, parameter)

    def get(self, cls: type[T]) -> T:
        parameter = inspect.Parameter(
            "result", inspect.Parameter.KEYWORD_ONLY, annotation=cls
        )
        provider = self._find_provider_for(cls, parameter)

        return self._run(provider, parameter)

    def _run(self, provider: _Provider[T], parameter: inspect.Parameter) -> T:
        result_key = provider.get_result_key(parameter)

        if provider.cachable and result_key in self._cache:
            return self._cache[result_key]

        if provider.run not in self._cache_stack:
            stack = self._build(provider, parameter, set())
            self._cache_stack[provider.run] = [
                row for row in stack if not row.cachable
            ]
        else:
            stack = self._cache_stack[provider.run]

        binds: dict[ResultKey[T], T] = {}
        for row in stack:
            if row.provider.cachable and row.result_key in self._cache:
                continue

            params = {}
            for param_name, result_key_ in row.param_map.items():
                if row.cachable:
                    params[param_name] = self._cache[result_key_]
                else:
                    params[param_name] = binds[result_key_]

            result = row.provider.run(**params)
            if row.cachable:
                self._cache[row.result_key] = result
            else:
                binds[row.result_key] = result
        return (
            self._cache[result_key] if provider.cachable else binds[result_key]
        )

    def _build(
        self,
        provider: _Provider[Any],
        parameter: inspect.Parameter,
        added: set[ResultKey[Any]],
    ) -> list[_Row[Any]]:
        result_key = provider.get_result_key(parameter)

        if result_key in added:
            return []

        added.add(result_key)
        param_map = {}
        stack = []

        for parameter_ in provider.get_dependencies():
            provider_ = self._find_provider_for(
                parameter_.annotation, parameter
            )
            param_map[parameter_.name] = provider_.get_result_key(parameter_)
            stack += self._build(provider_, parameter_, added)

        stack.append(_Row(provider, param_map, result_key, provider.cachable))
        return stack

    def _find_provider_for(
        self, cls: type[Any], parameter: inspect.Parameter
    ) -> _Provider[Any]:
        if cls is inspect.Parameter:
            return _Provider(lambda: parameter, cachable=False)

        if cls in self._providers:
            return self._providers[cls]

        for resolver in self._provide_resolvers:
            provider = resolver.resolve(cls)
            if provider:
                self._providers[cls] = provider
                return provider

        raise TypeError(f"Provider not found for {cls!r}")
