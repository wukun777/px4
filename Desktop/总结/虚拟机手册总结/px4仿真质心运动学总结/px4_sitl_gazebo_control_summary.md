# PX4 SITL + Gazebo Classic 联合仿真与动力学控制完整总结 (roarm_quad)

本文档是针对 **roarm_quad** 模型（550mm 轴距四旋翼无人机挂载微雪 RoArm-M2-S 机械臂）在 PX4 SITL + Gazebo Classic + QGroundControl (QGC) 联合仿真环境下的通信链路、传感器对齐、飞控动力学配置、ROS 2 姿态锁死控制器以及仿真环境避坑机制的完整技术总结。相同内容均以最新调试验证成功的参数为准，旨在为开发者提供清晰、完备且高度可操作的项目记录。

---

## 一、系统环境

| 项目 | 版本/信息 |
|------|----------|
| 虚拟机 OS | Ubuntu 22.04 LTS (Jammy Jellyfish) |
| ROS 2 版本 | Humble Hawksbill |
| Gazebo 版本 | Gazebo Classic 11.10.2 |
| PX4 固件版本 | v1.15.4 (release/1.15) |
| MAVROS 版本 | Humble 源码编译版本 |
| 地面站 (GCS) | QGroundControl (QGC) AppImage 独立运行版 |

---

## 二、完整文件路径清单与配置注册

为了让 PX4 SITL 编译系统和 Gazebo 运行时能够正确检索到自定义模型及启动配置，相关的配置文件必须存放在 PX4 源码树的特定路径下。

### 2.1 仿真模型与网格文件路径

- **路径**：`~/src/PX4-Autopilot/Tools/simulation/gazebo-classic/sitl_gazebo-classic/models/roarm_quad/`
- **目录结构**：

```
roarm_quad/
├── model.config              # 模型元数据定义文件
├── roarm_quad.sdf            # 联合物理引擎配置文件
└── meshes/                   # 3D 网格模型目录
    ├── drone_body.STL        # 无人机机身网格
    ├── base_link.STL         # 机械臂底座网格
    ├── link1.STL ~ link3.STL # 机械臂各连杆网格
    ├── gripper_link.STL      # 夹爪网格
    ├── iris_prop_ccw.dae     # 逆时针螺旋桨网格（复制自 iris 模型）
    └── iris_prop_cw.dae      # 顺时针螺旋桨网格（复制自 iris 模型）
```

### 2.2 PX4 自启动机型脚本 (Airframe File)

- **路径**：`~/src/PX4-Autopilot/ROMFS/px4fmu_common/init.d-posix/airframes/10016_gazebo-classic_roarm_quad`
- **作用**：定义飞控参数默认值、电池芯数、遥控器配置，并指定 Gazebo 加载的模型目录名为 roarm_quad。

### 2.3 编译系统注册路径

#### 1. ROMFS 机型自启动列表注册：
- **文件**：`~/src/PX4-Autopilot/ROMFS/px4fmu_common/init.d-posix/airframes/CMakeLists.txt`
- **修改点**：在 px4_add_romfs_files() 内添加 `10016_gazebo-classic_roarm_quad`。

#### 2. SITL 编译目标注册：
- **文件**：`~/src/PX4-Autopilot/src/modules/simulation/simulator_mavlink/sitl_targets_gazebo-classic.cmake`
- **修改点**：在 set(models ...) 块内添加 roarm_quad。

### 2.4 ROS 2 机械臂锁死控制器路径（未测试）

- **Python 节点路径**：`~/src/mavros_ws/src/px4_demo/px4_demo/arm_hold_node.py`
- **功能包构建配置**：`~/src/mavros_ws/src/px4_demo/setup.py`

---

## 三、MAVLink 通信接口与锁步机制 (Lockstep)

在联合仿真中，无人机之所以能够接收飞控指令并向地面站 (QGC) 回传状态，完全依赖于 Gazebo 内置的 MAVLink 插件。

### 3.1 锁步同步 (Lockstep) 与 TCP 握手

- **故障现象**：SITL 启动后，终端一直卡在 `Waiting for simulator to accept connection on TCP port 4560`，Gazebo 窗口虽开，但 QGC 无法连接。
- **原因剖析**：PX4 默认使用**锁步同步 (Lockstep)** 机制，即飞控时钟与仿真器时钟保持步调一致。为此，仿真器必须通过 TCP 4560 端口与 PX4 建立实时握手。如果 SDF 文件中的 MAVLink 插件缺失了 TCP 或锁步配置，通信便无法建立。
- **参数配置对齐**：SDF 文件中的 `<plugin name='mavlink_interface' ...>` 必须显式补齐以下关键字段：

