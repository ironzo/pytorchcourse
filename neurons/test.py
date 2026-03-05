import cl
from cl import ChannelSet, StimDesign
import random

# Канали 0-31 = ліва половина, 32-63 = права половина
LEFT_CHANNELS  = ChannelSet(list(range(0, 32)))
RIGHT_CHANNELS = ChannelSet(list(range(32, 64)))

REGULAR_STIM = StimDesign(160, -1.0, 160, 1.0)   # впорядкований = "відбив"
CHAOTIC_STIM = StimDesign(40,  -2.0, 40,  2.0)   # хаотичний = "промахнувся"

if __name__ == '__main__':
    # стан гри
    ball_x    = 0.5   # 0.0 = зліва, 1.0 = справа
    ball_dir  = 1     # +1 = вправо, -1 = вліво
    paddle_x  = 0.5   # позиція ракетки
    score     = 0
    misses    = 0

    with cl.open() as neurons:
        for tick in neurons.loop(ticks_per_second=100, stop_after_ticks=500):

            # рахуємо спайки зліва і справа
            left_spikes  = sum(1 for s in tick.analysis.spikes if s.channel < 32)
            right_spikes = sum(1 for s in tick.analysis.spikes if s.channel >= 32)

            # нейрони "вирішують" куди рухати ракетку
            total = left_spikes + right_spikes
            if total > 0:
                paddle_x += (right_spikes - left_spikes) / total * 0.05
                paddle_x  = max(0.0, min(1.0, paddle_x))

            # рухаємо м'яч
            ball_x += ball_dir * 0.02
            if ball_x >= 1.0:
                ball_dir = -1
            elif ball_x <= 0.0:
                # момент удару — ракетка поруч?
                if abs(paddle_x - ball_x) < 0.2:
                    score += 1
                    # впорядкована стимуляція = позитивний зворотній зв'язок
                    stim_side = LEFT_CHANNELS if ball_x < 0.5 else RIGHT_CHANNELS
                    neurons.stim(stim_side, REGULAR_STIM)
                    print(f"Tick {tick.tick_index:4d} | ВІД'ЄДНАВ  | м'яч={ball_x:.2f} ракетка={paddle_x:.2f} | рахунок={score}")
                else:
                    misses += 1
                    # хаотична стимуляція = негативний зворотній зв'язок
                    neurons.stim(LEFT_CHANNELS,  CHAOTIC_STIM)
                    neurons.stim(RIGHT_CHANNELS, CHAOTIC_STIM)
                    print(f"Tick {tick.tick_index:4d} | ПРОМАХ     | м'яч={ball_x:.2f} ракетка={paddle_x:.2f} | промахів={misses}")
                ball_dir = 1

            # стимулюємо канали відповідно до позиції м'яча
            if tick.tick_index % 10 == 0:
                stim_side = LEFT_CHANNELS if ball_x < 0.5 else RIGHT_CHANNELS
                neurons.stim(stim_side, REGULAR_STIM)

        print(f"\nФінал: відбито={score}, промахів={misses}")
        print(f"Точність: {score/(score+misses)*100:.1f}%" if (score+misses) > 0 else "Немає даних")