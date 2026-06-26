# PX4 SITL + Gazebo + Fast-LIO2 + MID360 仿真环境完整总结

## 一、系统环境

| 项目 | 版本/信息 |
|------|----------|
| 虚拟机 | VMware Workstation |
| 宿主机 OS | Windows（未确认具体版本） |
| 虚拟机 OS | Ubuntu 22.04 Jammy Jellyfish |
| ROS2 版本 | Humble Hawksbill |
| 用户名 | px4 |
| 用户主目录 | /home/px4 |
| Gazebo 版本 | 11.10.2 |
| PX4 固件版本 | 1.15.4 (release/1.15) |
| 内核版本 | 6.8.0 |
| GCC 版本 | 11.4.0 |

---

## 二、完整文件路径清单

### 2.1 系统级路径

```
/opt/ros/humble/setup.bash                    # ROS2 Humble 系统环境
/usr/bin/gazebo                               # Gazebo 可执行文件
/usr/bin/colcon                               # colcon 编译工具
```

### 2.2 用户主目录路径

```
/home/px4/
├── .bashrc                                   # bash 配置文件，source 了 /opt/ros/humble/setup.bash
├── .bash_history
├── .bash_logout
├── .cache
├── .config
├── .dotnet
├── .gazebo                                   # Gazebo 配置和模型缓存
│   └── models/                               # Gazebo 模型库
├── .local
├── .ros                                      # ROS2 日志和配置
│   └── log/                                  # ROS2 运行日志
├── .rviz2
├── build/                                    # 主工作空间编译产物
│   ├── hba/
│   ├── interface/
│   ├── livox_interfaces/
│   ├── livox_ros_driver2/
│   ├── localizer/
│   └── pgo/
├── install/                                  # 主工作空间安装产物
│   ├── interface/
│   ├── livox_interfaces/
│   └── livox_ros_driver2/
│   ├── local_setup.bash
│   ├── setup.bash
│   └── setup.zsh
├── log/                                      # colcon 编译日志
│   ├── build_2026-05-27_20-51-18/
│   ├── build_2026-05-27_20-52-57/
│   └── build_2026-05-27_20-53-54/
├── src/                                      # 源码总目录
│   ├── build/                                # src 下的 colcon 编译产物
│   ├── install/                              # src 下的 colcon 安装产物
│   ├── log/                                  # src 下的编译日志
│   ├── PX4-Autopilot/                        # PX4 固件源码（git clone）
│   │   ├── build/
│   │   │   ├── px4_fmu-v3_default/
│   │   │   └── px4_sitl_default/
│   │   ├── Tools/simulation/
│   │   │   ├── gazebo-classic/
│   │   │   │   └── sitl_gazebo-classic/
│   │   │   │       ├── models/
│   │   │   │       │   └── iris/
│   │   │   │       │       ├── iris.sdf                     # Iris 无人机模型 SDF（已修改 livox 传感器配置）
│   │   │   │       │       ├── iris.sdf.bak                 # 备份文件
│   │   │   │       │       ├── iris.sdf.jinja               # Jinja2 模板
│   │   │   │       │       └── iris.sdf.last_generated      # 上次生成的 SDF
│   │   │   │       └── worlds/
│   │   │   │           └── empty.world                      # 默认仿真世界
│   │   ├── launch/
│   │   ├── mid360.rviz                                      # MID360 RViz 配置文件
│   │   ├── Makefile
│   │   └── msg/
│   ├── fastlio2/                             # Fast-LIO2 源码（git clone）
│   │   ├── fastlio2/
│   │   │   ├── CMakeLists.txt
│   │   │   ├── config/
│   │   │   │   ├── lio.yaml                                # Fast-LIO2 参数文件（原始格式，ros__parameters 包装失败）
│   │   │   │   ├── lio.yaml.bak
│   │   │   │   └── lio (copy).yaml
│   │   │   ├── launch/
│   │   │   │   ├── lio_launch.py                           # Fast-LIO2 启动 launch 文件
│   │   │   │   └── __pycache__/
│   │   │   ├── package.xml
│   │   │   ├── rviz/
│   │   │   │   └── fastlio2.rviz                           # Fast-LIO2 RViz 配置文件
│   │   │   └── src/
│   │   │       ├── lio_node.cpp                            # Fast-LIO2 主节点源码
│   │   │       ├── utils.cpp                               # 工具函数（livox2PCL 转换）
│   │   │       ├── utils.h
│   │   │       └── map_builder/
│   │   │           ├── commons.cpp
│   │   │           ├── commons.h
│   │   │           ├── ikd_Tree.cpp
│   │   │           ├── ikd_Tree.h
│   │   │           ├── imu_processor.cpp                   # IMU 处理器（使用 cloud_start_time/cloud_end_time）
│   │   │           ├── imu_processor.h
│   │   │           ├── ieskf.cpp
│   │   │           ├── ieskf.h
│   │   │           ├── lidar_processor.cpp
│   │   │           ├── lidar_processor.h
│   │   │           ├── map_builder.cpp
│   │   │           └── map_builder.h
│   │   ├── hba/
│   │   ├── interface/
│   │   ├── localizer/
│   │   ├── pgo/
│   │   └── README.md                                       # Fast-LIO2 README（含启动命令和数据集链接）
│   ├── mavros_ws/                                          # MAVROS 工作空间
│   │   └── src/
│   │       ├── mavlink/
│   │       ├── mavros/
│   │       └── px4_demo/
│   │           ├── px4_demo/
│   │           │   └── offboard_simple.py                  # PX4 offboard 控制示例
│   │           ├── setup.cfg
│   │           ├── setup.py
│   │           └── test/
│   └── install/                                            # src/install（fastlio2 编译产物）
│       └── fastlio2/
│           └── share/fastlio2/
│               ├── config/lio.yaml
│               └── rviz/fastlio2.rviz
├── livox_laser_simulation_RO2/                             # Livox Gazebo 仿真插件源码
│   ├── CMakeLists.txt                                      # 包名：ros2_livox_simulation
│   ├── LICENSE
│   ├── README.md
│   ├── include/
│   │   └── ros2_livox/
│   │       ├── csv_reader.hpp
│   │       ├── livox_ode_multiray_shape.h
│   │       └── livox_points_plugin.h
│   ├── package.xml
│   ├── scan_mode/
│   │   ├── avia.csv
│   │   ├── HAP.csv
│   │   ├── horizon.csv
│   │   ├── mid360.csv                                      # MID360 扫描模式
│   │   ├── mid40.csv
│   │   ├── mid70.csv
│   │   └── tele.csv
│   ├── src/
│   │   ├── csv_reader.cpp
│   │   └── livox_points_plugin.cpp                         # Gazebo 插件主源码（含 CustomMsg 和 PointCloud2 发布）
│   └── urdf/
│       ├── avia.xacro
│       ├── HAP.xacro
│       ├── horizon.xacro
│       ├── mid360.xacro                                    # MID360 URDF/Xacro 定义
│       ├── mid40.xacro
│       ├── mid70.xacro
│       └── tele.xacro
├── hunter/
│   └── simulation/
│       └── install/
│           └── setup.bash
├── QGroundControl.AppImage                                 # QGC 地面站
└── Desktop/
```

