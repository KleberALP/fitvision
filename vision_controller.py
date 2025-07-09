import cv2
import mediapipe as mp
import numpy as np

# Importa as classes de exercícios e a função de utilidade
from exercises import Squat, BicepCurl, JumpingJack
from utils import calculate_angle

# --- Funções de UI e Desenho ---

def hex_to_bgr(hex_color):
    """Converte uma cor hexadecimal para o formato BGR do OpenCV."""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (4, 2, 0))

# Paleta de cores (Nord) para consistência visual
NORD_NIGHT = hex_to_bgr("#2E3440")
NORD_SNOW = hex_to_bgr("#D8DEE9")
NORD_FROST_GREEN = hex_to_bgr("#A3BE8C")
NORD_FROST_CYAN = hex_to_bgr("#88C0D0")
NORD_AURORA_RED = hex_to_bgr("#BF616A")

def draw_panel(image, x, y, width, height, color, alpha=0.6):
    """Desenha um painel semi-transparente na imagem."""
    overlay = image.copy()
    cv2.rectangle(overlay, (x, y), (x + width, y + height), color, -1)
    cv2.addWeighted(overlay, alpha, image, 1 - alpha, 0, image)


def start_exercise_session(exercise_name, level):
    """
    Inicia a sessão de exercício com a câmera, processando o exercício selecionado.
    """
    # --- CONFIGURAÇÕES GERAIS ---
    DISPLAY_WIDTH = 1280
    DISPLAY_HEIGHT = 720
    MIN_PERSON_HEIGHT_PROPORTION = 0.5
    MIN_LANDMARK_VISIBILITY = 0.6

    # --- FUNÇÃO AUXILIAR PARA OBTER INSTÂNCIA DO EXERCÍCIO ---
    def get_exercise_instance(name, lvl):
        if name == "squat":
            return Squat(lvl)
        elif name == "bicep_curl":
            return BicepCurl(lvl)
        elif name == "jumping_jack":
            return JumpingJack(lvl)
        return None

    # --- INICIALIZAÇÃO DA CÂMERA E MEDIAPIPE ---
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Erro: Não foi possível abrir a câmera.")
        return

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    mp_drawing = mp.solutions.drawing_utils
    mp_pose = mp.solutions.pose

    current_exercise = get_exercise_instance(exercise_name, level)
    if not current_exercise:
        print(f"Erro: Exercício '{exercise_name}' não reconhecido.")
        return

    print(f"Iniciando exercício: {exercise_name.upper()} | Nível: {level.upper()}")

    # --- LOOP PRINCIPAL DE PROCESSAMENTO DE VÍDEO ---
    with mp_pose.Pose(min_detection_confidence=0.6, min_tracking_confidence=0.7) as pose:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                print("Não foi possível receber o frame. Encerrando...")
                break

            # Redimensiona e processa o frame
            processed_frame = cv2.resize(frame, (DISPLAY_WIDTH, DISPLAY_HEIGHT))
            processed_frame = cv2.flip(processed_frame, 1)
            image = cv2.cvtColor(processed_frame, cv2.COLOR_BGR2RGB)
            
            image.flags.writeable = False
            results = pose.process(image)
            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

            general_errors = []
            person_detected = False

            # Lógica de detecção de pessoa
            if results.pose_landmarks:
                y_coords = [landmark.y for landmark in results.pose_landmarks.landmark]
                if max(y_coords) - min(y_coords) > MIN_PERSON_HEIGHT_PROPORTION:
                    person_detected = True
                else:
                    general_errors.append("Aproxime-se da camera!")
            else:
                general_errors.append("Ninguem detectado. Posicione-se na camera.")

            # Processa os landmarks se uma pessoa foi detectada
            if person_detected:
                try:
                    landmarks = results.pose_landmarks.landmark
                    current_exercise.process_landmarks(landmarks)
                except Exception as e:
                    print(f"ERRO AO PROCESSAR LANDMARKS: {e}")
                    general_errors.append("Erro no processamento. Tente se reposicionar.")
            else:
                current_exercise.reset()

            # --- DESENHA A NOVA INTERFACE NA TELA ---

            # 1. Painel de Repetições (canto superior direito)
            reps_text = str(current_exercise.reps)
            (w_reps_label, h_reps_label), _ = cv2.getTextSize("REPS", cv2.FONT_HERSHEY_SIMPLEX, 0.8, 2)
            (w_reps_num, h_reps_num), _ = cv2.getTextSize(reps_text, cv2.FONT_HERSHEY_TRIPLEX, 2, 5)
            
            panel_w = 160
            panel_h = 120
            panel_x = DISPLAY_WIDTH - panel_w - 40
            panel_y = 40
            
            draw_panel(image, panel_x, panel_y, panel_w, panel_h, NORD_NIGHT)
            cv2.putText(image, "REPS", (panel_x + (panel_w - w_reps_label) // 2, panel_y + 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, NORD_SNOW, 2, cv2.LINE_AA)
            cv2.putText(image, reps_text, (panel_x + (panel_w - w_reps_num) // 2, panel_y + 100), cv2.FONT_HERSHEY_TRIPLEX, 2, NORD_FROST_GREEN, 5, cv2.LINE_AA)

            # 2. Painel de Informações do Exercício (canto superior esquerdo)
            info_text_1 = f"Exercicio: {exercise_name.replace('_', ' ').upper()}"
            info_text_2 = f"Nivel: {level.upper()}"
            draw_panel(image, 40, 40, 350, 120, NORD_NIGHT) # Painel com tamanho fixo
            cv2.putText(image, info_text_1, (60, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.8, NORD_FROST_CYAN, 2, cv2.LINE_AA)
            cv2.putText(image, info_text_2, (60, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.8, NORD_FROST_CYAN, 2, cv2.LINE_AA)

            # 3. Painel de Feedback (centro inferior)
            feedback = current_exercise.feedback
            if feedback:
                (w, h), _ = cv2.getTextSize(feedback, cv2.FONT_HERSHEY_SIMPLEX, 1, 2)
                x_pos = (DISPLAY_WIDTH - w) // 2
                y_pos = DISPLAY_HEIGHT - 80
                draw_panel(image, x_pos - 20, y_pos - h - 10, w + 40, h + 30, NORD_NIGHT)
                feedback_color = NORD_FROST_GREEN if "Boa" in feedback else NORD_SNOW
                cv2.putText(image, feedback, (x_pos, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 1, feedback_color, 2, cv2.LINE_AA)

            # 4. Painel de Erros (canto inferior direito)
            all_errors = general_errors + current_exercise.errors
            if all_errors:
                error_panel_h = len(all_errors) * 35 + 25
                y_offset_errors = DISPLAY_HEIGHT - 40 - error_panel_h
                draw_panel(image, DISPLAY_WIDTH - 440, y_offset_errors, 400, error_panel_h, NORD_NIGHT)
                for i, error in enumerate(all_errors):
                    cv2.putText(image, f"- {error}", (DISPLAY_WIDTH - 420, y_offset_errors + 30 + i * 35), cv2.FONT_HERSHEY_SIMPLEX, 0.7, NORD_AURORA_RED, 2, cv2.LINE_AA)

            # Desenha os landmarks da pose por cima de tudo
            if results.pose_landmarks and person_detected:
                mp_drawing.draw_landmarks(
                    image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
                    mp_drawing.DrawingSpec(color=(245, 117, 66), thickness=2, circle_radius=2),
                    mp_drawing.DrawingSpec(color=(245, 66, 230), thickness=2, circle_radius=2)
                )

            cv2.imshow('FitVision - Pressione Q para Voltar ao Menu', image)

            if cv2.waitKey(10) & 0xFF == ord('q'):
                break

    cap.release()
    cv2.destroyAllWindows()
    print("Sessão encerrada. Retornando ao menu.")
