import numpy as np
import soundfile as sf
import os
from scipy import signal
import random
import math
import streamlit as st
from io import BytesIO
import zipfile

# Constants
GOLDEN_RATIO = (1 + math.sqrt(5)) / 2  # Approximately 1.618

# Define Solfeggio frequencies for mood transitions with brain regions affected
MOOD_TRANSITION_TO_SOLFEGGIO = {
    ("anxious", "relaxed"): (396, "Amygdala, Thalamus - Releases fear and guilt, emotional stabilization"),
    ("anxious", "happy"): (417, "Amygdala, Prefrontal Cortex - Emotional healing, processing change"),
    ("anxious", "focused"): (528, "Frontal Cortex, Hippocampus - Transformation, DNA repair"),
    ("anxious", "creative"): (852, "Frontal Cortex, Pineal Gland - Intuitive, higher consciousness"),
    ("sleepy", "focused"): (741, "Prefrontal Cortex, Thalamus - Enhanced focus, clarity, alertness"),
    ("sleepy", "relaxed"): (528, "Frontal Cortex, Hippocampus - Healing and repair"),
    ("sleepy", "happy"): (639, "Amygdala, Prefrontal Cortex - Harmonizing relationships"),
    ("sleepy", "creative"): (852, "Frontal Cortex, Pineal Gland - Intuitive, higher consciousness"),
    ("focused", "happy"): (528, "Frontal Cortex, Hippocampus - Transformation, healing"),
    ("focused", "relaxed"): (639, "Amygdala, Prefrontal Cortex - Relaxation, emotional balance"),
    ("focused", "creative"): (852, "Frontal Cortex, Pineal Gland - Intuition, creative thinking"),
    ("focused", "sleepy"): (741, "Prefrontal Cortex, Thalamus - Enhanced focus, clarity, alertness"),
    ("happy", "relaxed"): (528, "Frontal Cortex, Hippocampus - Healing and transformation"),
    ("happy", "focused"): (528, "Frontal Cortex, Hippocampus - Transformation, healing"),
    ("happy", "creative"): (852, "Frontal Cortex, Pineal Gland - Higher consciousness, creativity"),
    ("relaxed", "focused"): (741, "Prefrontal Cortex - Problem solving, detoxification"),
    ("relaxed", "happy"): (528, "Frontal Cortex, Hippocampus - Healing, positive transformation"),
    ("relaxed", "creative"): (852, "Frontal Cortex, Pineal Gland - Higher consciousness, creativity"),
    ("relaxed", "sleepy"): (528, "Frontal Cortex, Hippocampus - Healing and repair"),
    ("creative", "happy"): (528, "Frontal Cortex, Hippocampus - Love and transformation for creativity"),
    ("creative", "relaxed"): (396, "Amygdala, Thalamus - Relaxation, fear release for creativity"),
    ("creative", "focused"): (852, "Frontal Cortex, Pineal Gland - Intuitive, higher consciousness"),
    ("creative", "sleepy"): (852, "Frontal Cortex, Pineal Gland - Intuitive, higher consciousness"),
    ("stressed", "relaxed"): (396, "Amygdala, Thalamus - Releases stress and tension"),
    ("stressed", "focused"): (741, "Prefrontal Cortex - Relieves stress for mental clarity"),
    ("stressed", "happy"): (639, "Amygdala, Prefrontal Cortex - Stress relief through connection"),
    ("stressed", "creative"): (417, "Amygdala, Prefrontal Cortex - Transforming stress into creativity"),
    ("unmotivated", "focused"): (741, "Prefrontal Cortex - Motivation and drive"),
    ("unmotivated", "energized"): (852, "Frontal Cortex, Pineal Gland - Energy and inspiration"),
    ("distracted", "focused"): (741, "Prefrontal Cortex, Thalamus - Mental clarity and concentration"),
    ("energized", "relaxed"): (396, "Amygdala, Thalamus - Calming excessive energy"),
}

# Define natural soundscapes for different moods
NATURAL_SOUNDS = {
    "relaxed": "ocean_waves",
    "focused": "white_noise",
    "happy": "birds_chirping",
    "creative": "rain_gentle",
    "sleepy": "night_sounds",
    "anxious": "stream_water",
    "stressed": "forest_ambience",
    "energized": "morning_birds",
    "unmotivated": "rain_medium",
    "distracted": "wind_leaves"
}