### 2.3 重要环境变量

```bash
ROS_DISTRO=humble
ROS_VERSION=2
GAZEBO_MODEL_PATH=/usr/share/gazebo-11/models:/home/px4/.gazebo/models
```

### 2.4 .bashrc 追加内容（用户自定义工作空间）

```bash
# ========== 自定义 ROS2 工作空间 ==========
if [ -f ~/install/setup.bash ]; then
    source ~/install/setup.bash
fi
if [ -f ~/src/install/setup.bash ]; then
    source ~/src/install/setup.bash
fi
if [ -f ~/src/mavros_ws/install/setup.bash ]; then
    source ~/src/mavros_ws/install/setup.bash
fi
if [ -f ~/hunter/simulation/install/setup.bash ]; then
    source ~/hunter/simulation/install/setup.bash
fi
```

---

## 三、已安装的软件包

### 3.1 系统级 ROS2 包（apt 安装）

```
ros-humble-gazebo-dev
ros-humble-gazebo-msgs
ros-humble-gazebo-plugins
ros-humble-gazebo-ros
```

### 3.2 源码编译的 ROS2 包（colcon build）

| 包名 | 位置 | 状态 |
|------|------|------|
| fastlio2 | ~/src/fastlio2/fastlio2/ | ✅ 已编译，安装到 ~/src/install/ |
| hba | ~/src/fastlio2/hba/ | ✅ 已编译 |
| interface | ~/src/fastlio2/interface/ | ✅ 已编译 |
| localizer | ~/src/fastlio2/localizer/ | ✅ 已编译 |
| pgo | ~/src/fastlio2/pgo/ | ✅ 已编译 |
| livox_interfaces | ~/build/livox_interfaces/ | ✅ 已编译 |
| livox_ros_driver2 | ~/build/livox_ros_driver2/ | ✅ 已编译 |
| mavros | ~/src/mavros_ws/src/mavros/mavros/ | ✅ 已编译 |
| mavros_extras | ~/src/mavros_ws/src/mavros/mavros_extras/ | ✅ 已编译 |
| mavros_msgs | ~/src/mavros_ws/src/mavros/mavros_msgs/ | ✅ 已编译 |
| px4_demo | ~/src/mavros_ws/src/px4_demo/ | ✅ 已编译 |
| mavlink | ~/src/mavros_ws/src/mavlink/ | ✅ 已编译 |
| ros2_livox_simulation | ~/livox_laser_simulation_RO2/ | ⚠️ 源码存在，但 Gazebo 未加载 |

