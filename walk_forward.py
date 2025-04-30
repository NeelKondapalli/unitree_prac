#!/usr/bin/env python3
"""
Unitree G1 Robot Control Script
This script provides both keyboard and voice control for the Unitree G1 robot.
"""

import sys
import time
import tty
import termios
import threading
import assemblyai as aai
import dotenv
import os
from unitree_sdk2py.core.channel import ChannelFactoryInitialize
from unitree_sdk2py.g1.loco.g1_loco_client import LocoClient

# Load environment variables
dotenv.load_dotenv()

# Configuration constants
FORWARD_SPEED = 0.3     # Forward/backward speed in m/s
LATERAL_SPEED = 0.2     # Left/right speed in m/s
ROTATION_SPEED = 0.6    # Rotation speed in rad/s
STARTUP_DELAY = 1.0     # Delay after posture changes

# Configure AssemblyAI API key
aai.settings.api_key = os.getenv("ASSEMBLYAI_API_KEY")

class RobotController:
    def __init__(self, network_interface):
        # Initialize SDK
        try:
            ChannelFactoryInitialize(0, network_interface)
        except Exception as e:
            raise Exception(f"Failed to initialize SDK: {str(e)}")

        # Create and initialize client
        try:
            self.client = LocoClient()
            self.client.SetTimeout(10.0)
            self.client.Init()
            print("Robot initialized!")
        except Exception as e:
            raise Exception(f"Failed to initialize client: {str(e)}")

    def execute_command(self, text):
        """Execute voice commands."""
        text = text.lower()
        if "walk forward" in text or "move forward" in text:
            print("Walking forward...")
            self.client.Move(FORWARD_SPEED, 0.0, 0.0)
        elif "walk backward" in text or "move backward" in text:
            print("Walking backward...")
            self.client.Move(-FORWARD_SPEED, 0.0, 0.0)
        elif "move left" in text:
            print("Moving left...")
            self.client.Move(0.0, LATERAL_SPEED, 0.0)
        elif "move right" in text:
            print("Moving right...")
            self.client.Move(0.0, -LATERAL_SPEED, 0.0)
        elif "turn left" in text:
            print("Turning left...")
            self.client.Move(0.0, 0.0, ROTATION_SPEED)
        elif "turn right" in text:
            print("Turning right...")
            self.client.Move(0.0, 0.0, -ROTATION_SPEED)
        elif "stop" in text:
            print("Stopping...")
            self.client.Move(0.0, 0.0, 0.0)
        elif "sit down" in text:
            print("Sitting down...")
            self.client.Sit()
            time.sleep(STARTUP_DELAY)
        elif "stand up" in text:
            print("Standing up...")
            self.client.StandUp()
        elif "high stand" in text:
            print("Switching to high stand...")
            self.client.HighStand()
            time.sleep(STARTUP_DELAY)
        elif "low stand" in text:
            print("Switching to low stand...")
            self.client.LowStand()
            time.sleep(STARTUP_DELAY)
        elif "wave hand" in text:
            print("Waving hand...")
            self.client.WaveHand()
        elif "shake hand" in text:
            print("Shaking hand...")
            self.client.ShakeHand()

    def handle_movement(self, key):
        """Handle keyboard commands."""
        x_vel = 0.0
        y_vel = 0.0
        yaw_vel = 0.0
        status = "Stopped          "

        if key == 'w':
            x_vel = FORWARD_SPEED
            status = "Moving Forward    "
        elif key == 's':
            x_vel = -FORWARD_SPEED
            status = "Moving Backward   "
        elif key == 'a':
            y_vel = LATERAL_SPEED
            status = "Moving Left       "
        elif key == 'd':
            y_vel = -LATERAL_SPEED
            status = "Moving Right      "
        elif key == 'q':
            yaw_vel = ROTATION_SPEED
            status = "Rotating Left     "
        elif key == 'e':
            yaw_vel = -ROTATION_SPEED
            status = "Rotating Right    "
        elif key == 'g':
            try:
                print("\nSitting down...")
                self.client.Sit()
                time.sleep(STARTUP_DELAY)
                status = "Sitting Down      "
            except Exception as e:
                print(f"\nError during sit down: {str(e)}")
        elif key == 'f':
            try:
                print("\nStanding up...")
                self.client.StandUp()
                status = "Standing Up       "
            except Exception as e:
                print(f"\nError during stand up: {str(e)}")
                status = "Stand Up Failed   "
        elif key == 'h':
            try:
                print("\nSwitching to high stand...")
                self.client.HighStand()
                time.sleep(STARTUP_DELAY)
                status = "High Stand        "
            except Exception as e:
                print(f"\nError during high stand: {str(e)}")
        elif key == 'l':
            try:
                print("\nSwitching to low stand...")
                self.client.LowStand()
                time.sleep(STARTUP_DELAY)
                status = "Low Stand         "
            except Exception as e:
                print(f"\nError during low stand: {str(e)}")
        elif key == 'z':
            try:
                print("\nSwitching to zero torque...")
                self.client.ZeroTorque()
                status = "Zero Torque       "
            except Exception as e:
                print(f"\nError during zero torque: {str(e)}")
        elif key == 'v':
            try:
                print("\nWaving hand...")
                self.client.WaveHand()
                status = "Waving Hand       "
            except Exception as e:
                print(f"\nError during wave hand: {str(e)}")
        elif key == 'b':
            try:
                print("\nWaving hand with turn...")
                self.client.WaveHand(True)
                status = "Waving With Turn  "
            except Exception as e:
                print(f"\nError during wave hand with turn: {str(e)}")
        elif key == 'n':
            try:
                print("\nShaking hand...")
                self.client.ShakeHand()
                status = "Shaking Hand      "
            except Exception as e:
                print(f"\nError during shake hand: {str(e)}")
        elif key == ' ':
            try:
                print("\nDamping motors...")
                self.client.Damp()
                status = "Damped            "
            except Exception as e:
                print(f"\nError during damp: {str(e)}")
        elif ord(key) == 27:  # Esc key
            print("\nExiting...")
            return False

        print(f"\rCurrent Status: {status}", end='')
        if key in ['w', 's', 'a', 'd', 'q', 'e']:  # Only send move command for movement keys
            self.client.Move(x_vel, y_vel, yaw_vel)
        sys.stdout.flush()
        return True

