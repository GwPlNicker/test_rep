import xml.etree.ElementTree as ET

# Создание корневого элемента
robot = ET.Element("robot", name="quadcopter")

# Функция для добавления link с возможностью указания скорости вращения пропеллеров, скорости взлета и высоты
def add_link(name, geometry, material=None, sensor=None, mass=0, inertia=None, propeller_speed=None):
    link = ET.SubElement(robot, "link", name=name)

    # Установка физики
    if mass > 0:
        inertia_elem = ET.SubElement(link, "inertial")
        ET.SubElement(inertia_elem, "mass").text = str(mass)  # Масса в килограммах
        if inertia:
            inertia_elem = ET.SubElement(inertia_elem, "inertia")
            ET.SubElement(inertia_elem, "ixx").text = str(inertia[0])
            ET.SubElement(inertia_elem, "ixy").text = str(inertia[1])
            ET.SubElement(inertia_elem, "ixz").text = str(inertia[2])
            ET.SubElement(inertia_elem, "iyy").text = str(inertia[3])
            ET.SubElement(inertia_elem, "iyz").text = str(inertia[4])
            ET.SubElement(inertia_elem, "izz").text = str(inertia[5])

    visual = ET.SubElement(link, "visual")
    geom = ET.SubElement(visual, "geometry")

    # Определение типа геометрии
    if geometry["type"] == "mesh":
        ET.SubElement(geom, "mesh", filename=geometry["filename"])
    elif geometry["type"] == "box":
        ET.SubElement(geom, "box", size=geometry["size"])
    elif geometry["type"] == "cylinder":
        ET.SubElement(geom, "cylinder", radius=geometry["radius"], length=geometry["length"])

    if material:
        mat = ET.SubElement(visual, "material", name=material["name"])
        ET.SubElement(mat, "color", rgba=material["rgba"])

    # Если это пропеллер, добавим скорость вращения
    if propeller_speed is not None:
        ET.SubElement(link, "propeller_speed").text = str(propeller_speed)

# Добавление всех links с физическими параметрами
add_link("base_link", 
          {"type": "mesh", "filename": "C:/Users/user/ardupilot/Tools/gazebo/models/quadcopter_X/quadcopter_X.stl"}, 
          mass=1.5)

propeller_geometry = {"type": "cylinder", "radius": "1.5", "length": "10"}
material_black = {"name": "black", "rgba": "0 0 0 1"}

# Переменные для изменения скорости вращения пропеллеров,
# скорости взлета и высоты взлета
propeller_speed_value = 6000  # об/мин
takeoff_speed_value = 3  # м/с
max_flight_height = 10  # м

for i in range(1, 5):
    add_link(f"propeller{i}", propeller_geometry, material_black, mass=0.2, inertia=[0.01]*6, propeller_speed=propeller_speed_value)

flight_controller_geometry = {"type": "box", "size": "10 10 2"}
material_blue = {"name": "blue", "rgba": "0 0 1 1"}
add_link("flight_controller", flight_controller_geometry, material_blue, mass=0.3)

# Добавление других компонентов
mpu6050_sensor = {"name": "mpu6050_sensor", "type": "IMU", "update_rate": 100}
add_link("mpu6050", {"type": "box", "size": "2 2 1"}, {"name": "red", "rgba": "1 0 0 1"}, mpu6050_sensor)

bmp180_sensor = {"name": "bmp180_sensor", "type": "Barometer", "update_rate": 50}
add_link("bmp180", {"type": "box", "size": "2 2 1"}, {"name": "green", "rgba": "0 1 0 1"}, bmp180_sensor)

gps_sensor = {"name": "gps_sensor", "type": "GPS", "update_rate": 1}
add_link("gps_module", {"type": "box", "size": "2 2 1"}, {"name": "yellow", "rgba": "1 1 0 1"}, gps_sensor)

add_link("bluetooth_module", {"type": "box", "size": "2 2 1"}, {"name": "purple", "rgba": "0.5 0 0.5 1"})

# Функция для добавления joint
def add_joint(name, parent, child, origin):
    joint = ET.SubElement(robot, "joint", name=name, type="fixed")
    ET.SubElement(joint, "parent", link=parent)
    ET.SubElement(joint, "child", link=child)
    ET.SubElement(joint, "origin", rpy="0 0 0", xyz=origin)

# Добавление всех joints
add_joint("base_to_propeller1", "base_link", "propeller1", "-25 0 2.5")
add_joint("base_to_propeller2", "base_link", "propeller2", "25 0 2.5")
add_joint("base_to_propeller3", "base_link", "propeller3", "0 -25 2.5")
add_joint("base_to_propeller4", "base_link", "propeller4", "0 25 2.5")
add_joint("base_to_flight_controller", "base_link", "flight_controller", "0 0 6")
add_joint("controller_to_mpu6050", "flight_controller", "mpu6050", "3 0 1")
add_joint("controller_to_bmp180", "flight_controller", "bmp180", "-3 0 1")
add_joint("controller_to_gps", "flight_controller", "gps_module", "0 3 1")
add_joint("controller_to_bluetooth", "flight_controller", "bluetooth_module", "0 -3 1")

# Запись результата в файл
tree = ET.ElementTree(robot)
tree.write("quadcopter_sim.urdf", encoding="utf-8", xml_declaration=True)

# Дополнительные параметры, комментарии о скорости взлета и высоте
with open("quadcopter_sim.urdf", "a", encoding="utf-8") as file:  # Кодировка
    file.write("\n<!-- Параметры полета -->\n")
    file.write("<!-- Скорость взлета: {} м/с -->\n".format(takeoff_speed_value))
    file.write("<!-- Максимальная высота: {} м -->\n".format(max_flight_height))
    file.write("<!-- Скорость вращения пропеллеров: {} об/мин -->\n".format(propeller_speed_value))