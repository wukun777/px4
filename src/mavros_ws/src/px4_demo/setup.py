from setuptools import find_packages, setup

package_name = 'px4_demo'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='px4',
    maintainer_email='px4@todo.todo',
    description='TODO: Package description',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'offboard_start = px4_demo.offboard_simple:main',
            'arm_hold_node = px4_demo.arm_hold_node:main',
        ],
    },
)
