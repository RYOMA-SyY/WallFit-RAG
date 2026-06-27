import os
from PIL import Image, ImageDraw, ImageFont

# Set up paths
output_dir = r"c:\RIYOMA\Internship\WallfitAI\scratch\images"
os.makedirs(output_dir, exist_ok=True)

# Color palette
INDIGO = (30, 27, 75)       # #1E1B4B
PINK = (255, 77, 148)       # #FF4D94
CHARCOAL = (51, 51, 51)     # #333333
LIGHT_PINK = (255, 240, 245) # #FFF0F5
LIGHT_GREY = (245, 247, 250) # #F5F7FA
WHITE = (255, 255, 255)

# Load fonts
try:
    font_path = "arial.ttf"
    title_font = ImageFont.truetype(font_path, 20)
    normal_font = ImageFont.truetype(font_path, 14)
    bold_font = ImageFont.truetype("arialbd.ttf", 14)
    small_font = ImageFont.truetype(font_path, 11)
except IOError:
    title_font = ImageFont.load_default()
    normal_font = ImageFont.load_default()
    bold_font = ImageFont.load_default()
    small_font = ImageFont.load_default()

def draw_stick_figure(draw, x, y, label):
    # Head
    draw.ellipse([x - 15, y - 40, x + 15, y - 10], outline=INDIGO, fill=WHITE, width=2)
    # Body
    draw.line([x, y - 10, x, y + 25], fill=INDIGO, width=2)
    # Arms
    draw.line([x - 25, y, x + 25, y], fill=INDIGO, width=2)
    # Legs
    draw.line([x, y + 25, x - 15, y + 55], fill=INDIGO, width=2)
    draw.line([x, y + 25, x + 15, y + 55], fill=INDIGO, width=2)
    
    # Label
    w = draw.textlength(label, font=bold_font)
    draw.text((x - w/2, y + 65), label, fill=INDIGO, font=bold_font)

# ---------------------------------------------------------
# 1. Use Case Diagram
# ---------------------------------------------------------
def generate_use_case():
    img = Image.new("RGB", (1000, 700), WHITE)
    draw = ImageDraw.Draw(img)
    
    # Draw title
    draw.text((30, 20), "Diagramme de Cas d'Utilisation - Wallfit AI Assistant", fill=INDIGO, font=title_font)
    
    # System boundary box
    draw.rectangle([180, 80, 820, 650], outline=INDIGO, fill=LIGHT_GREY, width=3)
    draw.text((200, 95), "Système: Wallfit AI (WahibaFit RAG)", fill=PINK, font=bold_font)
    
    # Draw stick figures
    draw_stick_figure(draw, 90, 300, "Utilisatrice")
    draw_stick_figure(draw, 910, 200, "RAGEngine")
    draw_stick_figure(draw, 910, 480, "Administrateur")
    
    # Use Case Ellipses: text, y_center
    use_cases = [
        ("Poser des questions & Dialoguer (WahibaFit Chat)", 150),
        ("Écouter la réponse (Lecture Audio)", 230),
        ("Synchroniser le profil utilisateur (Laravel Context)", 320),
        ("Consulter les fiches d'entraînement", 410),
        ("Générer des fiches d'entraînement JSON (Structured Plan)", 500),
        ("Superviser l'état et évaluer l'assistant (Automated/LLM)", 590),
    ]
    
    ellipse_width = 360
    ellipse_height = 55
    x_center = 500
    
    # Store coordinates for linking
    uc_coords = []
    
    for label, y in use_cases:
        box = [x_center - ellipse_width/2, y - ellipse_height/2, x_center + ellipse_width/2, y + ellipse_height/2]
        draw.ellipse(box, fill=LIGHT_PINK, outline=PINK, width=2)
        w = draw.textlength(label, font=normal_font)
        draw.text((x_center - w/2, y - 8), label, fill=CHARCOAL, font=normal_font)
        uc_coords.append((x_center, y))
    
    # Draw link lines
    # Utilisatrice (90, 300) connects to UC 0, 1, 2, 3
    for i in [0, 1, 2, 3]:
        draw.line([130, 280, 320, uc_coords[i][1]], fill=INDIGO, width=2)
        
    # RAGEngine (910, 200) connects to UC 0, 2, 4
    for i in [0, 2, 4]:
        draw.line([870, 180, 680, uc_coords[i][1]], fill=INDIGO, width=2)
        
    # Administrateur (910, 480) connects to UC 5, 4
    for i in [4, 5]:
        draw.line([870, 480, 680, uc_coords[i][1]], fill=INDIGO, width=2)
        
    img.save(os.path.join(output_dir, "use_case_diagram.png"))
    print("Generated use_case_diagram.png")