---

## 四、当前状况（截至对话结束）

### 4.1 已确认正常运行的组件

| 组件 | 状态 | 验证方式 |
|------|------|----------|
| ROS2 Humble | ✅ | ros2 pkg list |
| Gazebo 11 | ✅ | gazebo --version |
| PX4 SITL (1.15.4) | ✅ | make px4_sitl gazebo_iris，QGC 显示 Ready To Fly |
| MAVROS | ✅ | ros2 launch mavros px4.launch，/mavros/state connected=true |
| Livox 激光雷达仿真（PointCloud2） | ✅ | RViz 显示 /livox/lidar 点云 |
| Livox IMU | ✅ | ros2 topic hz /livox/imu ≈ 87Hz |
| Fast-LIO2 节点启动 | ✅ | ros2 launch fastlio2 lio_launch.py 成功启动 |

### 4.2 存在的问题

#### 问题 1：Fast-LIO2 无法接收激光数据（核心问题）

**现象**：
- Fast-LIO2 启动成功（`LIO Node Started`）
- RViz 中 Fixed Frame `lidar` 不存在（`Frame [lidar] does not exist`）
- `/fastlio2/body_cloud` 和 `/fastlio2/world_cloud` 无数据
- `/Odometry` 无数据

**根本原因**：
- PX4 的 `iris.sdf` 使用的是 Gazebo 原生激光插件 `libgazebo_ros_ray_sensor.so`
- 该插件只发布 `sensor_msgs/PointCloud2`，不发布 `livox_ros_driver2/CustomMsg`
- Fast-LIO2 订阅的是 `CustomMsg`，两者类型不匹配
- `ros2 topic info /livox/lidar` 显示只有 `sensor_msgs/msg/PointCloud2`，无 `CustomMsg`
- `lsof` 确认 `libros2_livox.so` 未被 Gazebo 进程加载