# Enhanced beat patterns with fractal relationships
BEAT_PATTERNS = {
    "alpha": (8, 12, "Relaxation, calmness, positive thinking", [1, 1, 2, 3, 5, 8]),  # Fibonacci sequence
    "theta": (4, 8, "Deep relaxation, meditation, creativity", [1, 2, 4, 8, 16]),  # Powers of 2
    "delta": (0.5, 4, "Deep sleep, healing, regeneration", [1, 3, 9, 27]),  # Powers of 3
    "beta": (12, 30, "Focus, alertness, concentration", [5, 10, 20, 40]),  # Golden ratio inspired
    "gamma": (30, 100, "Higher cognitive processing, peak concentration", [10, 20, 30, 50, 80])  # Fibonacci
}


# Function to generate golden ratio related frequencies
def generate_golden_ratio_frequencies(base_freq, num_harmonics=5):
    """Generate frequencies related by the golden ratio"""
    return [base_freq * (GOLDEN_RATIO**i) for i in range(num_harmonics)]

# Function to generate fractal beat pattern
def generate_fractal_beats(base_freq, pattern, duration, sample_rate=44100):
    """Generate a fractal beat pattern using the given sequence"""
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    wave = np.zeros_like(t)
    
    for i, ratio in enumerate(pattern):
        freq = base_freq * ratio
        amplitude = 0.5 / (i + 1)  # Reduce amplitude for higher ratios
        wave += amplitude * np.sin(2 * np.pi * freq * t)
    
    return wave

# Function to generate white noise
def generate_noise(noise_type, duration, sample_rate=44100, amplitude=0.05):
    samples = int(duration * sample_rate)
    
    if noise_type == "white":
        noise = np.random.normal(0, amplitude, samples)
    elif noise_type == "pink":
        white_noise = np.random.normal(0, amplitude, samples)
        # Simple approximation of pink noise using a low-pass filter
        b, a = signal.butter(1, 0.1)
        noise = signal.lfilter(b, a, white_noise)
    elif noise_type == "brown":
        white_noise = np.random.normal(0, amplitude, samples)
        # Simple approximation of brown noise using a stronger low-pass filter
        b, a = signal.butter(1, 0.05)
        noise = signal.lfilter(b, a, white_noise)
    else:
        noise = np.random.normal(0, amplitude, samples)
        
    return noise

# Function to generate Shepard tone
def generate_shepard_tone(base_freq, duration, sample_rate=44100, octaves=3):
    """Generate a Shepard tone (auditory illusion of infinite ascent/descent)"""
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    tone = np.zeros_like(t)
    
    for i in range(octaves):
        freq = base_freq * (2 ** i)
        # Apply a bell curve envelope to each octave
        envelope = np.exp(-0.5 * ((i - octaves/2) / (octaves/4)) ** 2)
        tone += envelope * np.sin(2 * np.pi * freq * t)
    
    # Apply rising pitch illusion
    rising = np.linspace(1, 2, len(t))  # Linear frequency increase
    tone *= rising
    
    return tone * 0.3  # Reduce amplitude

# Function to generate binaural chord progression
def generate_binaural_chord(base_freq, chord_type, duration, sample_rate=44100):
    """Generate a binaural chord progression using golden ratio intervals"""
    if chord_type == "golden":
        # Create chord from golden ratio frequencies
        frequencies = [base_freq * (GOLDEN_RATIO**i) for i in [0, 1, 2]]
    elif chord_type == "fractal":
        # Create chord from fractal sequence
        frequencies = [base_freq * ratio for ratio in [1, 2, 3, 5]]
    else:  # default to major chord
        frequencies = [base_freq, base_freq * 1.25, base_freq * 1.5]
    
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    chord = np.zeros_like(t)
    
    for freq in frequencies:
        # Create binaural beats for each frequency in the chord
        beat_freq = random.choice([4, 8, 12])  # Random brainwave frequency
        left = np.sin(2 * np.pi * (freq - beat_freq/2) * t)
        right = np.sin(2 * np.pi * (freq + beat_freq/2) * t)
        chord += (left + right) * 0.2  # Add to chord with reduced amplitude
    
    return chord