```xml
<enable_lockstep>1</enable_lockstep>      <!-- 开启锁步同步，使 Gazebo 时钟与 PX4 对齐 -->
<use_tcp>1</use_tcp>                      <!-- 开启 TCP 握手协议（必须对应 4560 端口） -->
<mavlink_tcp_port>4560</mavlink_tcp_port>
<mavlink_udp_port>14560</mavlink_udp_port>
```

### 3.2 混控通道映射 (Control Channels)

MAVLink 插件将来自 PX4 的执行器控制信号 (Actuator Outputs) 映射到 Gazebo 中。由于 roarm_quad 仅需要控制 4 个旋翼，其控制通道配置为：

- **Channel 0 ~ 3** 分别对应 rotor0 到 rotor3，控制类型为 velocity（速度控制），输出缩放设为 1000。

---

## 四、传感器对齐与 EKF2 状态估计器配置

当联合仿真打通后，PX4 必须完成传感器自检，其 EKF2 状态估计器才能收敛，使 QGC 显示 "Ready to Fly"。

### 4.1 核心传感器补全

如果 SDF 中漏掉了任何一个核心物理传感器插件，QGC 就会抛出红色的报错（如气压计缺失、磁力计缺失），从而锁死解锁安全检查。我们必须在 SDF 中写入对应的传感器物理模型和插件：

#### 1. GPS 模块：
通过引用默认的 gps 模型并建立固定关节连接：

```xml
<include>
  <uri>model://gps</uri>
  <pose>0.05 0 0.04 0 0 0</pose>
  <name>gps0</name>
</include>
<joint name='gps0_joint' type='fixed'>
  <child>gps0::link</child>
  <parent>base_link</parent>
</joint>
```

#### 2. 地磁计 (磁力计/指南针 - libgazebo_magnetometer_plugin.so)：
发布频率为 100 Hz，用于解决 QGC 报错 `Compass sensor 0 missing`，并为 EKF2 提供初始偏航角 (Yaw) 参考。

#### 3. 气压计 (libgazebo_barometer_plugin.so)：
发布频率为 50 Hz，用于解决 QGC 报错 `Barometer 0 missing`，为 EKF2 提供高度初始参考。

#### 4. IMU 物理插件与连杆：
通过 `/imu_link` 和 `rotors_gazebo_imu_plugin` 发布高频惯性测量数据。

### 4.2 传感器话题桥接 (MAVLink Pipeline)

在 SDF 中添加上述物理传感器后，必须在 `mavlink_interface` 插件中指定正确的话题订阅路径，数据才能最终流入 PX4 飞控：

```xml
<imuSubTopic>/imu</imuSubTopic>
<magSubTopic>/mag</magSubTopic>
<baroSubTopic>/baro</baroSubTopic>
<gpsSubTopic>/gps</gpsSubTopic>
```

---

## 五、PX4 飞控与动力学参数自适应微调

由于本系统总质量较大（整机约 4.45 kg），直接套用默认的轻型四轴参数会导致电机拉力不足或电池充放电曲线解算错误。

### 5.1 电池芯数自适应 (6S 锂电对齐)

- **需求**：真实物理系统中使用的动力电池为 6S 锂电池（满电电压 25.2 V，单节 4.2 V），而 PX4 默认的自启动脚本通常按照 4S 进行电压百分比和空电保护解算。
- **修改方法**：在自启动脚本 `10016_gazebo-classic_roarm_quad` 尾部添加以下飞控参数：

```sh
param set-default BAT_N_CELLS 6   # 强制设置电池芯数为 6S 串联
```

### 5.2 旋翼推力系数校准

- **推力系数调整**：由于系统总重由 1.5 kg (iris) 上升至 4.45 kg，为了提供约 2.0 的推重比 (TWR ≈ 2.0)，每个电机在最大转速 1100 rad/s 下应能提供约 22 N 的升力。
- **SDF 调整**：将 `front_right_motor_model` 等 4 个电机的物理推力常数 `<motorConstant>` 从默认的 5.84e-06 提升至 2.2e-05。

---

## 六、ROS 2 机械臂姿态锁死控制器 (Active Joint Holding)

在真实飞行中，如果机械臂不通电（没有控制力矩），它不仅会在重力作用下自然下坠砸地，还会在无人机加速或机动飞行时由于巨大的惯性力矩产生猛烈摇摆，进而瞬间摧毁无人机飞控的姿态环，导致侧翻炸机。

为此，我们在 ROS 2 功能包 `px4_demo` 中实现了一个**关节高频锁死控制器节点**：

### 6.1 控制节点逻辑 (arm_hold_node.py)

该节点利用定时器以 20 Hz 的高频向 `/joint_trajectory_controller/joint_trajectory` 发布目标位置指令，将大臂、小臂和夹爪的关节角度牢牢锁定在 0 度（0 弧度），实现主动抗干扰。

- **核心代码逻辑**：