# ---------------------------------------------------------
# 2. Sequence Diagram
# ---------------------------------------------------------
def generate_sequence():
    img = Image.new("RGB", (1000, 750), WHITE)
    draw = ImageDraw.Draw(img)
    
    # Title
    draw.text((30, 20), "Diagramme de Séquence Systèmes - Flux d'une requête RAG", fill=INDIGO, font=title_font)
    
    # Lifelines: label, x_coord
    lifelines = [
        ("Utilisatrice", 100),
        ("FastAPI (main.py)", 280),
        ("Security (security.py)", 460),
        ("RAGEngine (engine.py)", 640),
        ("ChromaDB / BM25", 820),
        ("OpenRouter (LLM)", 940)
    ]
    
    y_start = 80
    y_end = 700
    
    # Draw lifeline headers and dashed vertical lines
    for label, x in lifelines:
        # Header box
        draw.rectangle([x - 70, y_start - 25, x + 70, y_start + 15], outline=INDIGO, fill=LIGHT_GREY, width=2)
        w = draw.textlength(label, font=bold_font)
        draw.text((x - w/2, y_start - 7), label, fill=INDIGO, font=bold_font)
        
        # Dashed line
        for y in range(y_start + 15, y_end, 10):
            if y % 20 == 0:
                draw.line([x, y, x, y + 10], fill=INDIGO, width=1)
                
    # Activation bars (y_start, y_end, x)
    activations = [
        (120, 680, 100),
        (120, 670, 280),
        (150, 210, 460),
        (250, 630, 640),
        (290, 400, 820),
        (470, 600, 940)
    ]
    
    for y1, y2, x in activations:
        draw.rectangle([x - 5, y1, x + 5, y2], fill=LIGHT_PINK, outline=PINK, width=1)
        
    # Draw messages (sender_x, receiver_x, y, label, is_return)
    messages = [
        (100, 280, 130, "1. POST /v1/query {query}", False),
        (280, 460, 160, "2. sanitize_query(query)", False),
        (460, 280, 200, "3. query_clean", True),
        (280, 640, 260, "4. ask(query_clean, history)", False),
        (640, 820, 300, "5. similarity_search + BM25 retrieve", False),
        (820, 640, 390, "6. relevant_chunks", True),
        (640, 640, 430, "7. score & rerank (CrossEncoder)", False),
        (640, 940, 480, "8. send(messages: prompt + context)", False),
        (940, 640, 580, "9. yield tokens / chunk stream", True),
        (640, 280, 620, "10. yield token Stream (SSE)", True),
        (280, 100, 650, "11. Stream update to UI", True)
    ]
    
    for sx, rx, y, label, is_return in messages:
        # Line
        if is_return:
            # Dashed arrow
            for lx in range(min(sx, rx), max(sx, rx), 8):
                if lx % 16 == 0:
                    draw.line([lx, y, lx + 8, y], fill=INDIGO, width=1)
            # Arrow head
            if rx < sx:
                draw.polygon([rx + 8, y - 4, rx, y, rx + 8, y + 4], fill=INDIGO)
            else:
                draw.polygon([rx - 8, y - 4, rx, y, rx - 8, y + 4], fill=INDIGO)
        else:
            # Solid arrow
            if rx < sx:
                draw.line([sx, y, rx, y], fill=INDIGO, width=2)
                draw.polygon([rx + 8, y - 4, rx, y, rx + 8, y + 4], fill=INDIGO)
            else:
                draw.line([sx, y, rx, y], fill=INDIGO, width=2)
                draw.polygon([rx - 8, y - 4, rx, y, rx - 8, y + 4], fill=INDIGO)
                
        # Text label
        tx = min(sx, rx) + abs(sx - rx)/2
        w = draw.textlength(label, font=small_font)
        draw.text((tx - w/2, y - 13), label, fill=CHARCOAL, font=small_font)
        
    img.save(os.path.join(output_dir, "sequence_diagram.png"))
    print("Generated sequence_diagram.png")