# Enhanced sine wave generator with golden ratio harmonics
def generate_sine_wave(frequency, duration, sample_rate=44100, amplitude=0.5, harmonics="golden"):
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    wave = amplitude * np.sin(2 * np.pi * frequency * t)
    
    # Add harmonics based on type
    if harmonics == "golden":
        golden_harmonics = generate_golden_ratio_frequencies(frequency, 3)
        for i, h_freq in enumerate(golden_harmonics[1:]):  # Skip base frequency
            wave += (amplitude * 0.3 / (i+1)) * np.sin(2 * np.pi * h_freq * t)
    elif harmonics == "fractal":
        fractal_harmonics = [frequency * ratio for ratio in [2, 3, 5, 8]]
        for i, h_freq in enumerate(fractal_harmonics):
            wave += (amplitude * 0.25 / (i+1)) * np.sin(2 * np.pi * h_freq * t)
    elif isinstance(harmonics, dict):  # Custom harmonics
        for harmonic_num, harmonic_amp in harmonics.items():
            wave += harmonic_amp * np.sin(2 * np.pi * frequency * harmonic_num * t)
    
    return wave

# Enhanced binaural beats generator with fractal patterns
def generate_binaural_beat_stereo(base_freq, beat_freq, duration, sample_rate=44100, wave_type="sine", pattern="fractal"):
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    
    left_freq = base_freq - beat_freq / 2
    right_freq = base_freq + beat_freq / 2
    
    if pattern == "fractal":
        # Generate fractal beat pattern for left and right channels
        left_wave = generate_fractal_beats(left_freq, [1, 2, 3, 5], duration, sample_rate)
        right_wave = generate_fractal_beats(right_freq, [1, 2, 3, 5], duration, sample_rate)
    else:
        if wave_type == "sine":
            left_wave = generate_sine_wave(left_freq, duration, sample_rate, harmonics="golden")
            right_wave = generate_sine_wave(right_freq, duration, sample_rate, harmonics="golden")
        elif wave_type == "triangle":
            left_wave = 0.5 * signal.sawtooth(2 * np.pi * left_freq * t, 0.5)
            right_wave = 0.5 * signal.sawtooth(2 * np.pi * right_freq * t, 0.5)
        elif wave_type == "square":
            left_wave = 0.3 * signal.square(2 * np.pi * left_freq * t)
            right_wave = 0.3 * signal.square(2 * np.pi * right_freq * t)
        else:  # default to sine
            left_wave = generate_sine_wave(left_freq, duration, sample_rate)
            right_wave = generate_sine_wave(right_freq, duration, sample_rate)
    
    return left_wave, right_wave

# Function to apply amplitude modulation
def apply_amplitude_modulation(carrier, mod_freq, depth=0.3, sample_rate=44100):
    t = np.linspace(0, len(carrier)/sample_rate, len(carrier), endpoint=False)
    modulator = 1 + depth * np.sin(2 * np.pi * mod_freq * t)
    return carrier * modulator


# Function to apply fade in and fade out
def apply_fade(signal, fade_duration, sample_rate=44100):
    fade_samples = int(fade_duration * sample_rate)
    fade_in = np.linspace(0, 1, fade_samples)
    fade_out = np.linspace(1, 0, fade_samples)
    signal[:fade_samples] *= fade_in
    signal[-fade_samples:] *= fade_out
    return signal


