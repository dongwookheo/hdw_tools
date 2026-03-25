from pathlib import Path
from rosbags.highlevel import AnyReader
from rosbags.typesys import Stores, get_typestore
import csv
import struct
import numpy as np

bagpath = Path("/root/data/0325_check_heightmap")
typestore = get_typestore(Stores.ROS2_HUMBLE)

PC2_DTYPE_MAP = {
    1: ("b", 1),
    2: ("B", 1),
    3: ("h", 2),
    4: ("H", 2),
    5: ("i", 4),
    6: ("I", 4),
    7: ("f", 4),
    8: ("d", 8),
}


# ── 핸들러: (headers, rows) 반환 ─────────────────────────────────────
# rows는 list of list. 한 메시지가 여러 행이 될 수 있음 (LaserScan 등)


def handle_imu(msg):
    headers = [
        "angular_velocity.x",
        "angular_velocity.y",
        "angular_velocity.z",
        "linear_acceleration.x",
        "linear_acceleration.y",
        "linear_acceleration.z",
        "orientation.x",
        "orientation.y",
        "orientation.z",
        "orientation.w",
        *[f"angular_velocity_covariance.{i}" for i in range(9)],
        *[f"linear_acceleration_covariance.{i}" for i in range(9)],
        *[f"orientation_covariance.{i}" for i in range(9)],
    ]
    row = [
        msg.angular_velocity.x,
        msg.angular_velocity.y,
        msg.angular_velocity.z,
        msg.linear_acceleration.x,
        msg.linear_acceleration.y,
        msg.linear_acceleration.z,
        msg.orientation.x,
        msg.orientation.y,
        msg.orientation.z,
        msg.orientation.w,
        *list(msg.angular_velocity_covariance),
        *list(msg.linear_acceleration_covariance),
        *list(msg.orientation_covariance),
    ]
    return headers, [row]


def handle_odometry(msg):
    headers = [
        "position.x",
        "position.y",
        "position.z",
        "orientation.x",
        "orientation.y",
        "orientation.z",
        "orientation.w",
        "linear.x",
        "linear.y",
        "linear.z",
        "angular.x",
        "angular.y",
        "angular.z",
        *[f"pose_covariance.{i}" for i in range(36)],
        *[f"twist_covariance.{i}" for i in range(36)],
    ]
    p = msg.pose.pose.position
    o = msg.pose.pose.orientation
    l = msg.twist.twist.linear
    a = msg.twist.twist.angular
    row = [
        p.x,
        p.y,
        p.z,
        o.x,
        o.y,
        o.z,
        o.w,
        l.x,
        l.y,
        l.z,
        a.x,
        a.y,
        a.z,
        *list(msg.pose.covariance),
        *list(msg.twist.covariance),
    ]
    return headers, [row]


def handle_navsatfix(msg):
    headers = [
        "latitude",
        "longitude",
        "altitude",
        *[f"position_covariance.{i}" for i in range(9)],
        "position_covariance_type",
    ]
    row = [
        msg.latitude,
        msg.longitude,
        msg.altitude,
        *list(msg.position_covariance),
        msg.position_covariance_type,
    ]
    return headers, [row]


def handle_float32multiarray(msg):
    data = list(msg.data)
    headers = [str(i) for i in range(len(data))]
    return headers, [data]


def handle_pointcloud2(msg):
    field_names = [f.name for f in msg.fields]
    rows = []
    for i in range(msg.width * msg.height):
        offset = i * msg.point_step
        point = []
        for f in msg.fields:
            fmt, _ = PC2_DTYPE_MAP.get(f.datatype, ("f", 4))
            try:
                val = struct.unpack_from(fmt, msg.data, offset + f.offset)[0]
            except struct.error:
                val = None
            point.append(val)
        rows.append(point)
    return field_names, rows


def handle_image(msg, topic_name, timestamp):
    dtype_map = {
        "mono8": (np.uint8, 1),
        "rgb8": (np.uint8, 3),
        "bgr8": (np.uint8, 3),
        "32FC1": (np.float32, 1),
        "16UC1": (np.uint16, 1),
    }
    dtype, channels = dtype_map.get(msg.encoding, (np.uint8, 1))
    arr = np.frombuffer(bytes(msg.data), dtype=dtype).reshape(
        msg.height, msg.width, channels
    )
    Path(f"{topic_name}_images").mkdir(exist_ok=True)
    npy_path = f"{topic_name}_images/{timestamp}.npy"
    np.save(npy_path, arr)

    headers = ["encoding", "height", "width", "npy_file"]
    row = [msg.encoding, msg.height, msg.width, npy_path]
    return headers, [row]


def handle_compressed_image(msg):
    headers = ["format", "size_bytes"]
    row = [msg.format, len(msg.data)]
    return headers, [row]