# ---------------------------------------------------------
# 3. Class Diagram
# ---------------------------------------------------------
def generate_class_diagram():
    img = Image.new("RGB", (1000, 750), WHITE)
    draw = ImageDraw.Draw(img)
    
    # Title
    draw.text((30, 20), "Diagramme de Classe - Moteur Wallfit AI RAG", fill=INDIGO, font=title_font)
    
    # Define classes structure: name, fields[], methods[], x, y, w, h
    classes = [
        {
            "name": "Settings",
            "fields": [
                "+ chroma_persist_dir: str",
                "+ model_id: str",
                "+ embed_model: str",
                "+ rerank_model: str",
                "+ context_char_limit: int",
                "+ max_query_length: int",
                "+ openai_api_key: str",
                "+ openai_model: str"
            ],
            "methods": [],
            "x": 50, "y": 80, "w": 250, "h": 220
        },
        {
            "name": "Security",
            "fields": [
                "+ INJECTION_PATTERNS: list",
                "+ COMPILED_PATTERNS: list"
            ],
            "methods": [
                "+ sanitize_query(q, max_len): str"
            ],
            "x": 380, "y": 80, "w": 280, "h": 140
        },
        {
            "name": "SessionManager",
            "fields": [
                "+ sessions: dict",
                "+ contexts: dict",
                "+ max_history: int"
            ],
            "methods": [
                "+ get_history(id): list",
                "+ add_message(id, r, c)",
                "+ set_context(id, ctx)",
                "+ get_context(id): dict"
            ],
            "x": 710, "y": 80, "w": 250, "h": 180
        },
        {
            "name": "RAGEngine",
            "fields": [
                "+ settings: Settings",
                "+ vector_db: Chroma",
                "+ tokenizer: AutoTokenizer",
                "+ llm: HuggingFacePipeline",
                "+ _reranker: CrossEncoder",
                "+ _bm25_by_db: dict"
            ],
            "methods": [
                "+ load_vector_store()",
                "+ load_generator()",
                "+ score_and_filter_docs(q): tuple",
                "+ ask(q, hist, ctx, stream): res",
                "+ summarize_session(hist): dict",
                "+ extract_metrics(hist): dict",
                "+ generate_structured_plan(hist): dict",
                "- _generate(msgs, stream): str/gen"
            ],
            "x": 320, "y": 320, "w": 380, "h": 360
        }
    ]
    
    for cls in classes:
        x, y, w, h = cls["x"], cls["y"], cls["w"], cls["h"]
        # Outer box
        draw.rectangle([x, y, x + w, y + h], outline=INDIGO, fill=LIGHT_GREY, width=2)
        # Header box
        draw.rectangle([x, y, x + w, y + 30], outline=INDIGO, fill=LIGHT_PINK, width=2)
        # Class name
        tw = draw.textlength(cls["name"], font=bold_font)
        draw.text((x + w/2 - tw/2, y + 7), cls["name"], fill=INDIGO, font=bold_font)
        
        # Fields
        yf = y + 40
        for field in cls["fields"]:
            draw.text((x + 10, yf), field, fill=CHARCOAL, font=small_font)
            yf += 18
            
        # Divider line if methods exist
        if cls["methods"]:
            draw.line([x, yf + 5, x + w, yf + 5], fill=INDIGO, width=1)
            yf += 15
            for method in cls["methods"]:
                draw.text((x + 10, yf), method, fill=CHARCOAL, font=small_font)
                yf += 18
                
    # Draw connections
    # RAGEngine uses Settings (line from 320, 500 to 175, 300)
    draw.line([320, 500, 175, 500, 175, 300], fill=INDIGO, width=2)
    # Arrow head (diamond for aggregation/association or regular arrow)
    draw.polygon([320, 500, 310, 495, 300, 500, 310, 505], fill=INDIGO) # Diamond at RAGEngine
    
    # RAGEngine uses Security (line from 510, 320 to 510, 220)
    draw.line([510, 320, 510, 220], fill=INDIGO, width=2)
    draw.polygon([510, 220, 505, 230, 515, 230], fill=INDIGO) # Arrow pointing to Security
    
    # RAGEngine interacts with SessionManager (FastAPI routes them)
    # Just draw dependency line from SessionManager to RAGEngine or vice versa
    
    img.save(os.path.join(output_dir, "class_diagram.png"))
    print("Generated class_diagram.png")

