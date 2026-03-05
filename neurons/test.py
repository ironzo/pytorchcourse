import cl
from cl import ChannelSet, StimDesign
import time

if __name__ == '__main__':
    with cl.open() as neurons:
        stim_channel = 32
        stim_design = StimDesign(160, -1.0, 160, 1.0)  # біфазний імпульс

        spike_counts_before = {}
        spike_counts_after = {}

        # збираємо базову активність (1 секунда БЕЗ стимуляції)
        for tick in neurons.loop(ticks_per_second=1000, stop_after_seconds=1):
            for spike in tick.analysis.spikes:
                spike_counts_before[spike.channel] = spike_counts_before.get(spike.channel, 0) + 1

        # стимулюємо канал 32
        neurons.stim(ChannelSet(stim_channel), stim_design)

        # збираємо активність після (1 секунда)
        for tick in neurons.loop(ticks_per_second=1000, stop_after_seconds=1):
            for spike in tick.analysis.spikes:
                spike_counts_after[spike.channel] = spike_counts_after.get(spike.channel, 0) + 1

        print(f"Канал {stim_channel} до: {spike_counts_before.get(stim_channel, 0)} спайків")
        print(f"Канал {stim_channel} після: {spike_counts_after.get(stim_channel, 0)} спайків")
        print(f"\nВсі канали до: {spike_counts_before}")
        print(f"Всі канали після: {spike_counts_after}")