# Function to simulate nature sounds (placeholder representations)
def generate_nature_sound(sound_type, duration, sample_rate=44100, amplitude=0.15):
    samples = int(duration * sample_rate)
    
    if sound_type == "ocean_waves":
        # Ocean waves - brown noise with slow amplitude modulation
        noise = generate_noise("brown", duration, sample_rate, amplitude)
        return apply_amplitude_modulation(noise, 0.1, 0.7, sample_rate)
    
    elif sound_type == "white_noise":
        # White noise with very subtle modulation
        noise = generate_noise("white", duration, sample_rate, amplitude*0.6)
        return apply_amplitude_modulation(noise, 0.05, 0.2, sample_rate)
    
    elif sound_type == "birds_chirping":
        # Birds chirping - high frequency modulated tones with random intervals
        base = np.zeros(samples)
        for _ in range(30):  # Number of chirps
            start = np.random.randint(0, samples - int(0.3 * sample_rate))
            chirp_len = int(np.random.uniform(0.05, 0.3) * sample_rate)
            chirp_freq = np.random.uniform(2000, 4000)
            chirp = generate_sine_wave(chirp_freq, chirp_len/sample_rate, sample_rate, amplitude*0.4)
            chirp = apply_fade(chirp, 0.02, sample_rate)
            end = min(start + len(chirp), samples)  # Use actual length of chirp
            chirp_segment = chirp[:end-start]  # Take only the needed portion
            base[start:end] += chirp_segment
        return base
    
    elif sound_type == "rain_gentle":
        # Gentle rain - filtered noise with droplet effects
        noise = generate_noise("pink", duration, sample_rate, amplitude*0.5)
        for _ in range(200):  # Number of droplets
            start = np.random.randint(0, samples - int(0.1 * sample_rate))
            drop_len = int(0.01 * sample_rate)
            drop = generate_noise("white", drop_len/sample_rate, sample_rate, amplitude*0.8)
            drop = apply_fade(drop, 0.005, sample_rate)
            end = min(start + len(drop), samples)  # Use actual length of drop
            drop_segment = drop[:end-start]  # Take only the needed portion
            noise[start:end] += drop_segment
        return noise
    
    
    elif sound_type == "night_sounds":
        # Night sounds - low frequency ambient noise with occasional cricket chirps
        base = generate_noise("brown", duration, sample_rate, amplitude*0.3)
        for _ in range(50):  # Number of cricket chirps
            start = np.random.randint(0, samples - int(0.2 * sample_rate))
            chirp_len = int(0.05 * sample_rate)
            chirp = generate_sine_wave(4500, chirp_len/sample_rate, sample_rate, amplitude*0.15)
            chirp = apply_fade(chirp, 0.01, sample_rate)
            chirp = apply_amplitude_modulation(chirp, 30, 0.9, sample_rate)
            end = min(start + len(chirp), samples)  # Use actual length of chirp
            chirp_segment = chirp[:end-start]  # Take only the needed portion
            base[start:end] += chirp_segment
        return base
    
    elif sound_type == "stream_water":
        # Stream water - modulated white and pink noise
        noise = generate_noise("pink", duration, sample_rate, amplitude*0.4)
        noise += generate_noise("white", duration, sample_rate, amplitude*0.15)
        return apply_amplitude_modulation(noise, 0.2, 0.4, sample_rate)
    
    elif sound_type == "forest_ambience":
        # Forest ambience - mix of wind, distant birds, and rustling
        base = generate_noise("pink", duration, sample_rate, amplitude*0.3)
        for _ in range(20):
            start = np.random.randint(0, samples - int(0.5 * sample_rate))
            sound_len = int(np.random.uniform(0.2, 0.5) * sample_rate)
            freq = np.random.uniform(1500, 3000)
            sound = generate_sine_wave(freq, sound_len/sample_rate, sample_rate, amplitude*0.1)
            sound = apply_fade(sound, 0.05, sample_rate)
            end = min(start + len(sound), samples)  # Use actual length of sound
            sound_segment = sound[:end-start]  # Take only the needed portion
            base[start:end] += sound_segment
        return base
    
    elif sound_type == "morning_birds":
        # Morning birds - higher pitched, more frequent bird sounds
        base = np.zeros(samples)
        for _ in range(50):
            start = np.random.randint(0, samples - int(0.3 * sample_rate))
            chirp_len = int(np.random.uniform(0.1, 0.3) * sample_rate)
            chirp_freq = np.random.uniform(2500, 5000)
            chirp = generate_sine_wave(chirp_freq, chirp_len/sample_rate, sample_rate, amplitude*0.3)
            chirp = apply_fade(chirp, 0.03, sample_rate)
            end = min(start + len(chirp), samples)  # Use actual length of chirp
            chirp_segment = chirp[:end-start]  # Take only the needed portion
            base[start:end] += chirp_segment
        return base
    
    elif sound_type == "rain_medium":
        # Medium rain - more intense than gentle rain
        noise = generate_noise("pink", duration, sample_rate, amplitude*0.6)
        for _ in range(400):
            start = np.random.randint(0, samples - int(0.1 * sample_rate))
            drop_len = int(0.015 * sample_rate)
            drop = generate_noise("white", drop_len/sample_rate, sample_rate, amplitude)
            drop = apply_fade(drop, 0.005, sample_rate)
            end = min(start + len(drop), samples)  # Use actual length of drop
            drop_segment = drop[:end-start]  # Take only the needed portion
            noise[start:end] += drop_segment
        return noise
    
    elif sound_type == "wind_leaves":
        # Wind through leaves
        base = generate_noise("pink", duration, sample_rate, amplitude*0.4)
        base = apply_amplitude_modulation(base, 0.3, 0.6, sample_rate)
        for _ in range(30):
            start = np.random.randint(0, samples - int(0.4 * sample_rate))
            sound_len = int(np.random.uniform(0.1, 0.4) * sample_rate)
            sound = generate_noise("pink", sound_len/sample_rate, sample_rate, amplitude*0.2)
            sound = apply_fade(sound, 0.05, sample_rate)
            end = min(start + len(sound), samples)  # Use actual length of sound
            sound_segment = sound[:end-start]  # Take only the needed portion
            base[start:end] += sound_segment
        return base
    
    else:
        # Default to gentle white noise
        return generate_noise("white", duration, sample_rate, amplitude*0.3)