# ---------------------------------------------------------
# 4. Organigramme de l'entreprise
# ---------------------------------------------------------
def generate_organigram():
    img = Image.new("RGB", (900, 500), WHITE)
    draw = ImageDraw.Draw(img)
    
    # Title
    draw.text((30, 20), "Organigramme Opérationnel du Projet W.ALLfit", fill=INDIGO, font=title_font)
    
    # Boxes: label, title, x, y, w, h
    boxes = [
        {"name": "M. Ali", "title": "Co-fondateur & Co-encadrant", "x": 350, "y": 80, "w": 200, "h": 70, "color": LIGHT_PINK, "border": PINK},
        {"name": "M. Abdlhak Fadili", "title": "Encadrant Pédagogique", "x": 70, "y": 200, "w": 200, "h": 70, "color": LIGHT_GREY, "border": INDIGO},
        {"name": "M. Ali (Startup W.ALLfit)", "title": "Encadrant Professionnel", "x": 630, "y": 200, "w": 200, "h": 70, "color": LIGHT_GREY, "border": INDIGO},
        {"name": "Stagiaire (BTS DAI)", "title": "Développeur RAG / DAI", "x": 350, "y": 340, "w": 200, "h": 70, "color": LIGHT_PINK, "border": PINK}
    ]
    
    for box in boxes:
        bx, by, bw, bh = box["x"], box["y"], box["w"], box["h"]
        draw.rectangle([bx, by, bx + bw, by + bh], outline=box["border"], fill=box["color"], width=2)
        
        tw1 = draw.textlength(box["name"], font=bold_font)
        draw.text((bx + bw/2 - tw1/2, by + 15), box["name"], fill=INDIGO, font=bold_font)
        
        tw2 = draw.textlength(box["title"], font=small_font)
        draw.text((bx + bw/2 - tw2/2, by + 40), box["title"], fill=CHARCOAL, font=small_font)
        
    # Connections
    # Top box (350+100, 150) -> Middle path
    draw.line([450, 150, 450, 340], fill=INDIGO, width=2)
    # Pédagogique (270, 235) -> middle line (350, 235)
    draw.line([270, 235, 350, 235], fill=INDIGO, width=2)
    draw.polygon([350, 235, 340, 230, 340, 240], fill=INDIGO)
    
    # Professionnel (630, 235) -> middle line (550, 235)
    draw.line([630, 235, 550, 235], fill=INDIGO, width=2)
    draw.polygon([550, 235, 560, 230, 560, 240], fill=INDIGO)
    
    img.save(os.path.join(output_dir, "organigramme.png"))
    print("Generated organigramme.png")

# ---------------------------------------------------------
# 5. Startup Logo (W.ALLfit Logo)
# ---------------------------------------------------------
def generate_wallfit_logo():
    img = Image.new("RGB", (400, 400), WHITE)
    draw = ImageDraw.Draw(img)
    
    # Draw an abstract dumbbell with pink/indigo gradient
    # Left weight
    draw.rounded_rectangle([80, 120, 130, 280], radius=15, fill=INDIGO, outline=PINK, width=2)
    # Right weight
    draw.rounded_rectangle([270, 120, 320, 280], radius=15, fill=INDIGO, outline=PINK, width=2)
    # Bar
    draw.rectangle([130, 185, 270, 215], fill=PINK)
    
    # Add a glowing pink circle in the center
    draw.ellipse([175, 175, 225, 225], fill=PINK, outline=INDIGO, width=3)
    
    # Write text W.ALLfit
    text = "W.ALLfit"
    try:
        logo_font = ImageFont.truetype("arialbd.ttf", 36)
    except IOError:
        logo_font = ImageFont.load_default()
    w = draw.textlength(text, font=logo_font)
    draw.text((200 - w/2, 310), text, fill=INDIGO, font=logo_font)
    
    text_sub = "HEALTH & AI COACHING"
    try:
        logo_sub_font = ImageFont.truetype("arial.ttf", 14)
    except IOError:
        logo_sub_font = ImageFont.load_default()
    w_sub = draw.textlength(text_sub, font=logo_sub_font)
    draw.text((200 - w_sub/2, 355), text_sub, fill=PINK, font=logo_sub_font)
    
    img.save(os.path.join(output_dir, "wallfit_logo.png"))
    print("Generated wallfit_logo.png")

