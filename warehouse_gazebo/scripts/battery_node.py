#!/usr/bin/env python3

from nav_msgs.msg import Odometry
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import BatteryState
from std_msgs.msg import String


class BatteryNode(Node):
    def __init__(self):
        super().__init__('battery_node')
        self.percentage = 100.0
        self.drain_idle = 0.05
        self.dt = 0.1
        self.x = 0.0
        self.y = 0.0
        self.speed = 0.0
        self.drain_moving = 0.2
        self.create_subscription(Odometry, 'odom', self.on_odom, 10)
        self.timer = self.create_timer(0.1, self.update)
        self.status_pub = self.create_publisher(String, 'dock/status', 10)
        self.battery_pub = self.create_publisher(BatteryState, 'battery/state', 10)

    def on_odom(self, msg):
        self.x = msg.pose.pose.position.x
        self.y = msg.pose.pose.position.y
        self.speed = msg.twist.twist.linear.x

    def update(self):
        inside = (-9.0 <= self.x <= -7.0) and (-1.0 <= self.y <= 1.0)
        status = 'DOCKED_CHARGING' if inside else 'NOT_DOCKED'
        self.status_pub.publish(String(data=status))
        if inside:
            self.percentage = self.percentage + 1.0 * 0.1
        else:
            if abs(self.speed) > 0.05:
                rate = self.drain_moving
            else:
                rate = self.drain_idle
            self.percentage = self.percentage - rate * self.dt
        self.percentage = min(100.0, max(0.0, self.percentage))
        msg = BatteryState()
        msg.percentage = self.percentage / 100.0
        msg.present = True
        if inside:
            msg.power_supply_status = BatteryState.POWER_SUPPLY_STATUS_CHARGING
        else:
            msg.power_supply_status = BatteryState.POWER_SUPPLY_STATUS_DISCHARGING
        self.battery_pub.publish(msg)
        self.get_logger().info(
            f'{self.percentage:.1f}  x={self.x:.2f} y={self.y:.2f} speed={self.speed:.2f}'
        )


def main():
    rclpy.init()
    node = BatteryNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
