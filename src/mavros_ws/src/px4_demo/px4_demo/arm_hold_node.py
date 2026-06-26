#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import rclpy
from rclpy.node import Node
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from builtin_interfaces.msg import Duration

class ArmHoldController(Node):
    def __init__(self):
        super().__init__('arm_hold_controller')
        
        # 💡 创建轨迹控制器指令发布者
        # 如果您使用的控制器名称不同，请将此处的 Topic 修改为您实际的控制器控制 Topic
        self.publisher_ = self.create_publisher(
            JointTrajectory, 
            '/joint_trajectory_controller/joint_trajectory', 
            10
        )
        
        # 💡 声明控制的机械臂关节名称列表（必须与您的 SDF/URDF 关节名称严格对齐）
        self.joint_names = [
            'base_link_to_link1',
            'link1_to_link2',
            'link2_to_link3',
            'link3_to_gripper_link'
        ]
        
        # 💡 设定目标角度：让所有关节始终保持在 0.0 弧度（0度）
        # 如果后续您需要让它保持在折叠状态，可以在此处修改对应的目标弧度值
        self.target_positions = [0.0, 0.0, 0.0, 0.0]
        
        # 💡 创建定时器：以 20Hz (每 0.05 秒) 的高频率持续注入位置指令
        # 极高频率的指令流能够对抗物理引擎中的惯性和重力，死死锁死关节
        self.timer = self.create_timer(0.05, self.publish_joint_commands)
        self.get_logger().info('机械臂 0度 锁死控制器已成功启动。')

    def publish_joint_commands(self):
        msg = JointTrajectory()
        
        # 1. 填充时间戳
        msg.header.stamp = self.get_clock().now().to_msg()
        
        # 2. 指定关节名称
        msg.joint_names = self.joint_names
        
        # 3. 创建轨迹点，指定各关节的控制目标
        point = JointTrajectoryPoint()
        point.positions = self.target_positions
        
        # 4. 设定时间容差：要求在 0.05 秒内必须达到该位置（维持控制的实时性）
        point.time_from_start = Duration(sec=0, nanosec=50000000)
        
        # 5. 打包并发布
        msg.points.append(point)
        self.publisher_.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = ArmHoldController()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info('控制器被用户手动中断。')
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()