#!/usr/bin/env python

import asyncio
import aiohttp
import websockets
import logging
logging.basicConfig(level=logging.INFO)


# Counter for the number of times the timer is triggered
counter = 0


async def process_partial_audio(data_messages):
    if data_messages:
        wav_data = format_audio_data(data_messages)

        # Save audio snippet locally
        global counter  # sorry
        save_audio_file(data_messages, suffix=counter)
        counter += 1

        # Send file for transcription
        async with aiohttp.ClientSession() as session:
            # async with session.post("http://host.docker.internal:5000/transcribe", data=wav_data, headers={
            async with session.post("http://localhost:5000/transcribe", data=wav_data, headers={
                "Content-Type": "application/octet-stream",
                "Content-Length": len(wav_data)
            }) as response:
                logging.info(f"Status: {response.status}")
                logging.info(f"Headers: {response.headers}")
                text = await response.text()
                logging.info(f"Body: {text}")

        # # Clean audio buffer
        # data_messages.clear()


async def timer(data_messages, delay=5):
    while True:
        await asyncio.sleep(delay)
        logging.info('Timer triggered.')
        await process_partial_audio(data_messages)


async def audio_handler(websocket):
    # Array to store the data messages
    data_messages = []
    data_messages_whole_audio = []

    timer_task = asyncio.create_task(timer(data_messages))

    try:
        async for message in websocket:
            # Store the data message in the array
            data_messages.append(message)
            data_messages_whole_audio.append(message)

            raw_data_len = consume(message)
            logging.debug(f">>> Received message with {raw_data_len} bytes")
    except websockets.ConnectionClosed:
        timer_task.cancel()
        logging.info(f"Closing connection from client.")
        save_audio_file(data_messages_whole_audio)


def consume(message):
    return len(message)


def format_audio_data(messages):
    audio_data = b''.join(messages)  # Concatenate the data messages
    header = create_wav_header(audio_data)
    wav_data = header + audio_data
    return wav_data


def save_audio_file(audio_buffer, suffix=None):
    wav_data = format_audio_data(audio_buffer)
    filename = f"sound_{suffix}.wav" if suffix else "sound.wav"
    with open(filename, "wb") as f:
        f.write(wav_data)
    logging.info(f"File {filename} saved.")


def create_wav_header(audio_data):
    # Parse the data to extract the necessary information for the WAV file header and metadata
    audio_length = len(audio_data)  # length of the audio data in bytes
    sample_rate = 96000  # sample rate in Hz
    channels = 1  # number of channels (1 for mono, 2 for stereo)
    bits_per_sample = 16  # bits per sample (8 or 16)

    # Calculate the number of bytes per sample
    bytes_per_sample = bits_per_sample // 8

    # Calculate the number of samples in the audio data
    num_samples = audio_length // bytes_per_sample

    # Calculate the audio duration in seconds
    duration = num_samples / sample_rate

    # Calculate the number of bytes in the header
    header_length = 44

    # Create the WAV file header
    header = bytearray(header_length)
    header[0:4] = b'RIFF'  # Chunk ID
    header[4:8] = (audio_length + header_length - 8).to_bytes(4, 'little')  # Chunk Size
    header[8:12] = b'WAVE'  # Format
    header[12:16] = b'fmt '  # Subchunk 1 ID
    header[16:20] = (16).to_bytes(4, 'little')  # Subchunk 1 Size
    header[20:22] = (1).to_bytes(2, 'little')  # Audio Format (1 for PCM)
    header[22:24] = channels.to_bytes(2, 'little')  # Number of Channels
    header[24:28] = sample_rate.to_bytes(4, 'little')  # Sample Rate
    header[28:32] = (sample_rate * channels * bytes_per_sample).to_bytes(4, 'little')  # Byte Rate
    header[32:34] = (channels * bytes_per_sample).to_bytes(2, 'little')  # Block Align
    header[34:36] = bits_per_sample.to_bytes(2, 'little')  # Bits per Sample
    header[36:40] = b'data'  # Subchunk 2 ID
    header[40:44] = audio_length.to_bytes(4, 'little')  # Subchunk 2 Size

    # Return the WAV file header
    return header


async def main():
    logging.info('Server up')
    async with websockets.serve(audio_handler, "0.0.0.0", 8765):
        await asyncio.Future()  # run forever


if __name__ == "__main__":
    asyncio.run(main())