**已尝试的解决方案**：
- 修改 `lio.yaml` 为 `ros__parameters` 格式 → 失败（Fast-LIO2 使用 yaml-cpp 直接解析，非 ROS2 参数格式）
- 恢复原始 `lio.yaml` 格式 → 成功启动，但仍无数据
- 分析仿真插件源码 → 发现 `iris.sdf` 未使用 `ros2_livox` 插件

**当前进展**：
- 已修改 `~/src/PX4-Autopilot/Tools/simulation/gazebo-classic/sitl_gazebo-classic/models/iris/iris.sdf`
- 将 `<plugin name="gazebo_ros_laser_controller" filename="libgazebo_ros_ray_sensor.so">` 替换为 `<plugin name="ros2_livox" filename="libros2_livox.so">`
- 添加了 `topic`、`csv_file_name`、`samples`、`downsample` 参数
- **尚未重启仿真验证**

#### 问题 2：QGC "Manual control loss" 警告

**现象**：QGC 反复提示 "Manual control loss: switching to RTL"

**原因**：SITL 仿真无实体遥控器（RC），PX4 检测不到 RC 信号

**影响**：不影响仿真继续，可忽略

**可选解决**：设置 `NAV_RCL_ACT = 0` 和 `COM_RC_IN_MODE = 1`

#### 问题 3：Fast-LIO2 参数文件解析机制

**发现**：Fast-LIO2 使用 `YAML::LoadFile()` 直接解析 YAML，不是 ROS2 标准参数机制
- 参数文件不需要 `ros__parameters` 包装
- 通过 `config_path` ROS2 参数传入文件路径
- 正确启动命令：`ros2 launch fastlio2 lio_launch.py`

---

## 五、仿真启动流程（当前）

### 5.1 完整启动命令（按顺序）

```bash
# 终端 1：启动 PX4 SITL + Gazebo
cd ~/src/PX4-Autopilot
make px4_sitl gazebo_iris

# 终端 2：启动 MAVROS
ros2 launch mavros px4.launch fcu_url:="udp://:14540@127.0.0.1:14557"

# 终端 3：启动 Fast-LIO2
ros2 launch fastlio2 lio_launch.py

# 终端 4：启动 RViz（可选）
rviz2 -d ~/src/PX4-Autopilot/mid360.rviz
# 或 Fast-LIO2 自带 RViz
# ros2 launch fastlio2 lio_launch.py 已自动启动 RViz
```

### 5.2 关键话题列表

| 话题名 | 类型 | 发布者 | 订阅者 | 状态 |
|--------|------|--------|--------|------|
| /livox/lidar | sensor_msgs/PointCloud2 | Gazebo 激光插件 | RViz, Fast-LIO2(期望CustomMsg) | ✅ PointCloud2 有数据，❌ 无 CustomMsg |
| /livox/imu | sensor_msgs/Imu | Gazebo IMU 插件 | Fast-LIO2 | ✅ 正常 |
| /fastlio2/body_cloud | sensor_msgs/PointCloud2 | Fast-LIO2 | RViz | ❌ 无数据 |
| /fastlio2/world_cloud | sensor_msgs/PointCloud2 | Fast-LIO2 | RViz | ❌ 无数据 |
| /fastlio2/lio_odom | nav_msgs/Odometry | Fast-LIO2 | （待转发到 MAVROS） | ❌ 无数据 |
| /fastlio2/lio_path | nav_msgs/Path | Fast-LIO2 | RViz | ❌ 无数据 |
| /mavros/vision_pose/pose | geometry_msgs/PoseStamped | （待创建转换节点） | MAVROS | ❌ 未启动 |
| /mavros/local_position/pose | geometry_msgs/PoseStamped | MAVROS | 用户节点 | ✅ 正常 |
| /tf | tf2_msgs/TFMessage | Fast-LIO2, MAVROS | RViz | ⚠️ Fast-LIO2 TF 不完整 |

---

## 六、PX4 飞控参数设置（已设置）