# ---------------------------------------------------------
# 6. Moroccan Ministry / BTS Logo Placeholder
# ---------------------------------------------------------
def generate_ministry_logo():
    img = Image.new("RGB", (400, 400), WHITE)
    draw = ImageDraw.Draw(img)
    
    # Stylized Moroccan star (green pentagram) in center with gold accents
    # Center: (200, 180)
    # Draw gold seal circle
    draw.ellipse([80, 60, 320, 300], outline=(197, 160, 89), width=4) # Gold
    
    # Draw green star (pentagram)
    # Coordinates of pentagram points
    # 0: top, 1: outer-right, 2: bottom-right, 3: bottom-left, 4: outer-left
    points = [
        (200, 95),   # Top
        (280, 235),  # Bottom-Right
        (150, 150),  # Top-Left-ish
        (250, 150),  # Top-Right-ish
        (120, 235),  # Bottom-Left
    ]
    # Reorder to draw star in single path: 0 -> 1 -> 3 -> 4 -> 2 -> 0?
    # No, standard 5-point star path: 0 -> 2 -> 4 -> 1 -> 3 -> 0
    star_path = [points[0], points[1], points[3], points[4], points[2], points[0]]
    # Connect them
    for i in range(len(star_path)-1):
        draw.line([star_path[i], star_path[i+1]], fill=(16, 124, 65), width=6) # Moroccan Green
        
    # Draw crown above star
    draw.polygon([(170, 75), (180, 60), (200, 70), (220, 60), (230, 75)], fill=(197, 160, 89))
    
    # Text
    text1 = "ROYAUME DU MAROC"
    text2 = "MINISTÈRE DE L'ÉDUCATION NATIONALE"
    text3 = "BREVET DE TECHNICIEN SUPÉRIEUR"
    
    w1 = draw.textlength(text1, font=small_font)
    draw.text((200 - w1/2, 315), text1, fill=INDIGO, font=bold_font)
    
    w2 = draw.textlength(text2, font=small_font)
    draw.text((200 - w2/2, 335), text2, fill=CHARCOAL, font=small_font)
    
    w3 = draw.textlength(text3, font=small_font)
    draw.text((200 - w3/2, 355), text3, fill=PINK, font=bold_font)
    
    img.save(os.path.join(output_dir, "ministry_logo.png"))
    print("Generated ministry_logo.png")

