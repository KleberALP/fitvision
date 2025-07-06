import cv2
import mediapipe as mp
import numpy as np

mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

def calculate_angle(a, b, c):
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)

    radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
    angle = np.abs(radians*180.0/np.pi)

    if angle > 180.0:
        angle = 360 - angle

    return angle

squat_stage = "up"
squat_reps = 0
feedback_message = ""
error_messages = []

selected_level = "beginner"

level_thresholds = {
    "beginner": {
        "knee_angle_up": 170,
        "knee_angle_down": 140,
        "hip_below_knee_required": False
    },
    "medium": {
        "knee_angle_up": 170,
        "knee_angle_down": 100,
        "hip_below_knee_threshold": 0.01,
        "hip_below_knee_required": True
    },
    "olympic": {
        "knee_angle_up": 170,
        "knee_angle_down": 90,
        "hip_below_knee_threshold": 0.005,
        "hip_below_knee_required": True
    }
}

current_level_thresholds = level_thresholds[selected_level]
THRESHOLD_UP_ANGLE = current_level_thresholds["knee_angle_up"]
THRESHOLD_DOWN_ANGLE = current_level_thresholds["knee_angle_down"]
HIP_BELOW_KNEE_REQUIRED = current_level_thresholds["hip_below_knee_required"]
THRESHOLD_HIP_BELOW_KNEE = current_level_thresholds.get("hip_below_knee_threshold", 0.0)
THRESHOLD_KNEE_FOOT_OFFSET = 0.025
DISPLAY_WIDTH = 1280
DISPLAY_HEIGHT = 720
MIN_PERSON_HEIGHT_PROPORTION = 0.5
MIN_LANDMARK_VISIBILITY = 0.6

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

if not cap.isOpened():
    print("Erro: Não foi possível abrir a câmera. Verifique se ela está conectada e não está em uso por outro programa.")
    exit()

print(f"Câmera aberta. Janela de exibição: {DISPLAY_WIDTH}x{DISPLAY_HEIGHT}. Pressione 'q' para sair.")
print(f"Nível de Avaliação Selecionado: {selected_level.upper()}")

