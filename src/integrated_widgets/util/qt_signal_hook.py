from typing import Generic, TypeVar, Callable, Optional
from logging import Logger

from PySide6.QtCore import SignalInstance, QObject, Signal

from observables.core import HookLike, DEFAULT_NEXUS_MANAGER, NexusManager, Hook, BaseListening, HookWithReactionMixin

T = TypeVar("T")

class _QtSignalEmitter(QObject):
    """Internal QObject for signal emission."""
    value_changed: Signal = Signal(object)


class QtSignalHook(HookWithReactionMixin[T], Hook[T], HookLike[T], BaseListening, Generic[T]):
    """
    Hook that connects to a Qt signal and also emits a signal.

    The receiving signal triggers the hook to fetch the value through the value_callback.

    The emitting signal emits when the value changes.
    
    This is similar to FloatingHook but adds Qt signal integration.
    """
    
    def __init__(
        self,
        receiving_signal: SignalInstance,
        value_callback: Callable[[], T],
        *,
        logger: Optional[Logger] = None,
        nexus_manager: NexusManager = DEFAULT_NEXUS_MANAGER
    ) -> None:

        # Fetch initial value
        initial_value: T = value_callback()
        
        # Initialize BaseListening first
        BaseListening.__init__(self, logger)
        
        # Initialize Hook with the initial value
        Hook.__init__(
            self,
            value=initial_value,
            nexus_manager=nexus_manager,
            logger=logger
        )
        
        self._receiving_signal: SignalInstance = receiving_signal
        self._value_callback: Callable[[], T] = value_callback
        
        # Create internal QObject for signal emission
        self._signal_emitter: _QtSignalEmitter = _QtSignalEmitter()
        
        # Initialize HookWithReactionMixin to react when nexus manager changes the value
        HookWithReactionMixin.__init__(
            self,
            react_to_value_changed_callback=lambda value: self._signal_emitter.value_changed.emit(value)
        )
        
        # Connect receiving signal to our update method
        def on_signal_received() -> None:
            """Called when the receiving signal fires."""
            new_value: T = value_callback()
            
            # Use the Hook's submit_value method to update the value
            # The HookWithReactionMixin will automatically emit the Qt signal via react_to_value_changed
            success, msg = self.submit_value(new_value)
            if not success:
                raise ValueError(msg)
        
        self._receiving_signal.connect(on_signal_received)

    @property
    def value_changed_signal(self) -> SignalInstance:
        """Get the Qt signal that emits when the value changes."""
        return self._signal_emitter.value_changed  # type: ignore[return-value]