# Function to add slow frequency sliding (for entrainment)
def apply_frequency_slide(start_freq, end_freq, duration, amplitude=0.5, sample_rate=44100):
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    freq = np.linspace(start_freq, end_freq, len(t))
    phase = 2 * np.pi * np.cumsum(freq) / sample_rate
    return amplitude * np.sin(phase)

# Enhanced dynamic binaural beats with Shepard tones and chord progressions
def create_dynamic_binaural(carrier_freq, target_brain_state, duration, sample_rate=44100):
    min_beat, max_beat, _, pattern = BEAT_PATTERNS[target_brain_state]
    
    initial_beat = max_beat
    target_beat = min_beat + (max_beat - min_beat) * 0.3
    
    left_channel = np.zeros(int(sample_rate * duration))
    right_channel = np.zeros(int(sample_rate * duration))
    
    # Primary carrier wave with slide and golden ratio harmonics
    left_slide = apply_frequency_slide(carrier_freq - initial_beat/2, carrier_freq - target_beat/2, 
                                     duration, amplitude=0.3, sample_rate=sample_rate)
    right_slide = apply_frequency_slide(carrier_freq + initial_beat/2, carrier_freq + target_beat/2, 
                                      duration, amplitude=0.3, sample_rate=sample_rate)
    
    left_channel += left_slide
    right_channel += right_slide
    
    # Add fractal beat pattern layer
    left_fractal = generate_fractal_beats(carrier_freq * 0.8, pattern, duration, sample_rate)
    right_fractal = generate_fractal_beats(carrier_freq * 1.2, pattern, duration, sample_rate)
    left_channel += left_fractal * 0.2
    right_channel += right_fractal * 0.2
    
    # Add Shepard tone layer for enhanced effect
    shepard_tone = generate_shepard_tone(carrier_freq/4, duration, sample_rate)
    left_channel += shepard_tone * 0.15
    right_channel += shepard_tone * 0.15
    
    # Add binaural chord progression
    chord = generate_binaural_chord(carrier_freq, "golden", duration, sample_rate)
    left_channel += chord * 0.25
    right_channel += chord * 0.25
    
    # Add subtle pink noise
    noise_left = generate_noise("pink", duration, sample_rate, 0.02)
    noise_right = generate_noise("pink", duration, sample_rate, 0.02)
    
    left_channel += noise_left
    right_channel += noise_right
    
    return left_channel, right_channel

