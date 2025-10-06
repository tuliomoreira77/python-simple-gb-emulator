from bus import *

class GameboyTimer:
    global_clock = 4194304
    divider_clock = 16384
    divider_step_limit = global_clock/divider_clock
    divider_cycle = 0
    timer_counter_cycle = 0
    timer_step_limit = 0

    clock_map = {
        0: 4096,
        1: 262144,
        2: 65536,
        3: 16384
    }

    def __init__(self, memory_bus:MemoryBus):
        self.memory_bus = memory_bus

    def step(self, cycles):
        self._step_divider(cycles)
        self._step_timer(cycles)

    def _step_divider(self, cycles):
        self.divider_cycle += cycles
        if self.divider_cycle > self.divider_step_limit:
            self.divider_cycle = self.divider_cycle % self.divider_step_limit
            self.memory_bus.inc_timer_div()

    def _step_timer(self, cycles):
        self.timer_counter_cycle += cycles
        timer_counter_control = self.memory_bus.read_byte(TIMER_CONTROL)

        enabled_inc = (timer_counter_control >> 2) & 0x1
        self._set_timer_config(timer_counter_control)
        if self.timer_counter_cycle > self.timer_step_limit:
            self.timer_counter_cycle = self.timer_counter_cycle % self.timer_step_limit
            if enabled_inc:
                self.memory_bus.inc_timer_counter()

    def _set_timer_config(self, timer_control):
        clock_index = timer_control & 0b11
        clock = self.clock_map[clock_index]
        self.timer_step_limit = self.global_clock/clock