| 参数名 | 值 | 说明 |
|--------|-----|------|
| EKF2_EV_CTRL | 15 | 启用外部视觉的位置+速度+偏航+高度融合（PX4 ≥ 1.14） |
| EKF2_HGT_MODE | 3 | Vision 作为高度源 |
| EKF2_EV_DELAY | 100 | 视觉延迟 100ms |

---

## 七、待完成任务

### 7.1 高优先级（阻塞 Fast-LIO2 运行）

1. **重启 PX4 SITL 仿真**，验证修改后的 `iris.sdf` 是否正确加载 `ros2_livox` 插件
2. 验证 `/livox/lidar` 上是否有 `CustomMsg` 数据
3. 如果 CustomMsg 有数据，Fast-LIO2 应能正常运行
4. 如果 Fast-LIO2 运行正常，创建 `/Odometry` → `/mavros/vision_pose/pose` 转换节点

### 7.2 中优先级（完善仿真流程）

5. 验证 MAVROS 接收视觉位姿后，PX4 EKF2 是否正确融合
6. 测试位置模式飞行
7. 解决 QGC "Manual control loss" 警告（可选）

### 7.3 低优先级（优化）

8. 创建一键启动脚本（`start_sim.sh`）
9. 优化 RViz 配置，同时显示原始点云和 Fast-LIO2 建图结果
10. 记录 bag 包用于后续分析

---

## 八、重要源码修改记录

### 8.1 已修改文件

1. **~/.bashrc**
   - 追加了 4 个工作空间的 source 命令

2. **~/src/PX4-Autopilot/Tools/simulation/gazebo-classic/sitl_gazebo-classic/models/iris/iris.sdf**
   - 备份：iris.sdf.bak
   - 修改：将 Gazebo 原生激光插件替换为 ros2_livox 插件
   - 新增参数：topic, csv_file_name, samples, downsample

3. **~/src/fastlio2/fastlio2/config/lio.yaml**
   - 备份：lio.yaml.bak, lio (copy).yaml
   - 修改：尝试 ros__parameters 格式（失败，已恢复原始格式）

### 8.2 发现的源码 BUG

1. **~/livox_laser_simulation_RO2/src/livox_points_plugin.cpp 第 183-188 行**
   - PointCloud 点云数据重复添加（每个点添加了两次）
   - 不影响 CustomMsg，但导致 PointCloud2 数据量翻倍

---

## 九、关键命令速查

```bash
# 环境 source
source /opt/ros/humble/setup.bash
source ~/install/setup.bash
source ~/src/install/setup.bash
source ~/src/mavros_ws/install/setup.bash

# 查看节点
ros2 node list
ros2 node info /fastlio2/lio_node
ros2 node info /mavros/mavros

# 查看话题
ros2 topic list
ros2 topic list -t
ros2 topic info /livox/lidar
ros2 topic hz /livox/imu
ros2 topic hz /livox/lidar

# 查看 TF
ros2 run tf2_tools view_frames

# PX4 版本
# 在 pxh> 提示符下输入：ver all

# 启动仿真
cd ~/src/PX4-Autopilot && make px4_sitl gazebo_iris

# 启动 MAVROS
ros2 launch mavros px4.launch fcu_url:="udp://:14540@127.0.0.1:14557"

# 启动 Fast-LIO2
ros2 launch fastlio2 lio_launch.py

# 启动 RViz
rviz2 -d ~/src/PX4-Autopilot/mid360.rviz
```

---

## 十、参考链接

- Fast-LIO2 原始仓库：https://github.com/hku-mars/FAST_LIO
- Livox SDK2：https://github.com/Livox-SDK/Livox-SDK2
- livox_ros_driver2：https://github.com/Livox-SDK/livox_ros_driver2
- PX4-Autopilot：https://github.com/PX4/PX4-Autopilot
- MAVROS：https://github.com/mavlink/mavros

---

*总结生成时间：2026-06-19*
*对话参与方：用户（px4）与 AI 助手（Kimi）*
