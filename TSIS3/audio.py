"""
audio.py
Procedural sound generation — no external audio files needed.
All sounds are synthesised with pygame.sndarray + numpy (or fallback).
Call AudioManager.init() once after pygame.mixer.init().
"""

import pygame
import math
import array


# ── low-level wave builders (pure Python, no numpy required) ─────────────────

SAMPLE_RATE = 22050   # Hz
CHANNELS    = 1


def _make_sound(samples: list[float]) -> pygame.mixer.Sound:
    """Convert a list of floats [-1,1] to a pygame Sound."""
    # 16-bit signed, mono
    buf = array.array("h", (int(max(-32767, min(32767, s * 32767))) for s in samples))
    snd = pygame.mixer.Sound(buffer=buf)
    return snd


def _sine(freq: float, dur: float, vol=1.0, fade_out=True) -> list[float]:
    n = int(SAMPLE_RATE * dur)
    out = []
    for i in range(n):
        t = i / SAMPLE_RATE
        v = math.sin(2 * math.pi * freq * t)
        if fade_out:
            env = 1.0 - i / n
        else:
            env = min(1.0, i / (SAMPLE_RATE * 0.01))   # fast attack
        out.append(v * env * vol)
    return out


def _square(freq: float, dur: float, vol=0.4, duty=0.5) -> list[float]:
    n = int(SAMPLE_RATE * dur)
    period = SAMPLE_RATE / freq
    out = []
    for i in range(n):
        phase = (i % period) / period
        v = 1.0 if phase < duty else -1.0
        env = 1.0 - i / n
        out.append(v * env * vol)
    return out


def _noise(dur: float, vol=0.5) -> list[float]:
    import random
    n = int(SAMPLE_RATE * dur)
    out = []
    prev = 0.0
    for i in range(n):
        # low-pass filtered noise (more rumble-y)
        raw  = random.uniform(-1, 1)
        prev = prev * 0.7 + raw * 0.3
        env  = 1.0 - i / n
        out.append(prev * env * vol)
    return out


def _mix(*channels) -> list[float]:
    """Mix multiple sample lists together (same length)."""
    length = max(len(c) for c in channels)
    out = [0.0] * length
    for ch in channels:
        for i, s in enumerate(ch):
            out[i] += s
    # normalise
    peak = max(abs(v) for v in out) or 1.0
    if peak > 1.0:
        out = [v / peak for v in out]
    return out


# ── sound recipes ────────────────────────────────────────────────────────────

def _build_coin():
    """Bright ding: two sine notes."""
    a = _sine(880, 0.08, 0.9)
    b = _sine(1320, 0.10, 0.7)
    # b starts slightly later
    delay = int(SAMPLE_RATE * 0.04)
    combined = a + [0.0] * (len(b) + delay - len(a))
    for i, v in enumerate(b):
        combined[delay + i] += v
    return _make_sound(combined)


def _build_crash():
    """Low thud + noise burst."""
    noise  = _noise(0.35, 0.8)
    thud   = _sine(80, 0.25, 0.9)
    thud2  = _sine(55, 0.30, 0.6)
    return _make_sound(_mix(noise, thud, thud2))


def _build_powerup():
    """Ascending arpeggio."""
    notes = [523, 659, 784, 1047]   # C5 E5 G5 C6
    samples: list[float] = []
    for freq in notes:
        samples += _sine(freq, 0.08, 0.8, fade_out=False)
    # overall fade
    n = len(samples)
    samples = [s * (1 - i/n) for i, s in enumerate(samples)]
    return _make_sound(samples)


def _build_obstacle():
    """Dull bump."""
    noise = _noise(0.18, 0.6)
    low   = _sine(120, 0.18, 0.7)
    return _make_sound(_mix(noise, low))


def _build_engine_loop():
    """
    Short loopable engine rumble built from detuned square waves.
    pygame will loop it seamlessly.
    """
    # two slightly detuned squares → beating effect
    a = _square(90,  0.5, 0.25, duty=0.4)
    b = _square(93,  0.5, 0.20, duty=0.5)
    c = _square(45,  0.5, 0.15, duty=0.3)   # sub octave
    mixed = _mix(a, b, c)
    # remove the fade-out so it can loop cleanly
    n  = len(mixed)
    # crossfade last 5 % into first 5 % to avoid click
    fade = int(n * 0.05)
    for i in range(fade):
        t = i / fade
        mixed[i]     = mixed[i] * t + mixed[n-fade+i] * (1-t)
    return _make_sound(mixed[:n-fade])


