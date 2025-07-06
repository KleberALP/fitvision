# crossfit-ai-coach

## Sistema Inteligente de Análise de Movimentos para CrossFit

Este repositório contém um projeto de Visão Computacional e Inteligência Artificial desenvolvido para oferecer feedback em tempo real e contagem de repetições para exercícios de CrossFit. O objetivo principal é ajudar atletas a aprimorar a forma, prevenir lesões e acompanhar o progresso com precisão. Atualmente, o sistema foca na **análise detalhada do agachamento (Squat)**, com planos de expansão para outros movimentos.

---

### Informações da Disciplina e Grupo

**Trabalho para a matéria de:** `[2025/1 BSI] Inteligência Artificial`
**Professor:** Sergio Nery Simoes

**Integrantes do Grupo:**

* Arthur Cremasco Amaral - 20212bsi0170
* João Marcos Rodrigues Pimentel - 20221bsi0170
* Kleber André Lirio Picoli - 20182bsi0515
* Manoel Rodrigues Loureiro - 20181bsi0431
* Renato Marques Teixeira Ferreira - 20171bsi0359
* Vinícius Gomes Caetano - 20221bsi0285

---

### Funcionalidades Atuais

* **Contagem de Repetições:** Precisão na contagem de agachamentos completos para diferentes níveis (Iniciante, Médio, Olímpico).
* **Feedback de Forma em Tempo Real:** Alertas visuais e textuais para erros comuns como:
    * Coluna curvada.
    * Joelho ultrapassando a ponta do pé.
    * Profundidade insuficiente no agachamento (ajustável por nível).
* **Filtragem Inteligente de Pose:** Evita contagens falsas e ruídos ao exigir a detecção de uma pose de corpo inteiro com visibilidade suficiente dos pontos-chave, garantindo que apenas pessoas reais e bem posicionadas sejam processadas.
* **Seleção de Nível:** Permite ajustar a dificuldade e os requisitos de profundidade do agachamento (`"beginner"`, `"medium"`, `"olympic"`).

### Tecnologias Utilizadas

* **Python:** Linguagem de programação principal.
* **MediaPipe Pose:** Framework do Google para detecção de pose humana de alta fidelidade em tempo real.
* **OpenCV (cv2):** Biblioteca amplamente utilizada para processamento de imagem e vídeo.
* **NumPy:** Biblioteca fundamental para operações numéricas e array multidimensionais.

### Instalação

Para configurar o ambiente e rodar o projeto em sua máquina, siga os passos abaixo:

1.  **Clone o repositório:**
    ```bash
    git clone [https://github.com/SEU_USUARIO/crossfit-ai-coach.git](https://github.com/SEU_USUARIO/crossfit-ai-coach.git) # Lembre-se de alterar SEU_USUARIO pelo seu usuário do GitHub e o nome do repositório se for diferente.
    cd crossfit-ai-coach
    ```
2.  **Crie e ative um ambiente virtual (altamente recomendado):**
    ```bash
    python -m venv venv
    # No Windows:
    .\venv\Scripts\activate
    # No macOS/Linux:
    source venv/bin/activate
    ```
3.  **Instale as dependências:**
    ```bash
    pip install mediapipe opencv-python numpy
    ```

### Como Rodar o Projeto

Após a instalação das dependências e com o ambiente virtual ativado:

1.  Certifique-se de que sua webcam está conectada e disponível para uso.
2.  Execute o arquivo principal do projeto:
    ```bash
    python main.py
    ```
3.  Uma janela com a visualização da sua câmera será aberta. Para encerrar o programa, basta pressionar a tecla `q` a qualquer momento.

### Uso

* **Posicionamento Ideal:** Para que o sistema funcione corretamente, é crucial que seu **corpo esteja completamente visível** para a câmera (da cabeça aos pés). Mantenha uma distância adequada da câmera para garantir um enquadramento completo. Uma boa iluminação ambiente é fundamental para a precisão da detecção de pose.
* **Seleção de Nível:** No arquivo `main.py`, você pode ajustar a variável `selected_level` (no início do código) para escolher a dificuldade do agachamento que deseja praticar: `"beginner"` (iniciante), `"medium"` (médio) ou `"olympic"` (olímpico/completo).
* **Feedback Visual:** Observe as mensagens exibidas na tela. Elas fornecerão a contagem das repetições e alertas em tempo real sobre a sua forma, ajudando-o a corrigir erros durante o exercício.

### Próximos Passos (Futuras Expansões)

* Adicionar suporte para a análise de outros movimentos de CrossFit e exercícios funcionais.
* Desenvolver funcionalidades para registro de sessões de treino e visualização gráfica do progresso ao longo do tempo.
* Melhorar a robustez da detecção de pose em diversas condições de iluminação e diferentes ângulos de câmera.
* Implementar uma Interface Gráfica do Usuário (GUI) para uma experiência mais intuitiva e amigável.
* Integrar modelos de Machine Learning mais avançados para reconhecimento de padrões de movimento complexos.

---

Feito por **Grupo IA - 2025/1 BSI**