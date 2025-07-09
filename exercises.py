import mediapipe as mp
from utils import calculate_angle

# Dicionário de configurações para os níveis de todos os exercícios
level_thresholds = {
    "squat": {
        "beginner": {"knee_angle_up": 170, "knee_angle_down": 140, "hip_below_knee_required": False},
        "medium": {"knee_angle_up": 170, "knee_angle_down": 100, "hip_below_knee_threshold": 0.01, "hip_below_knee_required": True},
        "advanced": {"knee_angle_up": 170, "knee_angle_down": 90, "hip_below_knee_threshold": 0.005, "hip_below_knee_required": True}
    },
    "bicep_curl": {
        "beginner": {"elbow_angle_up": 160, "elbow_angle_down": 50},
        "medium": {"elbow_angle_up": 165, "elbow_angle_down": 40},
        "advanced": {"elbow_angle_up": 170, "elbow_angle_down": 30}
    },
    "jumping_jack": {
        "beginner": {"shoulder_angle_up": 130, "feet_distance_apart": 0.15},
        "medium": {"shoulder_angle_up": 140, "feet_distance_apart": 0.20},
        "advanced": {"shoulder_angle_up": 150, "feet_distance_apart": 0.25}
    }
}

class BaseExercise:
    """Classe base para todos os exercícios."""
    def __init__(self):
        self.reps = 0
        self.stage = None
        self.feedback = ""
        self.errors = []

    def process_landmarks(self, landmarks):
        raise NotImplementedError("Este método deve ser implementado pela subclasse.")

    def reset(self):
        self.reps = 0
        self.stage = "up" if self.stage is not None else None
        self.feedback = ""
        self.errors = []

class Squat(BaseExercise):
    def __init__(self, level):
        super().__init__()
        self.stage = "up"
        self.level = level
        self.thresholds = level_thresholds["squat"][level]
        self.mp_pose = mp.solutions.pose
        self.THRESHOLD_KNEE_FOOT_OFFSET = 0.05

    def process_landmarks(self, landmarks):
        self.errors = []
        hip = [landmarks[self.mp_pose.PoseLandmark.LEFT_HIP.value].x, landmarks[self.mp_pose.PoseLandmark.LEFT_HIP.value].y]
        knee = [landmarks[self.mp_pose.PoseLandmark.LEFT_KNEE.value].x, landmarks[self.mp_pose.PoseLandmark.LEFT_KNEE.value].y]
        ankle = [landmarks[self.mp_pose.PoseLandmark.LEFT_ANKLE.value].x, landmarks[self.mp_pose.PoseLandmark.LEFT_ANKLE.value].y]
        shoulder = [landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value].x, landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
        foot_index = [landmarks[self.mp_pose.PoseLandmark.LEFT_FOOT_INDEX.value].x, landmarks[self.mp_pose.PoseLandmark.LEFT_FOOT_INDEX.value].y]
        knee_angle = calculate_angle(hip, knee, ankle)
        trunk_angle = calculate_angle(knee, hip, shoulder)
        is_hip_below_knee = (hip[1] > knee[1] - self.thresholds.get("hip_below_knee_threshold", 0.0)) if self.thresholds["hip_below_knee_required"] else True

        if self.stage == "up":
            if knee_angle < self.thresholds["knee_angle_down"]:
                if is_hip_below_knee:
                    self.stage = "down"
                    self.feedback = "Subindo..."
                else:
                    self.feedback = "Agache mais!"
                    self.errors.append("Agache mais!")
        elif self.stage == "down":
            if knee_angle > self.thresholds["knee_angle_up"]:
                self.reps += 1
                self.stage = "up"
                self.feedback = "Boa! Repeticao completa!"

        is_in_squat_position = knee_angle < 160
        if is_in_squat_position:
            if trunk_angle < 150:
                 self.errors.append("Coluna reta! Peito aberto.")
            if knee[0] > foot_index[0] + self.THRESHOLD_KNEE_FOOT_OFFSET:
                 self.errors.append("Joelhos para tras!")

