# Import required libs
import threading, time, serial
from os import path as os_path
import random

# Import Connext
import rti.connextdds as dds

# Import LSS library
import lss
import lss_const as lssc

def publish_telemetry(writer, motorlist):
    for i in range(5):
        lss = motorlist[i]

        telemetry = dds.DynamicData(motor_telemetry_t)

        telemetry['id'] = i
        telemetry['position_deg'] = int(lss.getPosition()) / 10.0
        telemetry['speed_rpm'] = int(lss.getSpeedRPM())
        telemetry['current_mA'] = int(lss.getCurrent())
        telemetry['voltage_V'] = int(lss.getVoltage()) / 1000.0
        telemetry['temp_c'] = int(lss.getTemperature()) / 10.0
        
        writer.write(telemetry)


# Constants
CST_LSS_Port = "/dev/ttyUSB0"		# For Linux/Unix platforms
# CST_LSS_Port = "COM230"				# For windows platforms
CST_LSS_Baud = lssc.LSS_DefaultBaud

maxrpm = [5,3,5,5,5] # How fast each servo should spin
limits = [(-90,180),(-30,75),(-90,15),(-85,65),(-90,-2)] # Movement limits for each servo

# Create and open a serial port
lss.initBus(CST_LSS_Port, CST_LSS_Baud)

# Create LSS objects
motorlist = []

for i in range(1,6):
    motorlist.append(lss.LSS(i))

for i in [0, 1, 2, 3, 4]:
    print("Resetting axis", i)
    lss = motorlist[i]
    lss.reset()
    time.sleep(1)
    lss.move(0) # go to inital position
            

time.sleep(2)

for i in [0, 1, 2, 3, 4]:
    motorlist[i].move(0) # go to initial position

print("Starting")
file_path = os_path.dirname(os_path.realpath(__file__))
provider = dds.QosProvider(uri=os_path.join(file_path, 'ConnextMedicalDemoArchitecture.xml'))

config_name='MedicalDemoParticipantLibrary::ArmController'
participant = provider.create_participant_from_config(config=config_name) 

motor_telemetry_t = provider.type('SurgicalRobot::MotorTelemetry')

telemetry_writer = dds.DynamicData.DataWriter(
    participant.find_datawriter('publisher::MotorTelemetryDW'))

control_reader = dds.DynamicData.DataReader(
    participant.find_datareader('subscriber::MotorControlDR'))

def get_motor_pos(motor_id): 
    return int(motorlist[motor_id].getPosition()) / 10.0

while True:
    publish_telemetry(telemetry_writer, motorlist)
    time.sleep(0.001)
    for data, info in control_reader.take():
        if info.valid:        
            delta = 0

            #print(data)

            motor_id = int(data["id"])
            direction = int(data["direction"])
        
            pos = int(motorlist[motor_id].getPosition()) / 10.0

            if direction == 1: # left leg in
                delta = maxrpm[motor_id]
                if pos+delta >= limits[motor_id][1]:
                    delta = 0

            elif direction == 2: # left leg out
                delta = -maxrpm[motor_id]
                if pos+delta <= limits[motor_id][0]:
                    delta = 0
            
            elif direction == 3: # do the hokey-cokey
                newpos = random.randint(limits[motor_id][0], limits[motor_id][1])
                if newpos > pos:
                    delta = newpos - pos
                elif pos > newpos:
                    delta = -(pos - newpos)
                else:
                    delta = 0

                if delta > 0 and motor_id in [1,3] or delta < 0 and motor_id == 2: # Motor sometimes touches its toes and gets stuck
                    if get_motor_pos(1) > 70 and get_motor_pos(2) < 15 and get_motor_pos(3) > 25: 
                        delta = 0
                

            print(f"Delta is {delta}, new position is {pos+delta}")

            if delta != 0: 
                rpm = maxrpm[motor_id]
                if direction == 2 and motor_id == 2:
                    rpm = rpm / 1.5

                motorlist[motor_id].setMaxSpeedRPM(rpm)
                motorlist[motor_id].move((pos+delta) * 10)
            
