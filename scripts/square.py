#! /usr/bin/env python
# Import ROS.
import rospy
# Import the API.
from sys_g.py_g_functions import *
# To print colours (optional).
from sysg_g.PrintColours import *
import time


def main():
    # Initializing ROS node.
    rospy.init_node("multi_drone_controller", anonymous=True)

    # List of namespaces for each drone (assuming namespaces are /drone1, /drone2, ..., /drone12).
    drone_namespaces = [f"/drone{i}" for i in range(1, 13)]

    # Create a list to store drone objects
    drones = []

    # Initialize each drone
    for namespace in drone_namespaces:
        rospy.loginfo(CGREEN2 + f"Initializing drone in namespace {namespace}" + CEND)
        drone = gnc_api(namespace=namespace)
        drone.wait4connect()
        drone.wait4start()
        drone.initialize_local_frame()
        drones.append(drone)

    # Staggered takeoff to avoid initial collisions
    for i, drone in enumerate(drones):
        rospy.loginfo(CGREEN2 + f"Drone {i+1} taking off with staggered delay." + CEND)
        drone.takeoff(3)
        time.sleep(2)  # 2-second delay between each drone's takeoff

    # Specify control loop rate. We recommend a low frequency to not overload the FCU with messages.
    rate = rospy.Rate(3)

    # Specify some waypoints for each drone, adding an offset to avoid collisions
    # Offset each drone's waypoints by a certain distance (e.g., 2 meters) to avoid collisions
    offset = 2.0
    waypoints = [
        [[0, i * offset, 3, 0], [5, i * offset, 3, -90], [5, 5 + i * offset, 3, 0],
         [0, 5 + i * offset, 3, 90], [0, i * offset, 3, 180], [0, i * offset, 3, 0]] 
        for i in range(12)
    ]

    # Control loop to send drones to each waypoint
    for i in range(len(waypoints[0])):
        for j, drone in enumerate(drones):
            drone.set_destination(
                x=waypoints[j][i][0], y=waypoints[j][i][1], z=waypoints[j][i][2], psi=waypoints[j][i][3])
        
        # Wait for all drones to reach the waypoint
        all_reached = False
        while not all_reached:
            all_reached = True
            for drone in drones:
                if not drone.check_waypoint_reached():
                    all_reached = False
            rate.sleep()

    # Land all drones after reaching all waypoints
    for drone in drones:
        drone.land()

    rospy.loginfo(CGREEN2 + "All waypoints reached by all drones, landing now." + CEND)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        exit()

