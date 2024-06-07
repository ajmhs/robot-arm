import pygame
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

class Buttons(IntEnum):
    PRIMARY_LEFT = 3
    PRIMARY_RIGHT = 0
    SECONDARY_LEFT  = 4
    SECONDARY_RIGHT = 1    

up_down = [Motors.SHOULDER, Motors.ELBOW, Motors.WRIST]
left_right = [Motors.BASE, Motors.HAND]

def poll_joystick(joystick):
    clock = pygame.time.Clock()
    output = dds.DynamicData(motor_control_t)
    last_event_time = 0 # Start in demo mode

    print('Creating DataWriter')

    writer = dds.DynamicData.DataWriter(
        participant.find_datawriter('publisher::MotorControlDW'))

    try:
        num_buttons = joystick.get_numbuttons()
        num_axes = joystick.get_numaxes()
        target = Motors.BASE

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
                
            current_time = int(time.time())

            # Poll joystick for button states            
            button_states = [joystick.get_button(i) for i in range(num_buttons)]
            # Poll joystick for axis states
            axis_states = [joystick.get_axis(i) for i in range(num_axes)]
            
            target = Motors.BASE

            if button_states[Buttons.PRIMARY_LEFT]:
                target = Motors.SHOULDER            
            elif button_states[Buttons.PRIMARY_RIGHT]:
                target = Motors.ELBOW
            elif button_states[Buttons.SECONDARY_LEFT]:
                target = Motors.WRIST
            elif button_states[Buttons.SECONDARY_RIGHT]:
                target = Motors.HAND                                

            # Left/right
            if target in left_right:
                if int(axis_states[0]) < 0: # left
                    output['id'] = target
                    output['direction'] = 2            
                    writer.write(output)
                    last_event_time = current_time      
                elif round(axis_states[0]) > 0: # right
                    output['id'] = target
                    output['direction'] = 1
                    writer.write(output)
                    last_event_time = current_time
            
            if target in up_down:
                if int(axis_states[1]) < 0: # up
                    output['id'] = target
                    output['direction'] = 1 if target == Motors.SHOULDER else 2
                    writer.write(output)
                    last_event_time = current_time
                elif round(axis_states[1]) > 0: # down
                    output['id'] = target
                    output['direction'] = 2 if target == Motors.SHOULDER else 1
                    writer.write(output)
                    last_event_time = current_time
                        
            if current_time - last_event_time >= 30: # No event for over 30 secs
                output['id'] = random.randint(Motors.BASE, Motors.HAND)
                output['direction'] = 3
                writer.write(output)
                time.sleep(1)
                

            #print("Axis States:", axis_states)

            # Adjust the clock speed as needed
            clock.tick(70)

    except KeyboardInterrupt:
        pygame.quit()

# Main function
def main():
    pygame.init()
    pygame.joystick.init()
    
    # Check if joystick is available
    if pygame.joystick.get_count() < 1:
        print("No joystick detected.")
        pygame.quit()
        return

    # Initialize joystick
    joystick = pygame.joystick.Joystick(0)
    joystick.init()

    print(f"Using joystick: {joystick.get_name()}")

    # Poll joystick for button and axis states
    poll_joystick(joystick)

if __name__ == "__main__":
    main()
