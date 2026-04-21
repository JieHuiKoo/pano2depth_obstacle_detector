from setuptools import find_packages, setup

package_name = 'p2d_node'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(
        include=['p2d_node', 'p2d_node.*']
    ),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', ['launch/p2d_node.launch.py']),
        ('share/' + package_name + '/launch', ['launch/static_tf.launch.py']),
        ('share/' + package_name + '/models', ['models/DA360_base.pth', 'models/DA360_large.pth', 'models/DA360_small.pth']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='jiehui',
    maintainer_email='koojiehui@outlook.com',
    description='TODO: Package description',
    license='MIT',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'p2d_node = p2d_node.p2d_node:main',
        ],
    },
)
