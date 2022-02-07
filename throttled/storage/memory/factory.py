from throttled.models import Rate
from throttled.storage.memory.storage import DURATION_CALC, MemoryStorage
from throttled.strategy.base import StorageFactory, Strategy


class MemoryStorageFactory(StorageFactory):
    def get_storage_for_strategy(
        self, strategy: Strategy, limit: Rate
    ) -> MemoryStorage:
        try:
            return MemoryStorage(
                interval=limit.interval,
                duration_calc=DURATION_CALC[type(strategy)],
            )
        except KeyError as err:
            raise TypeError(
                f"There is not MemoryStorage for strategy {strategy.__class__} implemented yet!"
            ) from err