def create_combined_track(mood_from, mood_to, duration=180, sample_rate=44100, quality="standard"):
    if (mood_from, mood_to) not in MOOD_TRANSITION_TO_SOLFEGGIO:
        st.error(f"Unknown mood transition: {mood_from} to {mood_to}")
        return None
    
    if quality == "high":
        sample_rate = 48000
    
    solfeggio_freq, brain_target = MOOD_TRANSITION_TO_SOLFEGGIO[(mood_from, mood_to)]
    
    if "relaxed" in (mood_from, mood_to) or "sleepy" in (mood_from, mood_to):
        target_brain_state = "alpha" if "relaxed" in (mood_from, mood_to) else "theta"
    elif "focused" in (mood_from, mood_to):
        target_brain_state = "beta"
    elif "creative" in (mood_from, mood_to):
        target_brain_state = "theta"
    else:
        target_brain_state = "alpha"
    
    # Generate solfeggio wave with golden ratio harmonics
    solfeggio_wave = generate_sine_wave(solfeggio_freq, duration, sample_rate, amplitude=0.2, harmonics="golden")
    
    # Generate enhanced dynamic binaural beats
    left_binaural, right_binaural = create_dynamic_binaural(solfeggio_freq, target_brain_state, duration, sample_rate)
    
    # Add nature sounds
    target_sound_type = NATURAL_SOUNDS.get(mood_to, "white_noise")
    nature_sound = generate_nature_sound(target_sound_type, duration, sample_rate)
    
    # Volume envelopes
    solfeggio_envelope = np.ones(int(sample_rate * duration))
    solfeggio_envelope = apply_fade(solfeggio_envelope, fade_duration=5, sample_rate=sample_rate)
    
    nature_envelope = np.ones(int(sample_rate * duration))
    nature_envelope[:int(sample_rate * 20)] *= np.linspace(0, 1, int(sample_rate * 20))
    
    # Final mix with all elements
    left_channel = (left_binaural + solfeggio_wave * solfeggio_envelope + nature_sound * 0.7 * nature_envelope)
    right_channel = (right_binaural + solfeggio_wave * solfeggio_envelope + nature_sound * 0.7 * nature_envelope)
    
    # Apply master fade
    left_channel = apply_fade(left_channel, fade_duration=5, sample_rate=sample_rate)
    right_channel = apply_fade(right_channel, fade_duration=5, sample_rate=sample_rate)
    
    # Normalize
    max_amp = max(np.max(np.abs(left_channel)), np.max(np.abs(right_channel)))
    if max_amp > 0.95:
        left_channel = left_channel * (0.95 / max_amp)
        right_channel = right_channel * (0.95 / max_amp)
    
    stereo_audio = np.stack([left_channel, right_channel], axis=-1)
    
    # Create in-memory file
    audio_bytes = BytesIO()
    sf.write(audio_bytes, stereo_audio, sample_rate, format='WAV')
    audio_bytes.seek(0)
    
    # Display information
    st.success(f"✅ Successfully generated enhanced beats for transition from '{mood_from}' to '{mood_to}'")
    st.write(f"🎵 Solfeggio Frequency Used: {solfeggio_freq} Hz (with Golden Ratio harmonics)")
    st.write(f"🧠 Brain Regions Targeted: {brain_target}")
    st.write(f"🌊 Nature Sound Added: {target_sound_type}")
    st.write(f"⚡ Brain Wave Pattern: {target_brain_state} ({BEAT_PATTERNS[target_brain_state][2]})")
    st.write(f"✨ Features: Golden Ratio Harmonics, Fractal Beat Patterns, Binaural Chords, Shepard Tones")
    st.write(f"⏱️ Duration: {duration//60} minutes")
    
    return audio_bytes

def create_meditation_sequence(sequence_name, mood_sequence, durations=None, sample_rate=44100, quality="standard"):
    if durations is None:
        durations = [180] * len(mood_sequence)
    
    if len(mood_sequence) != len(durations):
        st.error("Error: mood_sequence and durations must have the same length")
        return None
    
    all_files = []
    st.write(f"🧘 Creating meditation sequence: {sequence_name}")
    
    for i, (mood_pair, duration) in enumerate(zip(mood_sequence, durations)):
        mood_from, mood_to = mood_pair
        st.write(f"📋 Segment {i+1}/{len(mood_sequence)}: {mood_from} → {mood_to} ({duration//60} min)")
        audio_bytes = create_combined_track(mood_from, mood_to, duration=duration, 
                                         sample_rate=sample_rate, quality=quality)
        if audio_bytes:
            all_files.append((f"{mood_from}_to_{mood_to}_{duration//60}min.wav", audio_bytes))
    
    if not all_files:
        return None
    
    # Create sequence info
    sequence_info = f"Meditation Sequence: {sequence_name}\n"
    sequence_info += "=" * 50 + "\n\n"
    total_duration = sum(durations) // 60
    sequence_info += f"Total Duration: {total_duration} minutes\n\n"
    
    for i, (mood_pair, duration, (filename, _)) in enumerate(zip(mood_sequence, durations, all_files)):
        mood_from, mood_to = mood_pair
        sequence_info += f"Segment {i+1}: {mood_from.capitalize()} → {mood_to.capitalize()} " + \
                        f"({duration // 60} minutes)\n"
        solfeggio_freq, brain_target = MOOD_TRANSITION_TO_SOLFEGGIO[mood_pair]
        sequence_info += f"  - Solfeggio: {solfeggio_freq} Hz\n"
        sequence_info += f"  - Target: {brain_target}\n"
        sequence_info += f"  - File: {filename}\n\n"
    
    st.success(f"✅ Meditation sequence '{sequence_name}' created successfully!")
    st.write(f"⏱️ Total duration: {total_duration} minutes")
    
    return all_files, sequence_info

