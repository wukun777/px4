#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy, DurabilityPolicy
from mavros_msgs.msg import PositionTarget, State  # <-- 这里修改了导入名称
from mavros_msgs.srv import CommandBool, SetMode

class OffboardSimpleNode(Node):
    def __init__(self):
        super().__init__('offboard_simple_node')

        qos_profile = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            durability=DurabilityPolicy.TRANSIENT_LOCAL,
            history=HistoryPolicy.KEEP_LAST,
            depth=1
        )

        self.state_sub = self.create_subscription(State, '/mavros/state', self.state_cb, 10)
        # <-- 注意：发布的话题根据 PositionTarget 进行了微调，PX4 推荐使用 setpoint_raw/local
        self.setpoint_pub = self.create_publisher(PositionTarget, '/mavros/setpoint_raw/local', qos_profile)

        self.arm_client = self.create_client(CommandBool, '/mavros/cmd/arming')
        self.mode_client = self.create_client(SetMode, '/mavros/set_mode')

        self.current_state = State()
        self.timer = self.create_timer(0.05, self.timer_callback) 
        self.counter = 0

    def state_cb(self, msg):
        self.current_state = msg

    def timer_callback(self):
        msg = PositionTarget()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = "base_link"
        # 坐标系框架：使用本地坐标系 MAV_FRAME_LOCAL_NED
        msg.coordinate_frame = 1 
        # 忽略速度、加速度、受力、偏航率等，只控制位置 (Position)
        # 用二进制掩码告诉飞控：只看 position，忽略其他
        msg.type_mask = 3576  
        
        # 设定目标位置：X=0, Y=0, Z=2米 (注意：有些PX4固件里Z轴朝上，有些朝下。在PositionTarget中通常输入正数2即为起飞高度)
        msg.position.x = 0.0
        msg.position.y = 0.0
        msg.position.z = 2.0  
        
        self.setpoint_pub.publish(msg)

        if self.counter < 100:
            self.counter += 1
            return

        if self.current_state.mode != "OFFBOARD" and self.counter == 100:
            req = SetMode.Request()
            req.custom_mode = "OFFBOARD"
            self.mode_client.call_async(req)
            self.get_logger().info("正在请求切换到 OFFBOARD 模式...")
            self.counter += 1

        elif not self.current_state.armed and self.current_state.mode == "OFFBOARD" and self.counter == 101:
            req = CommandBool.Request()
            req.value = True
            self.arm_client.call_async(req)
            self.get_logger().info("正在请求解锁无人机...")
            self.counter += 1

def main(args=None):
    rclpy.init(args=args)
    node = OffboardSimpleNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