def _build_nitro():
    """Rising whoosh."""
    dur = 0.4
    n   = int(SAMPLE_RATE * dur)
    out = []
    for i in range(n):
        t    = i / SAMPLE_RATE
        freq = 200 + (i/n) * 800          # sweep up
        v    = math.sin(2*math.pi*freq*t)
        env  = math.sin(math.pi * i / n)  # bell envelope
        out.append(v * env * 0.6)
    return _make_sound(out)


def _build_finish():
    """Short fanfare."""
    melody = [523, 659, 784, 659, 784, 1047]
    durs   = [0.12, 0.10, 0.12, 0.10, 0.10, 0.28]
    samples: list[float] = []
    for freq, d in zip(melody, durs):
        chunk = _sine(freq, d, 0.85, fade_out=False)
        samples += chunk
    return _make_sound(samples)


# ── public AudioManager ───────────────────────────────────────────────────────

class AudioManager:
    """Singleton-style manager.  Call AudioManager.init() once."""

    _ready    = False
    _enabled  = True
    _volume   = 0.7

    # sound slots
    coin     : pygame.mixer.Sound | None = None
    crash    : pygame.mixer.Sound | None = None
    powerup  : pygame.mixer.Sound | None = None
    obstacle : pygame.mixer.Sound | None = None
    nitro    : pygame.mixer.Sound | None = None
    finish   : pygame.mixer.Sound | None = None
    engine   : pygame.mixer.Sound | None = None

    # dedicated channel for looping engine
    _engine_ch: pygame.mixer.Channel | None = None

    @classmethod
    def init(cls, enabled: bool = True, volume: float = 0.7):
        cls._enabled = enabled
        cls._volume  = volume

        if not pygame.mixer.get_init():
            return

        try:
            pygame.mixer.set_num_channels(16)

            cls.coin     = _build_coin()
            cls.crash    = _build_crash()
            cls.powerup  = _build_powerup()
            cls.obstacle = _build_obstacle()
            cls.nitro    = _build_nitro()
            cls.finish   = _build_finish()
            cls.engine   = _build_engine_loop()

            cls._apply_volumes()
            cls._ready = True
        except Exception as e:
            print(f"[audio] init failed: {e}")
            cls._ready = False

    @classmethod
    def _apply_volumes(cls):
        vol = cls._volume if cls._enabled else 0.0
        for snd in (cls.coin, cls.crash, cls.powerup,
                    cls.obstacle, cls.nitro, cls.finish):
            if snd:
                snd.set_volume(vol)
        if cls.engine:
            cls.engine.set_volume(vol * 0.35)   # engine softer

    @classmethod
    def set_enabled(cls, enabled: bool):
        cls._enabled = enabled
        cls._apply_volumes()
        if not enabled:
            cls.stop_engine()

    @classmethod
    def play(cls, sound: pygame.mixer.Sound | None):
        if cls._ready and cls._enabled and sound:
            sound.play()

    # -- convenience wrappers --------------------------------------------------
    @classmethod
    def play_coin(cls):     cls.play(cls.coin)

    @classmethod
    def play_crash(cls):    cls.play(cls.crash)

    @classmethod
    def play_powerup(cls):  cls.play(cls.powerup)

    @classmethod
    def play_obstacle(cls): cls.play(cls.obstacle)

    @classmethod
    def play_nitro(cls):    cls.play(cls.nitro)

    @classmethod
    def play_finish(cls):   cls.play(cls.finish)

    @classmethod
    def start_engine(cls):
        if not (cls._ready and cls._enabled and cls.engine):
            return
        if cls._engine_ch is None or not cls._engine_ch.get_busy():
            cls._engine_ch = cls.engine.play(loops=-1)   # infinite loop

    @classmethod
    def stop_engine(cls):
        if cls._engine_ch:
            cls._engine_ch.stop()

    @classmethod
    def set_engine_pitch(cls, speed_factor: float):
        """
        Fake 'pitch' by adjusting engine volume — higher speed = slightly louder rumble.
        True pitch shifting isn't easy in pygame, so we simulate it with volume.
        """
        if cls._engine_ch and cls._enabled:
            vol = min(1.0, cls._volume * 0.35 * (0.7 + speed_factor * 0.3))
            cls._engine_ch.set_volume(vol)
