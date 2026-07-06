#!/usr/bin/env python3
"""CEREBRO intro — neural pulses rippling out, neurons firing. Pure ANSI,
zero dependencies, ~4s. Prints one static frame when stdout is not a TTY.
Must never crash the host run: any exception exits silently with code 0.
"""
import math
import random
import sys
import time

W, H = 64, 18
CX, CY = W // 2, H // 2
PURPLE = "\033[38;5;135m"
DIM_PURPLE = "\033[38;5;60m"
WHITE = "\033[97m"
DIM = "\033[38;5;240m"
RESET = "\033[0m"
RING_CHARS = {True: "·", False: "o"}  # dotted = latent, solid-ish = active


def frame(t: float, neurons) -> str:
    grid = [[" "] * W for _ in range(H)]
    # background field of latent neurons
    for (x, y, born) in neurons:
        if 0 <= x < W and 0 <= y < H:
            lit = t > born
            grid[y][x] = (PURPLE + "*" + RESET) if lit else (DIM + "." + RESET)
    # expanding rings (aspect-corrected)
    for k in range(3):
        r = (t * 6 - k * 2.2)
        if r <= 0:
            continue
        latent = k > 0
        ch = RING_CHARS[latent]
        color = DIM_PURPLE if latent else PURPLE
        for a in range(0, 360, 4):
            x = int(CX + r * 2 * math.cos(math.radians(a)))
            y = int(CY + r * math.sin(math.radians(a)))
            if 0 <= x < W and 0 <= y < H:
                grid[y][x] = color + ch + RESET
    grid[CY][CX] = WHITE + "@" + RESET
    return "\n".join("".join(row) for row in grid)


def main() -> None:
    title = "C E R E B R O"
    sub = "every file · one mind"
    if not sys.stdout.isatty():
        rng = random.Random(7)
        neurons = [(rng.randrange(W), rng.randrange(H), 0.0) for _ in range(70)]
        print(frame(2.5, neurons))
        print(f"\n  {title}   —   {sub}\n  CEREBRO ONLINE")
        return
    rng = random.Random()
    neurons = [(rng.randrange(W), rng.randrange(H), rng.uniform(0.4, 3.2))
             for _ in range(70)]
    sys.stdout.write("\033[2J\033[?25l")
    t0 = time.time()
    try:
        while (t := time.time() - t0) < 3.6:
            sys.stdout.write("\033[H" + frame(t, neurons) + "\n\n")
            shown = title[: max(0, int((t - 0.5) * 8))]
            sys.stdout.write(f"  {WHITE}{shown}{RESET}\033[K\n")
            sys.stdout.write(f"  {DIM_PURPLE}{sub if t > 2.0 else ''}{RESET}\033[K\n")
            sys.stdout.flush()
            time.sleep(0.05)
        sys.stdout.write(f"\n  {PURPLE}CEREBRO ONLINE{RESET}\n")
    finally:
        sys.stdout.write("\033[?25h")
        sys.stdout.flush()


if __name__ == "__main__":
    try:
        main()
    except Exception:
        sys.exit(0)