with mp_pose.Pose(min_detection_confidence=0.6, min_tracking_confidence=0.7) as pose:
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            print("Não foi possível receber o frame (stream end?). Exiting ...")
            break

        processed_frame = cv2.resize(frame, (DISPLAY_WIDTH, DISPLAY_HEIGHT))
        processed_frame = cv2.flip(processed_frame, 1)
        image = cv2.cvtColor(processed_frame, cv2.COLOR_BGR2RGB)
        image.flags.writeable = False
        results = pose.process(image)
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        error_messages = []
        person_detected = False

        if results.pose_landmarks:
            y_coords = [landmark.y for landmark in results.pose_landmarks.landmark]
            min_y = min(y_coords)
            max_y = max(y_coords)
            pose_height_normalized = max_y - min_y
            pose_height_pixels = pose_height_normalized * DISPLAY_HEIGHT
            min_height_pixels_required = DISPLAY_HEIGHT * MIN_PERSON_HEIGHT_PROPORTION

            if pose_height_pixels > min_height_pixels_required:
                landmarks_to_check = [
                    mp_pose.PoseLandmark.LEFT_HIP,
                    mp_pose.PoseLandmark.LEFT_KNEE,
                    mp_pose.PoseLandmark.LEFT_ANKLE,
                    mp_pose.PoseLandmark.RIGHT_HIP,
                    mp_pose.PoseLandmark.RIGHT_KNEE,
                    mp_pose.PoseLandmark.RIGHT_ANKLE,
                    mp_pose.PoseLandmark.NOSE
                ]
                all_critical_landmarks_visible = True
                for lm_idx in landmarks_to_check:
                    if results.pose_landmarks.landmark[lm_idx.value].visibility < MIN_LANDMARK_VISIBILITY:
                        all_critical_landmarks_visible = False
                        break

                if all_critical_landmarks_visible:
                    person_detected = True
                else:
                    error_messages.append("Aproxime-se/Posicione-se! Pontos do corpo ocultos.")
                    squat_stage = "up"
                    feedback_message = ""
            else:
                error_messages.append(f"Posicione-se! Pessoa muito pequena ({int(pose_height_pixels)}px).")
                squat_stage = "up"
                feedback_message = ""
        else:
            error_messages.append("Nao consigo te ver! Posicione-se bem na camera.")
            feedback_message = ""
            squat_reps = 0
            squat_stage = "up"

        if person_detected:
            try:
                landmarks = results.pose_landmarks.landmark

                left_hip = [landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x, landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y]
                left_knee = [landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].x, landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].y]
                left_ankle = [landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].x, landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].y]
                left_shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x, landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
                left_heel = [landmarks[mp_pose.PoseLandmark.LEFT_HEEL.value].x, landmarks[mp_pose.PoseLandmark.LEFT_HEEL.value].y]
                left_foot_index = [landmarks[mp_pose.PoseLandmark.LEFT_FOOT_INDEX.value].x, landmarks[mp_pose.PoseLandmark.LEFT_FOOT_INDEX.value].y]

                left_knee_angle = calculate_angle(left_hip, left_knee, left_ankle)
                left_trunk_angle = calculate_angle(left_hip, left_shoulder, [left_shoulder[0], left_hip[1]])

                cv2.putText(image, f"Angulo Joelho E: {int(left_knee_angle)}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2, cv2.LINE_AA)
                cv2.putText(image, f"Angulo Tronco E: {int(left_trunk_angle)}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2, cv2.LINE_AA)
                cv2.putText(image, f"Estagio: {squat_stage}", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2, cv2.LINE_AA)
                cv2.putText(image, f"Nivel: {selected_level.upper()}", (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2, cv2.LINE_AA)

                is_hip_below_knee = False
                if HIP_BELOW_KNEE_REQUIRED:
                    is_hip_below_knee = (landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y >
                                         landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].y - THRESHOLD_HIP_BELOW_KNEE)
                else:
                    is_hip_below_knee = True

                if squat_stage == "up":
                    if left_knee_angle < THRESHOLD_DOWN_ANGLE:
                        if is_hip_below_knee:
                            squat_stage = "down"
                        else:
                            feedback_message = "Agache mais! Quadril abaixo dos joelhos."
                            error_messages.append("Agache mais!")
                elif squat_stage == "down":
                    if left_knee_angle > THRESHOLD_UP_ANGLE:
                        if is_hip_below_knee:
                            squat_reps += 1
                            squat_stage = "up"
                            feedback_message = "Boa! Repetição completa!"
                        else:
                            feedback_message = "Repetição incompleta: Agache mais!"
                            error_messages.append("Repetição incompleta!")
                            squat_stage = "up"

                current_angle_down_or_up = left_knee_angle < THRESHOLD_DOWN_ANGLE or \
                                           (squat_stage == "up" and left_knee_angle < THRESHOLD_UP_ANGLE)

                if current_angle_down_or_up:
                    if left_trunk_angle > 15 or left_trunk_angle < 0:
                        error_messages.append("Coluna reta! Peito aberto.")
                    if left_knee[0] < (left_foot_index[0] - THRESHOLD_KNEE_FOOT_OFFSET):
                        error_messages.append("Joelhos atrás dos pés! Empurre o quadril para trás.")
                    if HIP_BELOW_KNEE_REQUIRED and squat_stage == "up" and left_knee_angle < THRESHOLD_DOWN_ANGLE and not is_hip_below_knee:
                        feedback_message = "Agache mais! Quadril abaixo dos joelhos."
                        error_messages.append("Agache mais!")

            except Exception as e:
                print(f"ERRO DE PROCESSAMENTO DE LANDMARKS: {e}")
                error_messages.append("Problema com os pontos! Reposicione-se na camera.")
                feedback_message = ""
                squat_stage = "up"

        if results.pose_landmarks and person_detected:
            mp_drawing.draw_landmarks(
                image,
                results.pose_landmarks,
                mp_pose.POSE_CONNECTIONS,
                mp_drawing.DrawingSpec(color=(245, 117, 66), thickness=2, circle_radius=2),
                mp_drawing.DrawingSpec(color=(245, 66, 230), thickness=2, circle_radius=2)
            )

        text_offset_from_right = 20
        text_y_start = 30

        (text_width_reps, text_height_reps) = cv2.getTextSize(f"Repeticoes: {squat_reps}", cv2.FONT_HERSHEY_SIMPLEX, 1, 2)[0]
        cv2.putText(image, f"Repeticoes: {squat_reps}", (DISPLAY_WIDTH - text_width_reps - text_offset_from_right, text_y_start),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)

        feedback_color = (0, 255, 0) if "Boa!" in feedback_message else (0, 0, 255)
        (text_width_feedback, text_height_feedback) = cv2.getTextSize(feedback_message, cv2.FONT_HERSHEY_SIMPLEX, 0.8, 2)[0]
        cv2.putText(image, feedback_message, (DISPLAY_WIDTH - text_width_feedback - text_offset_from_right, text_y_start + 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, feedback_color, 2, cv2.LINE_AA)

        y_offset_errors = text_y_start + 80
        for error in error_messages:
            (text_width_error, text_height_error) = cv2.getTextSize(error, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)[0]
            cv2.putText(image, error, (DISPLAY_WIDTH - text_width_error - text_offset_from_right, y_offset_errors),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2, cv2.LINE_AA)
            y_offset_errors += 30

        cv2.imshow('Detecao de Pose e Avaliacao (Pressione Q para sair)', image)

        if cv2.waitKey(10) & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()
print("Aplicacao encerrada.")