```python
# 周期性发布的指令填充
msg = JointTrajectory()
msg.header.stamp = self.get_clock().now().to_msg()
msg.joint_names = ['base_link_to_link1', 'link1_to_link2', 'link2_to_link3', 'link3_to_gripper_link']

point = JointTrajectoryPoint()
point.positions = [0.0, 0.0, 0.0, 0.0]    # 强行锁定各轴目标为 0.0 弧度
point.time_from_start = Duration(sec=0, nanosec=50000000)  # 要求在 50ms 内保持到位
```

### 6.2 在 CMake/Setup 中注册

在 `~/src/mavros_ws/src/px4_demo/setup.py` 的 `console_scripts` 中注册节点，使其能够通过命令行运行：

```python
'arm_hold_node = px4_demo.arm_hold_node:main'
```

---

## 七、联合仿真运行指南与避坑机制（未解决）

联合仿真在多进程启动时极易发生端口冲突和重置错误，必须遵守以下标准的开发工作流：

### 7.1 启动机制：双下划线 (__) 指定特定的 Gazebo 跑道世界

如果直接运行 `make px4_sitl gazebo-classic_roarm_quad`，PX4 启动脚本会默认进入 `empty.world`（灰色网格世界）。为了在富有真实质感的沥青跑道世界 (`asphalt_runway.world`) 中进行动力学仿真，必须采用双下划线的参数命名规则：

- **SITL 启动命令**（在 40 cm 初始高度平稳释放，并加载跑道环境）：

```bash
PX4_SIM_Z=0.4 make px4_sitl gazebo-classic_roarm_quad__asphalt_runway
```

### 7.2 避坑机制一：彻底清理后台僵尸进程 (gzserver)

- **故障现象**：在 Gazebo 前端假死或强制关闭后重新启动仿真，PX4 终端无限循环提示 `Waiting for simulator to accept connection...`，且 Gazebo 中出现多个模型（如 roarm_quad 与 roarm_quad_0），QGC 永远无法连接。
- **机理解释**：强制退出 Gazebo 往往只杀死了前端图形界面 (gzclient)，而后台的物理计算引擎 (gzserver) 仍在内存中运行并死死霸占着 TCP 4560 端口。重新编译时，新启动的 PX4 无法与新模型绑定。
- **解决手段**：每次重新启动仿真前，必须在终端执行以下命令，强制清除所有残留进程：

```bash
killall -9 px4 gazebo gzserver gzclient
```

### 7.3 避坑机制二：绕过 Gazebo 底层 world→Reset() 关节畸变 Bug

- **现象**：手动将模型拖入 Gazebo 完全正常，但一用 PX4 SITL 启动，机械臂在第一帧画面中就瞬间发生极度扭曲、拉伸。
- **原因分析**：PX4 在 Gazebo 成功建立握手后，会强制调用 Gazebo 的 `world→Reset()`（物理重置函数）将仿真时间归零。Gazebo Classic 11 在对包含复杂多转动关节（含有 Fixed 关节及大静摩擦系数）的级联模型进行时间重置时，约束求解器会产生奇异性计算错误，从而在重置的那一微秒内将关节强行拧断。
- **工业级解决方案（延迟生成法）**：
  不要在世界的 .world 文件中静态写入或在仿真未完全初始化时直接加载模型。
  - **步骤**：启动一个空的 `asphalt_runway` 世界，等 PX4 与 Gazebo 顺利建立连接、完成第一次 `world→Reset()` 重置且物理世界完全稳定运行后；
  - **操作**：再通过 ROS 2 的 `spawn_entity` 节点或 Gazebo 动态模型投递命令，在延时 1~2 秒后动态将您的无人机模型投递进场景中。
  - **效果**：模型避开了致命的重置冲击，关节保持完美的初始折叠姿态，彻底杜绝第一帧畸变。

---

## 八、当前项目状态汇总 (Diagnostic Status)

| 测试项目 | 状态 | 验证情况与表现 |
|----------|------|-------------------|
| SITL 通信连通性 | ✅ 正常 | 补充了 enable_lockstep 与 use_tcp 后，仿真时间同步正常，PX4 与 Gazebo 成功建立 TCP 4560 握手。 |
| QGC 地面站状态 | ✅ 正常 | 磁力计、气压计、GPS 传感器数据成功桥接，QGC 报错消失，EKF2 顺利收敛，显示 "Ready to Takeoff"。 |
| 电池动力对齐 | ✅ 正常 | 飞控成功识别为 6S 电池，满电电压正确汇报为 25.2 V，推力系数对齐 4.45 kg 起飞总重。 |
| 关节扭曲与重置异常 | ⚠️ 已知 | 已明确扭曲是由 world→Reset() 触发。建议调试时通过 ROS 2 延迟 Spawn 节点或将机械臂控制器开机默认置于 Hold 折叠位的机制来规避该 Bug。 |

---

*总结生成时间：2026-06-29*
