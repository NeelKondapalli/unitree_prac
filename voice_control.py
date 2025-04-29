import asyncio
import sounddevice as sd
import websockets
import json
import base64
import openai
import time
import sys
from unitree_sdk2py.core.channel import ChannelFactoryInitialize
from unitree_sdk2py.g1.loco.g1_loco_client import LocoClient
import dotenv
import os

dotenv.load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

SAMPLE_RATE = 16000 
CHUNK_DURATION_MS = 250
CHUNK_SIZE = int(SAMPLE_RATE * CHUNK_DURATION_MS / 1000)

class RobotController:
    def __init__(self, interface):
        ChannelFactoryInitialize(0, interface)
        self.loco = LocoClient()
        self.loco.SetTimeout(10.0)
        self.loco.Init()
        print("Robot initialized!")

    def execute_command(self, text):
        text = text.lower()
        if "walk forward" in text:
            print("Walking forward...")
            self.loco.SetMoveCmd(x=0.2, y=0.0, yaw=0.0)
        elif "turn left" in text:
            print("Turning left...")
            self.loco.SetMoveCmd(x=0.0, y=0.0, yaw=0.3)
        elif "turn right" in text:
            print("Turning right...")
            self.loco.SetMoveCmd(x=0.0, y=0.0, yaw=-0.3)
        elif "stop" in text:
            print("Stopping...")
            self.loco.SetMoveCmd(x=0.0, y=0.0, yaw=0.0)
        elif "sit down" in text:
            print("Sitting down...")
            self.loco.SitDown()
        elif "stand up" in text:
            print("Standing up...")
            self.loco.StandUp()


def audio_stream_generator():
    with sd.InputStream(samplerate=SAMPLE_RATE, channels=1, dtype='int16') as stream:
        while True:
            audio_chunk, _ = stream.read(CHUNK_SIZE)
            yield audio_chunk.tobytes()


async def transcribe(robot):
    url = f"wss://api.openai.com/v1/audio/transcriptions/stream?language=en"
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}"
    }

    async with websockets.connect(url, extra_headers=headers) as ws:


        async def send_audio():
            for chunk in audio_stream_generator():
                payload = {
                    "audio": base64.b64encode(chunk).decode("utf-8"),
                    "format": "pcm",
                    "sample_rate": SAMPLE_RATE,
                }
                await ws.send(json.dumps(payload))
                await asyncio.sleep(CHUNK_DURATION_MS / 1000)


        async def receive_text():
            async for message in ws:
                data = json.loads(message)
                if "text" in data and data["text"].strip():
                    print(f"Transcription: {data['text']}")
                    robot.execute_command(data["text"])

        await asyncio.gather(send_audio(), receive_text())

def main():
    if len(sys.argv) < 2:
        print(f"Usage: python3 {sys.argv[0]} <network_interface>")
        sys.exit(1)

    interface = sys.argv[1]
    robot = RobotController(interface)
    asyncio.run(transcribe(robot))

if __name__ == "__main__":
    main() 