def getch():
    """Get a single character from the user without requiring Enter key."""
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

def print_controls():
    """Display available control commands to the user."""
    print("\nUnitree G1 Robot Controls:")
    print("-------------------------")
    print("Keyboard Controls:")
    print("  W: Move Forward")
    print("  S: Move Backward")
    print("  A: Move Left")
    print("  D: Move Right")
    print("  Q: Rotate Left")
    print("  E: Rotate Right")
    print("\nPosture Commands:")
    print("  F: Stand Up")
    print("  G: Sit Down")
    print("  H: High Stand")
    print("  L: Low Stand")
    print("  Z: Zero Torque")
    print("\nGesture Commands:")
    print("  V: Wave Hand")
    print("  B: Wave Hand with Turn")
    print("  N: Shake Hand")
    print("\nVoice Commands:")
    print("  'walk forward' or 'move forward'")
    print("  'walk backward' or 'move backward'")
    print("  'move left'")
    print("  'move right'")
    print("  'turn left'")
    print("  'turn right'")
    print("  'stop'")
    print("  'sit down'")
    print("  'stand up'")
    print("  'high stand'")
    print("  'low stand'")
    print("  'wave hand'")
    print("  'shake hand'")
    print("\nOther Commands:")
    print("  Space: Stop/Damp")
    print("  Esc: Quit")
    print("\nCurrent Status: Robot Ready")

def on_open(session_opened: aai.RealtimeSessionOpened):
    print("Voice control session started:", session_opened.session_id)

def on_data(transcript: aai.RealtimeTranscript, robot):
    if not transcript.text:
        return
    
    if isinstance(transcript, aai.RealtimeFinalTranscript):
        print(f"\nVoice command: {transcript.text}")
        robot.execute_command(transcript.text)
    else:
        print(f"Listening: {transcript.text}", end="\r")

def on_error(error: aai.RealtimeError):
    print("Voice control error:", error)

def on_close():
    print("Voice control session closed")

def start_voice_control(robot):
    """Start the voice control system in a separate thread."""
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

def main():
    """Main function to run the robot control program."""
    if len(sys.argv) < 2:
        print(f"Usage: python3 {sys.argv[0]} networkInterface")
        sys.exit(1)

    print("\nWARNING: Please ensure there are no obstacles around the robot.")
    print("IMPORTANT: Make sure the robot is NOT in debug mode!")
    print("         1. Do not use L2+R2, L2+A, L2+B on controller")
    print("         2. Use L1+A and L1+UP on controller to enable movement mode")
    print("         3. If in debug mode, reboot the robot to exit it")
    input("Press Enter when ready...")

    try:
        # Initialize robot
        robot = RobotController(sys.argv[1])
        print_controls()

        # Start voice control in a separate thread
        voice_thread = threading.Thread(target=start_voice_control, args=(robot,))
        voice_thread.daemon = True
        voice_thread.start()

        # Main keyboard control loop
        while True:
            key = getch().lower()
            if not robot.handle_movement(key):
                break

    except KeyboardInterrupt:
        print("\nProgram interrupted by user")
    except Exception as e:
        print(f"\nError occurred: {str(e)}")
    finally:
        # Ensure robot stops safely
        try:
            robot.client.Move(0, 0, 0)
            print("\nRobot stopped safely")
        except Exception as e:
            print(f"\nError stopping robot: {str(e)}")

if __name__ == "__main__":
    main()
                                                                              
