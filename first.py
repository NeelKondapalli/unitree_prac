import time
import sys
from unitree_sdk2py.core.channel import ChannelFactoryInitialize
from unitree_sdk2py.g1.loco.g1_loco_client import LocoClient

def main():
    if len(sys.argv) < 2:
        print(f"Usage: python3 {sys.argv[0]} <network_interface>")
        sys.exit(1)

    interface = sys.argv[1]
    ChannelFactoryInitialize(0, interface)

    loco = LocoClient()
    loco.SetTimeout(10.0)
    loco.Init()

    print("Starting walking sequence...")


    print("Walking forward...")
    loco.SetMoveCmd(x=0.2, y=0.0, yaw=0.0)  
    time.sleep(3) 

    print("Turning left...")
    loco.SetMoveCmd(x=0.0, y=0.0, yaw=0.3) # jit wull walk in curve 
    time.sleep(2) 

    print("Stopping...")
    loco.SetMoveCmd(x=0.0, y=0.0, yaw=0.0)
    time.sleep(1)

    print("Sitting down...")
    loco.SitDown()
    time.sleep(2) 

    print("Sequence complete!")

if __name__ == "__main__":
    main()


