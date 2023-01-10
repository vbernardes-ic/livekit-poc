#!/usr/bin/env python

import asyncio
import aiohttp
import websockets
import requests
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

TRANSCRIPTION_SERVER_URL = os.getenv('TRANSCRIPTION_SERVER_URL')


async def process_partial_audio(data_messages, conn_id, counter, last_processed_msg):

    logger.debug(f'Entering process_partial_audio for connection {conn_id}')
    logger.debug(f'Last processed message index: {last_processed_msg}')

    msgs_to_process = data_messages[last_processed_msg:]
    wav_data = format_audio_data(msgs_to_process)

    # Save audio snippet locally
    await save_audio_file(msgs_to_process, conn_id, suffix=counter)
    counter += 1

    # Send file for transcription
    transcription = await get_transcription(wav_data)

    # Update last processed index
    last_processed_msg = len(data_messages)
    logger.debug(f'Updated last processed message index to: {last_processed_msg}')

    return counter, last_processed_msg


async def get_transcription(wav_data, async_=True):
    logger.debug(f'Initiating {"ASYNC" if async_ else "SYNC"} transcription request...')
    # Send data for transcription
    req_url = TRANSCRIPTION_SERVER_URL+'transcribe_async' if async_ else TRANSCRIPTION_SERVER_URL+'transcribe'
    async with aiohttp.ClientSession() as session:
        async with session.post(req_url, data=wav_data, headers={
            "Content-Type": "application/octet-stream",
        }) as response:
            logger.info(f"Status: {response.status}")
            logger.info(f"Headers: {response.headers}")
            text = await response.text()
            logger.info(f"Body: {text}")
            return text


async def timer(data_messages, conn_id, counter, last_processed_msg, delay=5):
    while True:
        await asyncio.sleep(delay)
        logger.debug(f'Inside timer for connection {str(conn_id)[-4:]} -> counter: {counter}\tlast_processed_msg: {last_processed_msg}')
        if logger.level == logging.DEBUG:
            await heartbeat_trans_service()
        counter, last_processed_msg = await process_partial_audio(data_messages, conn_id, counter, last_processed_msg)


async def heartbeat_trans_service():
    ping = requests.get('http://transcription-server:5050/heartbeat')
    if ping.text == 'Ok':
        logger.info('Heartbeat >>> Transcription service is up.')
    else:
        logger.info('Heartbeat >>> Could not reach transcription service.')


async def audio_handler(websocket):
    logger.info(f'Connection initiated, with ID {websocket.id}')
    logger.debug(f'Connection {websocket.id} >>> Request Headers:\n{websocket.request_headers}')

    counter = 0  # Counter for the number of times the timer is triggered
    last_processed_msg = 0  # Index for data_messages

    # Array to store the data messages
    data_messages = []
    data_messages_whole_audio = []

    timer_task = asyncio.create_task(timer(data_messages, websocket.id, counter, last_processed_msg))

    try:
        async for message in websocket:
            # Store the data message in the array
            if isinstance(message, bytes):
                data_messages.append(message)
                data_messages_whole_audio.append(message)
            else:
                assert isinstance(message, str)
                logger.info(f'Received string message: {message}')

    except websockets.ConnectionClosed:
        timer_task.cancel()
        logger.info(f"Closing connection from client.")
        wav_data = format_audio_data(data_messages_whole_audio)
        transcription = await get_transcription(wav_data)
        logger.info(transcription)
        await save_audio_file(data_messages_whole_audio, conn_id=websocket.id)

        # debug
        logger.debug(f'Connection {websocket.id} >>> Num of messages received: {len(data_messages_whole_audio)}')


def format_audio_data(messages):
    audio_data = b''.join(messages)  # Concatenate the data messages
    header = create_wav_header(audio_data)
    wav_data = header + audio_data
    return wav_data


async def save_audio_file(audio_buffer, conn_id, suffix=None):
    id_suffix = str(conn_id)[-4:]
    wav_data = format_audio_data(audio_buffer)
    filename = f"sound_{id_suffix}_{suffix}.wav" if suffix is not None else f"sound_{id_suffix}.wav"
    with open(filename, "wb") as f:
        f.write(wav_data)
    logger.info(f"File {filename} saved.")


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
    logger.info('Server up, version 43')
    async with websockets.serve(audio_handler, "0.0.0.0", 8765):
        await asyncio.Future()  # run forever


if __name__ == "__main__":
    asyncio.run(main())
