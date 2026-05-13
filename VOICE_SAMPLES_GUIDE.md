# How to record your voice sample

The model copies what it hears. Garbage in, garbage out. Spending 15 minutes
on a good sample makes everything you generate afterward sound dramatically
better.

## What to aim for

- **Length:** 20–30 seconds. Anything under 10s is too short; over 60s
  doesn't help and can hurt.
- **Style:** Read in the exact tone, pace, and energy you want your YouTube
  videos to sound like. If you plan to sound calm and explanatory, record
  calm and explanatory. If you plan to sound upbeat, record upbeat.
- **Single take:** Don't splice clips together. The model picks up on the
  acoustic environment, and stitched clips confuse it.
- **One speaker:** Just you. No background music, no other voices, no
  laugh-tracks.

## Recording setup

- **Microphone:** Any of these works well, ranked best to worst:
  - USB condenser mic (Blue Yeti, Shure MV7, Samson Q2U) — best
  - AirPods Pro / AirPods Max in a quiet room — good
  - Built-in MacBook mic — okay if the room is dead quiet
  - iPhone Voice Memos app held 6 inches from your mouth — surprisingly good
- **Room:** As quiet and non-echoey as possible. A closet full of clothes,
  or under a blanket fort, beats a big empty room.
- **Distance:** ~6 inches from your mouth. Closer = boomy, further = roomy.
- **Format:** Save as `.wav` (preferred) or `.mp3` at 24 kHz or higher.
  Voice Memos on iPhone exports as `.m4a`, which works too.

## What to read

Pick something natural that hits a variety of sounds. Here's a 25-second
script that covers most English phonemes — read it at the pace and tone you
want the AI to copy:

> "Hey everyone, welcome back to the channel. Today I want to walk through
> something I've been thinking about for a while. We'll cover the basics
> first, then get into a few practical examples. If you find this useful,
> drop a comment below and let me know what you'd like to see next. Quick
> question before we dive in — what's the one thing you wish someone had
> explained clearly when you got started?"

Or just read aloud from any book or article for ~25 seconds. Anything works
as long as it sounds like you, talking normally.

## Common mistakes

- **Reading too fast or too slow.** The model will copy your pace exactly,
  so a rushed sample produces rushed output forever.
- **Sounding bored or wooden.** If your sample is monotone, every generation
  will be monotone.
- **Background noise.** A buzzing fridge, traffic, AC, or kids in the next
  room will all bleed into generations as a faint hum or hiss.
- **Heavy compression.** Don't record into a Bluetooth headset or use heavy
  noise-reduction filters. Raw is better than over-processed.
- **Holding your breath.** Sounds weird, but most people freeze up reading
  a script. Breathe normally between sentences.

## After recording

1. Listen back. Does it sound like you on a good day? If not, re-record.
2. Trim silence from the start and end (QuickTime → Edit → Trim works fine).
3. Drop the file into the `samples/` folder.
4. Launch the app, upload it, give it a name like `me_calm` or `me_upbeat`,
   and generate a test clip to confirm quality before recording a full
   script.

## If quality isn't great after one sample

Record a second sample with **different content** but the **same style and
environment**, and combine them (concatenate into one file). The model
benefits slightly from more diverse phonemes — but only if the second
recording matches the first in tone and acoustics.
