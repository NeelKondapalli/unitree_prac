import assemblyai as aai
import sounddevice as sd
import sys
from unitree_sdk2py.core.channel import ChannelFactoryInitialize
from unitree_sdk2py.g1.loco.g1_loco_client import LocoClient
import dotenv
import os

dotenv.load_dotenv()

# Configure AssemblyAI API key
aai.settings.api_key = os.getenv("ASSEMBLYAI_API_KEY")

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

def on_open(session_opened: aai.RealtimeSessionOpened):
    print("Session ID:", session_opened.session_id)

def on_data(transcript: aai.RealtimeTranscript, robot):
    if not transcript.text:
        return
    
    if isinstance(transcript, aai.RealtimeFinalTranscript):
        print(f"Final transcript: {transcript.text}")
        robot.execute_command(transcript.text)
    else:
        print(f"Partial: {transcript.text}", end="\r")

def on_error(error: aai.RealtimeError):
    print("An error occurred:", error)

def on_close():
    print("Closing Session")

def main():
    if len(sys.argv) < 2:
        print(f"Usage: python3 {sys.argv[0]} <network_interface>")
        sys.exit(1)

    interface = sys.argv[1]
    robot = RobotController(interface)


    transcriber = aai.RealtimeTranscriber(
        sample_rate=16_000,
        on_data=lambda transcript: on_data(transcript, robot),
        on_error=on_error,
        on_open=on_open,
        on_close=on_close,
    )


    transcriber.connect()

    microphone_stream = aai.extras.MicrophoneStream(sample_rate=16_000)
    transcriber.stream(microphone_stream)


    transcriber.close()

if __name__ == "__main__":
    main() 