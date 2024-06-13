from enum import IntEnum
import random
import time
import rti.connextdds as dds
from os import path as os_path

file_path = os_path.dirname(os_path.realpath(__file__))
provider = dds.QosProvider(uri=os_path.join(file_path, 'ConnextMedicalDemoArchitecture.xml'))

config_name='MedicalDemoParticipantLibrary::WebController'
participant = provider.create_participant_from_config(config=config_name) 

motor_control_t = provider.type('SurgicalRobot::MotorControl')

class Motors(IntEnum):
    BASE = 0
    SHOULDER = 1
    ELBOW = 2
    WRIST = 3
    HAND = 4

# Main function
def main():
    output = dds.DynamicData(motor_control_t)
    
    print('Creating DataWriter')
    writer = dds.DynamicData.DataWriter(
    participant.find_datawriter('publisher::MotorControlDW'))

    try:
        while True:                
            output['id'] = random.randint(Motors.BASE, Motors.HAND)
            output['direction'] = 3
            writer.write(output)
            time.sleep(1)
                
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
