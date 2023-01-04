import WebSocket, { WebSocketServer } from "ws";
import fs from "fs";

const wss = new WebSocketServer({ port: 8080 });
console.log("wss.js")

function createWavHeader(audioData) {
    // Parse the data to extract the necessary information for the WAV file header and metadata
    const audioLength = audioData.length; // length of the audio data in bytes
    const sampleRate = 96000; // sample rate in Hz
    const channels = 1; // number of channels (1 for mono, 2 for stereo)
    const bitsPerSample = 16; // bits per sample (8 or 16)

    // Calculate the number of bytes per sample
    const bytesPerSample = bitsPerSample / 8;

    // Calculate the number of samples in the audio data
    const numSamples = audioLength / bytesPerSample;

    // Calculate the audio duration in seconds
    const duration = numSamples / sampleRate;

    // Calculate the number of bytes in the header
    const headerLength = 44;

    // Create the WAV file header
    const header = Buffer.alloc(headerLength);
    header.write("RIFF"); // Chunk ID
    header.writeUInt32LE(audioLength + headerLength - 8, 4); // Chunk Size
    header.write("WAVE", 8); // Format
    header.write("fmt ", 12); // Subchunk 1 ID
    header.writeUInt32LE(16, 16); // Subchunk 1 Size
    header.writeUInt16LE(1, 20); // Audio Format (1 for PCM)
    header.writeUInt16LE(channels, 22); // Number of Channels
    header.writeUInt32LE(sampleRate, 24); // Sample Rate
    header.writeUInt32LE(sampleRate * channels * bytesPerSample, 28); // Byte Rate
    header.writeUInt16LE(channels * bytesPerSample, 32); // Block Align
    header.writeUInt16LE(bitsPerSample, 34); // Bits per Sample
    header.write("data", 36); // Subchunk 2 ID
    header.writeUInt32LE(audioLength, 40); // Subchunk 2 Size

    // Return the WAV file header
    return header;
}

wss.on("connection", function connection(ws) {
    console.log("connection");

    // Array to store the data messages
    let dataMessages = [];
    let dataMessagesWholeAudio = [];

    // Messages sent from Egress
    ws.on("message", function message(data) {
        // Store the data message in the array
        dataMessages.push(data);
        dataMessagesWholeAudio.push(data);
    });

    // Counter for the number of times the timer is triggered
    let counter = 0;
    // Save the data to a file every 3 seconds
    setInterval(() => {
        if (ws.readyState === ws.OPEN) {
            if (typeof dataMessages !== []) {
                const audioData = Buffer.concat(dataMessages);
                const header = createWavHeader(audioData);
                const wavData = Buffer.concat([header, audioData]);
                const filename = "sound_" + counter + ".wav";
                counter++;
                fs.writeFile(filename, wavData, (err) => {
                    if (err) {
                        console.error(err);
                    } else {
                        console.log("WAV file saved");
                    }
                });
                console.log("Saving audio snippet %s", filename)
                // Clean audio buffer
                dataMessages = [];
            }
        }
    }, 3000); // 3 seconds

    ws.on("close", () => {
        // Concatenate the data messages
        const audioData = Buffer.concat(dataMessagesWholeAudio);

        // Create WAV header
        const header = createWavHeader(audioData);

        // Create the WAV file by concatenating the header and the audio data
        const wavData = Buffer.concat([header, audioData]);

        // Save the WAV file
        fs.writeFile("sound.wav", wavData, (err) => {
            if (err) {
                console.error(err);
            } else {
                console.log("WAV file saved");
            }
        });
    });
});
