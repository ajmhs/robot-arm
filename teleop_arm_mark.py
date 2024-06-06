# Import required libs
import threading, time, serial
from os import path as os_path

# Import Connext
import rti.connextdds as dds

# Import LSS library
import lss
import lss_const as lssc

def publish_telemetry(writer, motorlist, printit):
    for i in range(5):
        lss = motorlist[i]
        status = lss.getStatus()
        pos = -1
        rpm = -1
        curr = -1
        temp = -1
        if status is None:
    #        lss.reset()
            status = lss.getStatus()
            print("Status is None for index:" + str(i))
        elif(status != lssc.LSS_StatusUnknown):
            pos_str = lss.getPosition()
            if pos_str is None:
                print("Position query returned None for index " + str(i))
            else:
                pos = int(pos_str) / 10.0

            rpm_str = lss.getSpeedRPM()
            if rpm_str is None:
                print("RPM query returned None for index " + str(i))
            else:
                rpm= int(rpm_str)
            curr_str = lss.getCurrent()
            if curr_str is None:
                print("Current query returned None for index " + str(i))
            else:
                curr = int(curr_str)
            volt_str = lss.getVoltage()
            if volt_str is None:
                print("Volts query returned None for index " + str(i))
            else:
                volt = int(volt_str) / 1000.0

            temp_str =  lss.getTemperature()
            if temp_str is None:
                print("Temp query returned None of index " + str(i))
            else:
                temp = int(temp_str) / 10

            telemetry = dds.DynamicData(motor_telemetry_t)

            telemetry['id'] = i
            telemetry['position_deg'] = pos
            telemetry['speed_rpm'] = rpm
            telemetry['current_mA'] = curr
            telemetry['voltage_V'] = volt
            telemetry['temp_c'] = temp
        
            writer.write(telemetry)
            if printit:
                print("Pos=", pos, " Curr=", curr, " Temp=", temp)

#
# Base (axis 0) rotates from 0 to 360 degrees, but actual
# value sent is 0 to 3600
#
# Logic here is we go from 0 to 180 to 0. Increment each time we get a
# value from the dance script
#
def move_axis_0(motorlist, position, inc):
    motor_id = 0
    positions = [0, 30, 60, 30, 0, -30, -60, -30, 0]

    if position >= 0 and position < len(positions):
        magnitude = positions[position] * 10
    else:
        magnitude = 0
        print("move_axis_0: position index out of range: ", position)

    print("Rotating base (0) to: ", magnitude/10)
    motorlist[motor_id].setMaxSpeedRPM(10)      
    motorlist[motor_id].move(magnitude)

    if inc:
        position = position + 1
        if position == len(positions):
            position = position - 1
            inc = False
    else:
        position = position - 1
        if position < 0:
            position = 0
            inc = True

    return position, inc

# Shoulder
def move_axis_1(motorlist, position, inc):
    motor_id = 1
    positions = [0, 10, 20, 30, 20, 10, 0]

    if position >= 0 and position < len(positions):
        magnitude = positions[position] * 10
    else:
        magnitude = 0
        print("move_axis_1: position index out of range: ", position)

    print("Rotating arm (1) to: ", magnitude/10)
    motorlist[motor_id].setMaxSpeedRPM(3)
    motorlist[motor_id].move(magnitude)

    if inc:
        position = position + 1
        if position == len(positions):
            position = position - 1
            inc = False
    else:
        position = position - 1
        if position < 0:
            position = 0
            inc = True

    return position, inc

# Elbow
def move_axis_2(motorlist, position, inc):
    motor_id = 2
    positions = [0, -10, -20, -30, -20, -10, 0]

    if position >= 0 and position < len(positions):
        magnitude = positions[position] * 10
    else:
        magnitude = 0
        print("move_axis_2: position index out of range: ", position)

    print("Rotating axis (2) to: ", magnitude/10)
    motorlist[motor_id].setMaxSpeedRPM(3)
    motorlist[motor_id].move(magnitude)

    if inc:
        position = position + 1
        if position == len(positions):
            position = position - 1
            inc = False
    else:
        position = position - 1
        if position < 0:
            position = 0
            inc = True

    return position, inc


