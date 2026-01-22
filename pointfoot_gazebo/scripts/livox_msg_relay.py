#!/usr/bin/env python
"""
Relay node: livox_laser_simulation::CustomMsg -> livox_ros_driver2::CustomMsg

Gazebo의 livox_laser_simulation 플러그인이 발행하는 CustomMsg를
FAST_LIO가 기대하는 livox_ros_driver2::CustomMsg로 변환합니다.
"""

import sys
import os

# catkin_ws의 Python 경로 추가 (livox_ros_driver2 메시지용)
catkin_ws_python_paths = [
    '/workspaces/lk_tron/catkin_ws/devel_isolated/livox_ros_driver2/lib/python3/dist-packages',
    '/home/bds0619/workspace/lk_tron/catkin_ws/devel_isolated/livox_ros_driver2/lib/python3/dist-packages',
]
for path in catkin_ws_python_paths:
    if os.path.exists(path) and path not in sys.path:
        sys.path.insert(0, path)

import rospy
from livox_laser_simulation.msg import CustomMsg as SimCustomMsg
from livox_ros_driver2.msg import CustomMsg as DriverCustomMsg
from livox_ros_driver2.msg import CustomPoint as DriverCustomPoint


class LivoxMsgRelay:
    def __init__(self):
        rospy.init_node('livox_msg_relay', anonymous=False)

        # Parameters
        self.input_topic = rospy.get_param('~input_topic', '/livox/lidar_sim')
        self.output_topic = rospy.get_param('~output_topic', '/livox/lidar')

        # Publisher
        self.pub = rospy.Publisher(self.output_topic, DriverCustomMsg, queue_size=10)

        # Subscriber
        self.sub = rospy.Subscriber(self.input_topic, SimCustomMsg, self.callback)

        rospy.loginfo("Livox Msg Relay: {} -> {}".format(self.input_topic, self.output_topic))

    def callback(self, sim_msg):
        # Create driver message
        driver_msg = DriverCustomMsg()

        # Copy header
        driver_msg.header = sim_msg.header
        driver_msg.timebase = sim_msg.timebase
        driver_msg.point_num = sim_msg.point_num
        driver_msg.lidar_id = sim_msg.lidar_id
        driver_msg.rsvd = sim_msg.rsvd

        # Copy points
        for sim_pt in sim_msg.points:
            driver_pt = DriverCustomPoint()
            driver_pt.offset_time = sim_pt.offset_time
            driver_pt.x = sim_pt.x
            driver_pt.y = sim_pt.y
            driver_pt.z = sim_pt.z
            driver_pt.reflectivity = sim_pt.reflectivity
            driver_pt.tag = sim_pt.tag
            driver_pt.line = sim_pt.line
            driver_msg.points.append(driver_pt)

        self.pub.publish(driver_msg)


if __name__ == '__main__':
    try:
        relay = LivoxMsgRelay()
        rospy.spin()
    except rospy.ROSInterruptException:
        pass