# ---------------------------------------------------------
# 7. Document Indexing Activity Diagram
# ---------------------------------------------------------
def generate_activity_diagram():
    img = Image.new("RGB", (900, 800), WHITE)
    draw = ImageDraw.Draw(img)
    
    # Title
    draw.text((30, 20), "Diagramme d'Activités - Flux d'Indexation des Documents", fill=INDIGO, font=title_font)
    
    # Helper to draw a rounded box with text
    def draw_action_box(label, x, y, w, h, bg_color=LIGHT_GREY, border_color=INDIGO):
        draw.rounded_rectangle([x, y, x + w, y + h], radius=8, outline=border_color, fill=bg_color, width=2)
        lines = label.split('\n')
        line_height = 16
        total_h = len(lines) * line_height
        start_y = y + (h - total_h)/2
        for idx, line in enumerate(lines):
            lw = draw.textlength(line, font=normal_font)
            draw.text((x + w/2 - lw/2, start_y + idx * line_height), line, fill=CHARCOAL, font=normal_font)

    # 1. Start node
    draw.ellipse([440, 70, 460, 90], fill=INDIGO)
    
    # Arrow from Start to Box 1
    draw.line([450, 90, 450, 120], fill=INDIGO, width=2)
    draw.polygon([450, 120, 445, 112, 455, 112], fill=INDIGO)
    
    # Box 1: Ingestion
    draw_action_box("1. Ingestion des Documents\n(PDF, Docx, CSV, Articles de Fitness, Guides W.ALLfit)", 200, 120, 500, 50)
    
    # Arrow to Box 2
    draw.line([450, 170, 450, 200], fill=INDIGO, width=2)
    draw.polygon([450, 200, 445, 192, 455, 192], fill=INDIGO)
    
    # Box 2: Cleaning (PII)
    draw_action_box("2. Nettoyage de Sécurité & Anonymisation\n(Masquage Regex des PII : emails, téléphones, etc.)", 200, 200, 500, 50, LIGHT_PINK, PINK)
    
    # Arrow to Box 3
    draw.line([450, 250, 450, 280], fill=INDIGO, width=2)
    draw.polygon([450, 280, 445, 272, 455, 272], fill=INDIGO)
    
    # Box 3: Splitter
    draw_action_box("3. Segmentation de Texte (RecursiveTextSplitter)\n(Chunks de 2800 caractères / Recouvrement de 400)", 200, 280, 500, 50)
    
    # Arrow to Fork
    draw.line([450, 330, 450, 370], fill=INDIGO, width=2)
    draw.polygon([450, 370, 445, 362, 455, 362], fill=INDIGO)
    
    # Fork Bar
    draw.line([200, 370, 700, 370], fill=INDIGO, width=6)
    
    # Arrow from Fork to Left branch (x=300)
    draw.line([300, 370, 300, 420], fill=INDIGO, width=2)
    draw.polygon([300, 420, 295, 412, 305, 412], fill=INDIGO)
    
    # Left Branch Action A1: Embedding
    draw_action_box("4A. Indexation Dense (Sémantique)\n- Vectorisation avec all-MiniLM-L6-v2\n- Insertion dans ChromaDB SQLite", 100, 420, 320, 70)
    
    # Arrow from Fork to Right branch (x=600)
    draw.line([600, 370, 600, 420], fill=INDIGO, width=2)
    draw.polygon([600, 420, 595, 412, 605, 412], fill=INDIGO)
    
    # Right Branch Action B1: BM25
    draw_action_box("4B. Indexation Sparse (Lexicale)\n- Indexation de mots-clés BM25\n- Sauvegarde dans chunks.pkl", 480, 420, 320, 70)
    
    # Arrow from Left Branch to Join
    draw.line([260, 490, 260, 540], fill=INDIGO, width=2)
    draw.polygon([260, 540, 255, 532, 265, 532], fill=INDIGO)
    
    # Arrow from Right Branch to Join
    draw.line([640, 490, 640, 540], fill=INDIGO, width=2)
    draw.polygon([640, 540, 635, 532, 645, 532], fill=INDIGO)
    
    # Join Bar
    draw.line([200, 540, 700, 540], fill=INDIGO, width=6)
    
    # Arrow from Join to Box 5
    draw.line([450, 540, 450, 590], fill=INDIGO, width=2)
    draw.polygon([450, 590, 445, 582, 455, 582], fill=INDIGO)
    
    # Box 5: Database Ready
    draw_action_box("5. Base de Données RAG Hybride Opérationnelle\n- ChromaDB et index BM25 prêts pour les requêtes\n- Reranking Cross-Encoder activé pour le filtrage final", 200, 590, 500, 60, LIGHT_PINK, PINK)
    
    # Arrow from Box 5 to End
    draw.line([450, 650, 450, 700], fill=INDIGO, width=2)
    draw.polygon([450, 700, 445, 692, 455, 692], fill=INDIGO)
    
    # End node: circle with outer ring
    draw.ellipse([438, 700, 462, 724], outline=INDIGO, width=2)
    draw.ellipse([442, 704, 458, 720], fill=INDIGO)
    
    img.save(os.path.join(output_dir, "activity_diagram.png"))
    print("Generated activity_diagram.png")

if __name__ == "__main__":
    generate_use_case()
    generate_sequence()
    generate_class_diagram()
    generate_organigram()
    generate_wallfit_logo()
    generate_ministry_logo()
    generate_activity_diagram()
    print("All assets generated successfully!")
