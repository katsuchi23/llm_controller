#!/usr/bin/env python3
import rclpy
from rclpy.action import ActionClient
from nav2_msgs.action import NavigateToPose
from geometry_msgs.msg import PoseStamped
from rclpy.node import Node
import math
from llm_controller.llm import random_point

class NavigateToPoseClient(Node):
    def __init__(self):
        super().__init__('navigate_to_pose_client')
        self._action_client = ActionClient(self, NavigateToPose, '/navigate_to_pose')
        
        # Timer to periodically send the goal (but send the goal first)
        self.send_goal()
        self.timer = self.create_timer(35.0, self.send_goal)
        self.goal_handle = None

    def send_goal(self):
        # Get parameter values
        x, y, theta = random_point()

        goal_x = x
        goal_y = y
        goal_theta = theta
        
        # Create a PoseStamped message for the goal
        pose = PoseStamped()
        pose.header.stamp = self.get_clock().now().to_msg()
        pose.header.frame_id = 'map'
        pose.pose.position.x = goal_x
        pose.pose.position.y = goal_y
        pose.pose.position.z = 0.0
        
        # Convert theta (radians) to quaternion (assuming rotation about Z-axis)
        qz = math.sin(goal_theta / 2.0)
        qw = math.cos(goal_theta / 2.0)
        pose.pose.orientation.x = 0.0
        pose.pose.orientation.y = 0.0
        pose.pose.orientation.z = qz
        pose.pose.orientation.w = qw

        self.get_logger().info(f"Sending goal: x={goal_x}, y={goal_y}, theta={goal_theta}")

        # Wait for the action server to become available
        if not self._action_client.wait_for_server(timeout_sec=10.0):
            self.get_logger().error('Action server not available after waiting 10 seconds.')
            return

        # Create and send the goal
        goal_msg = NavigateToPose.Goal()
        goal_msg.pose = pose
        send_goal_future = self._action_client.send_goal_async(goal_msg)
        send_goal_future.add_done_callback(self.goal_response_callback)

    def goal_response_callback(self, future):
        self.goal_handle = future.result()
        if not self.goal_handle.accepted:
            self.get_logger().info('Goal rejected.')
            self.shutdown()
            return

        self.get_logger().info('Goal accepted.')
        get_result_future = self.goal_handle.get_result_async()
        get_result_future.add_done_callback(self.get_result_callback)

    def get_result_callback(self, future):
        result = future.result().result
        status = future.result().status

        if status == 4:  # STATUS_ABORTED
            self.get_logger().info('Goal was aborted.')
        elif status == 5:  # STATUS_REJECTED
            self.get_logger().info('Goal was rejected.')
        else:
            self.get_logger().info('Goal succeeded!')

    def shutdown(self):
        self.get_logger().info('Shutting down node.')
        rclpy.shutdown()

def main(args=None):
    rclpy.init(args=args)
    action_client = NavigateToPoseClient()
    rclpy.spin(action_client)

if __name__ == '__main__':
    main()