class BicepCurl(BaseExercise):
    def __init__(self, level):
        super().__init__()
        self.stage = "down"
        self.level = level
        self.thresholds = level_thresholds["bicep_curl"][level]
        self.mp_pose = mp.solutions.pose
        self.ELBOW_MOVEMENT_THRESHOLD = 0.07
        self.initial_elbow_x = 0

    def process_landmarks(self, landmarks):
        self.errors = []
        shoulder = [landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x, landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y]
        elbow = [landmarks[self.mp_pose.PoseLandmark.RIGHT_ELBOW.value].x, landmarks[self.mp_pose.PoseLandmark.RIGHT_ELBOW.value].y]
        wrist = [landmarks[self.mp_pose.PoseLandmark.RIGHT_WRIST.value].x, landmarks[self.mp_pose.PoseLandmark.RIGHT_WRIST.value].y]
        hip = [landmarks[self.mp_pose.PoseLandmark.RIGHT_HIP.value].x, landmarks[self.mp_pose.PoseLandmark.RIGHT_HIP.value].y]
        knee = [landmarks[self.mp_pose.PoseLandmark.RIGHT_KNEE.value].x, landmarks[self.mp_pose.PoseLandmark.RIGHT_KNEE.value].y]
        elbow_angle = calculate_angle(shoulder, elbow, wrist)
        body_posture_angle = calculate_angle(knee, hip, shoulder)

        if body_posture_angle < 165:
            self.errors.append("Mantenha a postura reta!")

        if self.stage == "down":
            if elbow_angle < self.thresholds["elbow_angle_down"]:
                self.stage = "up"
                self.feedback = "Estenda o braco"
            self.initial_elbow_x = elbow[0]
        elif self.stage == "up":
            if abs(elbow[0] - self.initial_elbow_x) > self.ELBOW_MOVEMENT_THRESHOLD:
                self.errors.append("Mantenha o cotovelo fixo!")
            if elbow_angle > self.thresholds["elbow_angle_up"]:
                self.stage = "down"
                self.reps += 1
                self.feedback = "Boa!"
            elif elbow_angle > self.thresholds["elbow_angle_down"]:
                 self.feedback = "Estenda o braco completamente"

class JumpingJack(BaseExercise):
    def __init__(self, level):
        super().__init__()
        self.stage = "down"
        self.level = level
        self.thresholds = level_thresholds["jumping_jack"][level]
        self.mp_pose = mp.solutions.pose

    def process_landmarks(self, landmarks):
        self.errors = []
        left_shoulder = [landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value].x, landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
        left_hip = [landmarks[self.mp_pose.PoseLandmark.LEFT_HIP.value].x, landmarks[self.mp_pose.PoseLandmark.LEFT_HIP.value].y]
        left_elbow = [landmarks[self.mp_pose.PoseLandmark.LEFT_ELBOW.value].x, landmarks[self.mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
        left_ankle = landmarks[self.mp_pose.PoseLandmark.LEFT_ANKLE.value]
        right_ankle = landmarks[self.mp_pose.PoseLandmark.RIGHT_ANKLE.value]
        shoulder_angle = calculate_angle(left_hip, left_shoulder, left_elbow)
        feet_distance = abs(left_ankle.x - right_ankle.x)

        arms_up = shoulder_angle > self.thresholds["shoulder_angle_up"]
        legs_apart = feet_distance > self.thresholds["feet_distance_apart"]

        if self.stage == "down" and arms_up and legs_apart:
            self.stage = "up"
            self.feedback = "Fechando..."
        elif self.stage == "up" and not arms_up and not legs_apart:
            self.stage = "down"
            self.reps += 1
            self.feedback = "Boa!"
            
        if self.stage == 'up' and not arms_up:
            self.errors.append("Levante mais os bracos!")
        if self.stage == 'up' and not legs_apart:
            self.errors.append("Afaste mais as pernas!")
