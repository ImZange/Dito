import customtkinter as ctk
import classroom_logic
import db_logic
import threading

# Configuración de apariencia
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class AppEstudio(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("DITO | Asistente de Estudio")
        self.geometry("1100x750")
        
        # Inicializar base de datos local
        db_logic.init_db()
        
        # Atributo para rastrear el progreso de la sesión
        self.tareas_completadas_hoy = 0

        # Layout Principal
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- Sidebar (Menú Lateral) ---
        self.sidebar = ctk.CTkFrame(self, width=220, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        
        ctk.CTkLabel(self.sidebar, text="DITO", font=("Segoe UI", 26, "bold"), text_color="#3498DB").pack(pady=30)
        
        # Botones Principales del Menú
        self.btn_pendientes = ctk.CTkButton(
            self.sidebar, text="Mis Pendientes", border_color="blue", 
            font=("Segoe UI", 13, "bold"), height=40, command=self.mostrar_pendientes
        )
        self.btn_pendientes.pack(pady=10, padx=20, fill="x")

        # Botón Ayudante (Sin funcionalidad por ahora)
        self.btn_ayudante = ctk.CTkButton(
            self.sidebar, text="Ayudante", fg_color="transparent", border_width=2, 
            border_color="#9B59B6", text_color="white", font=("Segoe UI", 13, "bold"), 
            height=40, command=self.placeholder_function
        )
        self.btn_ayudante.pack(pady=10, padx=20, fill="x")

        # Botón Focus Mode (Sin funcionalidad por ahora)
        self.btn_focus = ctk.CTkButton(
            self.sidebar, text="Focus Mode", fg_color="transparent", border_width=2, 
            border_color="#E67E22", text_color="white", font=("Segoe UI", 13, "bold"), 
            height=40, command=self.placeholder_function
        )
        self.btn_focus.pack(pady=10, padx=20, fill="x")

        # Espaciador para empujar el botón de cerrar sesión al fondo
        self.spacer = ctk.CTkLabel(self.sidebar, text="")
        self.spacer.pack(expand=True, fill="both")

        # Botón de Cerrar Sesión
        self.btn_logout = ctk.CTkButton(
            self.sidebar, text="Cerrar Sesión", fg_color="#C0392B", 
            hover_color="#922B21", font=("Segoe UI", 13, "bold"), 
            height=40, command=self.logout_classroom
        )
        self.btn_logout.pack(pady=20, padx=20, fill="x")

        # --- Contenedor de Contenido ---
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.grid(row=0, column=1, padx=30, pady=30, sticky="nsew")
        self.main_container.grid_columnconfigure(0, weight=1)

        # Encabezado y Contador Dinámico
        self.lbl_count = ctk.CTkLabel(self.main_container, text="Mis Pendientes (0)", font=("Segoe UI", 22, "bold"))
        self.lbl_count.pack(anchor="w", pady=(0, 10))

        # Barra de Progreso Dinámica
        self.progress = ctk.CTkProgressBar(self.main_container, orientation="horizontal", height=12)
        self.progress.pack(fill="x", pady=(0, 20))
        self.progress.set(0)

        # Botonera de Acciones
        self.btn_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.btn_frame.pack(fill="x", pady=(0, 20))

        self.btn_add = ctk.CTkButton(self.btn_frame, text="+ Agregar Pendiente", command=self.agregar_manual)
        self.btn_add.pack(side="left", padx=5)

        self.btn_sync = ctk.CTkButton(self.btn_frame, text="Sincronizar Classroom", fg_color="#5D6D7E", command=self.sync_classroom)
        self.btn_sync.pack(side="left", padx=5)

        # Marco Deslizable para Tareas
        self.tasks_frame = ctk.CTkScrollableFrame(self.main_container, fg_color="transparent")
        self.tasks_frame.pack(fill="both", expand=True)

    def placeholder_function(self):
        """Función temporal para botones sin funcionalidad actual."""
        print("Esta función estará disponible en futuras actualizaciones del proyecto.")

    def mostrar_pendientes(self):
        """Refresca la vista de tareas (puedes añadir lógica de navegación aquí luego)."""
        self.sync_classroom()

    def logout_classroom(self):
        """Limpia la sesión y cierra la app."""
        if classroom_logic.cerrar_sesion():
            self.destroy()

    def agregar_manual(self):
        """Captura nombre y fecha para la nueva tarea manual."""
        dialog_n = ctk.CTkInputDialog(text="¿Qué tarea deseas agregar?", title="Nueva Tarea")
        nombre = dialog_n.get_input()
        
        if nombre:
            dialog_f = ctk.CTkInputDialog(text="Fecha de entrega (ej: Hoy, Mañana, 05/03):", title="Asignar Fecha")
            fecha = dialog_f.get_input()
            if not fecha: fecha = "Hoy"
            
            db_logic.guardar_tarea_manual(nombre, "Manual", fecha)
            self.sync_classroom()

    def sync_classroom(self):
        """Inicia la sincronización en un hilo secundario para evitar bloqueos."""
        self.btn_sync.configure(state="disabled", text="Sincronizando...")
        threading.Thread(target=self._worker_sync, daemon=True).start()

    def _worker_sync(self):
        """Procesa los datos en segundo plano."""
        try:
            api_data = classroom_logic.obtener_tareas()
            manual_data = db_logic.obtener_tareas_manuales()
            locales = db_logic.obtener_estados_locales()
            self.after(0, self._update_ui, api_data, manual_data, locales)
        except Exception as e:
            print(f"Error en sincronización: {e}")
            self.after(0, lambda: self.btn_sync.configure(state="normal", text="Reintentar"))

    def _update_ui(self, api, manual, locales):
        """Actualiza la interfaz y calcula el progreso inicial."""
        for w in self.tasks_frame.winfo_children(): w.destroy()
        
        pendientes_api = [t for t in api if len(t) > 3 and t[3] not in locales]
        total_actual = len(pendientes_api) + len(manual)
        
        self.lbl_count.configure(text=f"Mis Pendientes ({total_actual})")
        self.actualizar_barra_progreso(total_actual)

        for t in pendientes_api: self.add_task_card(t[0], t[1], t[2], t[3], "api")
        for m in manual: self.add_task_card(m[0], m[1], m[2], m[3], "manual")
        
        self.btn_sync.configure(state="normal", text="Sincronizar Classroom")

    def actualizar_barra_progreso(self, pendientes):
        """Calcula el porcentaje completado: Hechas / (Hechas + Pendientes)."""
        if pendientes == 0:
            self.progress.set(1.0)
        else:
            total_estimado = pendientes + self.tareas_completadas_hoy
            porcentaje = self.tareas_completadas_hoy / total_estimado
            self.progress.set(porcentaje)

    def add_task_card(self, titulo, materia, fecha, t_id, tipo):
        """Crea una tarjeta visual para la tarea."""
        card = ctk.CTkFrame(self.tasks_frame, corner_radius=12, border_width=1, border_color="#3D3D3D")
        card.pack(fill="x", pady=8, padx=5)
        
        info = ctk.CTkFrame(card, fg_color="transparent")
        info.pack(side="left", padx=20, pady=15)
        
        ctk.CTkLabel(info, text=materia.upper(), font=("Arial", 9, "bold"), text_color="#3498DB").pack(anchor="w")
        ctk.CTkLabel(info, text=titulo, font=("Arial", 15, "bold")).pack(anchor="w")
        ctk.CTkLabel(info, text=f"Entrega: {fecha}", font=("Arial", 11), text_color="#AAAAAA").pack(anchor="w")

        btn_done = ctk.CTkButton(card, text="✓", width=45, fg_color="#2ECC71", hover_color="#27AE60",
                                command=lambda: self.completar(t_id, tipo, card))
        btn_done.pack(side="right", padx=20)

    def completar(self, t_id, tipo, widget):
        """Marca como completada, actualiza la sesión y la barra."""
        if tipo == "api": 
            db_logic.guardar_estado_local(t_id, "completado")
        else: 
            db_logic.marcar_manual_completada(t_id)
            
        widget.destroy()
        self.tareas_completadas_hoy += 1
        
        try:
            actual = int(self.lbl_count.cget("text").split("(")[1].split(")")[0]) - 1
            self.lbl_count.configure(text=f"Mis Pendientes ({actual})")
            self.actualizar_barra_progreso(actual)
        except:
            self.sync_classroom()

if __name__ == "__main__":
    app = AppEstudio()
    app.mainloop()

#a