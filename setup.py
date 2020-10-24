from setuptools import setup

setup(name='chatster',
      version='1.0.0',
      description='A local bridge between a Minecraft server and your favorite IRC client',
      url='https://github.com/Ewpratten/chatster',
      author='Evan Pratten',
      author_email='ewpratten@gmail.com',
      license='GPLv3',
      packages=['chatster'],
      zip_safe=False,
      include_package_data=True,
      instapp_requires=[
          "requests",
          "git+https://github.com/ammaraskar/pyCraft"
      ],
      entry_points={
          'console_scripts': [
              'chatster = chatster.__main__:main'
          ]
      }
      )
