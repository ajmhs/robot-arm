import rti.connextdds as dds
import os
from os import path as os_path
#from inputs import get_gamepad
import time

print("Initializing Controller. Ensure Controller is set to X mode.")

joy_pos = [0,0,0,0,0]


file_path = os_path.dirname(os_path.realpath(__file__))
provider = dds.QosProvider(uri=os_path.join(file_path, 'ConnextMedicalDemoArchitecture.xml'))

config_name='MedicalDemoParticipantLibrary::WebController'
participant = provider.create_participant_from_config(config=config_name) 

motor_control_t = provider.type('SurgicalRobot::MotorControl')

# Writers
motor_writer = dds.DynamicData.DataWriter(
    participant.find_datawriter('publisher::MotorControlDW'))


#with rti.open_connector(config_name="MedicalDemoParticipantLibrary::WebController", url = "../system/ConnextMedicalDemoArchitecture.xml") as connector:
#    output = connector.get_output("publisher::MotorControlDW")

print("Starting Publisher")

x = 0
direction = 0
forward = True

motor = 0
pos = 1

# Move on these axis
movements = [0, 1, 2, 3, 4]

# Get Axis 1 to 90 so it doesn't hit anything
time.sleep(1)

output = dds.DynamicData(motor_control_t)
output['id'] = 1
output['direction'] = 0
motor_writer.write(output)
    
while True:
    time.sleep(1)

    # random would be cool
    if x >= 0 and x < len(movements):
        motor = movements[x]
    else:
        motor = movements[0]
        x = 0

    x = x + 1

    # all the movement logic is in teleop_arm_mark.py for now
    # till figure out how to send a number beyond 2
    # pos value ignored
    output['id'] = motor
    output['direction'] = pos
    motor_writer.write(output)
