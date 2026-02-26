package main

import (
	"fmt"
	"os"     
	"os/exec"
)

func main() {
	fmt.Println("Arrancando Orquestador de App de Estudio...")
	cmd := exec.Command("python", "gui.py")

	// ESTO ES CLAVE: Conecta la salida de Python con la consola de Go
	cmd.Stdout = os.Stdout
	cmd.Stderr = os.Stderr

	err := cmd.Start()
	if err != nil {
		fmt.Printf("Error al iniciar el proceso: %v\n", err)
		return
	}

	fmt.Println("Interfaz de Python iniciada. Esperando eventos...")
	
	err = cmd.Wait()
	if err != nil {
		fmt.Printf("\nLa aplicación de Python reportó un error: %v\n", err)
	}
}