def handle_laserscan(msg):
    headers = ["angle", "range", "intensity"]
    rows = []
    angle = msg.angle_min
    for i, r in enumerate(msg.ranges):
        intensity = msg.intensities[i] if i < len(msg.intensities) else None
        rows.append([angle, r, intensity])
        angle += msg.angle_increment
    return headers, rows


def handle_jointstate(msg):
    headers = ["joint", "position", "velocity", "effort"]
    rows = []
    for i, name in enumerate(msg.name):
        rows.append(
            [
                name,
                msg.position[i] if i < len(msg.position) else None,
                msg.velocity[i] if i < len(msg.velocity) else None,
                msg.effort[i] if i < len(msg.effort) else None,
            ]
        )
    return headers, rows


def handle_fallback(msg):
    """등록되지 않은 타입 → 최대한 flatten"""

    def _flatten(m, prefix=""):
        result = {}
        if isinstance(m, (int, float, bool, str, np.floating, np.integer)):
            result[prefix.rstrip(".")] = m
        elif isinstance(m, bytes):
            result[prefix.rstrip(".")] = f"<bytes len={len(m)}>"
        elif hasattr(m, "__iter__") and not isinstance(m, (str, bytes)):
            items = list(m)
            if not items:
                result[prefix.rstrip(".")] = "[]"
            elif isinstance(items[0], (int, float, np.floating, np.integer)):
                result[prefix.rstrip(".")] = str(
                    [x.item() if hasattr(x, "item") else x for x in items]
                )
            else:
                for i, v in enumerate(items):
                    result.update(_flatten(v, f"{prefix}{i}."))
        elif hasattr(m, "__dataclass_fields__"):
            for field in m.__dataclass_fields__:
                result.update(_flatten(getattr(m, field), f"{prefix}{field}."))
        else:
            result[prefix.rstrip(".")] = str(m)
        return result

    flat = _flatten(msg)
    return list(flat.keys()), [list(flat.values())]


def make_filename(topic, msgtype):
    topic_part = topic.lstrip("/").replace("/", "_")
    type_part = msgtype.replace("/msg/", "_").replace("/", "_")
    return f"{topic_part}__{type_part}"


# ── 핸들러 등록 테이블 ────────────────────────────────────────────────
HANDLERS = {
    "sensor_msgs/msg/Imu": handle_imu,
    "nav_msgs/msg/Odometry": handle_odometry,
    "sensor_msgs/msg/NavSatFix": handle_navsatfix,
    "std_msgs/msg/Float32MultiArray": handle_float32multiarray,
    "std_msgs/msg/Float64MultiArray": handle_float32multiarray,  # 구조 동일
    "sensor_msgs/msg/PointCloud2": handle_pointcloud2,
    "sensor_msgs/msg/CompressedImage": handle_compressed_image,
    "sensor_msgs/msg/LaserScan": handle_laserscan,
    "sensor_msgs/msg/JointState": handle_jointstate,
}


# ── 메인 처리 ─────────────────────────────────────────────────────────
with AnyReader([bagpath], default_typestore=typestore) as reader:

    csv_files = {}
    csv_writers = {}
    npy_counters = {}

    for connection, timestamp, rawdata in reader.messages():
        topic = connection.topic
        msgtype = connection.msgtype
        topic_name = make_filename(topic, msgtype)

        try:
            msg = reader.deserialize(rawdata, msgtype)
        except Exception as e:
            print(f"[WARN] 역직렬화 실패 {topic}: {e}")
            continue

        try:
            # Image는 npy 저장 경로가 필요해서 별도 분기
            if msgtype == "sensor_msgs/msg/Image":
                headers, rows = handle_image(msg, topic_name, timestamp)
                npy_counters[topic] = npy_counters.get(topic, 0) + 1
            else:
                handler = HANDLERS.get(msgtype, handle_fallback)
                headers, rows = handler(msg)

            # CSV 초기화 (첫 메시지 기준 헤더)
            if topic not in csv_files:
                f = open(f"{topic_name}.csv", "w", newline="")
                csv_files[topic] = f
                csv_writers[topic] = csv.writer(f)
                csv_writers[topic].writerow(["timestamp"] + headers)

            for row in rows:
                csv_writers[topic].writerow([timestamp] + row)

        except Exception as e:
            print(f"[WARN] 처리 실패 {topic} @ {timestamp}: {e}")
            continue

    for f in csv_files.values():
        f.close()

print("=== 저장 완료 ===")
for topic in csv_files:
    print(f"  {topic.lstrip('/').replace('/', '_')}.csv")
for topic, count in npy_counters.items():
    print(f"  {topic.lstrip('/').replace('/', '_')}_images/ ({count}개 .npy)")
