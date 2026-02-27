import customtkinter as ctk
import classroom_logic
import db_logic
from datetime import datetime

# Definición de colores estilo "Material Dark"
COLORS = {
    "bg_dark": "#1A1A1A",
    "sidebar": "#252525",
    "accent": "#3498DB",
    "success": "#2ECC71",
    "danger": "#E74C3C",
    "text_main": "#FFFFFF",
    "text_dim": "#AAAAAA",
    "card_bg": "#2E2E2E",
    "card_border": "#3D3D3D"
}

class AppEstudio(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("DITO | Asistente de Estudio")
        self.geometry("1100x750")
        
        db_logic.init_db()

        # Configuración del Layout
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.configure(fg_color=COLORS["bg_dark"])

        # --- SIDEBAR PROFESIONAL ---
        self.sidebar = ctk.CTkFrame(self, width=240, corner_radius=0, fg_color=COLORS["sidebar"], border_width=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        
        self.logo_label = ctk.CTkLabel(
            self.sidebar, text="DITO", 
            font=ctk.CTkFont(family="Segoe UI", size=28, weight="bold"),
            text_color=COLORS["accent"]
        )
        self.logo_label.pack(pady=(40, 10))
        
        self.status_label = ctk.CTkLabel(
            self.sidebar, text="Ingeniería Inteligente", 
            font=ctk.CTkFont(size=11), text_color=COLORS["text_dim"]
        )
        self.status_label.pack(pady=(0, 40))

        # Botones del menú
        self.btn_sync = self.create_menu_button("Sincronizar", self.sync_classroom, COLORS["accent"])
        self.btn_logout = self.create_menu_button("Cerrar Sesión", self.logout_classroom, COLORS["danger"])

        # --- PANEL DE CONTENIDO ---
        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.grid(row=0, column=1, padx=30, pady=30, sticky="nsew")
        self.container.grid_columnconfigure(0, weight=1)
        self.container.grid_rowconfigure(1, weight=1)

        # Encabezado dinámico
        self.header_label = ctk.CTkLabel(
            self.container, text="Mis Pendientes", 
            font=ctk.CTkFont(family="Segoe UI", size=24, weight="bold"),
            anchor="w"
        )
        self.header_label.grid(row=0, column=0, sticky="w", pady=(0, 20))

        # Marco de Tareas
        self.main_frame = ctk.CTkScrollableFrame(
            self.container, 
            fg_color="transparent",
            label_text=""
        )
        self.main_frame.grid(row=1, column=0, sticky="nsew")

    def create_menu_button(self, text, command, color):
        btn = ctk.CTkButton(
            self.sidebar, text=text, command=command,
            fg_color="transparent", border_width=2, border_color=color,
            hover_color=color, text_color=COLORS["text_main"],
            font=ctk.CTkFont(size=13, weight="bold"), height=40
        )
        btn.pack(pady=10, padx=30, fill="x")
        return btn

    def sync_classroom(self):
        self.btn_sync.configure(state="disabled", text="Procesando...")
        self.update()
        
        for widget in self.main_frame.winfo_children():
            widget.destroy()
            
        try:
            tareas_api = classroom_logic.obtener_tareas()
            estados_locales = db_logic.obtener_estados_locales()
            
            # Contador de tareas para el encabezado
            pendientes_reales = [t for t in tareas_api if t[3] not in estados_locales]
            self.header_label.configure(text=f"Tareas Pendientes ({len(pendientes_reales)})")

            for titulo, materia, fecha, t_id in tareas_api:
                if t_id not in estados_locales:
                    self.add_task_card(titulo, materia, fecha, t_id)
                
        except Exception as e:
            self.add_task_card("Error de sincronización", "Verifica tu conexión", "Fallo", "err")
            
        self.btn_sync.configure(state="normal", text="Sincronizar")

    def add_task_card(self, titulo, materia, fecha, t_id):
        # Contenedor principal de la tarjeta
        card = ctk.CTkFrame(
            self.main_frame, fg_color=COLORS["card_bg"], 
            corner_radius=15, border_width=1, border_color=COLORS["card_border"]
        )
        card.pack(fill="x", pady=10, padx=5)

        # --- SECCIÓN IZQUIERDA: TEXTO ---
        info_frame = ctk.CTkFrame(card, fg_color="transparent")
        info_frame.pack(side="left", fill="both", expand=True, padx=25, pady=20)
        
        ctk.CTkLabel(
            info_frame, text=materia.upper(), 
            font=ctk.CTkFont(size=10, weight="bold"), 
            text_color=COLORS["accent"], anchor="w"
        ).pack(fill="x")

        ctk.CTkLabel(
            info_frame, text=titulo, 
            font=ctk.CTkFont(size=16, weight="bold"), 
            text_color=COLORS["text_main"], anchor="w"
        ).pack(fill="x")

        # --- SECCIÓN DERECHA: FECHA Y ACCIONES ---
        action_frame = ctk.CTkFrame(card, fg_color="transparent")
        action_frame.pack(side="right", padx=25)

        # Diseño de Fecha tipo 'Badge'
        date_badge = ctk.CTkFrame(action_frame, fg_color=COLORS["bg_dark"], corner_radius=8)
        date_badge.pack(side="left", padx=20)
        
        ctk.CTkLabel(
            date_badge, text=fecha, 
            font=ctk.CTkFont(size=12, weight="bold"),
            padx=15, pady=8
        ).pack()

        # Botones de acción minimalistas
        btn_done = ctk.CTkButton(
            action_frame, text="Completar", width=100, height=32,
            fg_color=COLORS["success"], hover_color="#27AE60",
            command=lambda: self.gestionar_local(t_id, "completado", card)
        )
        btn_done.pack(side="left", padx=5)

        btn_hide = ctk.CTkButton(
            action_frame, text="Ocultar", width=80, height=32,
            fg_color="transparent", border_width=1, border_color=COLORS["text_dim"],
            hover_color=COLORS["card_border"],
            command=lambda: self.gestionar_local(t_id, "oculto", card)
        )
        btn_hide.pack(side="left", padx=5)

    def gestionar_local(self, t_id, estado, widget):
        db_logic.guardar_estado_local(t_id, estado)
        widget.destroy()
        # Actualizar contador en el encabezado
        actual = int(self.header_label.cget("text").split("(")[1].split(")")[0])
        self.header_label.configure(text=f"Tareas Pendientes ({actual - 1})")

    def logout_classroom(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        if classroom_logic.cerrar_sesion():
            self.header_label.configure(text="Sesión Finalizada")

if __name__ == "__main__":
    app = AppEstudio()
    app.mainloop()