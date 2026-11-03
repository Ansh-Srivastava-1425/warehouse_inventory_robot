from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    xacro_file = PathJoinSubstitution([
        FindPackageShare('warehouse_description'), 'urdf', 'warehouse_robot.urdf.xacro'
    ])

    worlds_file = PathJoinSubstitution([
        FindPackageShare('warehouse_gazebo'), 'worlds', 'warehouse_empty.sdf'
    ])

    robot_description = ParameterValue(
        Command(['xacro ', xacro_file]), value_type=str
    )

    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{'robot_description': robot_description,
                     'use_sim_time': True}],
    )

    gz_sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([
                FindPackageShare('ros_gz_sim'), 'launch', 'gz_sim.launch.py'
            ])
        ),
        launch_arguments={'gz_args': ['-r ', worlds_file]}.items(),
    )

    spawn = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=['-name', 'warehouse_robot',
                   '-topic', 'robot_description',
                   '-z', '0.05'],
        output='screen',
    )

    bridge_config = PathJoinSubstitution([
        FindPackageShare('warehouse_gazebo'), 'config', 'bridge.yaml'
    ])
    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        parameters=[{'config_file': bridge_config, 'use_sim_time': True}],
        output='screen',
    )

    return LaunchDescription([gz_sim, robot_state_publisher, spawn, bridge])