# Wrist
def move_axis_3(motorlist, position, inc):
    motor_id = 3
    positions = [0, 15, 30, 15, 0, -15, -30, -15, 0]

    if position >= 0 and position < len(positions):
        magnitude = positions[position] * 10
    else:
        magnitude = 0
        print("move_axis_3: position index out of range: ", position)
    
    print("Rotating clamp position (3) to: ", magnitude/10) 
    motorlist[motor_id].setMaxSpeedRPM(5)    
    motorlist[motor_id].move(magnitude)

    if inc:
        position = position + 1
        if position == len(positions):
            position = position - 1
            inc = False
    else:
        position = position - 1
        if position < 0:
            position = 0
            inc = True
        
    return position, inc

# Hand    
def move_axis_4(motorlist, position, inc):
    motor_id = 4
    positions = [0, -7.5, -15, -7.5, 0]

    if position >= 0 and position < len(positions):
        magnitude = positions[position] * 10
    else:
        magnitude = 0
        print("move_axis_4: position index out of range: ", position)
    
    print("Rotating clamp position (4) to: ", magnitude/10)
    motorlist[motor_id].setMaxSpeedRPM(5)    
    motorlist[motor_id].move(magnitude)

    if inc:
        position = position + 1
        if position == len(positions):
            position = position - 1
            inc = False
    else:
        position = position - 1
        if position < 0:
            position = 0
            inc = True
        
    return position, inc

                
# Constants
CST_LSS_Port = "/dev/ttyUSB0"		# For Linux/Unix platforms
# CST_LSS_Port = "COM230"				# For windows platforms
CST_LSS_Baud = lssc.LSS_DefaultBaud

# Create and open a serial port
lss.initBus(CST_LSS_Port, CST_LSS_Baud)

# Create LSS objects
motorlist = []
motordirection = []

for i in range(1,6):
    motorlist.append(lss.LSS(i))
    #lss.LSS(i).reset()
    motordirection.append(0)
    time.sleep(0.100)

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



print("Sleeping for 2")
time.sleep(2)

for i in [0, 1, 2, 3, 4]:
    print("Resetting axis", i)
    lss = motorlist[i]
    lss.reset()
    time.sleep(1)
    
print("Sleeping for 2")
time.sleep(2)

for i in [0, 1, 2, 3, 4]:
    motorlist[i].move(0) # go to initial position

interation = 0
printit = False
sleep_time = 0.01

motor0i = 0
motor1i = 0
motor2i = 0
motor3i = 0
motor4i = 0
motor0inc = True
motor1inc = True
motor2inc = True
motor3inc = True
motor4inc = True

while True:
    if interation == 1 / sleep_time:
        print("Printing ...")
        printit = True
        interation = 0
    else:
        printit = False
    interation = interation + 1 
    publish_telemetry(telemetry_writer, motorlist, printit)
    time.sleep(sleep_time)
    for data, info in control_reader.take():
        if info.valid: 
            motor_id = int(data["id"])
            direction = int(data["direction"])

            if  motor_id == 0:
                [motor0i, motor0inc] = move_axis_0(motorlist, motor0i, motor0inc)
            if  motor_id == 1:
                [motor1i, motor1inc] = move_axis_1(motorlist, motor1i, motor1inc)
            if  motor_id == 2:
                [motor2i, motor2inc] = move_axis_2(motorlist, motor2i, motor2inc)
            if  motor_id == 3:
                [motor3i, motor3inc] = move_axis_3(motorlist, motor3i, motor3inc)
            if  motor_id == 4:
                [motor4i, motor4inc] = move_axis_4(motorlist, motor4i, motor4inc)
