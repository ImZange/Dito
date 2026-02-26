import customtkinter as ctk


# Configuración de apariencia
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class AppEstudio(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Asistente de Estudio Inteligente")
        self.geometry("900x600")

        # Configuración de Grid
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Sidebar (Menú lateral)
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        
        self.logo_label = ctk.CTkLabel(self.sidebar, text="Mi Agenda", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.pack(pady=20)

        # Botón para sincronizar Classroom
        self.sync_button = ctk.CTkButton(self.sidebar, text="Sincronizar Classroom", command=self.sync_classroom)
        self.sync_button.pack(pady=10, padx=20)

        # Panel Principal (Lista de Tareas)
        self.main_frame = ctk.CTkScrollableFrame(self, label_text="Tareas Pendientes")
        self.main_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")

    def sync_classroom(self):
        # 1. Cambiar estado del botón para indicar carga
        self.sync_button.configure(state="disabled", text="Sincronizando...")
        self.update() # Fuerza a la interfaz a mostrar el cambio de texto
        
        # 2. Limpiar las tarjetas de tareas anteriores
        for widget in self.main_frame.winfo_children():
            widget.destroy()
            
        # 3. Llamar a la lógica de la API
        try:
            import classroom_logic
            tareas = classroom_logic.obtener_tareas()
            
            for titulo, fecha, estado in tareas:
                self.add_task_card(titulo, fecha, estado)
                
        except Exception as e:
            print(f"Error al sincronizar: {e}")
            self.add_task_card("Error de conexión", "Revisa la consola", "Fallo")
            
        # 4. Restaurar el botón
        self.sync_button.configure(state="normal", text="Sincronizar Classroom")

        self.logout_button = ctk.CTkButton(self.sidebar, text="Cerrar Sesión", command=self.logout_classroom, fg_color="#C0392B", hover_color="#922B21")
        self.logout_button.pack(pady=10, padx=20)
    
    def logout_classroom(self):
        try:
            import classroom_logic
            
            # Limpiar la pantalla de tareas actuales
            for widget in self.main_frame.winfo_children():
                widget.destroy()
                
            if classroom_logic.cerrar_sesion():
                self.add_task_card("Sesión cerrada", "El token fue eliminado.", "Info")
            else:
                self.add_task_card("Aviso", "No había ninguna sesión activa.", "Info")
                
        except Exception as e:
            print(f"Error al cerrar sesión: {e}")

    def add_task_card(self, titulo, fecha, estado):
        card = ctk.CTkFrame(self.main_frame)
        card.pack(fill="x", pady=5, padx=5)
        
        lbl_title = ctk.CTkLabel(card, text=f"{titulo} - {fecha}", font=("Arial", 14))
        lbl_title.pack(side="left", padx=10, pady=10)
        
        btn_ver = ctk.CTkButton(card, text="Ver Detalles", width=100)
        btn_ver.pack(side="right", padx=10)

if __name__ == "__main__":
    app = AppEstudio()
    app.mainloop()