def main():
    st.title("Rewire")
    
    option = st.radio("Choose an option:", ["Single Mood Transition", "Meditation Sequence"])
    
    if option == "Single Mood Transition":
        st.header("Single Mood Transition")
        
        col1, col2 = st.columns(2)
        with col1:
            mood_from = st.selectbox(
                "Current mood:",
                options=["anxious", "sleepy", "focused", "happy", "stressed", 
                         "relaxed", "creative", "unmotivated", "distracted", "energized"]
            )
        with col2:
            mood_to = st.selectbox(
                "Desired mood:",
                options=["relaxed", "focused", "happy", "creative", "sleepy", "energized"],
                index=0 if mood_from != "relaxed" else 1
            )
        
        duration = st.slider("Duration (minutes):", 1, 30, 10)
        quality = st.radio("Audio quality:", ["Standard", "High"])
        
        if st.button("Generate Audio"):
            if mood_from == mood_to:
                st.warning("Please select different starting and target moods.")
            else:
                with st.spinner("Generating your audio... This may take a moment..."):
                    audio_bytes = create_combined_track(
                        mood_from, 
                        mood_to, 
                        duration=duration*60, 
                        quality=quality.lower()
                    )
                    if audio_bytes:
                        st.audio(audio_bytes, format="audio/wav")
                        st.download_button(
                            label="Download Audio",
                            data=audio_bytes,
                            file_name=f"{mood_from}_to_{mood_to}_{duration}min.wav",
                            mime="audio/wav"
                        )
    
    else:  # Meditation Sequence
        st.header("Create Meditation Sequence")
        
        sequence_name = st.text_input("Sequence name:", "My Meditation")
        
        st.subheader("Sequence Segments")
        num_segments = st.slider("Number of segments:", 2, 5, 3)
        
        mood_sequence = []
        durations = []
        
        for i in range(num_segments):
            st.write(f"### Segment {i+1}")
            col1, col2 = st.columns(2)
            with col1:
                mood_from = st.selectbox(
                    f"Starting mood for segment {i+1}:",
                    options=["anxious", "sleepy", "focused", "happy", "stressed", 
                             "relaxed", "creative", "unmotivated", "distracted", "energized"],
                    key=f"from_{i}"
                )
            with col2:
                mood_to = st.selectbox(
                    f"Target mood for segment {i+1}:",
                    options=["relaxed", "focused", "happy", "creative", "sleepy", "energized"],
                    index=0 if mood_from != "relaxed" else 1,
                    key=f"to_{i}"
                )
            
            duration = st.slider(
                f"Duration for segment {i+1} (minutes):",
                1, 15, 5,
                key=f"dur_{i}"
            )
            
            mood_sequence.append((mood_from, mood_to))
            durations.append(duration * 60)
        
        quality = st.radio("Audio quality for sequence:", ["Standard", "High"])
        
        if st.button("Generate Meditation Sequence"):
            with st.spinner("Generating your meditation sequence... This may take several minutes..."):
                result = create_meditation_sequence(
                    sequence_name,
                    mood_sequence,
                    durations,
                    quality=quality.lower()
                )
                
                if result:
                    all_files, sequence_info = result
                    
                    # Create zip file of all audio segments
                    zip_bytes = BytesIO()
                    with zipfile.ZipFile(zip_bytes, 'w') as zip_file:
                        for filename, audio_bytes in all_files:
                            zip_file.writestr(filename, audio_bytes.getvalue())
                        zip_file.writestr(f"{sequence_name}_info.txt", sequence_info)
                    zip_bytes.seek(0)
                    
                    # Download button for the zip file
                    st.download_button(
                        label="Download Full Sequence (ZIP)",
                        data=zip_bytes,
                        file_name=f"{sequence_name}.zip",
                        mime="application/zip"
                    )
                    
                    # Display sequence info
                    st.subheader("Sequence Information")
                    st.text(sequence_info)
                    
                    # Play individual segments
                    st.subheader("Sequence Segments")
                    for filename, audio_bytes in all_files:
                        st.write(f"**{filename}**")
                        st.audio(audio_bytes, format="audio/wav")

if __name__ == "__main__":
    main()
